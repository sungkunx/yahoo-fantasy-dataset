#!/usr/bin/env python3
# debug_matchups.py - 매치업 데이터 구조 분석
import os
import json
import requests
from dotenv import load_dotenv

def load_token():
    """secrets.json에서 액세스 토큰 로드"""
    try:
        with open('secrets.json', 'r') as f:
            token_data = json.load(f)
        return token_data.get('access_token')
    except Exception as e:
        print(f"❌ 토큰 로드 실패: {e}")
        return None

def debug_matchup_structure():
    """매치업 데이터 구조 디버깅"""

    load_dotenv()

    access_token = load_token()
    if not access_token:
        return

    league_key = os.getenv('LEAGUE_KEY')
    print(f"🔍 매치업 데이터 구조 분석 중... (리그: {league_key})")

    # Week 1 매치업 요청
    matchups_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard;week=1?format=json"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(matchups_url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            # 원본 데이터를 파일로 저장
            with open('debug_matchups_raw.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print("✅ 원본 데이터를 debug_matchups_raw.json에 저장했습니다.")

            # 데이터 구조 분석
            print("\n🔍 데이터 구조 분석:")

            # 최상위 키들
            print(f"최상위 키들: {list(data.keys())}")

            if 'fantasy_content' in data:
                fantasy_content = data['fantasy_content']
                print(f"fantasy_content 키들: {list(fantasy_content.keys())}")

                if 'league' in fantasy_content:
                    league_data = fantasy_content['league']
                    print(f"league 타입: {type(league_data)}")

                    if isinstance(league_data, list) and len(league_data) > 1:
                        print(f"league[0] 키들: {list(league_data[0].keys()) if isinstance(league_data[0], dict) else 'Not dict'}")
                        print(f"league[1] 키들: {list(league_data[1].keys()) if isinstance(league_data[1], dict) else 'Not dict'}")

                        if 'scoreboard' in league_data[1]:
                            scoreboard = league_data[1]['scoreboard']
                            print(f"scoreboard 타입: {type(scoreboard)}")
                            print(f"scoreboard 키들: {list(scoreboard.keys()) if isinstance(scoreboard, dict) else 'Not dict'}")

                            # 숫자 키 찾기
                            numeric_keys = [k for k in scoreboard.keys() if k.isdigit()]
                            print(f"숫자 키들 (매치업들): {numeric_keys}")

                            # 첫 번째 매치업 구조 분석
                            if numeric_keys:
                                first_matchup_key = numeric_keys[0]
                                first_matchup = scoreboard[first_matchup_key]
                                print(f"\n첫 번째 매치업 ({first_matchup_key}) 구조:")
                                print(f"매치업 키들: {list(first_matchup.keys())}")

                                if 'matchup' in first_matchup:
                                    matchup_data = first_matchup['matchup']
                                    print(f"matchup 키들: {list(matchup_data.keys())}")

                                    if 'teams' in matchup_data:
                                        teams = matchup_data['teams']
                                        print(f"teams 타입: {type(teams)}")
                                        print(f"teams 키들: {list(teams.keys()) if isinstance(teams, dict) else 'Not dict'}")

            return True

        else:
            print(f"❌ API 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")
        return False

if __name__ == "__main__":
    debug_matchup_structure()