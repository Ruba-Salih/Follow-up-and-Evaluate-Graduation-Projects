from django.db import models

class University(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class College(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='colleges')
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.university.name})"

class Department(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.college.name}"
