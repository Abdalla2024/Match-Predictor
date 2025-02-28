import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        """Initialize database connection"""
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        # Teams table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                league TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Players table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team_id INTEGER,
                position TEXT,
                nationality TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (id)
            )
        ''')
        
        # Matches table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                home_team_id INTEGER,
                away_team_id INTEGER,
                home_score INTEGER,
                away_score INTEGER,
                date TIMESTAMP,
                competition TEXT,
                season TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (home_team_id) REFERENCES teams (id),
                FOREIGN KEY (away_team_id) REFERENCES teams (id)
            )
        ''')
        
        # Match Events table (goals, cards, etc.)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player_id INTEGER,
                event_type TEXT,
                minute INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Team Statistics table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                match_id INTEGER,
                possession FLOAT,
                shots INTEGER,
                shots_on_target INTEGER,
                corners INTEGER,
                fouls INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams (id),
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        ''')
        
        # Player Statistics table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                match_id INTEGER,
                minutes_played INTEGER,
                goals INTEGER,
                assists INTEGER,
                shots INTEGER,
                shots_on_target INTEGER,
                passes INTEGER,
                pass_accuracy FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (match_id) REFERENCES matches (id)
            )
        ''')
        
        self.conn.commit()
    
    def insert_team(self, name, league, country):
        """Insert a new team"""
        try:
            self.cursor.execute('''
                INSERT INTO teams (name, league, country)
                VALUES (?, ?, ?)
            ''', (name, league, country))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # If team already exists, return its ID
            self.cursor.execute('SELECT id FROM teams WHERE name = ?', (name,))
            return self.cursor.fetchone()[0]
    
    def insert_player(self, name, team_id, position, nationality):
        """Insert a new player"""
        self.cursor.execute('''
            INSERT INTO players (name, team_id, position, nationality)
            VALUES (?, ?, ?, ?)
        ''', (name, team_id, position, nationality))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def insert_match(self, home_team_id, away_team_id, home_score, away_score, 
                    date, competition, season):
        """Insert a new match"""
        self.cursor.execute('''
            INSERT INTO matches (home_team_id, away_team_id, home_score, 
                               away_score, date, competition, season)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (home_team_id, away_team_id, home_score, away_score, 
              date, competition, season))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def insert_match_event(self, match_id, player_id, event_type, minute):
        """Insert a match event"""
        self.cursor.execute('''
            INSERT INTO match_events (match_id, player_id, event_type, minute)
            VALUES (?, ?, ?, ?)
        ''', (match_id, player_id, event_type, minute))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def insert_team_stats(self, team_id, match_id, possession, shots, 
                         shots_on_target, corners, fouls):
        """Insert team statistics for a match"""
        self.cursor.execute('''
            INSERT INTO team_stats (team_id, match_id, possession, shots,
                                  shots_on_target, corners, fouls)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (team_id, match_id, possession, shots, shots_on_target, 
              corners, fouls))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def insert_player_stats(self, player_id, match_id, minutes_played, goals,
                           assists, shots, shots_on_target, passes, pass_accuracy):
        """Insert player statistics for a match"""
        self.cursor.execute('''
            INSERT INTO player_stats (player_id, match_id, minutes_played, goals,
                                    assists, shots, shots_on_target, passes,
                                    pass_accuracy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, match_id, minutes_played, goals, assists, shots,
              shots_on_target, passes, pass_accuracy))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_team_id(self, team_name):
        """Get team ID by name"""
        self.cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_player_id(self, player_name, team_id):
        """Get player ID by name and team"""
        self.cursor.execute('''
            SELECT id FROM players 
            WHERE name = ? AND team_id = ?
        ''', (player_name, team_id))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        """Close database connection"""
        self.conn.close() 