from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('list/', views.CensusList, name='census_list'),
    path('edit/<int:voting_id>/', views.editCensus, name='edit_census'),
    path('delete/<int:voting_id>/', views.deleteCensus, name='edit_census'),
    path('create', views.createCensus, name='create_census')
]
