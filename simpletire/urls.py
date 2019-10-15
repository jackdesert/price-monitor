from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index_view_name'),
    path('status', views.status_view, name='status_view_name'),
]
