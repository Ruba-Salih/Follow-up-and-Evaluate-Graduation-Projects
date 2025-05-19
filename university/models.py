from django.db import models
from django.utils.translation import gettext_lazy as _


class University(models.Model):
    name = models.CharField(_("University Name"), max_length=200)

    def __str__(self):
        return self.name


class College(models.Model):
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='colleges',
        verbose_name=_("University")
    )
    name = models.CharField(_("College Name"), max_length=200)
    location = models.CharField(_("Location"), max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.university.name})"


class Department(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name=_("College")
    )
    name = models.CharField(_("Department Name"), max_length=200)

    def __str__(self):
        return f"{self.name} - {self.college.name}"
