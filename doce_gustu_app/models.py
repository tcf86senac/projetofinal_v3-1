from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone

class ClienteManager(BaseUserManager):
    def create_user(self, telefone, nome, email, password=None, **extra_fields):
        if not telefone:
            raise ValueError('O telefone é obrigatório')
        if not email:
            raise ValueError('O email é obrigatório')
        
        # Remove qualquer formatação do telefone (mantém apenas números)
        telefone = ''.join(filter(str.isdigit, str(telefone)))
        
        email = self.normalize_email(email)
        cliente = self.model(
            telefone=telefone,  # Telefone limpo: 21999999999
            nome=nome,
            email=email,
            **extra_fields
        )
        
        cliente.set_password(password)
        cliente.save(using=self._db)
        return cliente
    
    def create_superuser(self, telefone, nome, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(telefone, nome, email, password, **extra_fields)

class Cliente(AbstractBaseUser, PermissionsMixin):
    telefone = models.CharField(
        max_length=11,  # 11 dígitos: 21999999999
        unique=True,
        verbose_name='Telefone (Login)'
    )
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'telefone'
    REQUIRED_FIELDS = ['nome', 'email']
    
    objects = ClienteManager()
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.nome} ({self.telefone})"
    
    @property
    def telefone_formatado(self):
        """Retorna o telefone formatado: (21) 99999-9999 (apenas para exibição)"""
        numero = str(self.telefone)
        if len(numero) == 11:
            return f"({numero[:2]}) {numero[2:7]}-{numero[7:]}"
        return numero

class Endereco(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='enderecos')
    apelido = models.CharField(max_length=50, verbose_name='Apelido (Ex: Casa, Trabalho)')
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100, default='Sua Cidade')
    cep = models.CharField(max_length=9, validators=[RegexValidator(regex=r'^\d{5}-\d{3}$')])
    referencia = models.CharField(max_length=200, blank=True, null=True)
    principal = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-principal', 'apelido']
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
    
    def __str__(self):
        return f"{self.apelido} - {self.rua}, {self.numero}"

class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrinho')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Carrinho de {self.cliente.nome}"
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.itens.all())
    
    @property
    def quantidade_itens(self):
        return sum(item.quantidade for item in self.itens.all())

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('saiu_entrega', 'Saiu para Entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao', 'Cartão na Entrega'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    endereco_entrega = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO)
    observacoes = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome}"
    
    @property
    def status_cor(self):
        cores = {
            'pendente': 'warning',
            'confirmado': 'info',
            'preparando': 'primary',
            'saiu_entrega': 'success',
            'entregue': 'success',
            'cancelado': 'danger',
        }
        return cores.get(self.status, 'secondary')

class ProdutoManager(models.Manager):
    def doces(self):
        return self.filter(categoria='doce')
    
    def salgados(self):
        return self.filter(categoria='salgado')
    
    def bebidas(self):
        return self.filter(categoria='bebida')
    
    def em_destaque(self):
        return self.filter(destaque=True)

class Produto(models.Model):
    CATEGORIAS = [
        ('doce', 'Doce'),
        ('salgado', 'Salgado'),
        ('bebida', 'Bebida'),
    ]
    
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    imagem_url = models.URLField(max_length=500, default='https://placehold.co/600x400?text=Sem+Imagem')
    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    
    objects = ProdutoManager()
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
    
    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['carrinho', 'produto']
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
    
    @property
    def subtotal(self):
        return self.quantidade * self.produto.preco
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
    
    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"