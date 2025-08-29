# Importa o path para criar URLs
from django.urls import path
# Importa as views da sua aplicação
from . import views
# Importa as views de autenticação do Django para o login e logout
from django.contrib.auth import views as auth_views

# Define o nome da sua aplicação para o sistema de URLs
app_name = 'doce_gustu_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('carrinho/remover/<int:item_id>/', views.remover_carrinho, name='remover_carrinho'),
    path('carrinho/aumentar/<int:item_id>/', views.aumentar_quantidade, name='aumentar_quantidade'),
    path('carrinho/diminuir/<int:item_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
    path('cadastro/', views.cliente_cadastro, name='cliente_cadastro'),
    path('cliente/', views.cliente_logado, name='cliente_logado'),
    path('produto/<int:produto_id>/', views.produto, name='produto'),
    path('doces/', views.todos_doces, name='todos_doces'),
    path('salgados/', views.todos_salgados, name='todos_salgados'),
    path('bebidas/', views.todos_bebidas, name='todos_bebidas'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('carrinho/editar/<int:produto_id>/', views.editar_item_carrinho, name='editar_item_carrinho'),
    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),
    path('pagamento/', views.pagamento, name='pagamento'),
    path('pagamento/processar/', views.processar_pagamento, name='processar_pagamento'),
    path('cadastro/criar/', views.criar_cliente, name='criar_cliente'),
]