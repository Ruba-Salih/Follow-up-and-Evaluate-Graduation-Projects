from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from .models import EvaluationForm
from .serializers import EvaluationFormSerializer

class EvaluationFormListCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forms/form_list.html'

    def get(self, request, *args, **kwargs):
        evaluation_forms = EvaluationForm.objects.all()
        serializer = EvaluationFormSerializer(evaluation_forms, many=True)
        return Response({'evaluation_forms': serializer.data}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        print("🔹 Received Data:", request.data)  # Debugging request data
        data_qd = request.data.copy()
        subcategories = []
        index = 0
        key = f'subcategories[{index}][sub_category]'
        while key in data_qd:
            value = data_qd.get(key, '')
            subcategories.append({"sub_category": value})
            index += 1
            key = f'subcategories[{index}][sub_category]'
        data = data_qd.dict()
        data['subcategories'] = subcategories
        print("✅ Processed Data (dict):", data)

        serializer = EvaluationFormSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("✅ Form successfully saved!")
            evaluation_forms = EvaluationForm.objects.all()
            return Response({'evaluation_forms': EvaluationFormSerializer(evaluation_forms, many=True).data}, template_name='forms/form_list.html')
        print("❌ Form validation failed:", serializer.errors)
        return Response({'serializer': serializer, 'errors': serializer.errors}, template_name='forms/form_create.html')


@method_decorator(csrf_exempt, name='dispatch')  # Temporarily disable CSRF for testing
class EvaluationFormCreateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forms/form_create.html'

    def get(self, request, *args, **kwargs):
        serializer = EvaluationFormSerializer()
        return Response({'serializer': serializer}, template_name=self.template_name)

    def post(self, request, *args, **kwargs):
        print("🔹 Received Data (Create View):", request.data)
        data_qd = request.data.copy()
        subcategories = []
        index = 0
        key = f'subcategories[{index}][sub_category]'
        while key in data_qd:
            value = data_qd.get(key, '')
            subcategories.append({"sub_category": value})
            index += 1
            key = f'subcategories[{index}][sub_category]'
        data = data_qd.dict()
        data['subcategories'] = subcategories
        print("✅ Processed Data (Create View):", data)

        serializer = EvaluationFormSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("✅ Form successfully saved in Create View!")
            return redirect('evaluation_form_list_create')
        print("❌ Form validation failed in Create View:", serializer.errors)
        return Response({'serializer': serializer, 'errors': serializer.errors}, template_name=self.template_name)

class EvaluationFormDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'forms/form_detail.html'

    def get_object(self, pk):
        return get_object_or_404(EvaluationForm, pk=pk)

    def get(self, request, pk, *args, **kwargs):
        evaluation_form = self.get_object(pk)
        serializer = EvaluationFormSerializer(evaluation_form)
        # Pass both the instance and the serialized data.
        return Response({
            'evaluation_form_instance': evaluation_form,
            'evaluation_form': serializer.data
        }, template_name=self.template_name)

    def post(self, request, pk, *args, **kwargs):
        evaluation_form = self.get_object(pk)
        
        # Process subcategories in a similar way as in the create view.
        data_qd = request.data.copy()
        subcategories = []
        index = 0
        key = f'subcategories[{index}][sub_category]'
        while key in data_qd:
            value = data_qd.get(key, '')
            subcategories.append({"sub_category": value})
            index += 1
            key = f'subcategories[{index}][sub_category]'
        data = data_qd.dict()
        data['subcategories'] = subcategories

        # If the delete flag is set, delete the evaluation form.
        if request.data.get('delete'):
            evaluation_form.delete()
            evaluation_forms = EvaluationForm.objects.all()
            return Response({
                'evaluation_forms': EvaluationFormSerializer(evaluation_forms, many=True).data
            }, template_name='forms/form_list.html')

        serializer = EvaluationFormSerializer(evaluation_form, data=data)
        if serializer.is_valid():
            serializer.save()
            # After update, re-fetch the updated instance
            evaluation_form = self.get_object(pk)
            serializer = EvaluationFormSerializer(evaluation_form)
            return Response({
                'evaluation_form_instance': evaluation_form,
                'evaluation_form': serializer.data
            }, template_name=self.template_name)
        return Response({
            'evaluation_form_instance': evaluation_form,
            'evaluation_form': serializer.data,
            'errors': serializer.errors
        }, template_name=self.template_name)

    def delete(self, request, pk, *args, **kwargs):
        evaluation_form = self.get_object(pk)
        evaluation_form.delete()
        evaluation_forms = EvaluationForm.objects.all()
        return Response({
            'evaluation_forms': EvaluationFormSerializer(evaluation_forms, many=True).data
        }, template_name='forms/form_list.html')
