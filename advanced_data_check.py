#!/usr/bin/env python3
# advanced_data_check.py - 고급 데이터 가용성 확인
import os
import json
import requests
from datetime import datetime
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

def make_api_request(url, access_token):
    """Yahoo API 요청"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ API 요청 실패: {response.status_code} - {url}")
            return None
    except Exception as e:
        print(f"❌ API 요청 오류: {e}")
        return None

def check_advanced_data():
    """고급 데이터 가용성 확인"""

    load_dotenv()

    access_token = load_token()
    if not access_token:
        return

    league_key = os.getenv('LEAGUE_KEY')
    print(f"🔍 고급 데이터 가용성 확인 중... (리그: {league_key})")

    # 1. 각 주차별 순위와 매치업 결과
    print("\n1️⃣ 주차별 순위와 매치업 결과 확인...")

    # Week 1 스탠딩
    standings_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/standings?format=json"
    standings_data = make_api_request(standings_url, access_token)
    if standings_data:
        print("   ✅ 리그 스탠딩 데이터 가용")

        # 스탠딩 구조 간단 분석
        try:
            teams = standings_data.get('fantasy_content', {}).get('league', [{}])[1].get('standings', {}).get('0', {}).get('teams', {})
            team_count = len([k for k in teams.keys() if k.isdigit()])
            print(f"   📊 스탠딩에서 확인된 팀 수: {team_count}")
        except:
            print("   📊 스탠딩 구조 분석 필요")

    # Week 2 매치업 시도 (다른 주차 데이터 확인)
    week2_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard;week=2?format=json"
    week2_data = make_api_request(week2_url, access_token)
    if week2_data:
        print("   ✅ Week 2 매치업 데이터 가용")
    else:
        print("   ⚠️ Week 2 매치업 데이터 미가용 (아직 시작 안됨)")

    # 2. 실제 NBA 경기 결과 확인
    print("\n2️⃣ NBA 경기 결과 데이터 확인...")

    # NBA 게임 정보 시도
    nba_games_url = f"https://fantasysports.yahooapis.com/fantasy/v2/game/nba/games;date=2024-10-24?format=json"
    nba_games = make_api_request(nba_games_url, access_token)
    if nba_games:
        print("   ✅ NBA 경기 결과 데이터 가용")

        # 경기 데이터 구조 확인
        with open('debug_nba_games.json', 'w', encoding='utf-8') as f:
            json.dump(nba_games, f, indent=2, ensure_ascii=False)
        print("   📁 NBA 경기 데이터를 debug_nba_games.json에 저장")
    else:
        print("   ⚠️ NBA 경기 결과 직접 접근 불가")

    # 3. 선수별 일일 스탯 확인
    print("\n3️⃣ 선수별 일일 스탯 확인...")

    # 특정 선수의 스탯 시도 (LeBron James 예시)
    player_stats_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players;player_keys=nba.p.3704/stats;type=date;date=2024-10-24?format=json"
    player_stats = make_api_request(player_stats_url, access_token)
    if player_stats:
        print("   ✅ 선수별 일일 스탯 데이터 가용")

        with open('debug_player_stats.json', 'w', encoding='utf-8') as f:
            json.dump(player_stats, f, indent=2, ensure_ascii=False)
        print("   📁 선수 스탯 데이터를 debug_player_stats.json에 저장")
    else:
        print("   ⚠️ 선수별 일일 스탯 직접 접근 어려움")

    # 4. 팀 로스터의 일일 스탯 확인
    print("\n4️⃣ 팀 로스터 일일 스탯 확인...")

    # 첫 번째 팀의 로스터 스탯 시도
    roster_stats_url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{league_key}.t.1/roster/players/stats;type=date;date=2024-10-24?format=json"
    roster_stats = make_api_request(roster_stats_url, access_token)
    if roster_stats:
        print("   ✅ 팀 로스터 일일 스탯 데이터 가용")

        with open('debug_roster_stats.json', 'w', encoding='utf-8') as f:
            json.dump(roster_stats, f, indent=2, ensure_ascii=False)
        print("   📁 로스터 스탯 데이터를 debug_roster_stats.json에 저장")
    else:
        print("   ⚠️ 팀 로스터 일일 스탯 접근 제한")

    # 5. 매치업 내 선수별 스탯 확인
    print("\n5️⃣ 매치업 내 선수별 스탯 확인...")

    # Week 1 매치업 상세 정보 (선수 스탯 포함)
    detailed_matchup_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard;week=1/matchups/teams/roster/players/stats?format=json"
    detailed_matchup = make_api_request(detailed_matchup_url, access_token)
    if detailed_matchup:
        print("   ✅ 매치업 내 선수별 스탯 데이터 가용")

        with open('debug_detailed_matchup.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_matchup, f, indent=2, ensure_ascii=False)
        print("   📁 상세 매치업 데이터를 debug_detailed_matchup.json에 저장")
    else:
        print("   ⚠️ 매치업 내 선수별 스탯 복잡한 접근 필요")

    print("\n📋 === 고급 데이터 가용성 요약 ===")
    print("✅ 가능한 데이터:")
    print("   • 리그 스탠딩 (전체 순위)")
    print("   • 주차별 매치업 결과")
    print("   • 팀별 로스터 정보")
    print("   • 트랜잭션 내역")

    print("\n🔍 추가 조사 필요:")
    print("   • NBA 실제 경기 결과 (다른 엔드포인트 필요)")
    print("   • 선수별 일일 스탯 (특별한 쿼리 방식 필요)")
    print("   • 매치업 내 상세 선수 성과")

if __name__ == "__main__":
    check_advanced_data()