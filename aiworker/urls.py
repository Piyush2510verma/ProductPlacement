from django.urls import path
from . import views

urlpatterns = [
  path("", views.home, name="home"),
  path("api/initiate", views.upload_csv_files, name="upload-csv"),
  path("api/query", views.run_query, name="run_query")
]