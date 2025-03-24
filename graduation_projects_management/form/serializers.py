from rest_framework import serializers
from .models import EvaluationForm, SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['sub_category']

class EvaluationFormSerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, required=False)
    
    class Meta:
        model = EvaluationForm
        fields = [
            'form_id',       # Ensure we have the primary key for URL reversing
            'form_name',     # Include the form name
            'main_category_number',
            'main_category',
            'weight',
            'type_of_grade',
            'subcategories',
        ]
    
    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        evaluation_form = EvaluationForm.objects.create(**validated_data)
        for sub_data in subcategories_data:
            SubCategory.objects.create(evaluation_form=evaluation_form, **sub_data)
        return evaluation_form

    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories', None)
        instance.form_name = validated_data.get('form_name', instance.form_name)
        instance.main_category_number = validated_data.get('main_category_number', instance.main_category_number)
        instance.main_category = validated_data.get('main_category', instance.main_category)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.type_of_grade = validated_data.get('type_of_grade', instance.type_of_grade)
        instance.save()
        if subcategories_data is not None:
            # For simplicity, clear existing subcategories and add new ones.
            instance.subcategories.all().delete()
            for sub_data in subcategories_data:
                SubCategory.objects.create(evaluation_form=instance, **sub_data)
        return instance
