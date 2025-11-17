
from django.urls import path
from . import views

app_name = 'laundry'

urlpatterns = [
    path('', views.landing_page_view, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('usar/<int:maquina_id>/', views.usar_maquina_view, name='usar_maquina'),
    path('sucesso/', views.sucesso_view, name='sucesso'),
]
