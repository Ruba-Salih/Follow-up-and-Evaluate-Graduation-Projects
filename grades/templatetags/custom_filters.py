from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_form_by_role(forms, role_name):

    if 'Committee' in role_name:
        # If role_name is something like "Committee 1", "Committee 2", etc.
        role_name = "Judgement Committee"

    if isinstance(forms, list):
        # Use list comprehension to filter by role name
        return next((form['form'] for form in forms if form['role'].name == role_name), None)
    # Otherwise, assume forms is a queryset and use .filter() method
    return forms.filter(target_role__name=role_name).first()

@register.filter
def get_grade_for_main(grades, main_id):
    print(f"Looking for main_category.id == {main_id}")
    for grade in grades:
        print(f"Checking grade.main_category.id = {grade.main_category.id}")
        if grade.main_category.id == main_id:
            print("Found a match!")
            return grade
    print("No match found.")
    return None
