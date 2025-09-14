from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'classroom_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()

    # 사용자 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 공지사항 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')

    # 과제 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            due_date TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    # 과제 제출 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            student_id INTEGER,
            filename TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assignment_id) REFERENCES assignments (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')

    # 채팅 메시지 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            room TEXT DEFAULT 'main',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 익명 건의사항 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 갤러리 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            uploaded_by INTEGER,
            approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users (id)
        )
    ''')

    # 기본 사용자 생성 (교사, 학생)
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # 교사 계정
        teacher_password = generate_password_hash('teacher123')
        c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                 ('teacher', teacher_password, 'teacher', '김선생님'))

        # 학생 계정들
        student_password = generate_password_hash('student123')
        students = [
            ('student1', '김학생'), ('student2', '이학생'), ('student3', '박학생'),
            ('student4', '최학생'), ('student5', '정학생')
        ]
        for username, name in students:
            c.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                     (username, student_password, 'student', name))

    conn.commit()
    conn.close()

# 로그인 확인 함수
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 교사 권한 확인
def teacher_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'teacher':
            flash('교사 권한이 필요합니다.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('classroom.db')
        c = conn.cursor()
        c.execute("SELECT id, password, role, name FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            session['name'] = user[3]
            flash(f'{user[3]}님, 환영합니다!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('잘못된 사용자명 또는 비밀번호입니다.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# 실시간 채팅
@app.route('/chat')
@login_required
def chat():
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("SELECT username, message, created_at FROM messages WHERE room = 'main' ORDER BY created_at DESC LIMIT 50")
    messages = c.fetchall()
    conn.close()
    return render_template('chat.html', messages=reversed(messages))

@socketio.on('join')
def on_join(data):
    username = session.get('username')
    join_room('main')
    emit('message', {'username': 'System', 'message': f'{username}님이 입장했습니다.'}, room='main')

@socketio.on('leave')
def on_leave(data):
    username = session.get('username')
    leave_room('main')
    emit('message', {'username': 'System', 'message': f'{username}님이 퇴장했습니다.'}, room='main')

@socketio.on('message')
def handle_message(data):
    if 'user_id' not in session:
        return

    username = session.get('username')
    message = data['message']

    # 데이터베이스에 저장
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, username, message, room) VALUES (?, ?, ?, ?)",
             (session['user_id'], username, message, 'main'))
    conn.commit()
    conn.close()

    emit('message', {
        'username': username,
        'message': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, room='main')

# 공지사항
@app.route('/notices')
@login_required
def notices():
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("""
        SELECT n.id, n.title, n.content, u.name, n.created_at
        FROM notices n
        JOIN users u ON n.author_id = u.id
        ORDER BY n.created_at DESC
    """)
    notices = c.fetchall()
    conn.close()
    return render_template('notices.html', notices=notices)

@app.route('/add_notice', methods=['POST'])
@teacher_required
def add_notice():
    title = request.form['title']
    content = request.form['content']

    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("INSERT INTO notices (title, content, author_id) VALUES (?, ?, ?)",
             (title, content, session['user_id']))
    conn.commit()
    conn.close()

    flash('공지사항이 등록되었습니다.', 'success')
    return redirect(url_for('notices'))

# 과제
@app.route('/assignments')
@login_required
def assignments():
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()

    if session['role'] == 'teacher':
        # 교사용: 모든 과제와 제출 현황
        c.execute("""
            SELECT a.id, a.title, a.description, a.due_date, a.created_at,
                   COUNT(s.id) as submission_count
            FROM assignments a
            LEFT JOIN submissions s ON a.id = s.assignment_id
            GROUP BY a.id
            ORDER BY a.created_at DESC
        """)
        assignments = c.fetchall()
    else:
        # 학생용: 과제와 자신의 제출 여부
        c.execute("""
            SELECT a.id, a.title, a.description, a.due_date, a.created_at,
                   s.filename as submitted_file
            FROM assignments a
            LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = ?
            ORDER BY a.created_at DESC
        """, (session['user_id'],))
        assignments = c.fetchall()

    conn.close()
    return render_template('assignments.html', assignments=assignments)

@app.route('/add_assignment', methods=['POST'])
@teacher_required
def add_assignment():
    title = request.form['title']
    description = request.form['description']
    due_date = request.form['due_date']

    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("INSERT INTO assignments (title, description, due_date, created_by) VALUES (?, ?, ?, ?)",
             (title, description, due_date, session['user_id']))
    conn.commit()
    conn.close()

    flash('과제가 등록되었습니다.', 'success')
    return redirect(url_for('assignments'))

@app.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    if 'file' not in request.files:
        flash('파일을 선택해주세요.', 'error')
        return redirect(url_for('assignments'))

    file = request.files['file']
    if file.filename == '':
        flash('파일을 선택해주세요.', 'error')
        return redirect(url_for('assignments'))

    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename

        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'assignments', filename)
        file.save(file_path)

        # 기존 제출물 삭제 후 새로 저장
        conn = sqlite3.connect('classroom.db')
        c = conn.cursor()
        c.execute("DELETE FROM submissions WHERE assignment_id = ? AND student_id = ?",
                 (assignment_id, session['user_id']))
        c.execute("INSERT INTO submissions (assignment_id, student_id, filename) VALUES (?, ?, ?)",
                 (assignment_id, session['user_id'], filename))
        conn.commit()
        conn.close()

        flash('과제가 제출되었습니다.', 'success')

    return redirect(url_for('assignments'))

# 익명 건의함
@app.route('/suggestions')
@login_required
def suggestions():
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()

    if session['role'] == 'teacher':
        c.execute("SELECT id, title, content, created_at FROM suggestions ORDER BY created_at DESC")
        suggestions = c.fetchall()
    else:
        suggestions = []

    conn.close()
    return render_template('suggestions.html', suggestions=suggestions)

@app.route('/add_suggestion', methods=['POST'])
@login_required
def add_suggestion():
    title = request.form['title']
    content = request.form['content']

    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("INSERT INTO suggestions (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()

    flash('익명 건의사항이 등록되었습니다.', 'success')
    return redirect(url_for('suggestions'))

# 갤러리
@app.route('/gallery')
@login_required
def gallery():
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()

    if session['role'] == 'teacher':
        # 교사용: 모든 사진 (승인/미승인)
        c.execute("""
            SELECT g.id, g.filename, g.original_name, u.name, g.approved, g.created_at
            FROM gallery g
            JOIN users u ON g.uploaded_by = u.id
            ORDER BY g.created_at DESC
        """)
    else:
        # 학생용: 승인된 사진만
        c.execute("""
            SELECT g.id, g.filename, g.original_name, u.name, g.approved, g.created_at
            FROM gallery g
            JOIN users u ON g.uploaded_by = u.id
            WHERE g.approved = 1
            ORDER BY g.created_at DESC
        """)

    photos = c.fetchall()
    conn.close()
    return render_template('gallery.html', photos=photos)

@app.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'file' not in request.files:
        flash('파일을 선택해주세요.', 'error')
        return redirect(url_for('gallery'))

    file = request.files['file']
    if file.filename == '':
        flash('파일을 선택해주세요.', 'error')
        return redirect(url_for('gallery'))

    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        original_name = file.filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename

        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'), exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', filename)
        file.save(file_path)

        conn = sqlite3.connect('classroom.db')
        c = conn.cursor()
        c.execute("INSERT INTO gallery (filename, original_name, uploaded_by) VALUES (?, ?, ?)",
                 (filename, original_name, session['user_id']))
        conn.commit()
        conn.close()

        flash('사진이 업로드되었습니다. 교사 승인 후 게시됩니다.', 'info')
    else:
        flash('이미지 파일만 업로드 가능합니다.', 'error')

    return redirect(url_for('gallery'))

@app.route('/approve_photo/<int:photo_id>')
@teacher_required
def approve_photo(photo_id):
    conn = sqlite3.connect('classroom.db')
    c = conn.cursor()
    c.execute("UPDATE gallery SET approved = 1 WHERE id = ?", (photo_id,))
    conn.commit()
    conn.close()

    flash('사진이 승인되었습니다.', 'success')
    return redirect(url_for('gallery'))

@app.route('/photo/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', filename))

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)