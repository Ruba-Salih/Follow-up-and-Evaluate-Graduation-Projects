from django.contrib import admin
from .models import User, Supervisor, Student, Coordinator, Admin

admin.site.register(User)
admin.site.register(Supervisor)
admin.site.register(Student)
admin.site.register(Coordinator)
admin.site.register(Admin)
