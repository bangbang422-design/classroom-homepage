import http.server
import socketserver
import webbrowser
import os

PORT = 3000

print(f"🎓 우리반 ON 서버 시작")
print(f"📖 브라우저에서 http://localhost:{PORT} 로 접속하세요")
print("🛑 서버를 중지하려면 Ctrl+C를 누르세요")

# 현재 디렉토리를 classroom_app으로 변경
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 로그인 페이지 생성
login_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>로그인 - 우리반 ON</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin: 20px;
            min-height: calc(100vh - 120px);
        }
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 500;
        }
        .feature-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            text-decoration: none;
            display: block;
            transition: all 0.3s ease;
            margin: 10px 0;
        }
        .feature-card:hover {
            color: white;
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-container p-4">
            <div class="text-center mb-5">
                <i class="fas fa-school fa-4x text-primary mb-3"></i>
                <h1>우리반 ON</h1>
                <p class="lead">학생과 교사가 실시간으로 연결되는 우리반만의 온라인 교실</p>
            </div>

            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body p-5">
                            <h3 class="text-center mb-4">🎓 데모 버전</h3>

                            <div class="alert alert-info">
                                <i class="fas fa-info-circle"></i>
                                현재 Python Flask 서버가 실행되지 않아 데모 페이지를 표시합니다.
                            </div>

                            <div class="row g-3">
                                <div class="col-md-6">
                                    <a href="dashboard.html" class="feature-card card">
                                        <div class="card-body text-center p-3">
                                            <i class="fas fa-comments fa-3x mb-2"></i>
                                            <h5>실시간 채팅</h5>
                                            <p class="small">반 친구들과 실시간 대화</p>
                                        </div>
                                    </a>
                                </div>

                                <div class="col-md-6">
                                    <a href="notices.html" class="feature-card card"
                                       style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                                        <div class="card-body text-center p-3">
                                            <i class="fas fa-bullhorn fa-3x mb-2"></i>
                                            <h5>공지사항</h5>
                                            <p class="small">중요한 공지 확인</p>
                                        </div>
                                    </a>
                                </div>

                                <div class="col-md-6">
                                    <a href="assignments.html" class="feature-card card"
                                       style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);">
                                        <div class="card-body text-center p-3">
                                            <i class="fas fa-tasks fa-3x mb-2"></i>
                                            <h5>과제</h5>
                                            <p class="small">과제 확인 및 제출</p>
                                        </div>
                                    </a>
                                </div>

                                <div class="col-md-6">
                                    <a href="gallery.html" class="feature-card card"
                                       style="background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);">
                                        <div class="card-body text-center p-3">
                                            <i class="fas fa-images fa-3x mb-2"></i>
                                            <h5>앨범</h5>
                                            <p class="small">우리반 추억 공유</p>
                                        </div>
                                    </a>
                                </div>
                            </div>

                            <div class="mt-4 p-3" style="background: #f8f9fa; border-radius: 10px;">
                                <h6><i class="fas fa-key"></i> 실제 로그인 정보 (Flask 서버 실행시):</h6>
                                <div class="row">
                                    <div class="col-6">
                                        <strong>교사:</strong><br>
                                        ID: teacher<br>
                                        PW: teacher123
                                    </div>
                                    <div class="col-6">
                                        <strong>학생:</strong><br>
                                        ID: student1<br>
                                        PW: student123
                                    </div>
                                </div>
                            </div>

                            <div class="mt-4 alert alert-warning">
                                <h6><i class="fas fa-wrench"></i> 완전한 기능 사용하려면:</h6>
                                <ol class="mb-0">
                                    <li>Python 설치 (<a href="https://python.org" target="_blank">python.org</a>)</li>
                                    <li>명령 프롬프트에서: <code>pip install flask flask-socketio</code></li>
                                    <li><code>python app.py</code> 실행</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

# 대시보드 페이지
dashboard_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>대시보드 - 우리반 ON</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .main-container { background: rgba(255, 255, 255, 0.95); border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 20px; min-height: calc(100vh - 120px); }
        .feature-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; text-decoration: none; display: block; transition: all 0.3s ease; }
        .feature-card:hover { color: white; transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <div class="main-container p-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1><i class="fas fa-home"></i> 우리반 ON 대시보드</h1>
                <a href="index.html" class="btn btn-outline-primary">홈으로</a>
            </div>

            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> 데모 페이지입니다. 실제 기능은 Flask 서버 실행 후 사용 가능합니다.
            </div>

            <div class="row g-4">
                <div class="col-md-6 col-lg-4">
                    <div class="feature-card card">
                        <div class="card-body text-center p-4">
                            <i class="fas fa-comments fa-4x mb-3"></i>
                            <h5>실시간 채팅</h5>
                            <p>반 친구들과 실시간으로 대화해요</p>
                            <small>Socket.IO 기반 실시간 메시징</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 col-lg-4">
                    <div class="feature-card card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
                        <div class="card-body text-center p-4">
                            <i class="fas fa-bullhorn fa-4x mb-3"></i>
                            <h5>공지사항</h5>
                            <p>중요한 공지사항을 확인하세요</p>
                            <small>교사 전용 공지 작성 기능</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 col-lg-4">
                    <div class="feature-card card" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);">
                        <div class="card-body text-center p-4">
                            <i class="fas fa-tasks fa-4x mb-3"></i>
                            <h5>과제 관리</h5>
                            <p>과제를 확인하고 제출하세요</p>
                            <small>파일 업로드 및 마감일 관리</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 col-lg-4">
                    <div class="feature-card card" style="background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);">
                        <div class="card-body text-center p-4">
                            <i class="fas fa-images fa-4x mb-3"></i>
                            <h5>앨범</h5>
                            <p>우리반의 소중한 추억을 공유해요</p>
                            <small>교사 승인 시스템</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 col-lg-4">
                    <div class="feature-card card" style="background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);">
                        <div class="card-body text-center p-4">
                            <i class="fas fa-envelope fa-4x mb-3"></i>
                            <h5>익명 건의함</h5>
                            <p>익명으로 건의사항을 남겨보세요</p>
                            <small>완전한 익명 보장</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 col-lg-4">
                    <div class="feature-card card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); opacity: 0.7;">
                        <div class="card-body text-center p-4">
                            <i class="fas fa-user-friends fa-4x mb-3"></i>
                            <h5>1:1 대화</h5>
                            <p>개인 메시지 (준비 중)</p>
                            <small>교사-학생 개별 상담</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''

# HTML 파일들 생성
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(login_html)

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

try:
    webbrowser.open(f'http://localhost:{PORT}')
except:
    pass

with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"✅ 우리반 ON 서버가 포트 {PORT}에서 실행 중입니다...")
    httpd.serve_forever()