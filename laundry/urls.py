
from django.urls import path
from . import views

app_name = 'laundry'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('home/<str:identificador_inquilino>/', views.home_view, name='home'),
    path('usar/<int:id_maquina>/<str:identificador_inquilino>/', views.usar_maquina_view, name='usar_maquina'),
]
