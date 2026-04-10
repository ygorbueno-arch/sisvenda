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
    cursor.execute('SELECT * FROM usuarios WHERE username = ? AND senha = ?', (usuario, senha))
    user = cursor.fetchone()
    conn.close()
    
    return user is not None

# --- NOVAS FUNÇÕES SOLICITADAS ---

def cadastrar_funcionario():
    print("\n--- CADASTRAR NOVO FUNCIONÁRIO ---")
    usuario = input("Defina o nome de usuário: ")
    senha = input("Defina a senha: ")
    
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', (usuario, senha))
        conn.commit()
        print(f"\n[OK] Funcionário '{usuario}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\n[ERRO] Este nome de usuário já existe.")
    finally:
        conn.close()

def repor_estoque():
    listar_produtos()
    try:
        id_p = int(input("\nID do produto para repor: "))
        qtd = int(input("Quantidade a ser adicionada: "))
        
        if qtd <= 0:
            print("[ERRO] A quantidade deve ser maior que zero.")
            return

        conn = conectar()
        cursor = conn.cursor()
        
        # Verifica se o produto existe
        cursor.execute('SELECT nome FROM produtos WHERE id = ?', (id_p,))
        produto = cursor.fetchone()
        
        if produto:
            cursor.execute('UPDATE produtos SET estoque = estoque + ? WHERE id = ?', (qtd, id_p))
            conn.commit()
            print(f"\n[OK] Estoque de '{produto[0]}' atualizado (+{qtd}).")
        else:
            print("\n[ERRO] Produto não encontrado.")
        conn.close()
    except ValueError:
        print("\n[ERRO] Entrada inválida. Use apenas números.")

# --- Funções Existentes Mantidas/Ajustadas ---

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
        print(f"\n[OK] Cliente {nome} cadastrado!")
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
    for c in clientes:
        print(f"ID: {c[0]} | Nome: {c[1]} | CPF: {c[2]}")
    conn.close()

def cadastrar_produto():
    print("\n--- NOVO PRODUTO ---")
    nome = input("Nome do produto: ")
    preco = float(input("Preço: "))
    estoque = int(input("Quantidade inicial: "))
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
    conn.commit()
    conn.close()
    print(f"\n[OK] {nome} cadastrado!")

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    print("\n--- ESTOQUE ATUAL ---")
    for p in produtos:
        print(f"ID: {p[0]} | {p[1]} | R$ {p[2]:.2f} | Estoque: {p[3]}")
    conn.close()

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
            total = res[1] * qtd
            cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (qtd, id_p))
            cursor.execute('INSERT INTO vendas (total) VALUES (?)', (total,))
            conn.commit()
            print(f"\n[SUCESSO] Venda concluída! Total: R$ {total:.2f}")
        else:
            print("\n[ERRO] Estoque insuficiente ou ID inválido.")
        conn.close()
    except ValueError:
        print("\n[ERRO] Entrada inválida.")

# --- Menu Principal ---

def menu():
    while True:
        print("\n=== SISVENDA - MENU PRINCIPAL ===")
        print("1. Nova Venda")
        print("2. Cadastrar Produto")
        print("3. Repor Estoque")
        print("4. Listar Estoque")
        print("5. Cadastrar Cliente")
        print("6. Listar Clientes")
        print("7. Cadastrar Funcionário")
        print("8. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1': nova_venda()
        elif opcao == '2': cadastrar_produto()
        elif opcao == '3': repor_estoque()
        elif opcao == '4': listar_produtos()
        elif opcao == '5': cadastrar_cliente()
        elif opcao == '6': listar_clientes()
        elif opcao == '7': cadastrar_funcionario()
        elif opcao == '8':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    inicializar_sistema()
    
    tentativas = 3
    while tentativas > 0:
        if login():
            menu()
            break
        else:
            tentativas -= 1
            print(f"Login incorreto! Tentativas restantes: {tentativas}")
    
    if tentativas == 0:
        print("Acesso bloqueado por segurança.")