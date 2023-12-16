from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render,redirect
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from voting.models import Voting
from django.contrib.auth.models import User
from rest_framework import generics
from .models import Census
from rest_framework.response import Response
from django.views.generic.list import ListView
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from .models import Census


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')

def staff_check(user):
   admin = user.is_staff
   return admin 

@login_required
@user_passes_test(staff_check)
def CensusList(request):
    census = getParsedCensus().items()
    return render(request, 'censusList.html', {
        'object_list':census
    })
    

def getParsedCensus():
    res = {}
    census = Census.objects.all()
    for c in census:
        voting = Voting.objects.get(pk=c.voting_id)
        voter = User.objects.get(pk=c.voter_id)
        if voting not in res.keys():
            res[voting] = []
        res[voting].append(voter)
    return res


@login_required
@user_passes_test(staff_check)
def deleteCensus(request, voting_id):
    census = Census.objects.filter(voting_id=voting_id)
    for c in census:
        Census.delete(c)

    return redirect('/census/list')

@login_required
@user_passes_test(staff_check)
def createCensus(request):
    votings = Voting.objects.all()
    users = Census.objects.all()
    return render(request, 'createCensus.html', {
        'votings':votings,
        'users': users
    })
