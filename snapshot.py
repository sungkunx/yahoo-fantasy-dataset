# snapshot.py (REST로 scoreboard 받기)
import os, sqlite3, json
from dotenv import load_dotenv
from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league
from datetime import datetime, timedelta
import pytz

load_dotenv()
LEAGUE_KEY = os.getenv("LEAGUE_KEY")      # 예: nba.l.12345
GAME_KEY   = os.getenv("GAME_KEY", "nba")
WEEK       = int(os.getenv("WEEK", "1"))

BASE = "https://fantasysports.yahooapis.com/fantasy/v2"

def db():
    return sqlite3.connect("fantasy.db")

def get_week_dates(con):
    row = con.execute("SELECT start_date, end_date FROM weeks WHERE game_key=? AND week=?",
                      (GAME_KEY, WEEK)).fetchone()
    if not row:
        raise RuntimeError("weeks 테이블이 비었습니다. 먼저 get_week_dates.py 실행.")
    return row[0], row[1]

def insert_snapshot(con, date_str, label):
    cur = con.cursor()
    cur.execute("INSERT INTO snapshots(league_key, snapshot_date, week, label) VALUES(?,?,?,?)",
                (LEAGUE_KEY, date_str, WEEK, label))
    con.commit()
    return cur.lastrowid

# ✅ 리그 스코어보드는 REST로 직접 호출
def fetch_scoreboard_json(oauth, league_key, week):
    url = f"{BASE}/league/{league_key}/scoreboard;week={week}?format=json"
    r = oauth.session.get(url)
    r.raise_for_status()
    return r.json()

def save_scoreboard_rest(con, oauth, snapshot_id):
    data = fetch_scoreboard_json(oauth, LEAGUE_KEY, WEEK)

    # 디버깅을 위해 응답 구조 출력 (더 많이)
    print("=== API 응답 구조 ===")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:5000])
    print("================")

    fc = data.get("fantasy_content", {})
    league_node = fc.get("league")

    # league_node가 list인 경우(일반적): scoreboard가 들어있는 dict를 찾아라
    scoreboard_list = None
    if isinstance(league_node, list):
        for item in league_node:
            if isinstance(item, dict) and "scoreboard" in item:
                scoreboard_list = item["scoreboard"]
                break
    elif isinstance(league_node, dict):
        scoreboard_list = league_node.get("scoreboard")

    if scoreboard_list is None:
        print("ERROR: scoreboard 노드를 찾지 못했습니다.")
        print(f"league_node type: {type(league_node)}")
        if isinstance(league_node, list):
            print(f"league_node items: {[list(item.keys()) if isinstance(item, dict) else type(item) for item in league_node]}")
        elif isinstance(league_node, dict):
            print(f"league_node keys: {list(league_node.keys())}")
        return  # 에러 대신 그냥 리턴

    # scoreboard_list는 {'week': '1', '0': {'matchups': {...}}} 형태의 dict
    matchups_node = None
    if isinstance(scoreboard_list, dict):
        # '0' 키에서 matchups 찾기
        if "0" in scoreboard_list and isinstance(scoreboard_list["0"], dict):
            matchups_node = scoreboard_list["0"].get("matchups")

    if not isinstance(matchups_node, dict):
        print("ERROR: matchups 노드를 찾지 못했습니다.")
        print(f"scoreboard_list type: {type(scoreboard_list)}")
        if isinstance(scoreboard_list, dict):
            print(f"scoreboard_list keys: {list(scoreboard_list.keys())}")
            if "0" in scoreboard_list:
                print(f"scoreboard_list['0'] keys: {list(scoreboard_list['0'].keys()) if isinstance(scoreboard_list['0'], dict) else type(scoreboard_list['0'])}")
        return  # 에러 대신 그냥 리턴

    count = int(matchups_node.get("count", 0))

    def extract_team_fields(team_node):
        """
        team_node는 보통 list:
        [
          {'team_key': 'nba.l.12345.t.1'},
          {'team_id': '1'},
          {'name': '...'},
          ...,
          {'team_points': {'total': '7'}},  # H2H 카테고리 리그 등
        ]
        """
        team_key = ""
        team_id = 0
        points_total = 0.0

        # list 또는 dict 모두 처리
        if isinstance(team_node, list):
            for elem in team_node:
                if isinstance(elem, dict):
                    if "team_key" in elem:
                        team_key = elem["team_key"]
                    if "team_id" in elem:
                        try:
                            team_id = int(elem["team_id"])
                        except Exception:
                            pass
                    if "team_points" in elem:
                        try:
                            points_total = float(elem["team_points"].get("total", 0) or 0)
                        except Exception:
                            points_total = 0.0
        elif isinstance(team_node, dict):
            team_key = team_node.get("team_key", "")
            try:
                team_id = int(team_node.get("team_id", 0))
            except Exception:
                team_id = 0
            tp = team_node.get("team_points", {})
            try:
                points_total = float(tp.get("total", 0) or 0)
            except Exception:
                points_total = 0.0

        return team_key, team_id, points_total

    for i in range(count):
        matchup = matchups_node[str(i)]["matchup"]

        # 실제 구조: matchup["0"]["teams"]["0"]["team"] 형태
        if "0" in matchup and "teams" in matchup["0"]:
            teams = matchup["0"]["teams"]
            if "0" in teams and "1" in teams:
                th = teams["0"]["team"]
                ta = teams["1"]["team"]
            else:
                print(f"Matchup {i}: teams 구조가 예상과 다릅니다. keys: {list(teams.keys())}")
                continue
        else:
            print(f"Matchup {i}: 예상 구조를 찾을 수 없습니다. keys: {list(matchup.keys())}")
            continue

        # 각 팀 정보 추출
        tkey_h, tid_h, pts_h = extract_team_fields(th)
        tkey_a, tid_a, pts_a = extract_team_fields(ta)

        # 홈/어웨이는 JSON에 명확치 않은 경우가 있어 team_id로 정렬(작은 id를 home으로)
        if tid_h == 0 or tid_a == 0:
            # team_id 판단이 어려우면 순서 그대로 기록
            team_key_home, team_key_away = tkey_h, tkey_a
            score_home, score_away = pts_h, pts_a
        else:
            if tid_h <= tid_a:
                team_key_home, team_key_away = tkey_h, tkey_a
                score_home, score_away = pts_h, pts_a
            else:
                team_key_home, team_key_away = tkey_a, tkey_h
                score_home, score_away = pts_a, pts_h

        con.execute(
            """INSERT INTO matchups(snapshot_id, matchup_id, team_key_home, team_key_away, score_home, score_away)
               VALUES(?,?,?,?,?,?)""",
            (
                snapshot_id,
                matchup.get("matchup_id", ""),
                team_key_home,
                team_key_away,
                score_home,
                score_away,
            ),
        )

    con.commit()


def save_rosters_injuries_stats(con, lg, snapshot_id, date_str):
    teams = lg.teams()
    print(f"팀 정보 타입: {type(teams)}")

    # teams가 dict인 경우 values를 사용하거나 keys를 사용
    if isinstance(teams, dict):
        print(f"팀 dict 키들: {list(teams.keys())}")
        team_keys = []
        # dict의 값들이 team_key라면
        for key, value in teams.items():
            if isinstance(value, str):
                team_keys.append(value)
            elif isinstance(value, dict) and 'team_key' in value:
                team_keys.append(value['team_key'])
            else:
                team_keys.append(key)  # 키 자체가 team_key일 수도
    else:
        team_keys = teams

    # 모든 팀 처리
    for team_key in team_keys:
        print(f"처리중인 팀: {team_key}")
        roster = lg.to_team(team_key).roster(date_str)  # 날짜별 로스터
        print(f"Roster 타입: {type(roster)}, 길이: {len(roster) if hasattr(roster, '__len__') else 'N/A'}")
        if roster and len(roster) > 0:
            print(f"첫 번째 플레이어 타입: {type(roster[0])}, 내용: {roster[0]}")

        for p in roster:
            if isinstance(p, str):
                print(f"플레이어가 문자열입니다: {p}")
                continue

            player_key = p.get('player_key', '') or str(p.get('player_id', ''))
            selected_pos = p.get('selected_position', '')
            if isinstance(selected_pos, dict):
                pos = selected_pos.get('position', '')
                starting_flag = 1 if selected_pos.get('is_starting', 0) else 0
            else:
                pos = str(selected_pos)  # 문자열인 경우
                starting_flag = 1  # 기본값

            con.execute("""INSERT INTO rosters(snapshot_id, team_key, player_key, position, starting_flag)
                           VALUES(?,?,?,?,?)""",
                        (snapshot_id, team_key, player_key, pos, starting_flag))

            status = p.get('status','')
            note = p.get('status_full','') or p.get('editorial_player_notes','')
            con.execute("""INSERT INTO injuries(snapshot_id, player_key, status_code, status_note)
                           VALUES(?,?,?,?)""",
                        (snapshot_id, player_key, status, note))

        # 팀의 모든 플레이어 통계를 한 번에 수집 (API 효율성을 위해)
        player_ids = [int(p.get('player_id', 0)) for p in roster if p.get('player_id')]
        if player_ids:
            try:
                stats_data = lg.player_stats(player_ids, 'date', date=date_str)
                print(f"팀 {team_key}의 {len(player_ids)}명 선수 통계 수집 시도")

                for player_stat in stats_data:
                    player_id = str(player_stat.get('player_id', ''))
                    if player_id:
                        for stat_key, stat_value in player_stat.items():
                            if stat_key not in ['player_id', 'name', 'position_type'] and stat_value is not None:
                                con.execute("""INSERT INTO player_stats(snapshot_id, player_key, stat_id, value)
                                               VALUES(?,?,?,?)""",
                                            (snapshot_id, player_id, stat_key, str(stat_value)))
                print(f"팀 {team_key} 통계 수집 완료")
            except Exception as e:
                print(f"팀 {team_key} 통계 수집 오류: {e}")
    con.commit()

if __name__ == "__main__":
    oauth = OAuth2(None, None, from_file='oauth2.json')
    lg = league.League(oauth, LEAGUE_KEY)
    con = db()

    start, end = get_week_dates(con)

    # 한국 시간 기준으로 설정 (KST = UTC+9)
    kst = pytz.timezone('Asia/Seoul')
    utc = pytz.UTC

    # 시작일을 한국 시간으로 변환
    d0 = datetime.fromisoformat(start)
    if d0.tzinfo is None:
        d0 = utc.localize(d0)  # UTC로 가정
    d0_kst = d0.astimezone(kst)

    # 한국 시간 기준 오후 6시 (경기 종료 후)를 고려한 스냅샷 시점
    snapshot_dates = [
        (d0_kst.strftime("%Y-%m-%d"), "week1_day1"),
        ((d0_kst + timedelta(days=3)).strftime("%Y-%m-%d"), "week1_day4"),
        (end, "week1_end"),  # 주차 종료일
    ]

    for date_str, label in snapshot_dates:
        print(f"[스냅샷] {label} @ {date_str}")
        sid = insert_snapshot(con, date_str, label)
        # 🔁 스코어보드(REST)
        save_scoreboard_rest(con, oauth, sid)
        # 🔁 로스터/부상/스탯(래퍼)
        save_rosters_injuries_stats(con, lg, sid, date_str)

    con.close()
    print("✅ 스냅샷 저장 완료")
