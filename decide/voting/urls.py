from django.urls import path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('list',views.VotingListView, name="list"), 
    path('question/list',views.ListQuestion.as_view(), name='questionList'),
    path('delete/<int:voting_id>',views.VotingDeleteView , name="votingDelete"),

]
