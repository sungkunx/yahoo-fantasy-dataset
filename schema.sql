CREATE TABLE IF NOT EXISTS weeks (
  game_key TEXT,
  week INTEGER,
  start_date TEXT,
  end_date TEXT,
  PRIMARY KEY (game_key, week)
);

CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  league_key TEXT,
  snapshot_date TEXT,
  week INTEGER,
  label TEXT
);

CREATE TABLE IF NOT EXISTS matchups (
  snapshot_id INTEGER,
  matchup_id TEXT,
  team_key_home TEXT,
  team_key_away TEXT,
  score_home REAL,
  score_away REAL
);

CREATE TABLE IF NOT EXISTS rosters (
  snapshot_id INTEGER,
  team_key TEXT,
  player_key TEXT,
  position TEXT,
  starting_flag INTEGER
);

CREATE TABLE IF NOT EXISTS player_stats (
  snapshot_id INTEGER,
  player_key TEXT,
  stat_id TEXT,
  value TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
  tx_id TEXT PRIMARY KEY,
  league_key TEXT,
  timestamp INTEGER,
  type TEXT,
  team_from TEXT,
  team_to TEXT,
  players TEXT
);

CREATE TABLE IF NOT EXISTS injuries (
  snapshot_id INTEGER,
  player_key TEXT,
  status_code TEXT,
  status_note TEXT
);
