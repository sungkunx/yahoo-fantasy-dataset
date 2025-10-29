# transactions.py
import os, json, sqlite3
from dotenv import load_dotenv
from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league
import pandas as pd

load_dotenv()
LEAGUE_KEY = os.getenv("LEAGUE_KEY")
GAME_KEY   = os.getenv("GAME_KEY", "nba")
WEEK       = int(os.getenv("WEEK", "1"))

def db():
    return sqlite3.connect("fantasy.db")

def get_week_range(con):
    row = con.execute("SELECT start_date, end_date FROM weeks WHERE game_key=? AND week=?",
                      (GAME_KEY, WEEK)).fetchone()
    if not row:
        raise RuntimeError("weeks 테이블이 비었습니다. 먼저 get_week_dates.py 실행.")
    return row[0], row[1]

if __name__ == "__main__":
    oauth = OAuth2(None, None, from_file='oauth2.json')
    lg = league.League(oauth, LEAGUE_KEY)
    con = db()

    start, end = get_week_range(con)
    ts_start = int(pd.Timestamp(start + " 00:00:00").timestamp())
    ts_end   = int(pd.Timestamp(end   + " 23:59:59").timestamp())

    # 모든 유형의 거래를 가져오기: add, drop, commish, trade
    tran_types = "add,drop,commish,trade"
    txs = lg.transactions(tran_types, count=50)  # 최근 50개 거래
    saved = 0
    for tx in txs:
        ts = int(tx.get('timestamp', 0))
        if ts_start <= ts <= ts_end:
            con.execute(
                """INSERT OR IGNORE INTO transactions
                   (tx_id, league_key, timestamp, type, team_from, team_to, players)
                   VALUES(?,?,?,?,?,?,?)""",
                (
                    tx.get('transaction_id', ''),
                    LEAGUE_KEY,
                    ts,
                    tx.get('type',''),
                    tx.get('team_key_from',''),
                    tx.get('team_key_to',''),
                    json.dumps(tx.get('players', []), ensure_ascii=False)
                )
            )
            saved += 1

    con.commit(); con.close()
    print(f"✅ Week{WEEK} 트랜잭션 저장: {saved}건")
