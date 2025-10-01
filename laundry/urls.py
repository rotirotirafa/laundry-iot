
from django.urls import path
from . import views

app_name = 'laundry'

urlpatterns = [
    path('', views.landing_page_view, name='landing_page'), # Rota para a raiz
    path('login/', views.login_view, name='login'),
    path('home/<str:identificador_inquilino>/', views.home_view, name='home'),
    path('usar/<int:id_maquina>/<str:identificador_inquilino>/', views.usar_maquina_view, name='usar_maquina'),
    path('sucesso/<str:identificador_inquilino>/', views.sucesso_view, name='sucesso'),
]
