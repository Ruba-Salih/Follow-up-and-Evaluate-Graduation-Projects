from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import Coordinator  
from project.models import Role  
from django.utils.timezone import now


class EvaluationForm(models.Model):
    """
    Represents an Evaluation Form.
    """
    name = models.CharField(_("Form Name"), max_length=255)
    coordinators = models.ManyToManyField(
        Coordinator,
        blank=True,
        related_name='evaluation_forms',
        verbose_name=_("Coordinators")
    )
    target_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("The role of users for whom this evaluation form is intended."),
        verbose_name=_("Target Role")
    )
    form_weight = models.FloatField(
        null=False,
        help_text=_("The weight of the entire evaluation form."),
        verbose_name=_("Form Weight")
    )
    created_at = models.DateTimeField(_("Created At"), default=now)

    def __str__(self):
        return f"{_('Form')} {self.id}: {self.name}"


class MainCategory(models.Model):
    """
    A main category belongs to a specific EvaluationForm.
    """
    GRADE_TYPE_CHOICES = (
        ('individual', _('Individual Grade')),
        ('group', _('Group Grade')),
    )

    evaluation_form = models.ForeignKey(
        EvaluationForm,
        on_delete=models.CASCADE,
        related_name='main_categories',
        verbose_name=_("Evaluation Form")
    )
    number = models.PositiveIntegerField(_("Number"))
    text = models.TextField(_("Category Text"))
    weight = models.FloatField(_("Category Weight"))
    grade_type = models.CharField(
        _("Grade Type"),
        max_length=20,
        choices=GRADE_TYPE_CHOICES
    )

    def __str__(self):
        return f"{_('Main Category')} {self.number} ({_('Form')} {self.evaluation_form.id})"


class SubCategory(models.Model):
    """
    A subcategory belongs to a specific MainCategory.
    """
    main_category = models.ForeignKey(
        MainCategory,
        on_delete=models.CASCADE,
        related_name='sub_categories',
        verbose_name=_("Main Category")
    )
    text = models.TextField(_("Subcategory Text"))

    def __str__(self):
        return f"{_('SubCategory for MainCategory')} {self.main_category.number}"
