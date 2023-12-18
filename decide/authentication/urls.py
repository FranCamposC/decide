from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from .views import GetUserView, LogoutView, RegisterView,Register,Login,LoginAdmin,UserView,cerrarSesion, AdminView


urlpatterns = [
    path('registro/',Register),
    path('logueo/',Login),
    path('admin/',LoginAdmin),
    path('cerrarSesion/',cerrarSesion),
    path('user/',UserView)

]
