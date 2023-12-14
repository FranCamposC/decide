from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.db import IntegrityError
from django.shortcuts import get_object_or_404,render,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from census.models import Census
from voting.models import Voting


from .serializers import UserSerializer


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

def WelcomeView(request):
    return render(request,'welcome.html')

def UserView(request):
    censos=Census.objects.filter(voter_id=request.user.id)
    id_votaciones=[censo.voting_id for censo in censos]
    votaciones_usuario=Voting.objects.filter(id__in=id_votaciones)
    return render(request,'userView.html',{'votaciones':votaciones_usuario,'usuario':request.user})

def AdminView(request):
    return render(request,'adminView.html')

def Register(request):
    if request.method == 'GET':
        return render(request,'register.html',{
            'form': UserCreationForm
        })
    else:   
        if request.POST['password1']==request.POST['password2']:  
            try:
                usuario=User.objects.create_user(username=request.POST['username'],     
                                    password=request.POST['password1'])
                usuario.save()
                login(request,usuario)
                return redirect('user')
            except:
                return render(request,'register.html',{
                'form': UserCreationForm,
                    'error':'El nombre del usuario ya existe'
        })
        else:
            return render(request,'register.html',{
                'form': UserCreationForm,
                'error':'Las contraseñas no coinciden'
        })

def cerrarSesion(request):
    logout(request)
    return redirect('home')


    
def Login(request):
    if request.method=='GET':
        return render(request,'login.html',{
            'form':AuthenticationForm,
            'admin':False
        })
    else:
        usuario=authenticate(
            request,username=request.POST['username'], password=request.POST
            ['password'])
        if usuario is None:
            return render(request,'login.html',{
                'form':AuthenticationForm,
                'error':'Usuario o contraseña incorrectos',
                'admin':False
            })
        else:
            login(request,usuario)
            return redirect('user')
        
def LoginAdmin(request):
    if request.method=='GET':
        return render(request,'login.html',{
            'form':AuthenticationForm,
            'admin':True
        })
    if request.method=='POST':
        usuario=authenticate(
            request,username=request.POST['username'], password=request.POST
            ['password'])
        if usuario is None or not usuario.is_staff:
            return render(request,'login.html',{
                'form':AuthenticationForm,
                'error':'Usuario o contraseña incorrectos',
                'admin':True
            })
        else:
            login(request,usuario)
            return redirect('/user/admin')

         