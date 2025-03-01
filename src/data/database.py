import sqlite3
import os
from datetime import datetime
import logging
from pathlib import Path

class Database:
    def __init__(self, db_path='data.db'):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                league TEXT NOT NULL,
                country TEXT,
                UNIQUE(name, league)
            );
            
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                home_team_id INTEGER,
                away_team_id INTEGER,
                home_score INTEGER,
                away_score INTEGER,
                date TEXT,
                competition TEXT,
                season TEXT,
                api_fixture_id INTEGER,
                FOREIGN KEY (home_team_id) REFERENCES teams (id),
                FOREIGN KEY (away_team_id) REFERENCES teams (id)
            );
            
            CREATE TABLE IF NOT EXISTS team_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                match_id INTEGER,
                possession REAL,
                shots INTEGER,
                shots_on_target INTEGER,
                corners INTEGER,
                fouls INTEGER,
                FOREIGN KEY (team_id) REFERENCES teams (id),
                FOREIGN KEY (match_id) REFERENCES matches (id),
                UNIQUE(team_id, match_id)
            );
        ''')
        self.conn.commit()
    
    def insert_team(self, name, league, country=None):
        """Insert a team and return its ID."""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO teams (name, league, country)
                VALUES (?, ?, ?)
            ''', (name, league, country))
            self.conn.commit()
            
            # Get the team ID (whether it was just inserted or already existed)
            self.cursor.execute('SELECT id FROM teams WHERE name = ? AND league = ?', (name, league))
            return self.cursor.fetchone()[0]
            
        except sqlite3.Error as e:
            logging.error(f"Database error inserting team {name}: {str(e)}")
            raise
    
    def insert_match(self, home_team_id, away_team_id, home_score, away_score, date, competition, season, api_fixture_id):
        """Insert a match and return its ID."""
        try:
            self.cursor.execute('''
                INSERT INTO matches (
                    home_team_id, away_team_id, home_score, away_score,
                    date, competition, season, api_fixture_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                home_team_id, away_team_id, home_score, away_score,
                date, competition, season, api_fixture_id
            ))
            self.conn.commit()
            return self.cursor.lastrowid
            
        except sqlite3.Error as e:
            logging.error(f"Database error inserting match: {str(e)}")
            raise
    
    def insert_team_stats(self, team_id, match_id, possession, shots, shots_on_target, corners, fouls):
        """Insert team statistics for a match."""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO team_stats (
                    team_id, match_id, possession, shots,
                    shots_on_target, corners, fouls
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                team_id, match_id, possession, shots,
                shots_on_target, corners, fouls
            ))
            self.conn.commit()
            
        except sqlite3.Error as e:
            logging.error(f"Database error inserting team stats: {str(e)}")
            raise
    
    def get_team_id(self, name):
        """Get team ID by name."""
        try:
            self.cursor.execute('SELECT id FROM teams WHERE name = ?', (name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
            
        except sqlite3.Error as e:
            logging.error(f"Database error getting team ID for {name}: {str(e)}")
            raise
    
    def get_matches_without_statistics(self, competition, season):
        """Get matches that don't have statistics recorded."""
        try:
            self.cursor.execute('''
                SELECT m.id, m.api_fixture_id
                FROM matches m
                LEFT JOIN team_stats ts ON m.id = ts.match_id
                WHERE m.competition = ? 
                AND m.season = ?
                AND ts.id IS NULL
            ''', (competition, season))
            return self.cursor.fetchall()
            
        except sqlite3.Error as e:
            logging.error(f"Database error getting matches without statistics: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close() 