# auth_init.py
from yahoo_oauth import OAuth2

# 중요한 포인트: from_file='oauth2.json'
oauth = OAuth2(None, None, from_file="oauth2.json", browser_callback=True)

# 토큰이 없거나 만료면 알아서 브라우저 열어 인증 → 같은 파일에 토큰을 기록
if not oauth.token_is_valid():
    oauth.refresh_access_token()

print("✅ 인증 완료. 이제 oauth2.json 안에 access_token/refresh_token이 들어 있습니다.")
