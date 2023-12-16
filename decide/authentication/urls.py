from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from .views import GetUserView, LogoutView, RegisterView,Register,Login,UserView,cerrarSesion


urlpatterns = [
    path('registro/',Register),
    path('logueo/',Login),
    path('cerrarSesion/',cerrarSesion),
    path('user/',UserView)

]
