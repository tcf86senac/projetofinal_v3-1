import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
import django
django.setup()

from django.core.files import File
from io import BytesIO
from PIL import Image
import tempfile

def criar_imagem_padrao(nome_arquivo):
    """Cria uma imagem padrão para os produtos"""
    image = Image.new('RGB', (300, 200), color='#f0f0f0')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return File(buffer, name=nome_arquivo)

def popular_produtos():
    from doce_gustu_app import Produto
    
    # Lista de produtos para cadastrar
    produtos_data = [
        # Salgados
        {
            'nome': 'Pão de Queijo Tradicional',
            'categoria': 'Salgados',
            'descricao': 'Um clássico indispensável, quentinho e com queijo derretido.',
            'preco': 3.50,
            'destaque': True
        },
        {
            'nome': 'Croissant',
            'categoria': 'Salgados',
            'descricao': 'Nas versões puro, com queijo e presunto, ou com chocolate.',
            'preco': 5.00,
            'destaque': False
        },
        {
            'nome': 'Sanduíche Natural',
            'categoria': 'Salgados',
            'descricao': 'Opção saudável e leve, com recheios como frango desfiado com requeijão ou atum.',
            'preco': 8.50,
            'destaque': False
        },
        {
            'nome': 'Coxinha',
            'categoria': 'Salgados',
            'descricao': 'Um dos salgados mais populares do Brasil, com massa macia e recheio de frango.',
            'preco': 4.00,
            'destaque': True
        },
        {
            'nome': 'Empada',
            'categoria': 'Salgados',
            'descricao': 'Pequena e saborosa, pode ser de frango com requeijão ou palmito.',
            'preco': 3.50,
            'destaque': False
        },
        {
            'nome': 'Esfiha',
            'categoria': 'Salgados',
            'descricao': 'Aberta de carne ou queijo, é uma opção rápida e prática.',
            'preco': 3.00,
            'destaque': False
        },
        {
            'nome': 'Quiche',
            'categoria': 'Salgados',
            'descricao': 'Torta salgada, pode ser de queijo (lorraine), alho-poró ou tomate seco com queijo.',
            'preco': 6.50,
            'destaque': False
        },
        {
            'nome': 'Pastel de Forno',
            'categoria': 'Salgados',
            'descricao': 'Recheado com carne, frango ou queijo e presunto. Uma ótima alternativa para quem busca algo crocante.',
            'preco': 4.50,
            'destaque': False
        },
        {
            'nome': 'Baguete Recheada',
            'categoria': 'Salgados',
            'descricao': 'Ofereça a baguete na chapa com recheios como queijo, presunto e tomate.',
            'preco': 9.00,
            'destaque': False
        },
        {
            'nome': 'Torta Salgada',
            'categoria': 'Salgados',
            'descricao': 'Porções individuais de torta de frango, frango com requeijão, ou palmito.',
            'preco': 7.50,
            'destaque': False
        },
        
        # Doces
        {
            'nome': 'Fatia de Bolo',
            'categoria': 'Doces',
            'descricao': 'O bolo caseiro é sempre um sucesso. Ofereça sabores como chocolate, fubá, laranja e cenoura com cobertura.',
            'preco': 6.00,
            'destaque': True
        },
        {
            'nome': 'Brigadeiro',
            'categoria': 'Doces',
            'descricao': 'O doce mais amado do Brasil, em versões tradicionais ou gourmets.',
            'preco': 2.50,
            'destaque': True
        },
        {
            'nome': 'Bolo de Pote',
            'categoria': 'Doces',
            'descricao': 'Prático para servir e vender, pode ser de chocolate com morango, red velvet, ou leite ninho com Nutella.',
            'preco': 8.00,
            'destaque': True
        },
        {
            'nome': 'Mousse',
            'categoria': 'Doces',
            'descricao': 'Leve e refrescante, pode ser de limão, maracujá ou chocolate.',
            'preco': 5.50,
            'destaque': False
        },
        {
            'nome': 'Brownie',
            'categoria': 'Doces',
            'descricao': 'Com casquinha crocante por fora e macio por dentro, com ou sem nozes.',
            'preco': 6.50,
            'destaque': False
        },
        {
            'nome': 'Cookie',
            'categoria': 'Doces',
            'descricao': 'Clássico americano com gotas de chocolate ou outros sabores.',
            'preco': 4.00,
            'destaque': False
        },
        {
            'nome': 'Pudim de Leite Condensado',
            'categoria': 'Doces',
            'descricao': 'Sobremesa tradicional e muito procurada.',
            'preco': 5.00,
            'destaque': False
        },
        {
            'nome': 'Palha Italiana',
            'categoria': 'Doces',
            'descricao': 'Combinação de brigadeiro e biscoito de maisena triturado.',
            'preco': 3.50,
            'destaque': False
        },
        {
            'nome': 'Cheesecake',
            'categoria': 'Doces',
            'descricao': 'Em porções individuais, com calda de frutas vermelhas ou goiabada.',
            'preco': 9.50,
            'destaque': True
        },
        {
            'nome': 'Doce de Leite',
            'categoria': 'Doces',
            'descricao': 'Servido em potes pequenos ou como recheio de tortas e bolos.',
            'preco': 4.50,
            'destaque': False
        },
    ]
    
    # Cadastrar os produtos
    for data in produtos_data:
        # Verificar se o produto já existe
        if not Produto.objects.filter(nome=data['nome']).exists():
            produto = Produto(
                nome=data['nome'],
                categoria=data['categoria'],
                descricao=data['descricao'],
                preco=data['preco'],
                destaque=data['destaque']
            )
            
            # Criar uma imagem padrão para o produto
            nome_arquivo = f"{data['nome'].replace(' ', '_').lower()}.png"
            produto.imagem.save(nome_arquivo, criar_imagem_padrao(nome_arquivo))
            
            produto.save()
            print(f"Produto cadastrado: {data['nome']}")
        else:
            print(f"Produto já existe: {data['nome']}")

if __name__ == '__main__':
    print("Iniciando cadastro de produtos...")
    popular_produtos()
    print("Cadastro concluído!")