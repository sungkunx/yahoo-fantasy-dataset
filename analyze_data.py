#!/usr/bin/env python3
# analyze_data.py - 데이터 분석 실행 스크립트

import sqlite3
import pandas as pd
import os
from datetime import datetime

def connect_db():
    """데이터베이스 연결"""
    return sqlite3.connect("fantasy.db")

def run_query(query, description=""):
    """쿼리 실행 및 결과 출력"""
    con = connect_db()
    try:
        print(f"\n{'='*60}")
        print(f"{description}")
        print('='*60)

        df = pd.read_sql_query(query, con)
        if len(df) > 0:
            print(df.to_string(index=False))
        else:
            print("결과가 없습니다.")

        return df
    except Exception as e:
        print(f"쿼리 실행 오류: {e}")
        return None
    finally:
        con.close()

def main():
    """메인 분석 실행"""
    print(f"Yahoo Fantasy Basketball 데이터 분석")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 전체 데이터 현황
    query1 = """
    SELECT
        'Snapshots' as table_name, COUNT(*) as count FROM snapshots
    UNION ALL
    SELECT 'Matchups', COUNT(*) FROM matchups
    UNION ALL
    SELECT 'Rosters', COUNT(*) FROM rosters
    UNION ALL
    SELECT 'Player Stats', COUNT(*) FROM player_stats
    UNION ALL
    SELECT 'Injuries', COUNT(*) FROM injuries
    UNION ALL
    SELECT 'Transactions', COUNT(*) FROM transactions;
    """
    run_query(query1, "📊 전체 데이터 현황")

    # 2. 스냅샷별 수집 현황
    query2 = """
    SELECT
        s.snapshot_date,
        s.label,
        COUNT(DISTINCT r.team_key) as teams,
        COUNT(r.player_key) as rosters,
        COUNT(ps.player_key) as stats
    FROM snapshots s
    LEFT JOIN rosters r ON s.id = r.snapshot_id
    LEFT JOIN player_stats ps ON s.id = ps.snapshot_id
    GROUP BY s.id, s.snapshot_date, s.label
    ORDER BY s.snapshot_date;
    """
    run_query(query2, "📅 스냅샷별 데이터 수집 현황")

    # 3. 최신 매치업 결과
    query3 = """
    SELECT
        m.team_key_home as Home,
        m.score_home as H_Score,
        m.team_key_away as Away,
        m.score_away as A_Score,
        CASE
            WHEN m.score_home > m.score_away THEN m.team_key_home
            WHEN m.score_away > m.score_home THEN m.team_key_away
            ELSE 'TIE'
        END as Winner,
        ABS(m.score_home - m.score_away) as Margin
    FROM matchups m
    JOIN snapshots s ON m.snapshot_id = s.id
    WHERE s.id = (SELECT MAX(id) FROM snapshots WHERE label LIKE '%end%' OR id = (SELECT MAX(id) FROM snapshots))
    ORDER BY Margin DESC
    LIMIT 10;
    """
    run_query(query3, "🏀 최신 매치업 결과 (상위 10개)")

    # 4. 부상 선수 현황
    query4 = """
    SELECT
        i.status_code as Status,
        COUNT(*) as Count
    FROM injuries i
    JOIN snapshots s ON i.snapshot_id = s.id
    WHERE s.id = (SELECT MAX(id) FROM snapshots)
    AND i.status_code != ''
    GROUP BY i.status_code
    ORDER BY Count DESC;
    """
    run_query(query4, "🏥 부상 선수 현황")

    # 5. 거래 활동
    query5 = """
    SELECT
        type as Transaction_Type,
        COUNT(*) as Count
    FROM transactions
    GROUP BY type
    ORDER BY Count DESC;
    """
    run_query(query5, "💱 거래 활동 요약")

    # 6. 최근 거래
    query6 = """
    SELECT
        datetime(timestamp, 'unixepoch', 'localtime') as Time,
        type as Type,
        team_from as From_Team,
        team_to as To_Team
    FROM transactions
    ORDER BY timestamp DESC
    LIMIT 5;
    """
    run_query(query6, "🕒 최근 거래 내역 (최신 5개)")

if __name__ == "__main__":
    main()