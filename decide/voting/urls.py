from django.urls import path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('question/list',views.ListQuestion, name='questionList'),
    path('question/delete/<int:question_id>',views.QuestionDeleteView, name='delete'),
    path('list',views.VotingListView, name="list"), 
    path('delete/<int:voting_id>',views.VotingDeleteView , name="votingDelete"),

]
