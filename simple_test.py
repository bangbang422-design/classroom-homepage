import http.server
import socketserver
import webbrowser
import os

PORT = 5000

print(f"🎓 우리반 ON 테스트 서버 시작")
print(f"📖 브라우저에서 http://localhost:{PORT} 로 접속하세요")
print("🛑 서버를 중지하려면 Ctrl+C를 누르세요")

# 현재 디렉토리를 classroom_app으로 변경
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 간단한 HTML 페이지 생성
html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>우리반 ON - 테스트</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 40px; text-align: center; color: white; min-height: 100vh;
        }
        .container { background: rgba(255,255,255,0.95); color: #333; padding: 40px; border-radius: 15px; max-width: 600px; margin: 0 auto; }
        h1 { color: #667eea; }
        .feature { background: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 10px; }
        .btn { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .btn:hover { background: #5a67d8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 우리반 ON</h1>
        <p>학생과 교사가 실시간으로 연결되는 우리반만의 온라인 교실</p>

        <div class="feature">
            <h3>🗨 실시간 대화창</h3>
            <p>모든 학생이 참여 가능한 실시간 채팅방</p>
        </div>

        <div class="feature">
            <h3>📢 공지사항</h3>
            <p>교사가 올리는 공지 목록, 읽음 여부 확인 가능</p>
        </div>

        <div class="feature">
            <h3>📝 과제 제시 및 제출</h3>
            <p>과제 업로드, 마감일 설정, 학생 제출 파일 확인</p>
        </div>

        <div class="feature">
            <h3>📷 앨범창</h3>
            <p>학생들이 사진 업로드, 교사 승인 후 게시</p>
        </div>

        <div class="feature">
            <h3>🕵 익명 건의함</h3>
            <p>익명으로 건의사항 작성 및 교사 피드백</p>
        </div>

        <h3 style="color: #e53e3e;">⚠️ 현재 상태: 테스트 모드</h3>
        <p>Python Flask 서버가 제대로 실행되지 않아 기본 HTML 페이지로 표시됩니다.</p>

        <h4>해결 방법:</h4>
        <ol style="text-align: left;">
            <li><strong>Python 설치 확인:</strong> 명령 프롬프트에서 <code>python --version</code> 실행</li>
            <li><strong>패키지 설치:</strong> <code>pip install flask flask-socketio</code></li>
            <li><strong>서버 실행:</strong> <code>python app.py</code></li>
        </ol>

        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <strong>💡 팁:</strong> Python이 설치되지 않았다면
            <a href="https://www.python.org/downloads/" target="_blank">python.org</a>에서 다운로드하세요.
        </div>
    </div>
</body>
</html>'''

with open('test_index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

try:
    webbrowser.open(f'http://localhost:{PORT}/test_index.html')
except:
    pass

with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"✅ 테스트 서버가 포트 {PORT}에서 실행 중입니다...")
    httpd.serve_forever()