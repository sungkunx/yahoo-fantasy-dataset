# auth_setup.py (강제 저장판)
import os
from yahoo_oauth import OAuth2
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

CLIENT_ID = os.getenv("YAHOO_CLIENT_ID")
CLIENT_SECRET = os.getenv("YAHOO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8080/callback")

# 저장 위치를 절대경로로 지정 (현재 폴더)
TOKEN_PATH = Path.cwd() / "oauth2.json"

print("1) Yahoo 로그인 창을 열 준비 중입니다...")

# 브라우저 콜백을 사용해 3-legged OAuth 진행
oauth = OAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    browser_callback=True,
)

# 토큰 유효성 체크/발급
if not oauth.token_is_valid():
    oauth.refresh_access_token()

# ★ 핵심: 토큰을 강제로 지정 경로에 저장
try:
    # yahoo_oauth는 기본 save()로 파일 생성 가능
    oauth.save(str(TOKEN_PATH))
except Exception as e:
    print("토큰 저장 중 예외 발생:", e)

print(f"2) 저장 시도 완료. 경로: {TOKEN_PATH}")
print(f"3) 존재 확인: {TOKEN_PATH.exists()}")
