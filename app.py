from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

# Koneksi ke database SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Untuk hasil query sebagai dictionary
    return conn

# Membuat tabel jika belum ada
def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        score INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Mendapatkan skor dari database
@app.route('/get_score')
def get_score():
    conn = get_db_connection()
    scores = conn.execute('SELECT * FROM scores ORDER BY score DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in scores])

# Menambahkan skor baru
@app.route('/add_score', methods=['POST'])
def add_score():
    username = request.form['username']
    score = request.form['score']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO scores (username, score) VALUES (?, ?)', (username, score))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Score added successfully'})

# Mengatur permainan Tic-Tac-Toe
players = []

@app.route('/join_game', methods=['GET'])
def join_game():
    if len(players) < 2:
        username = request.args.get('username')
        players.append(username)
        if len(players) == 2:
            return jsonify({'message': 'Game started!'})
        return jsonify({'message': 'Waiting for opponent...'})
    return jsonify({'message': 'Game is full!'})

@app.route('/game_result', methods=['POST'])
def game_result():
    result = request.json
    player1 = result.get('player1')
    player2 = result.get('player2')
    winner = result.get('winner')  # 1 if player1 wins, 2 if player2 wins, 0 for draw
    
    conn = get_db_connection()
    
    if winner == 0:
        conn.execute('UPDATE scores SET score = score + 1 WHERE username = ?', (player1,))
        conn.execute('UPDATE scores SET score = score + 1 WHERE username = ?', (player2,))
    elif winner == 1:
        conn.execute('UPDATE scores SET score = score + 1 WHERE username = ?', (player1,))
    else:
        conn.execute('UPDATE scores SET score = score + 1 WHERE username = ?', (player2,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Game result processed'})

if __name__ == '__main__':
    init_db()  # Memastikan tabel ada saat aplikasi dimulai
    app.run(host='0.0.0.0', port=5000, debug=True)
