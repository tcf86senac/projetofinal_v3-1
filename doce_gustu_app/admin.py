from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente, Endereco, Produto, Carrinho, ItemCarrinho, Pedido, ItemPedido

# Configuração personalizada para o Cliente no admin
class ClienteAdmin(UserAdmin):
    # Campos que serão mostrados na listagem
    list_display = ('telefone', 'nome', 'email', 'is_active', 'date_joined')
    
    # Campos que podem ser usados para buscar
    search_fields = ('telefone', 'nome', 'email')
    
    # Filtros laterais
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    # Ordenação padrão
    ordering = ('-date_joined',)
    
    # Campos que aparecem na edição (agrupados)
    fieldsets = (
        (None, {'fields': ('telefone', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'email')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Campos que aparecem ao adicionar novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telefone', 'nome', 'email', 'password1', 'password2'),
        }),
    )

# Configuração para Endereços
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'apelido', 'rua', 'numero', 'bairro', 'principal')
    list_filter = ('principal', 'bairro')
    search_fields = ('cliente__nome', 'cliente__telefone', 'rua', 'bairro')

# Registra os modelos no admin
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Endereco, EnderecoAdmin)
admin.site.register(Produto)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)
admin.site.register(Pedido)
admin.site.register(ItemPedido)