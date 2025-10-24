-- Yahoo Fantasy Basketball 분석 쿼리

-- ======================
-- 1. 기본 데이터 요약
-- ======================

-- 전체 데이터 현황
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

-- 스냅샷별 데이터 수집 현황
SELECT
    s.snapshot_date,
    s.label,
    COUNT(DISTINCT r.team_key) as teams_collected,
    COUNT(r.player_key) as roster_entries,
    COUNT(ps.player_key) as player_stats_entries,
    COUNT(i.player_key) as injury_entries
FROM snapshots s
LEFT JOIN rosters r ON s.id = r.snapshot_id
LEFT JOIN player_stats ps ON s.id = ps.snapshot_id
LEFT JOIN injuries i ON s.id = i.snapshot_id
GROUP BY s.id, s.snapshot_date, s.label
ORDER BY s.snapshot_date;

-- ======================
-- 2. 매치업 분석
-- ======================

-- 현재 주차 매치업 현황
SELECT
    m.matchup_id,
    m.team_key_home,
    m.team_key_away,
    m.score_home,
    m.score_away,
    CASE
        WHEN m.score_home > m.score_away THEN m.team_key_home
        WHEN m.score_away > m.score_home THEN m.team_key_away
        ELSE 'TIE'
    END as winning_team,
    ABS(m.score_home - m.score_away) as score_difference
FROM matchups m
JOIN snapshots s ON m.snapshot_id = s.id
WHERE s.label = 'week1_end'  -- 주차 종료 시점 데이터
ORDER BY score_difference DESC;

-- 팀별 승률 및 평균 점수
WITH team_records AS (
    SELECT
        team_key_home as team_key,
        CASE WHEN score_home > score_away THEN 1 ELSE 0 END as wins,
        CASE WHEN score_home < score_away THEN 1 ELSE 0 END as losses,
        score_home as points_scored,
        score_away as points_against
    FROM matchups m
    JOIN snapshots s ON m.snapshot_id = s.id
    WHERE s.label = 'week1_end'

    UNION ALL

    SELECT
        team_key_away as team_key,
        CASE WHEN score_away > score_home THEN 1 ELSE 0 END as wins,
        CASE WHEN score_away < score_home THEN 1 ELSE 0 END as losses,
        score_away as points_scored,
        score_home as points_against
    FROM matchups m
    JOIN snapshots s ON m.snapshot_id = s.id
    WHERE s.label = 'week1_end'
)
SELECT
    team_key,
    SUM(wins) as total_wins,
    SUM(losses) as total_losses,
    ROUND(CAST(SUM(wins) AS FLOAT) / (SUM(wins) + SUM(losses)), 3) as win_percentage,
    ROUND(AVG(points_scored), 2) as avg_points_scored,
    ROUND(AVG(points_against), 2) as avg_points_against,
    ROUND(AVG(points_scored) - AVG(points_against), 2) as point_differential
FROM team_records
GROUP BY team_key
ORDER BY win_percentage DESC, point_differential DESC;

-- ======================
-- 3. 선수 분석
-- ======================

-- 팀별 로스터 구성 (최신 스냅샷 기준)
SELECT
    r.team_key,
    COUNT(*) as total_players,
    SUM(r.starting_flag) as starting_players,
    COUNT(*) - SUM(r.starting_flag) as bench_players
FROM rosters r
JOIN snapshots s ON r.snapshot_id = s.id
WHERE s.id = (SELECT MAX(id) FROM snapshots)
GROUP BY r.team_key
ORDER BY r.team_key;

-- 부상 선수 현황 (최신 스냅샷 기준)
SELECT
    i.status_code,
    COUNT(*) as player_count,
    GROUP_CONCAT(i.player_key, ', ') as players
FROM injuries i
JOIN snapshots s ON i.snapshot_id = s.id
WHERE s.id = (SELECT MAX(id) FROM snapshots)
AND i.status_code != ''
GROUP BY i.status_code
ORDER BY player_count DESC;

-- ======================
-- 4. 거래 분석
-- ======================

-- 거래 유형별 통계
SELECT
    type,
    COUNT(*) as transaction_count,
    COUNT(DISTINCT team_from) as teams_involved_from,
    COUNT(DISTINCT team_to) as teams_involved_to
FROM transactions
GROUP BY type
ORDER BY transaction_count DESC;

-- 최근 거래 내역
SELECT
    datetime(timestamp, 'unixepoch', 'localtime') as transaction_time,
    type,
    team_from,
    team_to,
    players
FROM transactions
ORDER BY timestamp DESC
LIMIT 10;

-- 팀별 거래 활발도
SELECT
    COALESCE(team_from, team_to) as team_key,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN type IN ('add', 'drop') THEN 1 ELSE 0 END) as waiver_moves,
    SUM(CASE WHEN type = 'trade' THEN 1 ELSE 0 END) as trades
FROM transactions
WHERE team_from IS NOT NULL OR team_to IS NOT NULL
GROUP BY COALESCE(team_from, team_to)
ORDER BY total_transactions DESC;

-- ======================
-- 5. 선수 통계 분석 (예시)
-- ======================

-- 통계 카테고리별 집계 (최신 스냅샷 기준)
SELECT
    stat_id,
    COUNT(*) as player_count,
    AVG(CAST(value AS FLOAT)) as avg_value,
    MAX(CAST(value AS FLOAT)) as max_value,
    MIN(CAST(value AS FLOAT)) as min_value
FROM player_stats ps
JOIN snapshots s ON ps.snapshot_id = s.id
WHERE s.id = (SELECT MAX(id) FROM snapshots)
AND value != '' AND value IS NOT NULL
AND value GLOB '[0-9]*'  -- 숫자인 값만
GROUP BY stat_id
ORDER BY stat_id;

-- ======================
-- 6. 시계열 분석
-- ======================

-- 스냅샷별 데이터 변화 추이
SELECT
    s.snapshot_date,
    s.label,
    COUNT(DISTINCT r.team_key) as active_teams,
    COUNT(DISTINCT r.player_key) as total_players,
    COUNT(DISTINCT CASE WHEN i.status_code != '' THEN i.player_key END) as injured_players
FROM snapshots s
LEFT JOIN rosters r ON s.id = r.snapshot_id
LEFT JOIN injuries i ON s.id = i.snapshot_id
GROUP BY s.id, s.snapshot_date, s.label
ORDER BY s.snapshot_date;

-- ======================
-- 7. 성능 분석을 위한 뷰
-- ======================

-- 팀 성과 요약 뷰 생성
CREATE VIEW IF NOT EXISTS team_performance AS
WITH latest_snapshot AS (
    SELECT MAX(id) as snapshot_id FROM snapshots
),
team_stats AS (
    SELECT
        r.team_key,
        COUNT(*) as roster_size,
        SUM(r.starting_flag) as starting_players
    FROM rosters r
    JOIN latest_snapshot ls ON r.snapshot_id = ls.snapshot_id
    GROUP BY r.team_key
),
team_matchups AS (
    SELECT
        team_key_home as team_key,
        score_home as score,
        score_away as opponent_score
    FROM matchups m
    JOIN snapshots s ON m.snapshot_id = s.id
    WHERE s.label = 'week1_end'

    UNION ALL

    SELECT
        team_key_away as team_key,
        score_away as score,
        score_home as opponent_score
    FROM matchups m
    JOIN snapshots s ON m.snapshot_id = s.id
    WHERE s.label = 'week1_end'
)
SELECT
    ts.team_key,
    ts.roster_size,
    ts.starting_players,
    tm.score as latest_score,
    tm.opponent_score as latest_opponent_score,
    CASE
        WHEN tm.score > tm.opponent_score THEN 'W'
        WHEN tm.score < tm.opponent_score THEN 'L'
        ELSE 'T'
    END as latest_result
FROM team_stats ts
LEFT JOIN team_matchups tm ON ts.team_key = tm.team_key;