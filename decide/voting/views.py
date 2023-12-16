from django.contrib.auth.decorators import login_required, user_passes_test
import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone

from django.shortcuts import get_object_or_404, redirect,render

from rest_framework import generics, status
from rest_framework.response import Response
from django.views.generic.list import ListView
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required

from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth

def staff_check(user):
   admin = user.is_staff
   return admin 

class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('id', )

    def get(self, request, *args, **kwargs):
        idpath = kwargs.get('voting_id')
        self.queryset = Voting.objects.all()
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'question', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('question'))
        question.save()
        for idx, q_opt in enumerate(request.data.get('question_opt')):
            opt = QuestionOption(question=question, option=q_opt, number=idx)
            opt.save()
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),
                question=question)
        voting.save()

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)


class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)
    

@login_required
@user_passes_test(staff_check)
def VotingListView(request):
    templates_name= "listVotings.html"
    votings = Voting.objects.all()
    context = {
        'votings': votings
    }
    return render(request, 'listVotings.html', context)



@login_required
@user_passes_test(staff_check)
def ListQuestion(request):
        census = Question.objects.all()
        return render(request, 'listQuestion.html', {
            'object_list':census
        })

    

@login_required
@user_passes_test(staff_check)  
def QuestionDeleteView(request, question_id):
    question = Question.objects.filter(pk=question_id).first()
    Question.delete(question)

    return redirect('/voting/question/list')


@login_required
@user_passes_test(staff_check)   
def VotingDeleteView(request,voting_id):
    voting = Voting.objects.filter(pk=voting_id).first()

    Voting.delete(voting)

    return redirect('/voting/list')

@login_required
@user_passes_test(staff_check)   
def createQuestion(request):

    if request.method == 'POST':

        numero= request.POST.get("number")



        return redirect("/voting/question/create/"+ str(numero))
    return render(request, 'numberAnswer.html', {

    })


def auxCreateQuestion(request, numero):
    numero_range = range(numero)
    if request.method == 'POST':
        desc=request.POST.get("desc")
        q=Question.objects.create(desc=desc)
        Question.save(q)
        for n in range(numero):
            ans= request.POST.get("ans_"+ str(n))
            respuesta= QuestionOption.objects.create(option=ans,question=q,number=n+1)   
            QuestionOption.save(respuesta)

        return redirect('/voting/question/list')
    return render(request, 'createQuestion.html', {  
        "numero":numero_range
    })

