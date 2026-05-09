from django.urls import path
from . import views

urlpatterns = [
    path('feedback/', views.feedback_view, name='feedback'),
    path('api/report-search-problem/', views.report_search_problem, name='report_search_problem'),
]
