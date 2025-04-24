from rest_framework import serializers
from .models import EvaluationForm, MainCategory, SubCategory

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'text']

class MainCategorySerializer(serializers.ModelSerializer):
    sub_categories = SubCategorySerializer(many=True)

    class Meta:
        model = MainCategory
        fields = ['id', 'number', 'text', 'weight', 'grade_type', 'sub_categories']

    def create(self, validated_data):
        subcategories_data = validated_data.pop('sub_categories')
        main_category = MainCategory.objects.create(**validated_data)
        for subcategory_data in subcategories_data:
            SubCategory.objects.create(main_category=main_category, **subcategory_data)
        return main_category

    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('sub_categories', [])

        # Update MainCategory fields
        instance.number = validated_data.get('number', instance.number)
        instance.text = validated_data.get('text', instance.text)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.grade_type = validated_data.get('grade_type', instance.grade_type)
        instance.save()

        # Update or create subcategories
        instance.sub_categories.all().delete()
        for subcategory_data in subcategories_data:
            SubCategory.objects.create(main_category=instance, **subcategory_data)

        return instance

class EvaluationFormSerializer(serializers.ModelSerializer):
    main_categories = MainCategorySerializer(many=True)
    
    class Meta:
        model = EvaluationForm
        fields = ['id', 'name', 'coordinators', 'target_role', 'form_weight', 'created_at', 'main_categories']

    def create(self, validated_data):
        main_categories_data = validated_data.pop('main_categories')
        evaluation_form = EvaluationForm.objects.create(**validated_data)
        
        for main_category_data in main_categories_data:
            sub_categories_data = main_category_data.pop('sub_categories')
            main_category = MainCategory.objects.create(evaluation_form=evaluation_form, **main_category_data)
            
            for subcategory_data in sub_categories_data:
                SubCategory.objects.create(main_category=main_category, **subcategory_data)

        return evaluation_form

    def update(self, instance, validated_data):
        main_categories_data = validated_data.pop('main_categories', [])

        # Update EvaluationForm fields
        instance.name = validated_data.get('name', instance.name)
        instance.target_role = validated_data.get('target_role', instance.target_role)
        instance.form_weight = validated_data.get('form_weight', instance.form_weight)
        instance.save()

        # Update MainCategories
        instance.main_categories.all().delete()
        for main_category_data in main_categories_data:
            sub_categories_data = main_category_data.pop('sub_categories')
            main_category = MainCategory.objects.create(evaluation_form=instance, **main_category_data)

            for subcategory_data in sub_categories_data:
                SubCategory.objects.create(main_category=main_category, **subcategory_data)

        return instance
