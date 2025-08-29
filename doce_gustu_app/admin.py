from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente, Endereco, Produto, Carrinho, ItemCarrinho, Pedido, ItemPedido

# Configuração personalizada para o Cliente no admin
class ClienteAdmin(UserAdmin):
    # Campos que serão mostrados na listagem
    list_display = ('telefone', 'nome', 'is_active', 'data_cadastro')

    # Campos que podem ser usados para buscar
    search_fields = ('telefone', 'nome')

    # Filtros laterais
    list_filter = ('is_active', 'is_staff', 'data_cadastro')

    # Ordenação padrão
    ordering = ('-data_cadastro',)

    # Campos que aparecem na edição (agrupados)
    fieldsets = (
        (None, {'fields': ('telefone', 'password')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'data_cadastro')}),
    )

    # Campos que aparecem ao adicionar novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telefone', 'nome', 'password', 'password2'),
        }),
    )

    # Adicionando o campo 'telefone' ao 'list_display'
    list_display_links = ('telefone', 'nome')

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