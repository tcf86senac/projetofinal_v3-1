from django.urls import path
from . import views

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
    
    # 🎯 CORRIGIDO: Agora usa a sua view personalizada
    path('login/', views.login_view, name='login'),
    
    path('carrinho/editar/<int:produto_id>/', views.editar_item_carrinho, name='editar_item_carrinho'),
    path('finalizar-pedido/', views.finalizar_pedido, name='finalizar_pedido'),
    path('pagamento/', views.pagamento, name='pagamento'),
    path('processar-pagamento/', views.processar_pagamento, name='processar_pagamento'),
    path('criar-cliente/', views.criar_cliente, name='criar_cliente'),
]