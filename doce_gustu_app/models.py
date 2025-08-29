from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone

# Gerenciador de Usuário Personalizado (necessário para AbstractBaseUser)
class ClienteManager(BaseUserManager):
    def create_user(self, telefone, nome, password=None, **extra_fields):
        if not telefone:
            raise ValueError('O telefone é obrigatório para o cadastro')

        # Remove qualquer formatação do telefone (mantém apenas números)
        telefone = ''.join(filter(str.isdigit, str(telefone)))

        cliente = self.model(
            telefone=telefone,
            nome=nome,
            **extra_fields
        )

        cliente.set_password(password)
        cliente.save(using=self._db)
        return cliente

    def create_superuser(self, telefone, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(telefone, nome, password, **extra_fields)

# Modelo de Cliente (Usuário)
class Cliente(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(
        max_length=15,
        unique=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'telefone'
    REQUIRED_FIELDS = ['nome']

    objects = ClienteManager()

    def __str__(self):
        return self.nome

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

# Demais modelos do seu projeto
class Produto(models.Model):
    CATEGORIA_CHOICES = (
        ('doce', 'Doce'),
        ('salgado', 'Salgado'),
        ('bebida', 'Bebida'),
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem_url = models.URLField(max_length=200, blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='doce')
    destaque = models.BooleanField(default=False)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"

class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrinho')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return f"Carrinho de {self.cliente.nome}"

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    observacoes = models.TextField(blank=True, null=True)

    @property
    def subtotal(self):
        return self.quantidade * self.produto.preco

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    )

    FORMA_PAGAMENTO_CHOICES = (
        ('cartao', 'Cartão de Crédito'),
        ('dinheiro', 'Dinheiro'),
        ('pix', 'Pix'),
    )

    TIPO_ENTREGA_CHOICES = (
        ('delivery', 'Delivery'),
        ('retirada', 'Retirada no Local'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES)
    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA_CHOICES)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} no Pedido #{self.pedido.id}"

class Endereco(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='enderecos')
    apelido = models.CharField(max_length=100)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default='Cachoeiras de Macacu')
    estado = models.CharField(max_length=2, default='RJ')
    cep = models.CharField(max_length=9)
    referencia = models.TextField(blank=True, null=True)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.apelido}: {self.rua}, {self.numero}"