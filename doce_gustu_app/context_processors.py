from .models import Produto

def menu_categorias(request):
    """Fornece as categorias de produtos para todos os templates"""
    return {
        'doces': Produto.objects.doces().order_by('nome')[:5],  # 5 primeiros doces
        'salgados': Produto.objects.salgados().order_by('nome')[:5],  # 5 primeiros salgados
        'bebidas': Produto.objects.bebidas().order_by('nome')[:5],  # 5 primeiros bebidas
    }