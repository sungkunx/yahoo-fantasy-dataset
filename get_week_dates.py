# get_week_dates.py (League.week_date_range 버전)
import os, sqlite3
from dotenv import load_dotenv
from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league
from datetime import datetime, timedelta

load_dotenv()
LEAGUE_KEY = os.getenv("LEAGUE_KEY")      # 예: basketball.l.12345
GAME_KEY   = os.getenv("GAME_KEY", "nba") # DB용 메타
WEEK       = int(os.getenv("WEEK", "1"))

def save_week(con, game_key, week, start, end):
    con.execute("""INSERT OR REPLACE INTO weeks(game_key, week, start_date, end_date)
                   VALUES(?,?,?,?)""", (game_key, week, start, end))
    con.commit()

if __name__ == "__main__":
    oauth = OAuth2(None, None, from_file='oauth2.json')
    lg = league.League(oauth, LEAGUE_KEY)

    # ✅ 핵심: 리그 객체의 week_date_range 사용
    start_date, end_date = lg.week_date_range(WEEK)   # returns datetime.date, datetime.date
    start = start_date.strftime("%Y-%m-%d")
    end   = end_date.strftime("%Y-%m-%d")

    d0 = datetime.fromisoformat(start)
    day1 = d0.strftime("%Y-%m-%d")
    day4 = (d0 + timedelta(days=3)).strftime("%Y-%m-%d")
    day_end = end

    con = sqlite3.connect("fantasy.db")
    save_week(con, GAME_KEY, WEEK, start, end)
    con.close()

    print(f"Week{WEEK}: start={start}, end={end}")
    print("스냅샷 권장 일자:", [day1, day4, day_end])
