import sqlite3

def conectar():
    return sqlite3.connect('sisvenda.db')

def inicializar_sistema():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Usuários (Funcionários)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT
        )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome TEXT NOT NULL, 
            preco REAL NOT NULL, 
            estoque INTEGER NOT NULL
        )
    ''')

    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            produto_nome TEXT,
            quantidade INTEGER,
            total REAL
        )
    ''')
    
    # Criar admin padrão caso não exista
    try:
        cursor.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', ('admin', '123'))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    conn.close()

def login():
    print("\n--- ACESSO AO SISTEMA ---")
    usuario = input("Usuário: ")
    senha = input("Senha: ") 
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM usuarios WHERE username = ? AND senha = ?', (usuario, senha))
    user = cursor.fetchone()
    conn.close()
    
    return user[0] if user else None

# --- FUNÇÕES DE CLIENTES ---

def cadastrar_cliente():
    print("\n--- NOVO CADASTRO DE CLIENTE ---")
    nome = input("Nome completo: ")
    cpf = input("CPF (apenas números): ")
    telefone = input("Telefone: ")
    
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO clientes (nome, cpf, telefone) VALUES (?, ?, ?)', (nome, cpf, telefone))
        conn.commit()
        print(f"\n[OK] Cliente '{nome}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\n[ERRO] Este CPF já está cadastrado.")
    finally:
        conn.close()

def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()
    
    print("\n--- LISTA DE CLIENTES ---")
    if not clientes:
        print("Nenhum cliente cadastrado.")
    else:
        print(f"{'ID':<4} | {'NOME':<20} | {'CPF':<15} | {'TELEFONE':<15}")
        print("-" * 60)
        for c in clientes:
            print(f"{c[0]:<4} | {c[1]:<20} | {c[2]:<15} | {c[3]:<15}")
    conn.close()

# --- FUNÇÕES DE VENDAS E PRODUTOS ---

def nova_venda():
    listar_produtos()
    try:
        id_p = int(input("\nID do produto: "))
        qtd = int(input("Quantidade: "))
        
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT nome, preco, estoque FROM produtos WHERE id = ?', (id_p,))
        res = cursor.fetchone()
        
        if res and res[2] >= qtd:
            nome_p, preco_p, estoque_p = res
            total = preco_p * qtd
            
            cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (qtd, id_p))
            cursor.execute('INSERT INTO vendas (produto_nome, quantidade, total) VALUES (?, ?, ?)', (nome_p, qtd, total))
            conn.commit()
            print(f"\n[SUCESSO] Venda concluída! Total: R$ {total:.2f}")
        else:
            print("\n[ERRO] Estoque insuficiente ou ID inválido.")
        conn.close()
    except ValueError:
        print("\n[ERRO] Entrada inválida.")

def listar_vendas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT data, produto_nome, quantidade, total FROM vendas ORDER BY data DESC')
    vendas = cursor.fetchall()
    print("\n--- HISTÓRICO DE VENDAS ---")
    for v in vendas:
        print(f"Data: {v[0]} | Produto: {v[1]} | Qtd: {v[2]} | Total: R$ {v[3]:.2f}")
    conn.close()

def cadastrar_produto():
    print("\n--- NOVO PRODUTO ---")
    nome = input("Nome: "); preco = float(input("Preço: ")); estoque = int(input("Estoque: "))
    conn = conectar(); cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
    conn.commit(); conn.close()
    print(f"\n[OK] Produto {nome} cadastrado!")

def listar_produtos():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    print("\n--- ESTOQUE ATUAL ---")
    for p in produtos:
        print(f"ID: {p[0]} | {p[1]} | R$ {p[2]:.2f} | Estoque: {p[3]}")
    conn.close()

def cadastrar_funcionario():
    print("\n--- CADASTRAR FUNCIONÁRIO ---")
    u = input("Usuário: "); s = input("Senha: ")
    conn = conectar(); cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', (u, s))
        conn.commit(); print(f"[OK] Funcionário {u} criado!")
    except: print("[ERRO] Usuário já existe.")
    finally: conn.close()

# --- MENU PRINCIPAL ---

def menu(usuario_logado):
    while True:
        print(f"\n=== SISVENDA - Usuário: {usuario_logado} ===")
        print("1. Nova Venda")
        print("2. Ver Histórico de Vendas")
        print("3. Cadastrar Cliente")
        print("4. Listar Clientes")
        print("5. Cadastrar Produto")
        print("6. Listar Estoque")
        print("7. Cadastrar Funcionário (SÓ ADMIN)")
        print("8. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1': nova_venda()
        elif opcao == '2': listar_vendas()
        elif opcao == '3': cadastrar_cliente()
        elif opcao == '4': listar_clientes()
        elif opcao == '5': cadastrar_produto()
        elif opcao == '6': listar_produtos()
        elif opcao == '7':
            if usuario_logado == 'admin':
                cadastrar_funcionario()
            else:
                print("\n[ERRO] Acesso negado. Apenas o administrador pode cadastrar funcionários.")
        elif opcao == '8':
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    inicializar_sistema()
    user = login()
    if user:
        menu(user)
    else:
        print("Falha no login.")