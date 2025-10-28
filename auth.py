#!/usr/bin/env python3
# auth.py - Yahoo Fantasy OAuth 인증
import os
from dotenv import load_dotenv
from yahoo_oauth import OAuth2

def setup_oauth():
    """Yahoo Fantasy API OAuth 인증 설정"""

    load_dotenv()

    client_id = os.getenv('YAHOO_CLIENT_ID')
    client_secret = os.getenv('YAHOO_CLIENT_SECRET')

    print("🔐 Yahoo Fantasy API 인증 시작...")
    print(f"CLIENT_ID: {client_id[:15]}...")

    try:
        # OAuth 객체 생성 (브라우저 자동 열림)
        oauth = OAuth2(client_id, client_secret)

        print("✅ OAuth 인증 성공!")
        print("📁 oauth2.json 파일이 생성되었습니다.")

        return oauth

    except Exception as e:
        print(f"❌ OAuth 인증 실패: {e}")
        return None

if __name__ == "__main__":
    oauth = setup_oauth()
    if oauth:
        print("🎉 인증 완료! 이제 데이터를 수집할 수 있습니다.")
    else:
        print("❌ 인증 실패. 다시 시도해주세요.")