from django.urls import path
from . import views

urlpatterns = [
    path("manage-colleges/", views.ManageCollegesView.as_view(), name="manage-colleges"),                      # GET and POST
    path("manage-colleges/<int:college_id>/", views.ManageCollegesView.as_view(), name="edit-college"),       # PUT
    path("manage-colleges/delete/<int:college_id>/", views.ManageCollegesView.as_view(), name="delete-college"),  # DELETE

    path("manage-departments/", views.DepartmentView.as_view(), name="manage-departments"),
    path("departments/<int:pk>/", views.DepartmentView.as_view(), name="department-detail"),
]
