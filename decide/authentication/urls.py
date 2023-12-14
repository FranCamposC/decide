from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterView,Register,Login,LoginAdmin,UserView,cerrarSesion


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('registro/',Register),
    path('logueo/',Login),
    path('admin/',LoginAdmin),
    path('cerrarSesion/',cerrarSesion),
    path('user/',UserView)
]
