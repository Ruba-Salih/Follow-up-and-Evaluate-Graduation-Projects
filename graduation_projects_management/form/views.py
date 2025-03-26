from django.shortcuts import render, get_object_or_404, redirect
from .models import EvaluationForm, MainCategory, SubCategory
from .serializers import EvaluationFormSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = EvaluationFormSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Evaluation form created successfully!'}, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    return render(request, 'forms/form_create.html')

@csrf_exempt
def edit_evaluation_form(request, form_id):
    """Edit an existing evaluation form."""
    form = get_object_or_404(EvaluationForm, id=form_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = EvaluationFormSerializer(form, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Evaluation form updated successfully!'}, status=200)
        return JsonResponse(serializer.errors, status=400)

    return render(request, 'forms/edit.html', {'form': form})

