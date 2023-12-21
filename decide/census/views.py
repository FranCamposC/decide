from http.client import HTTPResponse
from django.http import HttpResponse
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
    HTTP_409_CONFLICT as ST_409,
    HTTP_500_INTERNAL_SERVER_ERROR as ST_500
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
        voting = Voting.objects.filter(pk=c.voting_id).first()
        voter = User.objects.filter(pk=c.voter_id).first()
        if not voting == None or not voter == None:
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
    votings = Voting.objects.all().order_by('name')
    users = User.objects.all().order_by('username')

    if request.method == 'POST':

        voting = request.POST.get('v')
        user = request.POST.getlist('u')
        for u in user:
            census = Census(voting_id=int(voting), voter_id=int(u))
            census.save()


        return redirect('/census/list' )
    return render(request, 'createCensus.html', {
        'votings':votings,
        'users': users
    })

@login_required
@user_passes_test(staff_check)
def editCensus(request, voting_id):
    voting = Voting.objects.get(pk=voting_id)
    users = User.objects.all().order_by('username')
    census = Census.objects.filter(voting_id=voting_id)
    selectedUsers = []
    for c in census:
        selectedUsers.append(User.objects.filter(pk=c.voter_id).first())
    if request.method == 'POST':
        user = request.POST.getlist('u')

        for c in census:
            Census.delete(c)
        for u in user:
            census = Census(voting_id=voting_id, voter_id=int(u))
            census.save()
        return redirect('/census/list' )
    return render(request, 'editCensus.html', {
        'voting':voting,
        'users': users,
        'selectedUsers': selectedUsers
    })

class CensusExport(generics.RetrieveAPIView):
    def retrieve(self, request, voting_id, *args, **kwargs):
        try:
            import csv
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="census.csv"'

            writer = csv.writer(response)
            writer.writerow(['voting_id', 'voter_id'])

            for census in Census.objects.filter(voting_id=voting_id).values_list('voting_id', 'voter_id'):
                writer.writerow(census)
            #Cambio
        except Exception as e:
            return Response('Error processing request', status=ST_500)
        return response
