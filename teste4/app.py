from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_mestra_sisvenda'

def conectar():
    conn = sqlite3.connect('sisvenda.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicialização completa do banco
def init_db():
    with conectar() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, senha TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, telefone TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL, estoque INTEGER)')
        conn.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, produto_id INTEGER, quantidade INTEGER, total REAL, FOREIGN KEY (produto_id) REFERENCES produtos(id))')
        try:
            conn.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', ('admin', '123'))
        except: pass

init_db()

# --- ROTAS DE NAVEGAÇÃO ---

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario, senha = request.form.get('usuario'), request.form.get('senha')
    with conectar() as conn:
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND senha = ?', (usuario, senha)).fetchone()
    if user:
        session['user'] = user['username']
        return redirect(url_for('dashboard'))
    flash('Login inválido!', 'error')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('dashboard.html', usuario=session['user'])

# --- GESTÃO DE PRODUTOS E ESTOQUE ---

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if 'user' not in session: return redirect(url_for('index'))
    with conectar() as conn:
        if request.method == 'POST':
            nome, preco, estoque = request.form.get('nome'), request.form.get('preco'), request.form.get('estoque')
            conn.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', (nome, preco, estoque))
            flash('Produto cadastrado!', 'success')
        lista = conn.execute('SELECT * FROM produtos').fetchall()
    return render_template('produtos.html', produtos=lista)

@app.route('/repor', methods=['POST'])
def repor():
    id_p, qtd = request.form.get('id'), request.form.get('quantidade')
    with conectar() as conn:
        conn.execute('UPDATE produtos SET estoque = estoque + ? WHERE id = ?', (qtd, id_p))
    flash('Estoque atualizado!', 'success')
    return redirect(url_for('produtos'))

# --- GESTÃO DE VENDAS ---

@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    if 'user' not in session: return redirect(url_for('index'))
    with conectar() as conn:
        if request.method == 'POST':
            id_p, qtd = request.form.get('produto_id'), int(request.form.get('quantidade'))
            prod = conn.execute('SELECT * FROM produtos WHERE id = ?', (id_p,)).fetchone()
            if prod and prod['estoque'] >= qtd:
                total = prod['preco'] * qtd
                conn.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (qtd, id_p))
                conn.execute('INSERT INTO vendas (produto_id, quantidade, total) VALUES (?, ?, ?)', (id_p, qtd, total))
                flash('Venda realizada!', 'success')
            else: flash('Erro no estoque!', 'error')
        
        historico = conn.execute('SELECT v.*, p.nome FROM vendas v JOIN produtos p ON v.produto_id = p.id ORDER BY v.data DESC').fetchall()
        prods = conn.execute('SELECT * FROM produtos').fetchall()
    return render_template('vendas.html', vendas=historico, produtos=prods)

# --- GESTÃO DE CLIENTES ---

@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'user' not in session: return redirect(url_for('index'))
    with conectar() as conn:
        if request.method == 'POST':
            nome, cpf, tel = request.form.get('nome'), request.form.get('cpf'), request.form.get('tel')
            try:
                conn.execute('INSERT INTO clientes (nome, cpf, telefone) VALUES (?, ?, ?)', (nome, cpf, tel))
                flash('Cliente cadastrado!', 'success')
            except: flash('CPF já existe!', 'error')
        lista = conn.execute('SELECT * FROM clientes').fetchall()
    return render_template('clientes.html', clientes=lista)

# --- GESTÃO DE FUNCIONÁRIOS (SÓ ADMIN) ---

@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if session.get('user') != 'admin':
        flash('Acesso negado!', 'error')
        return redirect(url_for('dashboard'))
    with conectar() as conn:
        if request.method == 'POST':
            u, s = request.form.get('u'), request.form.get('s')
            try:
                conn.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', (u, s))
                flash('Funcionário criado!', 'success')
            except: flash('Usuário já existe!', 'error')
        lista = conn.execute('SELECT id, username FROM usuarios').fetchall()
    return render_template('usuarios.html', usuarios=lista)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)