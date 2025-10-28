#!/usr/bin/env python3
# debug_deeper.py - 더 깊은 매치업 구조 분석
import json

def analyze_deeper():
    """저장된 매치업 데이터를 더 깊이 분석"""

    try:
        with open('debug_matchups_raw.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("🔍 더 깊은 구조 분석...")

        # scoreboard -> 0 -> matchups 경로로 이동
        scoreboard = data['fantasy_content']['league'][1]['scoreboard']['0']
        print(f"scoreboard['0'] 키들: {list(scoreboard.keys())}")

        if 'matchups' in scoreboard:
            matchups = scoreboard['matchups']
            print(f"matchups 타입: {type(matchups)}")
            print(f"matchups 키들: {list(matchups.keys()) if isinstance(matchups, dict) else 'Not dict'}")

            # 숫자 키들 찾기 (실제 매치업들)
            numeric_keys = [k for k in matchups.keys() if k.isdigit()]
            print(f"매치업 숫자 키들: {numeric_keys}")
            print(f"총 매치업 수: {len(numeric_keys)}")

            # 첫 번째 매치업 구조 분석
            if numeric_keys:
                first_key = numeric_keys[0]
                first_matchup = matchups[first_key]
                print(f"\n매치업 {first_key} 구조:")
                print(f"매치업 키들: {list(first_matchup.keys())}")

                if 'matchup' in first_matchup:
                    matchup_data = first_matchup['matchup']
                    print(f"실제 매치업 데이터 키들: {list(matchup_data.keys())}")

                    if 'teams' in matchup_data:
                        teams = matchup_data['teams']
                        print(f"teams 키들: {list(teams.keys())}")

                        # 첫 번째 팀 구조 확인
                        team_keys = [k for k in teams.keys() if k.isdigit()]
                        if team_keys:
                            first_team = teams[team_keys[0]]
                            print(f"첫 번째 팀 구조: {list(first_team.keys())}")

                            if 'team' in first_team:
                                team_data = first_team['team']
                                print(f"팀 데이터 타입: {type(team_data)}")
                                if isinstance(team_data, list):
                                    print(f"팀 데이터 길이: {len(team_data)}")
                                    if len(team_data) > 0:
                                        print(f"team[0] 키들: {list(team_data[0].keys()) if isinstance(team_data[0], dict) else 'Not dict'}")
                                    if len(team_data) > 1:
                                        print(f"team[1] 키들: {list(team_data[1].keys()) if isinstance(team_data[1], dict) else 'Not dict'}")

        return True

    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return False

if __name__ == "__main__":
    analyze_deeper()