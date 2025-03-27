from django.shortcuts import render, get_object_or_404, redirect
from .models import EvaluationForm, MainCategory, SubCategory
from .serializers import EvaluationFormSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from project.models import Role  

def evaluation_form_list(request):
    """List all evaluation forms."""
    forms = EvaluationForm.objects.all()
    return render(request, 'forms/form_list.html', {'forms': forms})

def evaluation_form_detail(request, form_id):
    """View an evaluation form."""
    form = get_object_or_404(EvaluationForm, id=form_id)
    return render(request, 'forms/form_detail.html', {'form': form})

@csrf_exempt
def create_evaluation_form(request):
    """Create a new evaluation form."""
    roles = Role.objects.all()
    print("Roles:", roles)

    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = EvaluationFormSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Evaluation form created successfully!'}, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    return render(request, 'forms/form_create.html', {'roles': roles})

@csrf_exempt
def edit_evaluation_form(request, form_id):
    """Edit an existing evaluation form."""
    form = get_object_or_404(EvaluationForm, id=form_id)
    roles = Role.objects.all()

    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = EvaluationFormSerializer(form, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Evaluation form updated successfully!'}, status=200)
        return JsonResponse(serializer.errors, status=400)

    return render(request, 'forms/edit.html', {'form': form})

@csrf_exempt
def delete_evaluation_form(request, form_id):
    """Delete an evaluation form by ID."""
    if request.method == "DELETE":
        form = get_object_or_404(EvaluationForm, id=form_id)
        form.delete()
        return JsonResponse({'message': 'Evaluation form deleted successfully!'}, status=200)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_main_category(request, main_category_id):
    if request.method == "DELETE":
        main_category = get_object_or_404(MainCategory, id=main_category_id)
        main_category.delete()
        return JsonResponse({'success': True, 'message': 'Main category deleted successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@csrf_exempt
def delete_subcategory(request, subcategory_id):
    if request.method == "DELETE":
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        subcategory.delete()
        return JsonResponse({'success': True, 'message': 'Subcategory deleted successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)