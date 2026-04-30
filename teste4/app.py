from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_vendas' # Necessário para usar sessões (login)

# --- CONFIGURAÇÕES DO BANCO (Igual ao anterior) ---
def conectar():
    conn = sqlite3.connect('sisvenda.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializa o banco ao rodar o app
with conectar() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, senha TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, preco REAL, estoque INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS vendas (id INTEGER PRIMARY KEY AUTOINCREMENT, data TIMESTAMP DEFAULT CURRENT_TIMESTAMP, produto_id INTEGER, quantidade INTEGER, total REAL, FOREIGN KEY (produto_id) REFERENCES produtos(id))')
    try:
        conn.execute('INSERT INTO usuarios (username, senha) VALUES (?, ?)', ('admin', '123'))
    except: pass

# --- ROTAS ---

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')
    
    with conectar() as conn:
        user = conn.execute('SELECT * FROM usuarios WHERE username = ? AND senha = ?', (usuario, senha)).fetchone()
    
    if user:
        session['user'] = user['username']
        return redirect(url_for('dashboard'))
    else:
        flash('Usuário ou senha incorretos!', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    with conectar() as conn:
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
        # Pega as últimas 5 vendas para o histórico rápido
        vendas = conn.execute('''
            SELECT v.data, p.nome, v.quantidade, v.total 
            FROM vendas v JOIN produtos p ON v.produto_id = p.id 
            ORDER BY v.data DESC LIMIT 5
        ''').fetchall()
        
    return render_template('dashboard.html', produtos=produtos, vendas=vendas, usuario=session['user'])

@app.route('/vender', methods=['POST'])
def vender():
    id_p = request.form.get('produto_id')
    qtd = int(request.form.get('quantidade'))
    
    with conectar() as conn:
        prod = conn.execute('SELECT * FROM produtos WHERE id = ?', (id_p,)).fetchone()
        
        if prod and prod['estoque'] >= qtd:
            total = prod['preco'] * qtd
            conn.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (qtd, id_p))
            conn.execute('INSERT INTO vendas (produto_id, quantidade, total) VALUES (?, ?, ?)', (id_p, qtd, total))
            conn.commit()
            flash(f'Venda de {prod["nome"]} realizada!', 'success')
        else:
            flash('Erro: Estoque insuficiente ou produto inválido.', 'error')
            
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)