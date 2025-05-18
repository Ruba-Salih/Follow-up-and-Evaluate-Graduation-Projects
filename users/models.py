from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from university.models import Department


class User(AbstractUser):
    phone_number = models.CharField(_("Phone Number"), max_length=15, blank=True, null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        verbose_name=_("Department")
    )

    def save(self, *args, **kwargs):
        if not self.is_superuser and self.department is None:
            raise ValueError(_("Non-superusers must have a department."))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Supervisor(User):
    qualification = models.CharField(_("Qualification"), max_length=100)
    total_projects = models.IntegerField(_("Total Projects"), default=0)
    supervisor_id = models.CharField(_("Supervisor ID"), max_length=20, unique=True)
    work_place = models.CharField(_("Workplace"), max_length=100)

    def __str__(self):
        return f"{_('Supervisor')}: {self.username}"


class Student(User):
    student_id = models.CharField(_("Student ID"), max_length=20, unique=True)
    sitting_number = models.CharField(_("Sitting Number"), max_length=20)

    def __str__(self):
        return f"{_('Student')}: {self.username}"


class Coordinator(User):
    coord_id = models.CharField(_("Coordinator ID"), max_length=20, unique=True, blank=True, default="")
    is_super = models.BooleanField(_("Is Super Coordinator?"), default=False)

    def __str__(self):
        return f"{_('Coordinator')}: {self.username}"


class Role(models.Model):
    name = models.CharField(_("Role Name"), max_length=50, unique=True)

    def __str__(self):
        return self.name


class Admin(User):

    def __str__(self):
        return f"{_('Admin')}: {self.username}"


class UserCreationLog(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="creation_log", verbose_name=_("User"))
    added_by = models.ForeignKey(
        Coordinator,
        on_delete=models.SET_NULL,
        null=True,
        related_name="added_users",
        verbose_name=_("Added By")
    )
    added_at = models.DateTimeField(_("Added At"), auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {_('added by')} {self.added_by.username if self.added_by else _('Unknown')}"
