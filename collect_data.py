#!/usr/bin/env python3
# collect_data.py - Yahoo Fantasy 데이터 수집
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from yahoo_oauth import OAuth2
from yahoo_fantasy_api import League

def collect_fantasy_data():
    """AI 콘텐츠 생성용 Fantasy Basketball 데이터 수집"""

    load_dotenv()

    print("🏀 Yahoo Fantasy Basketball 데이터 수집 시작...")

    try:
        # OAuth 인증
        client_id = os.getenv('YAHOO_CLIENT_ID')
        client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        oauth = OAuth2(client_id, client_secret, from_file='secrets.json')
        league_key = os.getenv('LEAGUE_KEY')

        print(f"리그 키: {league_key}")

        # League 객체 생성
        league = League(oauth, league_key)

        # 데이터 수집
        data = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "league_key": league_key,
                "purpose": "AI content generation for fantasy basketball analysis"
            }
        }

        print("1️⃣ 리그 기본 정보 수집...")
        league_info = league.league()
        data["league_info"] = league_info

        print("2️⃣ 팀 정보 수집...")
        teams = league.teams()
        data["teams"] = teams
        print(f"   📊 팀 수: {len(teams)}개")

        print("3️⃣ 선수 풀 수집...")
        # 전체 선수 정보 (소유권 포함)
        all_players = []
        start = 0
        batch_size = 25

        while True:
            try:
                players_batch = league.player_details([], start=start, count=batch_size)
                if not players_batch:
                    break
                all_players.extend(players_batch)
                start += batch_size
                print(f"   📈 수집된 선수: {len(all_players)}명...")

                # 너무 많으면 제한
                if len(all_players) >= 700:
                    break

            except Exception as e:
                print(f"   ⚠️ 선수 배치 수집 중단: {e}")
                break

        data["all_players"] = all_players
        print(f"   ✅ 총 선수: {len(all_players)}명")

        print("4️⃣ 트랜잭션 정보 수집...")
        transactions = league.transactions()
        data["transactions"] = transactions
        print(f"   📊 트랜잭션: {len(transactions)}개")

        print("5️⃣ 스탠딩 정보 수집...")
        standings = league.standings()
        data["standings"] = standings

        # 파일 저장
        output_dir = "fantasy_data"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{output_dir}/fantasy_data_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(output_file)
        print(f"\n✅ 데이터 수집 완료!")
        print(f"📁 파일: {output_file}")
        print(f"📊 크기: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")

        # 요약 정보 출력
        print(f"\n📋 === 수집 요약 ===")
        print(f"🏀 리그: {league_info.get('name', 'Unknown')}")
        print(f"👥 팀: {len(teams)}개")
        print(f"🏃 선수: {len(all_players)}명")
        print(f"💰 트랜잭션: {len(transactions)}개")

        return output_file

    except Exception as e:
        print(f"❌ 데이터 수집 실패: {e}")
        return None

if __name__ == "__main__":
    if not os.path.exists('secrets.json'):
        print("❌ secrets.json 파일이 없습니다.")
        print("먼저 'python3 auth.py'를 실행해주세요.")
    else:
        collect_fantasy_data()