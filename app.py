from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import time
import datetime
import os

app = Flask(__name__)
app.secret_key = 'cyhack_secret_key_2026'
DB_PATH = 'database.db'

# Quiz Questions
QUESTIONS = [
    {"id": 1, "question": "A system administrator notices multiple login attempts from different IPs targeting the same account.", "options": ["Dictionary attack", "Distributed brute force attack", "Man-in-the-Middle attack", "ARP Spoofing"], "answer": "B"},
    {"id": 2, "question": "Packets claim to be from your router IP but with a different MAC address.", "options": ["DNS Poisoning", "ARP Spoofing", "Port Scanning", "Session Hijacking"], "answer": "B"},
    {"id": 3, "question": "nmap -sS 192.168.1.10", "options": ["UDP Scan", "SYN Scan", "ACK Scan", "Full TCP Scan"], "answer": "B"},
    {"id": 4, "question": "Files encrypted with public key decrypted with private key", "options": ["Symmetric", "Hashing", "Asymmetric", "Steganography"], "answer": "C"},
    {"id": 5, "question": "SGVsbG8gU2VjdXJpdHk=", "options": ["SHA256", "Base64", "AES", "RSA"], "answer": "B"},
    {"id": 6, "question": "Which ensures data integrity", "options": ["Encryption", "Hashing", "Encoding", "Compression"], "answer": "B"},
    {"id": 7, "question": "Low privilege user becomes root", "options": ["Enumeration", "Privilege Escalation", "Reconnaissance", "Persistence"], "answer": "B"},
    {"id": 8, "question": "' OR '1'='1", "options": ["Command Injection", "SQL Injection", "XSS", "CSRF"], "answer": "B"},
    {"id": 9, "question": "Fake email asking reset password", "options": ["Phishing", "Spoofing", "Social Engineering", "Both A and C"], "answer": "D"},
    {"id": 10, "question": "Command shows open ports", "options": ["ps", "netstat", "top", "chmod"], "answer": "B"},
    {"id": 11, "question": "Change file permission", "options": ["chmod", "chown", "passwd", "grep"], "answer": "A"},
    {"id": 12, "question": "grep 'failed' auth.log", "options": ["delete logs", "search word", "encrypt logs", "permission"], "answer": "B"},
    {"id": 13, "question": "Two factor authentication", "options": ["password", "password + OTP", "password + username", "OTP"], "answer": "B"},
    {"id": 14, "question": "Plain text password storage violates", "options": ["Confidentiality", "Availability", "Integrity", "Authentication"], "answer": "A"},
    {"id": 15, "question": "Packet capture between user and website", "options": ["MITM", "DDoS", "Brute force", "Port scan"], "answer": "A"},
    {"id": 16, "question": "../../../../etc/passwd", "options": ["RCE", "Directory traversal", "CSRF", "Clickjacking"], "answer": "B"},
    {"id": 17, "question": "Amplified traffic using reflection", "options": ["Reflection DDoS", "SYN flood", "Port scan", "Sniffing"], "answer": "A"},
    {"id": 18, "question": "DNS random queries to communicate", "options": ["DNS tunneling", "ARP poisoning", "FTP brute", "Port knocking"], "answer": "A"},
    {"id": 19, "question": "Malicious JS stored in comment", "options": ["Stored XSS", "Reflected XSS", "SQL injection", "Command injection"], "answer": "A"},
    {"id": 20, "question": "Failed login then privilege escalation", "options": ["Recon", "Initial access", "Exploitation", "Exfiltration"], "answer": "C"}
]

ACCESS_CODE = "Cyhack2016#!"
ADMIN_PASS = "admin@cyhack"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT UNIQUE,
            score INTEGER DEFAULT 0,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT,
            question_id INTEGER,
            selected_option TEXT,
            correct INTEGER,
            points INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    code = data.get('code')
    team_name = data.get('team_name')

    if code == ACCESS_CODE and team_name:
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO teams (team_name) VALUES (?)', (team_name,))
            conn.commit()
        except sqlite3.IntegrityError:
            # Team already exists, but we'll allow them to re-enter if they haven't finished? 
            # Or just deny. The prompt says "Students must enter", implying a new start.
            return jsonify({"status": "error", "message": "Team name already taken"}), 400
        finally:
            conn.close()
        
        session['team_name'] = team_name
        session['question_index'] = 0
        return jsonify({"status": "success"})
    
    return jsonify({"status": "error", "message": "Invalid access code"}), 401

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    team_name = session.get('team_name')
    if not team_name:
        return jsonify({"status": "error", "message": "No session"}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE teams SET start_time = ? WHERE team_name = ?', (datetime.datetime.now().isoformat(), team_name))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_question')
def get_question():
    if 'team_name' not in session:
        return jsonify({"status": "error", "message": "Forbidden"}), 403
    
    idx = session.get('question_index', 0)
    if idx >= len(QUESTIONS):
        return jsonify({"status": "finished"})
    
    q = QUESTIONS[idx].copy()
    # Don't send the answer to client!
    q.pop('answer')
    return jsonify({"status": "success", "question": q, "total": len(QUESTIONS), "current": idx + 1})

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'team_name' not in session:
        return jsonify({"status": "error", "message": "Forbidden"}), 403
    
    data = request.json
    selected = data.get('option')
    idx = session.get('question_index', 0)
    
    if idx >= len(QUESTIONS):
        return jsonify({"status": "error", "message": "Quiz already submitted"}), 400

    q = QUESTIONS[idx]
    is_correct = (selected == q['answer'])
    points = 5 if is_correct else 0
    
    team_name = session['team_name']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO answers (team_name, question_id, selected_option, correct, points) VALUES (?, ?, ?, ?, ?)',
                   (team_name, q['id'], selected, 1 if is_correct else 0, points))
    cursor.execute('UPDATE teams SET score = score + ? WHERE team_name = ?', (points, team_name))
    conn.commit()
    conn.close()
    
    session['question_index'] = idx + 1
    return jsonify({"status": "success", "correct": is_correct})

@app.route('/finish_quiz', methods=['POST'])
def finish_quiz():
    team_name = session.get('team_name')
    if not team_name:
        return jsonify({"status": "error"}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE teams SET end_time = ? WHERE team_name = ?', (datetime.datetime.now().isoformat(), team_name))
    conn.commit()
    conn.close()
    # Do NOT clear session yet, they need to see leaderboard? Or just clear and redirect.
    # The prompt says: "Students cannot refresh quiz page." 
    session['finished'] = True
    return jsonify({"status": "success"})

@app.route('/quiz')
def quiz_page():
    if 'team_name' not in session or session.get('finished'):
        return redirect(url_for('index'))
    return render_template('quiz.html')

@app.route('/leaderboard')
def leaderboard_page():
    conn = get_db()
    cursor = conn.cursor()
    # Sort by Score DESC, then (end_time - start_time) ASC
    # In SQLite, we can handle time difference.
    cursor.execute('''
        SELECT team_name, score, 
        (SELECT count(*) FROM answers WHERE answers.team_name = teams.team_name AND correct = 1) as correct_answers,
        (SELECT count(*) FROM answers WHERE answers.team_name = teams.team_name AND correct = 0) as wrong_answers,
        start_time, end_time
        FROM teams 
        WHERE end_time IS NOT NULL
        ORDER BY score DESC, (julianday(end_time) - julianday(start_time)) ASC
    ''')
    results = cursor.fetchall()
    conn.close()
    
    formatted_results = []
    for row in results:
        res = dict(row)
        # Calculate time finished (duration)
        if res['start_time'] and res['end_time']:
            start = datetime.datetime.fromisoformat(res['start_time'])
            end = datetime.datetime.fromisoformat(res['end_time'])
            duration = end - start
            res['time_finished'] = str(duration).split('.')[0] # HH:MM:SS
        else:
            res['time_finished'] = "N/A"
        formatted_results.append(res)

    return render_template('leaderboard.html', results=formatted_results)

@app.route('/admin')
def admin_login_page():
    return render_template('admin.html')

@app.route('/admin_results', methods=['POST'])
def admin_results():
    data = request.json
    password = data.get('password')
    if password != ADMIN_PASS:
        return jsonify({"status": "error", "message": "Invalid Password"}), 401
    
    # Return same data as leaderboard but in JSON for dynamic dashboard
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT team_name, score, 
        (SELECT count(*) FROM answers WHERE answers.team_name = teams.team_name AND correct = 1) as correct_answers,
        (SELECT count(*) FROM answers WHERE answers.team_name = teams.team_name AND correct = 0) as wrong_answers,
        start_time, end_time
        FROM teams 
        ORDER BY score DESC, (julianday(end_time) - julianday(start_time)) ASC
    ''')
    results = cursor.fetchall()
    conn.close()
    
    formatted_results = []
    for row in results:
        res = dict(row)
        if res['start_time'] and res['end_time']:
            start = datetime.datetime.fromisoformat(res['start_time'])
            end = datetime.datetime.fromisoformat(res['end_time'])
            duration = end - start
            res['time_finished'] = str(duration).split('.')[0]
        else:
            res['time_finished'] = "Pending"
        formatted_results.append(res)
        
    return jsonify({"status": "success", "results": formatted_results})

# Initialize DB on start
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
