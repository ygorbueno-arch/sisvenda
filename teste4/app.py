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

    # Tabela de Vendas (Atualizada com detalhes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            produto_nome TEXT,
            quantidade INTEGER,
            total REAL
        )
    ''')
    
    # Criar admin padrão
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

# --- GESTÃO DE ESTOQUE ---

def cadastrar_produto():
    print("\n--- NOVO PRODUTO ---")
    nome = input("Nome: ")
    preco = float(input("Preço: "))
    estoque = int(input("Estoque Inicial: "))
    conn = conectar(); cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
    conn.commit(); conn.close()
    print(f"\n[OK] Produto {nome} cadastrado!")

def listar_produtos():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    print("\n--- ESTOQUE ATUAL ---")
    print(f"{'ID':<4} | {'PRODUTO':<20} | {'PREÇO':<10} | {'ESTOQUE':<8}")
    print("-" * 50)
    for p in produtos:
        print(f"{p[0]:<4} | {p[1]:<20} | R$ {p[2]:>7.2f} | {p[3]:<8}")
    conn.close()

def repor_estoque():
    listar_produtos()
    try:
        id_p = int(input("\nID do produto para repor: "))
        qtd = int(input("Quantidade a adicionar: "))
        conn = conectar(); cursor = conn.cursor()
        cursor.execute('SELECT nome FROM produtos WHERE id = ?', (id_p,))
        if cursor.fetchone():
            cursor.execute('UPDATE produtos SET estoque = estoque + ? WHERE id = ?', (qtd, id_p))
            conn.commit()
            print("\n[OK] Estoque atualizado com sucesso!")
        else:
            print("\n[ERRO] Produto não encontrado.")
        conn.close()
    except ValueError:
        print("\n[ERRO] Entrada inválida.")

# --- GESTÃO DE VENDAS ---

def nova_venda():
    listar_produtos()
    try:
        id_p = int(input("\nID do produto: "))
        qtd = int(input("Quantidade: "))
        
        conn = conectar(); cursor = conn.cursor()
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
    conn = conectar(); cursor = conn.cursor()
    cursor.execute('SELECT data, produto_nome, quantidade, total FROM vendas ORDER BY data DESC')
    vendas = cursor.fetchall()
    print("\n--- HISTÓRICO DE VENDAS ---")
    print(f"{'DATA/HORA':<20} | {'PRODUTO':<15} | {'QTD':<5} | {'TOTAL':<10}")
    print("-" * 60)
    for v in vendas:
        print(f"{v[0]:<20} | {v[1]:<15} | {v[2]:<5} | R$ {v[3]:>8.2f}")
    conn.close()

# --- GESTÃO DE CLIENTES E FUNCIONÁRIOS ---

def cadastrar_cliente():
    nome = input("Nome: "); cpf = input("CPF: "); tel = input("Tel: ")
    conn = conectar(); cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO clientes (nome, cpf, telefone) VALUES (?, ?, ?)', (nome, cpf, tel))
        conn.commit(); print(f"[OK] Cliente {nome} cadastrado!")
    except: print("[ERRO] CPF já cadastrado.")
    finally: conn.close()

def listar_clientes():
    conn = conectar(); cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes'); clientes = cursor.fetchall()
    print("\n--- CLIENTES ---")
    for c in clientes: print(f"ID: {c[0]} | {c[1]} | CPF: {c[2]}")
    conn.close()

def cadastrar_funcionario():
    u = input("Usuário: "); s = input("Senha: ")
    conn = conectar(); cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', (u, s))
        conn.commit(); print(f"[OK] Funcionário {u} criado!")
    except: print("[ERRO] Usuário já existe.")
    finally: conn.close()

# --- MENU ---

def menu(usuario_logado):
    while True:
        print(f"\n=== SISVENDA - Logado: {usuario_logado} ===")
        print("1. Nova Venda")
        print("2. Ver Histórico de Vendas")
        print("3. Repor Estoque")
        print("4. Listar Estoque")
        print("5. Cadastrar Produto")
        print("6. Cadastrar Cliente")
        print("7. Listar Clientes")
        print("8. Cadastrar Funcionário (SÓ ADMIN)")
        print("9. Sair")
        opcao = input("Escolha: ")

        if opcao == '1': nova_venda()
        elif opcao == '2': listar_vendas()
        elif opcao == '3': repor_estoque()
        elif opcao == '4': listar_produtos()
        elif opcao == '5': cadastrar_produto()
        elif opcao == '6': cadastrar_cliente()
        elif opcao == '7': listar_clientes()
        elif opcao == '8':
            if usuario_logado == 'admin':
                cadastrar_funcionario()
            else:
                print("\n[ERRO] Apenas o admin pode cadastrar funcionários.")
        elif opcao == '9': break
        else: print("Opção inválida!")

if __name__ == "__main__":
    inicializar_sistema()
    user = login()
    if user: menu(user)
    else: print("Login falhou.")