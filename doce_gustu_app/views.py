from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Produto, Carrinho, ItemCarrinho, Pedido, ItemPedido  # ← ADICIONE OS NOVOS MODELOS

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

# View para a página de carrinho
def carrinho(request):
    """
    Renderiza a página do carrinho com os itens do usuário
    """
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login para ver o carrinho.')
        return redirect('doce_gustu_app:login')
    
    try:
        # Busca o carrinho do usuário e seus itens
        carrinho = Carrinho.objects.get(cliente=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho).select_related('produto')
        
        # Calcula o total do carrinho usando a propriedade subtotal que já existe
        total_carrinho = sum(item.subtotal for item in itens_carrinho)
        
    except Carrinho.DoesNotExist:
        # Se não tem carrinho, mostra vazio
        itens_carrinho = []
        total_carrinho = 0
    
    contexto = {
        'itens_carrinho': itens_carrinho,  # Agora passamos os objetos diretamente
        'total_carrinho': total_carrinho,
    }
    
    return render(request, 'carrinho.html', contexto)

# View para a página de cadastro de cliente
def cliente_cadastro(request):
    """
    Renderiza a página de cadastro de cliente (cliente_cadastro.html).
    """
    return render(request, 'cliente_cadastro.html')

# View para a página do cliente logado
def cliente_logado(request):
    """
    Renderiza a página do cliente logado (cliente_logado.html).
    """
    return render(request, 'cliente_logado.html')

# View para a página de detalhes de um produto
def produto(request, produto_id):
    """
    Renderiza a página de detalhes de um produto específico.
    """
    produto = get_object_or_404(Produto, id=produto_id)
    
    # Verificar se o produto já está no carrinho do usuário
    item_no_carrinho = None
    if request.user.is_authenticated:
        try:
            carrinho = Carrinho.objects.get(cliente=request.user)
            item_no_carrinho = ItemCarrinho.objects.filter(
                carrinho=carrinho, 
                produto=produto
            ).first()
        except (Carrinho.DoesNotExist, ItemCarrinho.DoesNotExist):
            pass
    
    contexto = {
        'produto': produto,
        'item_no_carrinho': item_no_carrinho,  # Novo: informação se já está no carrinho
    }
    
    return render(request, 'produto.html', contexto)

def todos_doces(request):
    """Renderiza a página com todos os doces"""
    doces = Produto.objects.filter(categoria='doce')
    contexto = {'produtos': doces, 'categoria': 'Doces'}
    return render(request, 'categoria.html', contexto)

def todos_salgados(request):
    """Renderiza a página com todos os salgados"""
    salgados = Produto.objects.filter(categoria='salgado')
    contexto = {'produtos': salgados, 'categoria': 'Salgados'}
    return render(request, 'categoria.html', contexto)

def todos_bebidas(request):
    """Renderiza a página com todos as bebidas"""
    bebidas = Produto.objects.filter(categoria='bebida')
    contexto = {'produtos': bebidas, 'categoria': 'Bebidas'}
    return render(request, 'categoria.html', contexto)

def adicionar_carrinho(request, produto_id):
    """Adiciona um produto ao carrinho"""
    print("=" * 60)
    print("🎯 DEBUG: ADICIONAR CARRINHO FOI CHAMADO!")
    print("=" * 60)
    print(f"📝 Método: {request.method}")
    print(f"👤 Usuário: {request.user}")
    print(f"🔐 Está autenticado: {request.user.is_authenticated}")
    
    if not request.user.is_authenticated:
        print("❌ DEBUG: Usuário NÃO está logado - redirecionando para login")
        messages.warning(request, 'Você precisa fazer login para adicionar itens ao carrinho.')
        return redirect('doce_gustu_app:login')
    else:
        print("✅ DEBUG: Usuário ESTÁ logado")
    
    # Verifica se é um POST
    if request.method != 'POST':
        print("❌ DEBUG: Não é método POST - é:", request.method)
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:produto', produto_id=produto_id)
    
    print("✅ DEBUG: É método POST")
    
    # Pega dados do formulário
    quantidade = request.POST.get('quantidade', '1')
    observacoes = request.POST.get('observacoes', '')
    print(f"📦 Quantidade: {quantidade}")
    print(f"📝 Observações: {observacoes}")
    
    # Converte quantidade para número
    try:
        quantidade = int(quantidade)
    except ValueError:
        print("❌ DEBUG: Quantidade inválida")
        messages.error(request, 'Quantidade inválida.')
        return redirect('doce_gustu_app:produto', produto_id=produto_id)
    
    # Busca o produto
    try:
        produto = Produto.objects.get(id=produto_id)
        print(f"📦 Produto: {produto.nome} (ID: {produto.id})")
    except Produto.DoesNotExist:
        print("❌ DEBUG: Produto não encontrado")
        messages.error(request, 'Produto não encontrado.')
        return redirect('doce_gustu_app:home')
    
    # PASSO 1: Pegar ou criar carrinho
    print("🛒 PASSO 1: Criando/pegando carrinho...")
    try:
        carrinho, created = Carrinho.objects.get_or_create(cliente=request.user)
        print(f"✅ Carrinho: {carrinho.id}, Criado: {created}")
    except Exception as e:
        print(f"❌ ERRO ao criar carrinho: {e}")
        messages.error(request, 'Erro ao acessar carrinho.')
        return redirect('doce_gustu_app:produto', produto_id=produto.id)
    
    # PASSO 2: Adicionar item ao carrinho
    print("📦 PASSO 2: Adicionando item...")
    try:
        item, item_created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'quantidade': quantidade, 'observacoes': observacoes}
        )
        
        print(f"✅ Item: {item}, Item criado: {item_created}")
        
        # Se já existir, atualizar a quantidade
        if not item_created:
            print("📈 Item já existe - atualizando quantidade...")
            item.quantidade += quantidade
            if observacoes:
                item.observacoes = observacoes
            item.save()
            print(f"✅ Quantidade atualizada: {item.quantidade}")
        
        messages.success(request, f'{quantidade}x {produto.nome} adicionado ao carrinho!')
        print("🎉 Sucesso: Produto adicionado ao carrinho!")
        
    except Exception as e:
        print(f"❌ ERRO ao adicionar item: {e}")
        messages.error(request, 'Erro ao adicionar produto ao carrinho.')
    
    print("🔄 Redirecionando de volta para o produto...")
    # ↓↓↓↓ ESTA É A LINHA IMPORTANTE DO PASSO 3 ↓↓↓↓
    return redirect('doce_gustu_app:produto', produto_id=produto.id)


def editar_item_carrinho(request, produto_id):
    """Edita um item existente no carrinho"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login.')
        return redirect('doce_gustu_app:login')
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:produto', produto_id=produto_id)
    
    produto = get_object_or_404(Produto, id=produto_id)
    nova_quantidade = request.POST.get('quantidade')
    novas_observacoes = request.POST.get('observacoes', '')
    
    try:
        # Converte quantidade para número
        nova_quantidade = int(nova_quantidade)
        if nova_quantidade < 1:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'Quantidade inválida.')
        return redirect('doce_gustu_app:produto', produto_id=produto_id)
    
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
        item = ItemCarrinho.objects.get(carrinho=carrinho, produto=produto)
        
        # Atualiza quantidade e observações
        item.quantidade = nova_quantidade
        item.observacoes = novas_observacoes
        item.save()
        
        messages.success(request, f'Pedido de {produto.nome} atualizado!')
        
    except (Carrinho.DoesNotExist, ItemCarrinho.DoesNotExist):
        messages.error(request, 'Item não encontrado no carrinho.')
    
    return redirect('doce_gustu_app:produto', produto_id=produto_id)

def remover_carrinho(request, item_id):
    """Remove um item do carrinho"""
    print(f"🔴 DEBUG: REMOVER ITEM - ID: {item_id}")
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login.')
        return redirect('doce_gustu_app:login')
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:carrinho')
    
    try:
        # Busca o item específico no carrinho do usuário
        carrinho = Carrinho.objects.get(cliente=request.user)
        item = ItemCarrinho.objects.get(id=item_id, carrinho=carrinho)
        
        # Remove o item
        produto_nome = item.produto.nome
        item.delete()
        
        messages.success(request, f'{produto_nome} removido do carrinho!')
        print(f"✅ Item {item_id} removido com sucesso!")
        
    except (Carrinho.DoesNotExist, ItemCarrinho.DoesNotExist):
        messages.error(request, 'Item não encontrado no carrinho.')
        print(f"❌ Item {item_id} não encontrado!")
    
    return redirect('doce_gustu_app:carrinho')

def aumentar_quantidade(request, item_id):
    """Aumenta a quantidade de um item no carrinho"""
    print(f"📈 DEBUG: AUMENTAR QUANTIDADE - ID: {item_id}")
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login.')
        return redirect('doce_gustu_app:login')
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:carrinho')
    
    try:
        # Busca o item específico
        carrinho = Carrinho.objects.get(cliente=request.user)
        item = ItemCarrinho.objects.get(id=item_id, carrinho=carrinho)
        
        # Aumenta a quantidade
        item.quantidade += 1
        item.save()
        
        messages.success(request, f'Quantidade de {item.produto.nome} aumentada!')
        print(f"✅ Quantidade aumentada para {item.quantidade}")
        
    except (Carrinho.DoesNotExist, ItemCarrinho.DoesNotExist):
        messages.error(request, 'Item não encontrado no carrinho.')
        print(f"❌ Item {item_id} não encontrado!")
    
    return redirect('doce_gustu_app:carrinho')

def diminuir_quantidade(request, item_id):
    """Diminui a quantidade de um item no carrinho"""
    print(f"📉 DEBUG: DIMINUIR QUANTIDADE - ID: {item_id}")
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login.')
        return redirect('doce_gustu_app:login')
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:carrinho')
    
    try:
        # Busca o item específico
        carrinho = Carrinho.objects.get(cliente=request.user)
        item = ItemCarrinho.objects.get(id=item_id, carrinho=carrinho)
        
        # Diminui a quantidade (mínimo 1)
        if item.quantidade > 1:
            item.quantidade -= 1
            item.save()
            messages.success(request, f'Quantidade de {item.produto.nome} diminuída!')
            print(f"✅ Quantidade diminuída para {item.quantidade}")
        else:
            # Se quantidade for 1, remove o item
            produto_nome = item.produto.nome
            item.delete()
            messages.success(request, f'{produto_nome} removido do carrinho!')
            print(f"✅ Item removido (quantidade era 1)")
        
    except (Carrinho.DoesNotExist, ItemCarrinho.DoesNotExist):
        messages.error(request, 'Item não encontrado no carrinho.')
        print(f"❌ Item {item_id} não encontrado!")
    
    return redirect('doce_gustu_app:carrinho')

def finalizar_pedido(request):
    """
    Redireciona para a página de pagamento
    """
    print("🔄 DEBUG: REDIRECIONANDO PARA PAGAMENTO")
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login.')
        return redirect('doce_gustu_app:login')
    
    # Verifica se o carrinho tem itens
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
        itens = ItemCarrinho.objects.filter(carrinho=carrinho)
        
        if not itens.exists():
            messages.warning(request, 'Seu carrinho está vazio!')
            return redirect('doce_gustu_app:carrinho')
            
    except Carrinho.DoesNotExist:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('doce_gustu_app:carrinho')
    
    # Redireciona para a página de pagamento
    return redirect('doce_gustu_app:pagamento')

def pagamento(request):
    """
    Página de pagamento/checkout
    """
    print("💳 DEBUG: PÁGINA DE PAGAMENTO")
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login para finalizar a compra.')
        return redirect('doce_gustu_app:login')
    
    try:
        # Busca o carrinho do usuário
        carrinho = Carrinho.objects.get(cliente=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho).select_related('produto')
        
        if not itens_carrinho.exists():
            messages.warning(request, 'Seu carrinho está vazio!')
            return redirect('doce_gustu_app:carrinho')
        
        # Calcula o total
        total_carrinho = sum(item.subtotal for item in itens_carrinho)
        
        # Busca endereços do cliente
        enderecos = request.user.enderecos.all()
        
    except Carrinho.DoesNotExist:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('doce_gustu_app:carrinho')
    
    contexto = {
        'itens_carrinho': itens_carrinho,
        'total_carrinho': total_carrinho,
        'enderecos': enderecos,
        'usuario': request.user,  # ← ADICIONE ESTA LINHA
    }
    
    return render(request, 'pagamento.html', contexto)

def processar_pagamento(request):
    """
    Processa o pagamento e cria o pedido
    """
    print("💰 DEBUG: PROCESSANDO PAGAMENTO")
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Você precisa fazer login.')
        return redirect('doce_gustu_app:login')
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:pagamento')
    
    try:
        # Busca dados do formulário
        endereco_id = request.POST.get('endereco_id')
        forma_pagamento = request.POST.get('forma_pagamento')
        observacoes = request.POST.get('observacoes', '')
        
        # Busca carrinho e itens
        carrinho = Carrinho.objects.get(cliente=request.user)
        itens_carrinho = ItemCarrinho.objects.filter(carrinho=carrinho)
        
        if not itens_carrinho.exists():
            messages.warning(request, 'Seu carrinho está vazio!')
            return redirect('doce_gustu_app:carrinho')
        
        # Calcula total
        total = sum(item.subtotal for item in itens_carrinho)
        
        # Cria o pedido
        pedido = Pedido.objects.create(
            cliente=request.user,
            endereco_entrega_id=endereco_id,
            forma_pagamento=forma_pagamento,
            observacoes=observacoes,
            total=total
        )
        
        # Adiciona itens ao pedido
        for item in itens_carrinho:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item.produto,
                quantidade=item.quantidade,
                preco_unitario=item.produto.preco,
                observacoes=item.observacoes
            )
        
        # Limpa o carrinho
        itens_carrinho.delete()
        
        messages.success(request, f'Pedido #{pedido.id} realizado com sucesso!')
        print(f"✅ Pedido #{pedido.id} criado com sucesso!")
        
        return redirect('doce_gustu_app:cliente_logado')  # Ou uma página de confirmação
        
    except Exception as e:
        print(f"❌ ERRO ao processar pagamento: {e}")
        messages.error(request, 'Erro ao processar pedido. Tente novamente.')
        return redirect('doce_gustu_app:pagamento')
    
def criar_cliente(request):
    """
    Processa o formulário de cadastro de cliente e seus endereços
    """
    print("👤 DEBUG: CRIANDO CLIENTE COM ENDEREÇOS")
    print(f"📝 Método: {request.method}")
    
    if request.method != 'POST':
        messages.error(request, 'Método inválido.')
        return redirect('doce_gustu_app:cliente_cadastro')
    
    try:
        # Pega dados do formulário
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        print(f"📝 Dados recebidos:")
        print(f"   Nome: {nome}")
        print(f"   Email: {email}") 
        print(f"   Telefone: {telefone}")
        print(f"   Senha: {senha}")
        print(f"   Confirmar Senha: {confirmar_senha}")
        
        # Validações básicas
        if not all([nome, email, telefone, senha, confirmar_senha]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('doce_gustu_app:cliente_cadastro')
        
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('doce_gustu_app:cliente_cadastro')
        
        if len(senha) != 6 or not senha.isdigit():
            messages.error(request, 'A senha deve ter exatamente 6 números.')
            return redirect('doce_gustu_app:cliente_cadastro')
        
        # Limpa formatação do telefone (remove parênteses, traços, espaços)
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        print(f"📱 Telefone limpo: {telefone_limpo}")
        
        # Verifica se tem 10 ou 11 dígitos (com DDD)
        if len(telefone_limpo) not in [10, 11]:
            messages.error(request, 'Telefone deve ter 10 ou 11 dígitos (com DDD).')
            return redirect('doce_gustu_app:cliente_cadastro')
        
        # Verifica se telefone já existe (é único)
        from .models import Cliente
        if Cliente.objects.filter(telefone=telefone_limpo).exists():
            messages.error(request, 'Este telefone já está cadastrado.')
            return redirect('doce_gustu_app:cliente_cadastro')
        
        # Verifica se email já existe (é único)
        if Cliente.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return redirect('doce_gustu_app:cliente_cadastro')
        
        # Cria o usuário - TELEFONE É O USERNAME (LOGIN)
        from django.contrib.auth import login
        
        print("🎯 Tentando criar cliente...")
        cliente = Cliente.objects.create_user(
            telefone=telefone_limpo,
            nome=nome,
            email=email,
            password=senha
        )
        
        print(f"✅ Cliente criado com sucesso: {cliente}")
        
        # PASSO IMPORTANTE: CRIAR ENDEREÇOS
        print("🏠 Processando endereços...")
        from .models import Endereco
        
        # Contador para endereços
        endereco_count = 0
        
        # Processa cada endereço do formulário
        for key in request.POST:
            if key.startswith('enderecos['):
                # Extrai o índice do endereço
                index = key.split('[')[1].split(']')[0]
                campo = key.split('[')[2].split(']')[0]
                
                # Pega os dados do endereço
                if f'enderecos[{index}][apelido]' in request.POST:
                    apelido = request.POST.get(f'enderecos[{index}][apelido]')
                    rua = request.POST.get(f'enderecos[{index}][rua]')
                    bairro = request.POST.get(f'enderecos[{index}][bairro]')
                    cep = request.POST.get(f'enderecos[{index}][cep]')
                    referencia = request.POST.get(f'enderecos[{index}][referencia]', '')
                    
                    # Cria o endereço
                    if apelido and rua and bairro and cep:
                        Endereco.objects.create(
                            cliente=cliente,
                            apelido=apelido,
                            rua=rua,
                            numero='S/N',  # Default se não tiver número
                            bairro=bairro,
                            cep=cep,
                            referencia=referencia,
                            principal=(endereco_count == 0)  # Primeiro endereço é principal
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