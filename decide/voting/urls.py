from django.urls import path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('question/list',views.ListQuestion, name='questionList'),
    path('question/delete/<int:question_id>',views.QuestionDeleteView, name='delete'),
    path('list',views.VotingListView, name="list"), 
    path('delete/<int:voting_id>',views.VotingDeleteView , name="votingDelete"),
    path('question/create/',views.createQuestion, name="createQuestion"),
    path('question/create/<int:numero>',views.auxCreateQuestion, name="createQuestion2"),
    path('edit/<int:voting_id>',views.VotingEditView , name="votingEdit"),
    path('create',views.VotingCreateView , name="votingCreate")

]
