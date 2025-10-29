#!/usr/bin/env python3
# simple_collect.py - 직접 API 호출로 데이터 수집
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

def collect_fantasy_data():
    """Fantasy Basketball 데이터 수집"""

    load_dotenv()

    print("🏀 Yahoo Fantasy Basketball 데이터 수집 시작...")

    # 액세스 토큰 로드
    access_token = load_token()
    if not access_token:
        return None

    league_key = os.getenv('LEAGUE_KEY')
    print(f"리그 키: {league_key}")

    # 데이터 수집
    data = {
        "metadata": {
            "collected_at": datetime.now().isoformat(),
            "league_key": league_key,
            "purpose": "AI content generation for fantasy basketball analysis"
        }
    }

    # 1. 리그 정보
    print("1️⃣ 리그 정보 수집...")
    league_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}?format=json"
    league_info = make_api_request(league_url, access_token)
    if league_info:
        data["league_info"] = league_info
        print("   ✅ 리그 정보 수집 완료")

    # 2. 팀 정보
    print("2️⃣ 팀 정보 수집...")
    teams_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams?format=json"
    teams_info = make_api_request(teams_url, access_token)
    if teams_info:
        data["teams"] = teams_info
        # 팀 수 계산
        try:
            teams_count = len(teams_info.get('fantasy_content', {}).get('league', [{}])[1].get('teams', {})) - 1
            print(f"   ✅ 팀 정보 수집 완료: {teams_count}개 팀")
        except:
            print("   ✅ 팀 정보 수집 완료")

    # 3. 선수 정보 (배치로 수집)
    print("3️⃣ 선수 정보 수집...")
    all_players = []
    start = 0
    batch_size = 25

    while len(all_players) < 700:
        players_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players;start={start};count={batch_size}?format=json"
        players_batch = make_api_request(players_url, access_token)

        if players_batch:
            try:
                # Yahoo API 응답에서 선수 데이터 추출
                players_data = players_batch.get('fantasy_content', {}).get('league', [{}])[1].get('players', {})
                if isinstance(players_data, dict) and len(players_data) > 1:
                    batch_players = []
                    for key, player in players_data.items():
                        if key.isdigit():  # 숫자 키만 선수 데이터
                            batch_players.append(player)

                    if not batch_players:
                        break

                    all_players.extend(batch_players)
                    print(f"   📈 수집된 선수: {len(all_players)}명...")
                    start += batch_size
                else:
                    break
            except Exception as e:
                print(f"   ⚠️ 선수 데이터 파싱 오류: {e}")
                break
        else:
            break

    data["all_players"] = all_players
    print(f"   ✅ 총 선수: {len(all_players)}명")

    # 4. 트랜잭션
    print("4️⃣ 트랜잭션 수집...")
    transactions_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/transactions?format=json"
    transactions_info = make_api_request(transactions_url, access_token)
    if transactions_info:
        data["transactions"] = transactions_info
        try:
            trans_data = transactions_info.get('fantasy_content', {}).get('league', [{}])[1].get('transactions', {})
            trans_count = len([k for k in trans_data.keys() if k.isdigit()]) if isinstance(trans_data, dict) else 0
            print(f"   ✅ 트랜잭션 수집 완료: {trans_count}개")
        except:
            print("   ✅ 트랜잭션 수집 완료")

    # 5. 스탠딩
    print("5️⃣ 스탠딩 수집...")
    standings_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/standings?format=json"
    standings_info = make_api_request(standings_url, access_token)
    if standings_info:
        data["standings"] = standings_info
        print("   ✅ 스탠딩 수집 완료")

    # 6. Week 1 매치업 정보 (가장 중요!)
    print("6️⃣ Week 1 매치업 수집...")
    matchups_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard;week=1?format=json"
    matchups_info = make_api_request(matchups_url, access_token)

    parsed_matchups = []
    if matchups_info:
        data["week1_matchups_raw"] = matchups_info  # 원본 데이터도 저장

        try:
            # Yahoo API 응답에서 스코어보드 추출 - 올바른 경로
            scoreboard_data = matchups_info.get('fantasy_content', {}).get('league', [{}])[1].get('scoreboard', {}).get('0', {})
            matchups_data = scoreboard_data.get('matchups', {})

            if isinstance(matchups_data, dict):
                # 각 매치업 파싱 (0~7)
                for key in matchups_data.keys():
                    if key.isdigit():  # 숫자 키가 매치업 데이터
                        matchup_container = matchups_data[key]
                        matchup_data = matchup_container.get('matchup', {})

                        if matchup_data:
                            matchup_info = {
                                "matchup_id": key,
                                "week": 1,
                                "teams": [],
                                "winner": None,
                                "is_tied": matchup_data.get('is_tied', False),
                                "is_playoffs": matchup_data.get('is_playoffs', False),
                                "winner_team_key": matchup_data.get('winner_team_key', ''),
                                "status": matchup_data.get('status', ''),
                                "stat_winners": matchup_data.get('stat_winners', {})
                            }

                            # 팀 데이터는 '0' 키에 있음
                            teams_data = matchup_data.get('0', {})
                            if 'teams' in teams_data:
                                teams = teams_data['teams']

                                # 각 팀 정보 파싱
                                for team_key in teams.keys():
                                    if team_key.isdigit():
                                        team_container = teams[team_key]
                                        team_data = team_container.get('team', [{}])

                                        if len(team_data) > 1:
                                            team_info = {
                                                "team_key": team_data[0].get('team_key', ''),
                                                "name": team_data[0].get('name', 'Unknown'),
                                                "team_stats": team_data[1].get('team_stats', {}),
                                                "team_points": team_data[1].get('team_points', {}),
                                                "win_probability": team_data[1].get('win_probability', 0)
                                            }
                                            matchup_info["teams"].append(team_info)

                            # 승자 결정
                            if len(matchup_info["teams"]) == 2:
                                team1, team2 = matchup_info["teams"]

                                # 점수 비교로 승자 결정
                                team1_total = team1.get("team_points", {}).get("total", 0)
                                team2_total = team2.get("team_points", {}).get("total", 0)

                                if matchup_info["winner_team_key"]:
                                    # API에서 제공하는 승자 키 사용
                                    winner_key = matchup_info["winner_team_key"]
                                    if team1["team_key"] == winner_key:
                                        matchup_info["winner"] = team1["name"]
                                    elif team2["team_key"] == winner_key:
                                        matchup_info["winner"] = team2["name"]
                                else:
                                    # 점수로 승자 결정
                                    if team1_total > team2_total:
                                        matchup_info["winner"] = team1["name"]
                                    elif team2_total > team1_total:
                                        matchup_info["winner"] = team2["name"]

                                matchup_info["score"] = f"{team1_total}-{team2_total}"

                            parsed_matchups.append(matchup_info)

            print(f"   ✅ Week 1 매치업 파싱 완료: {len(parsed_matchups)}개 매치업")

        except Exception as e:
            print(f"   ⚠️ 매치업 파싱 오류: {e}")

    data["week1_matchups"] = parsed_matchups

    # 7. 현재 주차 매치업 (진행 중인 주차)
    print("7️⃣ 현재 주차 매치업 수집...")
    current_matchups_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard?format=json"
    current_matchups = make_api_request(current_matchups_url, access_token)

    current_parsed_matchups = []
    if current_matchups:
        data["current_matchups_raw"] = current_matchups  # 원본 데이터도 저장

        try:
            # 현재 주차 매치업도 동일하게 파싱
            current_scoreboard = current_matchups.get('fantasy_content', {}).get('league', [{}])[1].get('scoreboard', {})

            if isinstance(current_scoreboard, dict):
                for key in current_scoreboard.keys():
                    if key.isdigit():
                        matchup_data = current_scoreboard[key].get('matchup', {})

                        if matchup_data:
                            teams = matchup_data.get('teams', {})

                            matchup_info = {
                                "matchup_id": key,
                                "week": "current",
                                "teams": [],
                                "winner": None,
                                "is_tied": False,
                                "is_playoffs": matchup_data.get('is_playoffs', False)
                            }

                            for team_key in teams.keys():
                                if team_key.isdigit():
                                    team_data = teams[team_key].get('team', [{}])

                                    if len(team_data) > 1:
                                        team_info = {
                                            "team_key": team_data[0][0].get('team_key', ''),
                                            "name": team_data[0][0].get('name', 'Unknown'),
                                            "team_stats": team_data[1].get('team_stats', {}),
                                            "team_points": team_data[1].get('team_points', {}),
                                            "win_probability": team_data[1].get('win_probability', 0)
                                        }
                                        matchup_info["teams"].append(team_info)

                            # 현재 진행 상황 파악
                            if len(matchup_info["teams"]) == 2:
                                team1, team2 = matchup_info["teams"]
                                team1_total = team1.get("team_points", {}).get("total", 0)
                                team2_total = team2.get("team_points", {}).get("total", 0)

                                if team1_total > team2_total:
                                    matchup_info["leader"] = team1["name"]
                                elif team2_total > team1_total:
                                    matchup_info["leader"] = team2["name"]

                                matchup_info["current_score"] = f"{team1_total}-{team2_total}"

                            current_parsed_matchups.append(matchup_info)

            print(f"   ✅ 현재 주차 매치업 파싱 완료: {len(current_parsed_matchups)}개 매치업")

        except Exception as e:
            print(f"   ⚠️ 현재 매치업 파싱 오류: {e}")

    data["current_matchups"] = current_parsed_matchups

    # 8. 각 팀의 로스터 정보
    print("8️⃣ 팀별 로스터 수집...")
    if teams_info:
        team_rosters = {}
        try:
            teams_data = teams_info.get('fantasy_content', {}).get('league', [{}])[1].get('teams', {})
            team_keys = [k for k in teams_data.keys() if k.isdigit()]

            for i, team_key in enumerate(team_keys[:8]):  # 처음 8개 팀만 (시간 절약)
                team_data = teams_data.get(team_key, {}).get('team', [{}])
                if len(team_data) > 0:
                    team_id = team_data[0][0].get('team_key', '')
                    roster_url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{team_id}/roster?format=json"
                    roster_info = make_api_request(roster_url, access_token)
                    if roster_info:
                        team_rosters[team_id] = roster_info
                        print(f"   📊 팀 {i+1} 로스터 수집 완료")

            data["team_rosters"] = team_rosters
            print(f"   ✅ 총 {len(team_rosters)}개 팀 로스터 수집 완료")
        except Exception as e:
            print(f"   ⚠️ 로스터 수집 중 오류: {e}")

    # 9. 부상자 리스트 (DL/IL 선수들)
    print("9️⃣ 부상자 정보 수집...")
    injured_players = []
    if all_players:
        for player in all_players:
            try:
                player_data = player.get('player', [{}])
                if len(player_data) > 1:
                    player_info = player_data[1]
                    status = player_info.get('status')
                    if status in ['DL', 'IL', 'O', 'D']:  # 부상 관련 상태
                        injured_players.append({
                            'name': player_data[0][0].get('name', {}).get('full', 'Unknown'),
                            'status': status,
                            'team': player_info.get('editorial_team_abbr', 'Unknown')
                        })
            except:
                continue

    data["injured_players"] = injured_players
    print(f"   ✅ 부상자 정보 수집 완료: {len(injured_players)}명")

    # 10. 최근 트레이드만 필터링
    print("🔟 트레이드 내역 분석...")
    trades = []
    if transactions_info:
        try:
            trans_data = transactions_info.get('fantasy_content', {}).get('league', [{}])[1].get('transactions', {})
            if isinstance(trans_data, dict):
                for trans_key in trans_data.keys():
                    if trans_key.isdigit():
                        transaction = trans_data[trans_key].get('transaction', [{}])
                        if len(transaction) > 0:
                            trans_type = transaction[0][0].get('type', '')
                            if trans_type == 'trade':
                                trades.append(transaction)
        except Exception as e:
            print(f"   ⚠️ 트레이드 분석 중 오류: {e}")

    data["trades"] = trades
    print(f"   ✅ 트레이드 내역 분석 완료: {len(trades)}건")

    # 11. 현재 주차까지의 순위 변동 추적
    print("1️⃣1️⃣ 순위 변동 추적...")
    weekly_standings = {}

    # 현재가 Week 1의 3일째라면 Week 1 스탠딩만 확인
    current_week = 1  # 실제로는 리그 정보에서 가져올 수 있음

    for week in range(1, current_week + 1):
        standings_url = f"https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/standings?format=json"
        week_standings = make_api_request(standings_url, access_token)

        if week_standings:
            try:
                teams_data = week_standings.get('fantasy_content', {}).get('league', [{}])[1].get('standings', {}).get('0', {}).get('teams', {})

                parsed_standings = []
                for team_key in teams_data.keys():
                    if team_key.isdigit():
                        team_info = teams_data[team_key].get('team', [{}])
                        if len(team_info) > 1:
                            standings_info = {
                                "team_key": team_info[0].get('team_key', ''),
                                "name": team_info[0].get('name', 'Unknown'),
                                "rank": team_info[1].get('team_standings', {}).get('rank', 0),
                                "wins": team_info[1].get('team_standings', {}).get('outcome_totals', {}).get('wins', 0),
                                "losses": team_info[1].get('team_standings', {}).get('outcome_totals', {}).get('losses', 0),
                                "ties": team_info[1].get('team_standings', {}).get('outcome_totals', {}).get('ties', 0),
                                "points_for": team_info[1].get('team_standings', {}).get('points_for', 0),
                                "points_against": team_info[1].get('team_standings', {}).get('points_against', 0)
                            }
                            parsed_standings.append(standings_info)

                # 순위순으로 정렬
                parsed_standings.sort(key=lambda x: x['rank'])
                weekly_standings[f"week_{week}"] = parsed_standings

            except Exception as e:
                print(f"   ⚠️ Week {week} 스탠딩 파싱 오류: {e}")

    data["weekly_standings"] = weekly_standings
    print(f"   ✅ 순위 추적 완료: {len(weekly_standings)}주차")

    # 12. 선수별 일일 스탯 수집 (현재 주차의 지난 날짜들)
    print("1️⃣2️⃣ 선수별 일일 스탯 수집...")

    # Week 1의 3일째라면 10/21, 10/22, 10/23의 스탯 수집
    dates_to_collect = [
        "2024-10-21",  # Week 1 Day 1
        "2024-10-22",  # Week 1 Day 2
        "2024-10-23",  # Week 1 Day 3
    ]

    daily_player_stats = {}

    # 각 팀의 로스터 선수들의 일일 스탯 수집
    if teams_info:
        try:
            teams_data = teams_info.get('fantasy_content', {}).get('league', [{}])[1].get('teams', {})
            team_keys = [k for k in teams_data.keys() if k.isdigit()]

            for date in dates_to_collect:
                print(f"   📅 {date} 스탯 수집 중...")
                daily_player_stats[date] = {}

                # 처음 4개 팀만 테스트 (전체는 시간이 오래 걸림)
                for i, team_key in enumerate(team_keys[:4]):
                    team_data = teams_data.get(team_key, {}).get('team', [{}])
                    if len(team_data) > 0:
                        team_id = team_data[0].get('team_key', '')
                        team_name = team_data[0].get('name', f'Team_{i+1}')

                        # 해당 팀의 해당 날짜 스탯 요청
                        roster_stats_url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{team_id}/roster/players/stats;type=date;date={date}?format=json"
                        roster_stats = make_api_request(roster_stats_url, access_token)

                        if roster_stats:
                            daily_player_stats[date][team_name] = roster_stats
                            print(f"   📊 {team_name} {date} 스탯 수집 완료")
                        else:
                            print(f"   ⚠️ {team_name} {date} 스탯 수집 실패")

                print(f"   ✅ {date} 일일 스탯 수집 완료")

        except Exception as e:
            print(f"   ⚠️ 일일 스탯 수집 오류: {e}")

    data["daily_player_stats"] = daily_player_stats
    total_dates = len([date for date in daily_player_stats.keys() if daily_player_stats[date]])
    print(f"   ✅ 일일 스탯 수집 완료: {total_dates}일")

    # 13. 매치업별 상세 선수 성과 분석
    print("1️⃣3️⃣ 매치업별 선수 성과 분석...")

    matchup_player_performance = {}

    if parsed_matchups:
        # Week 1 매치업에서 각 팀의 선수별 성과 수집
        for matchup in parsed_matchups[:2]:  # 처음 2개 매치업만 테스트
            matchup_id = matchup['matchup_id']
            matchup_player_performance[f"matchup_{matchup_id}"] = {}

            for team in matchup['teams']:
                team_key = team['team_key']
                team_name = team['name']

                # 해당 팀의 Week 1 선수별 스탯
                team_week_stats_url = f"https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}/roster/players/stats;type=week;week=1?format=json"
                team_week_stats = make_api_request(team_week_stats_url, access_token)

                if team_week_stats:
                    matchup_player_performance[f"matchup_{matchup_id}"][team_name] = team_week_stats
                    print(f"   📊 매치업 {matchup_id} - {team_name} 선수 성과 수집 완료")

    data["matchup_player_performance"] = matchup_player_performance
    print(f"   ✅ 매치업 선수 성과 분석 완료: {len(matchup_player_performance)}개")

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

    return output_file

if __name__ == "__main__":
    if not os.path.exists('secrets.json'):
        print("❌ secrets.json 파일이 없습니다.")
        print("먼저 'python3 auth.py'를 실행해주세요.")
    else:
        collect_fantasy_data()