from .models import Produto

def menu_categorias(request):
    """Fornece as categorias de produtos para todos os templates"""
    return {
        'doces': Produto.objects.filter(categoria='doce').order_by('nome')[:5],  # 5 primeiros doces
        'salgados': Produto.objects.filter(categoria='salgado').order_by('nome')[:5],  # 5 primeiros salgados
        'bebidas': Produto.objects.filter(categoria='bebida').order_by('nome')[:5],  # 5 primeiros bebidas
    }