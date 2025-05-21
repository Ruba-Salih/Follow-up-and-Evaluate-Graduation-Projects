from django.shortcuts import render
from django.http import JsonResponse
from form.models import EvaluationForm, MainCategory  # Adjust if the model is named differently
from project.models import Project, ProjectMembership, StudentProjectMembership  # Assuming the project model is called Project
from .models import Grade, IndividualGrade, Grading, MemberGrade, MemberIndividualGrade  # Adjust according to your model names
from users.models import Role
from users.models import Student
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
import uuid
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from collections import defaultdict
from .models import Grading
from university.models import Department
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Count, Max
from django.http import HttpResponseForbidden



def grade_form(request, project_id):
    project = Project.objects.get(id=project_id)
    user = request.user

    # Check membership and get role
    project_membership = ProjectMembership.objects.filter(user=user, project=project).first()
    if not project_membership:
        return render(request, 'access_denied.html', {"message": "You are not authorized to grade this project."})

    user_role = project_membership.role
    form = EvaluationForm.objects.filter(target_role=user_role).first()
    supervisor_membership = ProjectMembership.objects.filter(project=project, role__name="Supervisor").first()
    if supervisor_membership:
        supervisor = supervisor_membership.user
    else:
        supervisor = None
    print(f"Supervisor is: {supervisor}")

    if not form:
        return render(request, 'access_denied.html', {"message": "No form available for your role in this project."})

    print(f"evaluation_form_id: {form.id}")
    main_categories = form.main_categories.all()
    students = Student.objects.filter(project_membership__project=project)
    department = supervisor.department
    college = department.college
    university = college.university

    context = {
        'university_name': university.name,
        'college_name': college.name,
        'project': project,
        'form': form,
        'main_categories': main_categories,
        'students': students,
        'form_name': form.name,
        'supervisor_name': supervisor.get_full_name(),
        'project_name': project.name,
        'evaluation_form_id': form.id,
    }

    return render(request, 'forms/form.html', context)



def generate_id(prefix, evaluation_form_id, grade_id, student_id):
    return f"{prefix}-{evaluation_form_id}-{grade_id}-{student_id}-{uuid.uuid4().hex[:6].upper()}"



@login_required
def submit_grades(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user = request.user

    if request.method == 'POST':
        evaluation_form_id = request.POST.get('evaluation_form_id')
        if not evaluation_form_id:
            return HttpResponse("Evaluation form ID is missing!", status=400)

        try:
            evaluation_form = EvaluationForm.objects.get(id=evaluation_form_id)
        except EvaluationForm.DoesNotExist:
            return HttpResponse("Evaluation form not found!", status=404)

        main_categories = evaluation_form.main_categories.all()
        if not main_categories:
            return HttpResponse("This evaluation form does not have any main categories.", status=400)

        try:
            membership = ProjectMembership.objects.get(user=request.user, project=project)
            role = membership.role
        except ProjectMembership.DoesNotExist:
            return HttpResponse("You are not assigned to this project!", status=403)

        students = Student.objects.filter(project_membership__project=project).distinct()

        with transaction.atomic():
            student_grade_tracker = {student.id: [] for student in students}

            for main_category in main_categories:
                if main_category.grade_type == 'individual':
                    for student in students:
                        grade_key = f'grade_{main_category.id}_student_{student.id}'
                        grade_value = request.POST.get(grade_key)

                        if grade_value:
                            try:
                                grade_value = float(grade_value)
                                grade_value = round(grade_value, 2)  # round raw grade
                                weighted_grade = round(grade_value * main_category.weight, 2)  # round weighted
                                
                                # Check if individual grade exists by this user
                                existing_mig = MemberIndividualGrade.objects.filter(
                                    member=user,
                                    individual_grade__evaluation_form=evaluation_form,
                                    individual_grade__student=student,
                                    individual_grade__grade__main_category=main_category,
                                    individual_grade__grade__project=project,
                                ).first()

                                if existing_mig:
                                    # Update existing
                                    individual_grade = existing_mig.individual_grade
                                    individual_grade.final_grade = weighted_grade
                                    individual_grade.grade.grade = grade_value
                                    individual_grade.grade.final_grade = weighted_grade
                                    individual_grade.grade.save()
                                    individual_grade.save()
                                else:
                                    # Create new
                                    grade = Grade.objects.create(
                                        grade=grade_value,
                                        final_grade=weighted_grade,
                                        evaluation_form=evaluation_form,
                                        project=project,
                                        main_category=main_category,
                                    )

                                    individual_grade = IndividualGrade.objects.create(
                                        evaluation_form=evaluation_form,
                                        grade=grade,
                                        final_grade=weighted_grade,
                                        student=student,
                                    )

                                    MemberIndividualGrade.objects.create(
                                        member=user,
                                        individual_grade=individual_grade
                                    )

                                student_grade_tracker[student.id].append(weighted_grade)

                            except ValueError:
                                return HttpResponse(f"Invalid grade value for student {student.id} in category {main_category.id}", status=400)

                elif main_category.grade_type == 'group':
                    grade_key = f'grade_{main_category.id}'
                    grade_value = request.POST.get(grade_key)

                    if grade_value:
                        try:
                            grade_value = float(grade_value)
                            grade_value = round(grade_value, 2)  # round raw grade
                            weighted_grade = round(grade_value * main_category.weight, 2)  # round weighted

                            # Check if grade exists by this user for this main category
                            existing_mg = MemberGrade.objects.filter(
                                member=user,
                                grade__evaluation_form=evaluation_form,
                                grade__main_category=main_category,
                                grade__project=project
                            ).first()

                            if existing_mg:
                                grade = existing_mg.grade
                                grade.grade = grade_value
                                grade.final_grade = weighted_grade
                                grade.save()
                            else:
                                grade = Grade.objects.create(
                                    grade=grade_value,
                                    final_grade=weighted_grade,
                                    evaluation_form=evaluation_form,
                                    project=project,
                                    main_category=main_category,
                                )
                                MemberGrade.objects.create(
                                    member=user,
                                    grade=grade,
                                )

                            for student in students:
                                student_grade_tracker[student.id].append(weighted_grade)

                        except ValueError:
                            return HttpResponse(f"Invalid grade value for group in category {main_category.id}", status=400)

            # Compute and save final aggregated grade per student
            for student in students:
                final_grade = calculate_final_grade(student, project)

        return JsonResponse({'success': True, 'project_name': project.name})

    return redirect('grade_form', project_id=project_id)


@login_required
def grade_success(request, project_id):
    # Get the project based on project_id
    project = get_object_or_404(Project, id=project_id)
    
    # Render the success template with the project context
    return render(request, 'forms/grade_success.html', {'project': project})

#funtion to convert to the nearst up 14.5 -> 15
def round_half_up(n):
    return int(Decimal(n).quantize(0, rounding=ROUND_HALF_UP))

#function to give the Role grade as his weight
def convert_total(raw_total, role_name):
    """Convert raw total grade using the actual grade of the form and the form's weight."""
    role_name = str(role_name).strip().lower()

    if raw_total is None:
        return 0

    # Try to get the role object
    try:
        role = Role.objects.get(name__iexact=role_name)  # Adjust if the role field is different
    except Role.DoesNotExist:
        return 0  # If the role doesn't exist, return 0

    # Get the evaluation form associated with this role
    form = EvaluationForm.objects.filter(target_role=role).first()  # Get the first form with the role

    if not form:
        return 0  # If no form found, return 0

    # Extract the form's weight
    form_weight = form.form_weight

    # If form weight is 0 or None, return 0 to avoid division by zero
    if form_weight <= 0:
        return 0

    # Calculate the actual grade by summing MainCategory weights multiplied by their respective numbers
    actual_grade = sum(cat.weight * 10 for cat in form.main_categories.all())

    # If actual_grade is 0, return 0 to avoid division by zero
    if actual_grade == 0:
        return 0

    # Normalize the raw_total based on the actual grade and form weight
    converted_grade = (raw_total / actual_grade) * form_weight

    # Return the converted grade rounded to nearst number
    return round_half_up(converted_grade)



def calculate_form_grade(user, project, role, group_grades, individual_grades):
    print(f" role is: {role}")
    total_grades_by_student = defaultdict(float)

    for ig in individual_grades:
        student_name = ig.student.username  # get the username of the student 
        total_grades_by_student[student_name] += ig.final_grade

    for student, grade in total_grades_by_student.items():
        print(f"{student}: {grade}")

    
    # 1. Fetch students in the project
    student_memberships = StudentProjectMembership.objects.filter(project=project).select_related('student')
    students = [membership.student for membership in student_memberships]

    results = []

    for student in students:

        student_name = student.username

        for grade in group_grades:
            total_grades_by_student[student_name] += grade.grade.final_grade
        
        print (f"total grade is: {total_grades_by_student[student_name]}")
        # Convert the role grade to the final grade format if needed
        converted_grade = convert_total(raw_total=total_grades_by_student[student_name], role_name=role)
        print (f"converted grade is: {converted_grade}")
        # Append the result for the student
        results.append({
            'student': student,
            'grade': total_grades_by_student[student_name],
            'converted_grade': converted_grade
        })

    return results


def view_grades(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Get students in the project using the StudentProjectMembership model
    student_memberships = StudentProjectMembership.objects.filter(project=project).select_related('student')
    students = [membership.student for membership in student_memberships]

    # Get the current user's role in this project
    try:
        membership = ProjectMembership.objects.get(user=request.user, project=project)
        role = membership.role
        print(f"role is{role}")
    except ProjectMembership.DoesNotExist:
        return HttpResponse("You are not assigned to this project!", status=403)

    # Get evaluation form for this role
    evaluation_form = EvaluationForm.objects.filter(target_role=role).first()
    if not evaluation_form:
        return HttpResponse("No evaluation form found for your role in this project!", status=404)

    # Get main categories linked to this evaluation form
    main_categories = evaluation_form.main_categories.all()

    group_grades = MemberGrade.objects.filter(
        member=request.user, 
        grade__project=project, 
        grade__evaluation_form=evaluation_form,
        grade__main_category__in=main_categories.filter(grade_type='group')
    )
    print(f"group grades are: {group_grades}")

    individual_grades = []

    for student in students:
        member_grades = MemberIndividualGrade.objects.filter(
            member=request.user,
            individual_grade__grade__project=project,
            individual_grade__evaluation_form=evaluation_form,
            individual_grade__student=student,
            individual_grade__grade__main_category__in=main_categories.filter(grade_type='individual')
        ).select_related('individual_grade__grade__main_category', 'individual_grade__student')

        # Extract the related IndividualGrade objects and add to the array
        individual_grades.extend([mg.individual_grade for mg in member_grades])
        print(f"individual grades are: {individual_grades}")

    student_grades = calculate_form_grade(user=request.user, project=project, role=role, group_grades=group_grades, individual_grades=individual_grades)

    supervisor_membership = ProjectMembership.objects.filter(project=project, role__name="Supervisor").first()

    if supervisor_membership:
        supervisor = supervisor_membership.user
    else:
        supervisor = None  # or handle this case

    department = supervisor.department
    college = department.college
    university = college.university

    # Pass data to template for rendering
    return render(request, 'forms/view_grades.html', {
        'university_name': university.name,
        'college_name': college.name,
        'project': project,
        'evaluation_form': evaluation_form,
        'main_categories': main_categories,
        'group_grades': group_grades,
        'individual_grades': individual_grades,
        'students': students,
        'student_grades': student_grades,
        'supervisor_name': supervisor.get_full_name,
        'project_name': project.name,
    })


from collections import defaultdict

def calculate_final_grade(student, project):
    memberships = ProjectMembership.objects.filter(project=project).exclude(user=student)

    if not memberships.exists():
        print("No evaluators found for this project.")
        return None

    # Map roles to users
    role_user_map = defaultdict(list)
    for mem in memberships:
        role_user_map[mem.role].append(mem.user)

    role_grades_sum = {}
    role_weights = {}

    for role, users in role_user_map.items():
        form = EvaluationForm.objects.filter(target_role=role).first()
        if not form:
            print(f"No evaluation form found for role: {role}")
            continue

        main_categories = form.main_categories.all()
        max_possible = sum(cat.weight * 10 for cat in main_categories)
        if max_possible == 0:
            print(f"Max possible grade is 0 for form {form}. Skipping...")
            continue

        total_combined_grade = 0

        # Get individual grades for this student/project/form
        individual_grades = IndividualGrade.objects.filter(
            student=student,
            grade__project=project,
            evaluation_form=form
        )

        graded_evaluators = []
        for evaluator in users:
            # Sum individual grades given by this evaluator
            evaluator_individual_links = MemberIndividualGrade.objects.filter(
                member=evaluator,
                individual_grade__in=individual_grades
            )
            individual_sum = sum(link.individual_grade.final_grade for link in evaluator_individual_links)

            # Sum group grades given by this evaluator
            evaluator_group_links = MemberGrade.objects.filter(
                member=evaluator,
                grade__project=project,
                grade__evaluation_form=form
            )
            group_sum = sum(link.grade.final_grade for link in evaluator_group_links)

            # Only add to total if they contributed grades
            if individual_sum > 0 or group_sum > 0:
                total_combined_grade += individual_sum + group_sum
                graded_evaluators.append(evaluator)

        # Normalize
        if len(graded_evaluators) > 1:
            normalized_avg = (round_half_up((round_half_up(total_combined_grade) / len(graded_evaluators))) / max_possible)
        else:
            normalized_avg = total_combined_grade / max_possible

        role_grades_sum[role] = normalized_avg

        # Get weight from form
        role_weights[role] = getattr(form, "form_weight", 0)

    # Final grade aggregation
    final_grade = 0
    for role, normalized_score in role_grades_sum.items():
        weight = role_weights.get(role, 0)
        final_grade += normalized_score * weight

    final_grade = round_half_up(final_grade)
    final_grade = min(final_grade, 100)

    grading, created = Grading.objects.get_or_create(
        student=student,
        project=project,
        defaults={'final_grade': final_grade}
    )

    if not created:
        grading.final_grade = final_grade
        grading.save()

    print(f"Final grade saved: {final_grade}")
    return final_grade


@login_required
def manage_projects(request):
    user = request.user

    memberships = ProjectMembership.objects.filter(user=user).select_related('project', 'role')
    project_roles = [(membership.project.id, membership.project.name, membership.role.name) for membership in memberships]

    context = {
        'project_roles': project_roles,
    }

    return render(request, 'teacher/manage_projects.html', context)

from django.urls import reverse


@login_required
def project_role_dashboard(request, project_id, role):
    project = get_object_or_404(Project, id=project_id)

    role = role.lower()
    buttons = []
    # Get the user from the request
    user = request.user

    if role == 'supervisor':
        buttons = [
            ('Reports', '#'),
            ('Project Plan Form', '#'),
            ('Assessment Form', reverse('grade_form', args=[project.id])),
            ('Meetings', '#'),
            ('Annual Grade', '#'),
            ('Review Exchanges', '#'),
        ]
    elif role == 'reader':
        buttons = [
            ('Assessment Form', reverse('grade_form', args=[project.id])),
            ('Feedback', '#'),
        ]
    elif role == 'judgement committee':
        buttons = [
            ('Assessment Form', reverse('grade_form', args=[project.id])),
        ]
    else:
        buttons = []

    # Ensure the variable 'assessment_submitted' is defined
    assessment_submitted = False

    # Check if the user has already submitted an assessment form for the project
    if role in ['supervisor', 'reader', 'judgement committee']:
        assessment_submitted = MemberGrade.objects.filter(member=user, grade__project=project).exists() or \
                               MemberIndividualGrade.objects.filter(member=user, individual_grade__grade__project=project).exists()

    return render(request, 'teacher/project_dashboard.html', {
        'project': project,
        'buttons': buttons,
        'role': role.capitalize(),
        'assessment_submitted': assessment_submitted,  # Pass the status to the template
    })



def manage_grades_view(request):
    user = request.user
    is_coordinator = hasattr(user, 'coordinator')  # Check if user is a Coordinator
    department = user.department

    if not is_coordinator:
        return HttpResponseForbidden("Access Denied: You are not a Coordinator.")

    coordinator = user.coordinator
    is_super = coordinator.is_super

    department = coordinator.department
    if not department:
        return HttpResponseForbidden("Coordinator does not have an assigned department.")

    college = department.college
    departments = Department.objects.filter(college=college).values_list('name', flat=True)

    if is_super:
        projects = Project.objects.filter(department__college=college).prefetch_related('grades')
    else:
        projects = Project.objects.filter(department=department).prefetch_related('grades') 

    print(f"project are: {projects}")
    forms = EvaluationForm.objects.all()
    data = []
    committee_numbers = 0

    for project in projects:
        student_memberships = StudentProjectMembership.objects.filter(project=project).select_related('student')
        students = [membership.student for membership in student_memberships]

        memberships = ProjectMembership.objects.filter(project=project).select_related('user', 'role')

        #evaluators = [{"user": m.user, "role": m.role.name} for m in memberships]
        role_order = ['Supervisor', 'Reader', 'Judgement Committee']
        evaluators = sorted(
            [{"user": m.user, "role": m.role.name} for m in memberships],
            key=lambda e: (role_order.index(e['role']) if e['role'] in role_order else 99, e['user'].id)
        )
        committee_count = memberships.filter(role__name="Judgement Committee").count()
        committee_numbers = committee_count
        project_data = {
            'project': project,
            'students': [],
            'evaluator_headers': ['Supervisor', 'Reader'] + [f'Committee {i+1}' for i in range(committee_count)],
            'evaluators': evaluators,
        }

        for student in students:
            student_row = {
                'student': student,
                'grades_by_role': {}
            }
            evaluator_totals = []

            for evaluator in evaluators:
                user = evaluator["user"]
                role_name = evaluator["role"]

                role = Role.objects.get(name=role_name)
                eval_form = EvaluationForm.objects.filter(target_role=role).first()

                if not eval_form:
                    if role_name not in student_row['grades_by_role']:
                        student_row['grades_by_role'][role_name] = {
                            'evaluators': []
                        }

                    student_row['grades_by_role'][role_name]['evaluators'].append({
                        'evaluator_name': user.get_full_name(),
                        'user_id': user.id,
                        'group_grades': group_grades,
                        'individual_grades': individual_grades,
                        'ordered_grades': ordered_grades,
                        'total': round_half_up(converted_total),
                    })
                    evaluator_totals.append(0)
                    continue

                main_categories = MainCategory.objects.filter(evaluation_form=eval_form)

                group_grades = MemberGrade.objects.filter(
                    member=user,
                    grade__project=project,
                    grade__evaluation_form=eval_form,
                    grade__main_category__in=main_categories.filter(grade_type='group')
                )

                individual_grades = MemberIndividualGrade.objects.filter(
                    member=user,
                    individual_grade__grade__project=project,
                    individual_grade__evaluation_form=eval_form,
                    individual_grade__student=student,
                    individual_grade__grade__main_category__in=main_categories.filter(grade_type='individual')
                ).select_related('individual_grade')

                individual_grades_list = [g.individual_grade for g in individual_grades if g.individual_grade.final_grade is not None]
                group_grades_list = [g.grade for g in group_grades if g.grade.final_grade is not None]

                all_grades = individual_grades_list + group_grades_list
                total = sum(g.final_grade for g in all_grades if g.final_grade is not None)

                # Build a list in form order
                ordered_grades = []
                raw_total = 0

                for main in main_categories:
                    if main.grade_type == 'group':
                        grade_obj = next(
                            (g for g in group_grades if g.grade.main_category_id == main.id),
                            None
                        )
                        if grade_obj:
                            raw_total += grade_obj.grade.final_grade or 0
                        ordered_grades.append(grade_obj)

                    elif main.grade_type == 'individual':
                        grade_obj = next(
                            (g for g in individual_grades if g.individual_grade.grade.main_category_id == main.id),
                            None
                        )
                        if grade_obj:
                            raw_total += grade_obj.individual_grade.final_grade or 0
                        ordered_grades.append(grade_obj)

                # Convert the raw total based on role
                converted_total = convert_total(raw_total, role_name)

                evaluator_totals.append(converted_total)

                if role_name not in student_row['grades_by_role']:
                    student_row['grades_by_role'][role_name] = {
                        'evaluators': []
                    }

                student_row['grades_by_role'][role_name]['evaluators'].append({
                    'evaluator_name': user.get_full_name(),
                    'user_id': user.id,
                    'group_grades': group_grades,
                    'individual_grades': individual_grades,
                    'ordered_grades': ordered_grades,
                    'total': round(converted_total),
                })

            grading = Grading.objects.filter(student=student, project=project).first()
            full_grade = grading.final_grade if grading else "N/A"

            # Create a mapping from role name to score (this is now done correctly)
            committee_scores = [
                total for evaluator, total in zip(evaluators, evaluator_totals)
                if evaluator["role"].strip().lower() == "judgement committee"
                and total is not None and total > 0
            ]

            committee_count = len(committee_scores)
            print(f"committee scores are {sum(committee_scores)}, and their count is {committee_count}")

            committee_avg = round_half_up(sum(committee_scores) / committee_count) if committee_scores else 0


            student_row['committee_avg'] = committee_avg
            student_row['full_grade'] = full_grade
            project_data['students'].append(student_row)

        data.append(project_data)

    evaluation_forms = EvaluationForm.objects.all()
    evaluation_forms_with_counts = []
    for form in evaluation_forms:
        role = form.target_role
        main_categories_count = form.main_categories.count()
        evaluation_forms_with_counts.append({
            'role': role,
            'main_categories_count': main_categories_count,
            'form': form
        })


    # Count how many committee members each project has
    projects_with_committee_counts = (
        ProjectMembership.objects
        .filter(role__name="Judgement Committee")
        .values('project')  # Group by project
        .annotate(committee_count=Count('id'))  # Count committee members per project
    )

    # Get the maximum count
    committee_numbers = projects_with_committee_counts.aggregate(Max('committee_count'))['committee_count__max']

    print(f"department are: {departments}")
    print(f"data is: {data}")
    return render(request, 'forms/manage_grades.html', {
        'data': data,
        'evaluation_forms': evaluation_forms,
        'committee_numbers': committee_numbers,
        'evaluation_forms_with_counts': evaluation_forms_with_counts,
        'departments': departments,
        'user_department': coordinator.department,
        'is_superuser': is_super,
    })


@login_required
def view_my_grade(request):
    student = request.user
    grading = Grading.objects.filter(student=student, is_sent=True).first()

    return render(request, 'student/view_my_grade.html', {
        'grading': grading,
        'grade_available': grading is not None
    })


@login_required
def send_grades_to_all(request):
    user = request.user
    is_coordinator = hasattr(user, 'coordinator')  # Check if user is a Coordinator

    if not is_coordinator:
        return HttpResponseForbidden("Access Denied: You are not a Coordinator.")

    # Collect all the project IDs correctly
    project_ids = request.POST.getlist('project_ids')
    print("DEBUG - Project IDs received:", project_ids)
    
    for project_id in project_ids:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            continue  # skip invalid project ID
        
        # Get all grading records for this project where grades are not yet sent
        gradings = Grading.objects.filter(project=project, is_sent=False)
        print(f"Found {gradings.count()} gradings for project {project_id}")

        # Mark all gradings as sent for the project
        for grading in gradings:
            grading.is_sent = True
            grading.save(update_fields=['is_sent'])

    # Redirect back to the page with a success message
    return redirect('manage_grades')  # or any other appropriate view

def view_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    student_memberships = StudentProjectMembership.objects.filter(project=project).select_related('student')
    students = [membership.student for membership in student_memberships]
    memberships = ProjectMembership.objects.filter(project=project).select_related('user', 'role')

    supervisor_data = []
    reader_data = []
    committee_data = []
    student_committee_averages = {}
    student_grades = {}  # Store grades for each student by role

    for membership in memberships:
        user = membership.user
        role = membership.role
        role_name = role.name.lower()

        try:
            eval_form = EvaluationForm.objects.get(target_role=role)
        except EvaluationForm.DoesNotExist:
            continue

        main_categories = MainCategory.objects.filter(evaluation_form=eval_form).order_by('number')

        evaluator_info = {
            "name": user.get_full_name(),
            "grades": []
        }

        for student in students:
            ordered_grades = []
            total_grade = 0

            for main in main_categories:
                grade_value = None

                if main.grade_type == 'group':
                    member_grade = MemberGrade.objects.filter(
                        member=user,
                        grade__project=project,
                        grade__main_category=main
                    ).select_related('grade').first()

                    if member_grade and member_grade.grade.final_grade is not None:
                        grade_value = member_grade.grade.final_grade
                        total_grade += grade_value

                elif main.grade_type == 'individual':
                    member_individual_grade = MemberIndividualGrade.objects.filter(
                        member=user,
                        individual_grade__grade__project=project,
                        individual_grade__student=student,
                        individual_grade__grade__main_category=main
                    ).select_related('individual_grade').first()

                    if member_individual_grade and member_individual_grade.individual_grade.final_grade is not None:
                        grade_value = member_individual_grade.individual_grade.final_grade
                        total_grade += grade_value

                ordered_grades.append({
                    "main_category": main.text,
                    "weight": main.weight,
                    "grade": grade_value
                })

            final_grade = convert_total(total_grade, role_name)

            evaluator_info["grades"].append({
                "student_id": student.id,
                "student_name": student.get_full_name(),
                "ordered_grades": ordered_grades,
                "total": total_grade,
                "final_grade": final_grade
            })

            # Store grades for the summary table
            if student.id not in student_grades:
                student_grades[student.id] = {
                    "student_name": student.get_full_name(),
                    "supervisor_final_grade": None,
                    "reader_final_grade": None,
                    "committee_final_grade": None,
                    "final_grade": None
                }

            # Assign final grade based on the role
            if "supervisor" in role_name:
                student_grades[student.id]["supervisor_final_grade"] = final_grade
            elif "reader" in role_name:
                student_grades[student.id]["reader_final_grade"] = final_grade
            elif "committee" in role_name:
                student_grades[student.id]["committee_final_grade"] = final_grade

        if "supervisor" in role_name:
            supervisor_data.append(evaluator_info)
        elif "reader" in role_name:
            reader_data.append(evaluator_info)
        elif "committee" in role_name:
            committee_data.append(evaluator_info)

    # Calculate average final grade for Judging Committee per student
    for student in students:
        committee_final_grades = []
        for evaluator in committee_data:
            for grade_info in evaluator["grades"]:
                if grade_info["student_id"] == student.id:
                    committee_final_grades.append(grade_info["final_grade"])
                    break
        average = round_half_up(sum(committee_final_grades) / len(committee_final_grades)) if committee_final_grades else 0
        student_committee_averages[student.id] = average
        student_grades[student.id]["final_grade"] = student_grades[student.id]["supervisor_final_grade"] + student_grades[student.id]["reader_final_grade"] + average

    context = {
        "project": project,
        "supervisors": supervisor_data,
        "readers": reader_data,
        "committees": committee_data,
        "students": students,
        "student_committee_averages": student_committee_averages,
        "student_grades": student_grades,
    }

    return render(request, "forms/view_project.html", context)
