from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Produto, Carrinho, ItemCarrinho, Pedido, ItemPedido, Cliente, Endereco
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.db.models import Sum

# View para a página inicial (Home)
def home(request):
    try:
        # Busca produtos em destaque de forma aleatória
        produtos_destaque = Produto.objects.filter(destaque=True).order_by('?')[:3]
    except Exception as e:
        print(f"Erro ao buscar produtos de destaque: {e}")
        produtos_destaque = []

    try:
        doces = Produto.objects.filter(categoria='doce')[:3]
        salgados = Produto.objects.filter(categoria='salgado')[:3]
        bebidas = Produto.objects.filter(categoria='bebida')[:3]
    except Exception as e:
        print(f"Erro ao buscar produtos por categoria: {e}")
        doces = []
        salgados = []
        bebidas = []

    contexto = {
        'produtos_destaque': produtos_destaque,
        'doces': doces,
        'salgados': salgados,
        'bebidas': bebidas,
    }

    return render(request, 'index.html', contexto)

# View para a página de login
def login_view(request):
    """
    Trata o formulário de login usando o telefone e a senha.
    """
    if request.method == 'POST':
        telefone = request.POST.get('telefone')
        senha = request.POST.get('senha')
        
        try:
            # Tenta encontrar o cliente pelo telefone
            cliente = Cliente.objects.get(telefone=telefone)
            
            # 🎯 CORREÇÃO CRÍTICA: Verifique se o cliente está ativo e se a senha está correta
            if cliente.is_active and check_password(senha, cliente.password):
                # Se tudo estiver correto, faz o login do usuário
                login(request, cliente)
                messages.success(request, f'Bem-vindo(a), {cliente.nome}!')
                return redirect('doce_gustu_app:home')
            else:
                # Se o cliente não estiver ativo ou a senha estiver incorreta
                messages.error(request, 'Telefone ou senha inválidos. Tente novamente.')
        
        except Cliente.DoesNotExist:
            # Se o cliente não for encontrado
            messages.error(request, 'Telefone ou senha inválidos. Tente novamente.')
        
        return render(request, 'login.html')

    return render(request, 'login.html')

# View para a página de carrinho
def carrinho(request):
    """
    Renderiza a página do carrinho com os itens do usuário
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login para ver o carrinho.')
        return redirect('doce_gustu_app:login')

    try:
        # Pega o carrinho do usuário logado
        carrinho_usuario, criado = Carrinho.objects.get_or_create(cliente=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario)
        
        # Calcula o total do carrinho
        total_carrinho = itens_carrinho.aggregate(Sum('subtotal'))['subtotal__sum'] or 0.00
        
        contexto = {
            'itens_carrinho': itens_carrinho,
            'total_carrinho': total_carrinho,
        }
        return render(request, 'carrinho.html', contexto)

    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao carregar o carrinho: {e}')
        return redirect('doce_gustu_app:home')

# View para adicionar produtos ao carrinho
def adicionar_carrinho(request, produto_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para adicionar itens ao carrinho.')
        return redirect('doce_gustu_app:login')

    produto = get_object_or_404(Produto, id=produto_id)
    observacoes = request.POST.get('observacoes', '').strip()
    quantidade = int(request.POST.get('quantidade', 1))

    carrinho_usuario, criado = Carrinho.objects.get_or_create(cliente=request.user)
    
    # Verifica se o produto já existe no carrinho com as mesmas observações
    item_existente = ItemCarrinho.objects.filter(
        carrinho=carrinho_usuario,
        produto=produto,
        observacoes=observacoes
    ).first()

    if item_existente:
        item_existente.quantidade += quantidade
        item_existente.subtotal = item_existente.quantidade * produto.preco
        item_existente.save()
        messages.success(request, f'{produto.nome} foi adicionado novamente ao carrinho.')
    else:
        # Se o item não existir, cria um novo
        subtotal = quantidade * produto.preco
        ItemCarrinho.objects.create(
            carrinho=carrinho_usuario,
            produto=produto,
            quantidade=quantidade,
            observacoes=observacoes,
            subtotal=subtotal
        )
        messages.success(request, f'{produto.nome} foi adicionado ao carrinho.')
        
    return redirect('doce_gustu_app:carrinho')
    
# View para remover um item do carrinho
def remover_carrinho(request, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para gerenciar seu carrinho.')
        return redirect('doce_gustu_app:login')
        
    try:
        item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__cliente=request.user)
        item.delete()
        messages.success(request, f'Item removido do carrinho.')
    except Exception as e:
        messages.error(request, f'Erro ao remover item: {e}')
        
    return redirect('doce_gustu_app:carrinho')

# View para aumentar a quantidade de um item no carrinho
def aumentar_quantidade(request, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para gerenciar seu carrinho.')
        return redirect('doce_gustu_app:login')
        
    try:
        item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__cliente=request.user)
        item.quantidade += 1
        item.subtotal = item.quantidade * item.produto.preco
        item.save()
        messages.success(request, f'Quantidade de {item.produto.nome} aumentada.')
    except Exception as e:
        messages.error(request, f'Erro ao aumentar a quantidade: {e}')
        
    return redirect('doce_gustu_app:carrinho')

# View para diminuir a quantidade de um item no carrinho
def diminuir_quantidade(request, item_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Faça login para gerenciar seu carrinho.')
        return redirect('doce_gustu_app:login')
        
    try:
        item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__cliente=request.user)
        if item.quantidade > 1:
            item.quantidade -= 1
            item.subtotal = item.quantidade * item.produto.preco
            item.save()
            messages.success(request, f'Quantidade de {item.produto.nome} diminuída.')
        else:
            messages.warning(request, 'Não é possível diminuir a quantidade para menos de 1.')
    except Exception as e:
        messages.error(request, f'Erro ao diminuir a quantidade: {e}')
        
    return redirect('doce_gustu_app:carrinho')

# View para a página de cadastro de clientes
def cliente_cadastro(request):
    return render(request, 'cliente_cadastro.html')

# View para a página do cliente logado
def cliente_logado(request):
    if request.user.is_authenticated:
        contexto = {
            'cliente': request.user
        }
        return render(request, 'cliente_logado.html', contexto)
    else:
        messages.warning(request, 'Você precisa fazer login para acessar essa página.')
        return redirect('doce_gustu_app:login')

# View para a página de um único produto
def produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    item_no_carrinho = None
    
    if request.user.is_authenticated:
        try:
            carrinho_usuario = Carrinho.objects.get(cliente=request.user)
            item_no_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario, produto=produto).first()
        except Carrinho.DoesNotExist:
            pass
            
    contexto = {
        'produto': produto,
        'item_no_carrinho': item_no_carrinho,
    }
    return render(request, 'produto.html', contexto)

# View para todos os doces
def todos_doces(request):
    doces = Produto.objects.filter(categoria='doce').order_by('nome')
    contexto = {'doces': doces}
    return render(request, 'doces.html', contexto)

# View para todos os salgados
def todos_salgados(request):
    salgados = Produto.objects.filter(categoria='salgado').order_by('nome')
    contexto = {'salgados': salgados}
    return render(request, 'salgados.html', contexto)

# View para todas as bebidas
def todos_bebidas(request):
    bebidas = Produto.objects.filter(categoria='bebida').order_by('nome')
    contexto = {'bebidas': bebidas}
    return render(request, 'bebidas.html', contexto)
    
# View para editar item do carrinho
def editar_item_carrinho(request, produto_id):
    if request.method == 'POST':
        # Assegura que o usuário está logado
        if not request.user.is_authenticated:
            messages.warning(request, 'Faça login para editar o carrinho.')
            return redirect('doce_gustu_app:login')

        produto = get_object_or_404(Produto, id=produto_id)
        carrinho_usuario = get_object_or_404(Carrinho, cliente=request.user)
        
        # Pega o item do carrinho
        item = get_object_or_404(ItemCarrinho, carrinho=carrinho_usuario, produto=produto)
        
        # Pega a nova quantidade e observações do formulário
        nova_quantidade = int(request.POST.get('quantidade', item.quantidade))
        novas_observacoes = request.POST.get('observacoes', '').strip()

        # Atualiza o item
        item.quantidade = nova_quantidade
        item.observacoes = novas_observacoes
        item.subtotal = nova_quantidade * produto.preco
        item.save()
        
        messages.success(request, f'Item {produto.nome} foi atualizado no carrinho.')
        
    return redirect('doce_gustu_app:produto', produto_id=produto_id)
    
# View para a página de finalização do pedido
def finalizar_pedido(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa estar logado para finalizar o pedido.')
        return redirect('doce_gustu_app:login')

    try:
        carrinho_usuario = get_object_or_404(Carrinho, cliente=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario)
        
        if not itens_carrinho.exists():
            messages.warning(request, 'Seu carrinho está vazio.')
            return redirect('doce_gustu_app:carrinho')
            
        total_carrinho = itens_carrinho.aggregate(Sum('subtotal'))['subtotal__sum'] or 0.00
        
        # Pega os endereços do cliente
        enderecos = Endereco.objects.filter(cliente=request.user)
        
        # Opcional: define um endereço padrão (o primeiro ou o marcado como principal)
        endereco_padrao = enderecos.filter(principal=True).first()
        if not endereco_padrao and enderecos.exists():
            endereco_padrao = enderecos.first()
            
        contexto = {
            'itens_carrinho': itens_carrinho,
            'total_carrinho': total_carrinho,
            'enderecos': enderecos,
            'endereco_padrao': endereco_padrao,
        }
        
        return render(request, 'finalizar_pedido.html', contexto)
        
    except Exception as e:
        print(f"Erro ao finalizar pedido: {e}")
        messages.error(request, 'Ocorreu um erro ao finalizar o pedido. Tente novamente.')
        return redirect('doce_gustu_app:carrinho')

# View para a página de pagamento
def pagamento(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa estar logado para acessar o pagamento.')
        return redirect('doce_gustu_app:login')
        
    try:
        carrinho_usuario = get_object_or_404(Carrinho, cliente=request.user)
        total_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario).aggregate(Sum('subtotal'))['subtotal__sum'] or 0.00

        if total_carrinho == 0:
            messages.warning(request, 'Seu carrinho está vazio. Adicione itens antes de prosseguir.')
            return redirect('doce_gustu_app:carrinho')
            
        contexto = {
            'total_carrinho': total_carrinho,
        }
        return render(request, 'pagamento.html', contexto)

    except Exception as e:
        messages.error(request, 'Ocorreu um erro ao processar o pagamento. Tente novamente.')
        return redirect('doce_gustu_app:carrinho')

# View para processar o pagamento
def processar_pagamento(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Você precisa estar logado para processar o pagamento.')
            return redirect('doce_gustu_app:login')
        
        try:
            carrinho_usuario = get_object_or_404(Carrinho, cliente=request.user)
            itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho_usuario)
            
            # 1. Pega os dados do formulário
            forma_pagamento = request.POST.get('forma_pagamento')
            tipo_entrega = request.POST.get('tipo_entrega')
            
            # Validações básicas
            if not forma_pagamento or not tipo_entrega:
                messages.error(request, 'Por favor, selecione uma forma de pagamento e um tipo de entrega.')
                return redirect('doce_gustu_app:finalizar_pedido')
            
            # Lógica para criar o pedido e transferir os itens do carrinho
            total_pedido = itens_carrinho.aggregate(Sum('subtotal'))['subtotal__sum'] or 0.00
            
            novo_pedido = Pedido.objects.create(
                cliente=request.user,
                total=total_pedido,
                status='pendente',
                forma_pagamento=forma_pagamento,
                tipo_entrega=tipo_entrega
            )
            
            for item_carrinho in itens_carrinho:
                ItemPedido.objects.create(
                    pedido=novo_pedido,
                    produto=item_carrinho.produto,
                    quantidade=item_carrinho.quantidade,
                    subtotal=item_carrinho.subtotal
                )
            
            # Limpa o carrinho após a criação do pedido
            itens_carrinho.delete()
            carrinho_usuario.save()
            
            messages.success(request, 'Seu pedido foi realizado com sucesso! Em breve entraremos em contato.')
            return redirect('doce_gustu_app:home')
            
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao processar o pagamento: {e}')
            return redirect('doce_gustu_app:finalizar_pedido')
            
    messages.error(request, 'Método de requisição inválido.')
    return redirect('doce_gustu_app:finalizar_pedido')
    
# View para criar um cliente
def criar_cliente(request):
    print("Iniciando a criação de cliente...")
    if request.method == 'POST':
        try:
            # Pega os dados do formulário
            nome = request.POST.get('nome')
            telefone = request.POST.get('telefone')
            senha = request.POST.get('senha')
            
            print(f"✅ Dados recebidos. Nome: {nome}, Telefone: {telefone}")
            
            # Cria o cliente (usuário)
            cliente = Cliente.objects.create_user(
                telefone=telefone,
                nome=nome,
                password=senha,
                username=telefone  # Usa o telefone como username para autenticação
            )
            print("✅ Cliente criado com sucesso.")
            
            # Processa os endereços
            endereco_count = 0
            # Itera sobre os campos de endereço
            for index in range(5):  # Limita a 5 endereços para evitar sobrecarga
                if f'enderecos[{index}][rua]' in request.POST:
                    print(f"  Encontrado formulário de endereço na posição {index}")
                    apelido = request.POST.get(f'enderecos[{index}][apelido]')
                    rua = request.POST.get(f'enderecos[{index}][rua]')
                    numero = request.POST.get(f'enderecos[{index}][numero]', 'S/N')
                    bairro = request.POST.get(f'enderecos[{index}][bairro]')
                    cep = request.POST.get(f'enderecos[{index}][cep]')
                    referencia = request.POST.get(f'enderecos[{index}][referencia]', '')
                    
                    # Cria o endereço
                    if apelido and rua and bairro and cep:
                        Endereco.objects.create(
                            cliente=cliente,
                            apelido=apelido,
                            rua=rua,
                            numero=numero,
                            bairro=bairro,
                            cep=cep,
                            referencia=referencia,
                            principal=(endereco_count == 0)
                        )
                        endereco_count += 1
                        print(f"   ✅ Endereço criado: {apelido}")
            
            print(f"🏠 Total de endereços criados: {endereco_count}")
            
            # Faz login automático
            login(request, cliente)
            messages.success(request, f'Bem-vindo(a), {nome}! Cadastro realizado com {endereco_count} endereço(s).')
            print(f"🎉 Login automático realizado para: {cliente.telefone}")
            
            return redirect('doce_gustu_app:home')
            
        except Exception as e:
            print(f"❌ ERRO ao criar cliente: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erro ao criar conta. Tente novamente.')
            return redirect('doce_gustu_app:cliente_cadastro')