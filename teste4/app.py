from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_recuperacao_total'

def conectar():
    conn = sqlite3.connect('sisvenda.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializa o banco do zero
def init_db():
    with conectar() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, senha TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT UNIQUE, telefone TEXT, senha TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL, estoque INTEGER)')
        conn.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, produto_id INTEGER, quantidade INTEGER, total REAL, FOREIGN KEY (produto_id) REFERENCES produtos(id))')
        try:
            conn.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', ('admin', '123'))
        except: pass

init_db()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u, s = request.form.get('usuario'), request.form.get('senha')
    with conectar() as conn:
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND senha = ?', (u, s)).fetchone()
    if user:
        session['user'] = user['username']
        return redirect(url_for('dashboard'))
    flash('Usuário ou senha incorretos!', 'error')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('dashboard.html', usuario=session['user'])

# --- PRODUTOS ---
@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if 'user' not in session: return redirect(url_for('index'))
    with conectar() as conn:
        if request.method == 'POST':
            conn.execute('INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)', 
                         (request.form.get('nome'), request.form.get('preco'), request.form.get('estoque')))
            flash('Produto cadastrado!')
        lista = conn.execute('SELECT * FROM produtos').fetchall()
    return render_template('produtos.html', produtos=lista)

@app.route('/repor', methods=['POST'])
def repor():
    with conectar() as conn:
        conn.execute('UPDATE produtos SET estoque = estoque + ? WHERE id = ?', 
                     (request.form.get('quantidade'), request.form.get('id')))
    flash('Estoque atualizado!')
    return redirect(url_for('produtos'))

@app.route('/excluir_produto/<int:id>')
def excluir_produto(id):
    with conectar() as conn:
        conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
    flash('Produto removido!')
    return redirect(url_for('produtos'))

# --- CLIENTES ---
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if 'user' not in session: return redirect(url_for('index'))
    with conectar() as conn:
        if request.method == 'POST':
            conn.execute('INSERT INTO clientes (nome, cpf, telefone, senha) VALUES (?, ?, ?, ?)',
                         (request.form.get('nome'), request.form.get('cpf'), request.form.get('tel'), request.form.get('senha')))
            flash('Cliente cadastrado!')
        lista = conn.execute('SELECT * FROM clientes').fetchall()
    return render_template('clientes.html', clientes=lista)

@app.route('/excluir_cliente/<int:id>')
def excluir_cliente(id):
    with conectar() as conn:
        conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    return redirect(url_for('clientes'))

# --- VENDAS ---
@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    if 'user' not in session: return redirect(url_for('index'))
    with conectar() as conn:
        if request.method == 'POST':
            id_p, qtd = request.form.get('produto_id'), int(request.form.get('quantidade'))
            prod = conn.execute('SELECT * FROM produtos WHERE id = ?', (id_p,)).fetchone()
            if prod and prod['estoque'] >= qtd:
                conn.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (qtd, id_p))
                conn.execute('INSERT INTO vendas (produto_id, quantidade, total) VALUES (?, ?, ?)', 
                             (id_p, qtd, prod['preco'] * qtd))
                flash('Venda realizada!')
            else: flash('Estoque insuficiente!', 'error')
        v = conn.execute('SELECT v.*, p.nome FROM vendas v JOIN produtos p ON v.produto_id = p.id').fetchall()
        p = conn.execute('SELECT * FROM produtos').fetchall()
    return render_template('vendas.html', vendas=v, produtos=p)

# --- USUÁRIOS (ADMIN) ---
@app.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    if session.get('user') != 'admin': return redirect(url_for('dashboard'))
    with conectar() as conn:
        if request.method == 'POST':
            conn.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', (request.form.get('u'), request.form.get('s')))
        lista = conn.execute('SELECT * FROM usuarios').fetchall()
    return render_template('usuarios.html', usuarios=lista)

@app.route('/excluir_usuario/<int:id>')
def excluir_usuario(id):
    with conectar() as conn:
        conn.execute('DELETE FROM usuarios WHERE id = ? AND username != "admin"', (id,))
    return redirect(url_for('usuarios'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)