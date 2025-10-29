# Yahoo Fantasy Basketball Dataset

🏀 A comprehensive data collection and analysis system for Yahoo Fantasy Basketball leagues.

## 📊 Overview

This project automatically collects and analyzes Yahoo Fantasy Basketball data including:
- **Matchup scores and results**
- **Team rosters and lineup decisions**
- **Player statistics and performance**
- **Injury reports and status updates**
- **Trade and waiver wire transactions**

## 🚀 Features

- **Time-series snapshots**: Multiple collection points per week (Day 1, Day 4, Week End)
- **Korean timezone optimization**: Scheduled collection after NBA games finish
- **Automated scheduling**: Cron-based regular data collection
- **Comprehensive analysis**: SQL queries and Python analytics tools
- **Real-time data**: Direct API integration with Yahoo Fantasy Sports

## 📁 Project Structure

```
yahoo-fantasy-dataset/
├── snapshot.py              # Main data collection script
├── transactions.py          # Trade/waiver data collection
├── get_week_dates.py        # Weekly schedule management
├── auth_setup.py           # OAuth authentication setup
├── run_schedule.py         # Automated scheduler
├── analyze_data.py         # Data analysis tool
├── analysis_queries.sql    # SQL analysis queries
├── schema.sql             # Database schema
├── crontab_setup.txt      # Cron configuration
├── fantasy.db            # SQLite database (gitignored)
├── oauth2.json           # OAuth tokens (gitignored)
├── .env                  # Environment variables (gitignored)
└── logs/                # Log files (gitignored)
```

## 🛠️ Setup

### 1. Prerequisites

```bash
# Python 3.8+
pip install -r requirements.txt
```

### 2. Yahoo API Setup

1. Create a Yahoo Developer App at https://developer.yahoo.com/apps/
2. Get your Client ID and Client Secret
3. Set redirect URI to `http://localhost:8080/callback`

### 3. Environment Configuration

Create `.env` file:
```env
YAHOO_CLIENT_ID=your_client_id_here
YAHOO_CLIENT_SECRET=your_client_secret_here
REDIRECT_URI=http://localhost:8080/callback
LEAGUE_KEY=nba.l.YOUR_LEAGUE_ID
GAME_KEY=nba
WEEK=1
```

### 4. Database Setup

```bash
# Initialize database
sqlite3 fantasy.db < schema.sql

# Set up authentication
python auth_setup.py

# Test data collection
python get_week_dates.py
python snapshot.py
```

## 🔄 Data Collection

### Manual Collection

```bash
# Collect weekly schedule
python get_week_dates.py

# Collect snapshots (matchups, rosters, stats, injuries)
python snapshot.py

# Collect transaction data
python transactions.py
```

### Automated Collection

Set up cron jobs for automatic data collection:

```bash
# Create log directory
mkdir -p logs

# Install cron schedule
crontab -e
# Copy contents from crontab_setup.txt
```

**Schedule:**
- **Daily 6PM & 9PM KST**: Main data collection (weekdays only)
- **Sunday midnight**: Weekly schedule update

## 📈 Data Analysis

### Quick Analysis

```bash
# Run comprehensive analysis
python analyze_data.py
```

### Custom Queries

```bash
# Access database directly
sqlite3 fantasy.db

# Run predefined analysis queries
sqlite3 fantasy.db < analysis_queries.sql
```

### Sample Analyses

- **Team Performance**: Win rates, scoring averages, point differentials
- **Player Trends**: Statistics tracking, injury monitoring
- **Trade Activity**: Transaction patterns, team activity levels
- **Lineup Decisions**: Starting lineup changes over time

## 📋 Database Schema

### Core Tables

- **`snapshots`**: Collection timestamps and metadata
- **`matchups`**: Head-to-head game results
- **`rosters`**: Team lineups and player positions
- **`player_stats`**: Individual player performance data
- **`injuries`**: Player injury status and notes
- **`transactions`**: Trades, adds, drops, and waiver claims
- **`weeks`**: Fantasy season schedule information

## 🌏 Korean Timezone Features

The system is optimized for Korean users:
- **KST timezone handling**: All timestamps in Korean Standard Time
- **NBA game schedule awareness**: Collection after games typically finish (6PM-9PM KST)
- **Weekday scheduling**: Automatic collection Monday-Friday

## 🔐 Security Notes

- OAuth tokens are stored locally and not committed to git
- Environment variables contain sensitive API credentials
- Database contains personal league information

## 📊 Sample Data Output

Current dataset includes:
- 18+ snapshots across multiple timepoints
- 80+ matchup records
- 900+ roster entries
- 100+ player statistics
- 30+ transaction records

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal fantasy league analysis only. Please respect Yahoo's Terms of Service and API rate limits.

## 🙋‍♂️ Support

For questions or issues:
1. Check the [Issues](https://github.com/sungkunx/yahoo-fantasy-dataset/issues) page
2. Create a new issue with detailed information
3. Include relevant log files and error messages

---

**Made with ❤️ for fantasy basketball enthusiasts**