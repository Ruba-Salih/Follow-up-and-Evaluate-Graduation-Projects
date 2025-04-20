from django.shortcuts import render
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


def grade_form(request, project_id):
    project = Project.objects.get(id=project_id)
    user = request.user

    # Check membership and get role
    project_membership = ProjectMembership.objects.filter(user=user, project=project).first()
    if not project_membership:
        return render(request, 'access_denied.html', {"message": "You are not authorized to grade this project."})

    user_role = project_membership.role
    form = EvaluationForm.objects.filter(target_role=user_role).first()

    if not form:
        return render(request, 'access_denied.html', {"message": "No form available for your role in this project."})

    print(f"evaluation_form_id: {form.id}")
    main_categories = form.main_categories.all()
    students = Student.objects.filter(project_membership__project=project)
    supervisor = project.supervisor
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
        'supervisor_name': supervisor.get_full_name,
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
                                weighted_grade = grade_value * main_category.weight

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
                            weighted_grade = grade_value * main_category.weight

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

        return redirect('grade_success', project_id=project.id)

    return redirect('grade_form', project_id=project_id)


@login_required
def grade_success(request, project_id):
    # Get the project based on project_id
    project = get_object_or_404(Project, id=project_id)
    
    # Render the success template with the project context
    return render(request, 'forms/grade_success.html', {'project': project})


def calculate_form_grade(user, project, role, evaluation_form):
    # Define roles to track their total grades
    supervisor_role = Role.objects.get(name='Supervisor')
    reader_role = Role.objects.get(name='Reader')
    committee_role = Role.objects.get(name='Judgement Committee')

    role_grades = {
        supervisor_role: 0,
        reader_role: 0,
        committee_role: 0,
    }

    # Get the current user's role membership for this project
    user_membership = ProjectMembership.objects.filter(user=user, project=project).first()
    
    if not user_membership:
        print(f"[Error] User {user} does not have a membership in project {project}")
        return []
    
    # Only add grades to the current user's role by using MemberGrade
    member_grades = MemberGrade.objects.filter(member=user, grade__project=project, grade__evaluation_form=evaluation_form)
    
    for member_grade in member_grades:
        if user_membership.role in role_grades:
            role_grades[user_membership.role] += member_grade.grade.final_grade
            print(f"[Group Grade] Added {member_grade.grade.final_grade} to role {user_membership.role}")

    # 2. Fetch students in the project
    student_memberships = StudentProjectMembership.objects.filter(project=project).select_related('student')
    students = [membership.student for membership in student_memberships]

    results = []
    temp_role_grades = role_grades.copy()

    for student in students:
        # Aggregate individual grades for the current user’s role
        member_individual_grades = MemberIndividualGrade.objects.filter(member=user, individual_grade__grade__project=project, individual_grade__evaluation_form=evaluation_form, individual_grade__student=student)
        
        for member_individual_grade in member_individual_grades:
            # Only aggregate if the role matches the current user's role
            if user_membership.role in role_grades:
                role_grades[user_membership.role] += member_individual_grade.individual_grade.final_grade
                print(f"[Individual Grade] Added {member_individual_grade.individual_grade.final_grade} to role {user_membership.role}")

        # For this view, we only want to show the grade for the current user’s role
        final_grade = 0
        target_role = role

        # Calculate the grade only for the current user's role
        if target_role in role_grades:
            final_grade = role_grades[target_role]
            print(f"[Final] Student: {student.get_full_name()}, Role: {target_role}, Grade: {final_grade}")
        else:
            print(f"[Warning] Role {target_role} not found in role_grades")

        # Convert the role grade to the final grade format if needed
        converted_grade = convert_role_grade(role=role, role_grade=final_grade)
        
        # Append the result for the student
        results.append({
            'student': student,
            'grade': final_grade,
            'converted_grade': converted_grade
        })
        
        # Reset role grades to the temp copy for the next iteration
        role_grades = temp_role_grades.copy()

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
    

    student_grades = calculate_form_grade(user=request.user, project=project, role=role, evaluation_form=evaluation_form)

    supervisor = project.supervisor
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

def convert_role_grade(role, role_grade):

    print(f"Role received: {role}")
    # Define the maximum possible grade for eacph role
    max_grades = {
        'Supervisor': 50,
        'Reader': 20,
        'Judgement Committee': 30
    }

    # Actual maximum values for each role (you can adjust this as needed)
    actual_max_grades = {
        'Supervisor': 50,
        'Reader': 40,
        'Judgement Committee': 30
    }

    # Get the grade for the given role
    role_score = role_grade
    print(f"Role: {role}, Role Score: {role_score}")

    role_name = role.name
    # Convert the grade based on max value for the role
    if role_name == 'Supervisor':
        actual_max = actual_max_grades.get('Supervisor', 0)
        print(f"Actual Max for Supervisor: {actual_max}")
        converted_grade = (role_score / actual_max) * max_grades['Supervisor'] if actual_max else 0
        print(f"Converted Grade for Supervisor: {converted_grade}")

    elif role_name == 'Reader':
        actual_max = actual_max_grades.get('Reader', 0)
        print(f"Actual Max for Reader: {actual_max}")
        converted_grade = (role_score / actual_max) * max_grades['Reader'] if actual_max else 0
        print(f"Converted Grade for Reader: {converted_grade}")

    elif role_name == 'Judgement Committee':
        actual_max = actual_max_grades.get('Judgement Committee', 0)
        print(f"Actual Max for Committee: {actual_max}")
        converted_grade = (role_score / actual_max) * max_grades['Judgement Committee'] if actual_max else 0
        print(f"Converted Grade for Judgement Committee: {converted_grade}")
    else:
        converted_grade = 0
        print(f"Role {role} not found, setting grade to 0")

    return converted_grade


def calculate_final_grade(student, project):
    try:
        supervisor_role = Role.objects.get(name='Supervisor')
        reader_role = Role.objects.get(name='Reader')
        committee_role = Role.objects.get(name='Judgement Committee')
    except Role.DoesNotExist:
        print("Roles not found.")
        return None  # Handle the case where roles are missing

    
    committee_members = ProjectMembership.objects.filter(project=project, role=committee_role)
    committee_count = committee_members.count()
    print(f"number of ommittee members {committee_count}")

    # Define the maximum possible grade for each role
    max_grades = {
        supervisor_role: 50,
        reader_role: 20,
        committee_role: 30
    }
    
    supervisor_actual_max = 50  # Example actual max for Supervisor
    reader_actual_max = 40     # Example actual max for Reader
    committee_actual_max = 30  # Example actual max for each Judgement Committee member

    # Weight definitions for each role (this is just for reference)
    weights = {
        supervisor_role: 0.5,
        reader_role: 0.2,
        committee_role: 0.3
    }

    print("Max grades:", max_grades)
    print("Weights:", weights)

    # Assign grades to roles (using existing grades from individual and group assignments)
    role_grades = {
        supervisor_role: 0,
        reader_role: 0,
        committee_role: 0
    }

    print("Initial role grades:", role_grades)
    
    # Fetch individual grades for the student in the given project
    individual_grades = IndividualGrade.objects.filter(student=student, grade__project=project)
    print(f"Found {len(individual_grades)} individual grades for student {student}")

    # Assign grades from individual assignments to the appropriate roles
    for ind_grade in individual_grades:
        member_link = MemberIndividualGrade.objects.filter(individual_grade=ind_grade).first()
        if not member_link:
            continue
        member = member_link.member
        role_obj = ProjectMembership.objects.filter(user=member, project=project).first()
        if role_obj and role_obj.role in role_grades:
            role_grades[role_obj.role] += ind_grade.final_grade
            print(f"Assigned individual grade {ind_grade.final_grade} to role {role_obj.role}")

    # Fetch group grades for the project
    group_grades = Grade.objects.filter(project=project).exclude(individual_grades__isnull=False)
    print(f"Found {len(group_grades)} group grades for project {project}")

    # Assign group grades to roles
    for group_grade in group_grades:
        member_link = MemberGrade.objects.filter(grade=group_grade).first()
        if not member_link:
            continue
        member = member_link.member
        role_obj = ProjectMembership.objects.filter(user=member, project=project).first()
        if role_obj and role_obj.role in role_grades:
            role_grades[role_obj.role] += group_grade.final_grade
            print(f"Assigned group grade {group_grade.final_grade} to role {role_obj.role}")

    # Now calculate the final grade by summing up the grades of all roles
    final_grade = 0

    # Add up grades for each role, without weighting them again
    print("Summing up grades for each role:")
    for role, total_grade in role_grades.items():
        print(f"Role: {role}, Grade: {total_grade}")
        final_grade += total_grade

    # Now, convert the grades based on max values for each role
    supervisor_score = role_grades[supervisor_role]
    supervisor_final = (supervisor_score / supervisor_actual_max) * 50 if supervisor_actual_max else 0

    reader_score = role_grades[reader_role]
    reader_final = (reader_score / reader_actual_max) * 20 if reader_actual_max else 0

    committee_score = role_grades[committee_role]
    avg_score = committee_score / committee_count
    print(f"average: {avg_score}")
    committee_final = (avg_score / committee_actual_max) * 30 if committee_actual_max else 0

    # Combine all roles' converted grades to get the final grade
    final_grade = supervisor_final + reader_final + committee_final

    # Ensure the final grade does not exceed 100
    final_grade = min(final_grade, 100)

    # Save the final grade in the Grading model
    grading, created = Grading.objects.get_or_create(student=student, project=project)
    grading.final_grade = final_grade
    grading.save()

    print(f"Final grade saved: {final_grade}")

    return final_grade


def teacher_home(request):
    print("Hello from teacher_home view!")
    user = request.user
    # Get the projects where the current user is a member
    project_memberships = ProjectMembership.objects.filter(user=user)
    total_projects = project_memberships.values('project').distinct().count()

    context = {
        'total_projects': total_projects,
    }
    return render(request, 'teacher/home.html', context)



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
    print("hello from manage grades view")
    
    department = request.user.department
    print(f"Department: {department}")

    projects = Project.objects.filter(department=department.name).prefetch_related('grades')
    print(f"Projects: {projects}")

    forms = EvaluationForm.objects.all()
    data = []

    for project in projects:
        print(f"Project: {project.name}")
        student_memberships = StudentProjectMembership.objects.filter(project=project).select_related('student')
        students = [membership.student for membership in student_memberships]
        print(f"Students: {students}")

        memberships = ProjectMembership.objects.filter(project=project).select_related('user', 'role')

        evaluators = [{"user": m.user, "role": m.role.name} for m in memberships]
        committee_count = memberships.filter(role__name="Judgement Committee").count()

        project_data = {
            'project': project,
            'students': [],
            'evaluator_headers': ['Supervisor', 'Reader'] + [f'Committee {i+1}' for i in range(committee_count)],
            'evaluators': evaluators,
        }

        for student in students:
            student_row = {
                'student': student,
                'grades_by_evaluator': {}
            }
            evaluator_totals = []

            for evaluator in evaluators:
                user = evaluator["user"]
                role_name = evaluator["role"]
                print(f"Evaluator: {user}, Role: {role_name}")

                role = Role.objects.get(name=role_name)
                eval_form = EvaluationForm.objects.filter(target_role=role).first()

                if not eval_form:
                    student_row['grades_by_evaluator'][user.id] = {
                        'evaluator_name': user.get_full_name(),
                        'role': role_name,
                        'group_grades': [],
                        'individual_grades': [],
                        'grades_by_main': {},
                        'total': 0
                    }
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

                # Prepare grade map by main category ID
                grades_by_main = {}

                for main in main_categories:
                    grade_value = "N/A"

                    if main.grade_type == "group":
                        match = next((g.grade.final_grade for g in group_grades if g.grade.main_category_id == main.id), None)
                        if match is not None:
                            grade_value = round(match, 2)
                    elif main.grade_type == "individual":
                        match = next((ig.individual_grade.final_grade for ig in individual_grades
                                      if ig.individual_grade.grade.main_category_id == main.id and
                                         ig.individual_grade.student_id == student.id), None)
                        if match is not None:
                            grade_value = round(match, 2)

                    grades_by_main[main.id] = grade_value

                student_row['grades_by_evaluator'][user.id] = {
                    'evaluator_name': user.get_full_name(),
                    'role': role_name,
                    'group_grades': group_grades,
                    'individual_grades': individual_grades,
                    'grades_by_main': grades_by_main,
                    'total': round(total, 2)
                }

                evaluator_totals.append(total)

                print(f"Student row so far: {student_row}")

            supervisor_score = evaluator_totals[0] if len(evaluator_totals) > 0 else 0
            reader_score = evaluator_totals[1] if len(evaluator_totals) > 1 else 0

            supervisor_max = 50
            reader_max = 40
            committee_max = 30

            if len(evaluator_totals) > 2:
                committee_scores = [(g / committee_max) * 30 for g in evaluator_totals[2:] if g is not None]
                committee_avg = round(sum(committee_scores) / len(committee_scores), 2) if committee_scores else 0
            else:
                committee_avg = 0

            supervisor_final = (supervisor_score / supervisor_max) * 50 if supervisor_max else 0
            reader_final = (reader_score / reader_max) * 20 if reader_max else 0
            full_grade = round(supervisor_final + reader_final + committee_avg, 2)

            student_row['committee_avg'] = committee_avg
            student_row['full_grade'] = full_grade
            project_data['students'].append(student_row)

        data.append(project_data)

    print(f"Final data: {data}")
    evaluation_forms = EvaluationForm.objects.all()
    
    return render(request, 'forms/manage_grades.html', {
        'data': data,
        'evaluation_forms': evaluation_forms,
    })
