"""Database operations module."""

import sqlite3
from typing import Optional, List
from pathlib import Path
from models import TranslationRecord, DatabaseConfig
from logger import get_logger

logger = get_logger(__name__)


class TranslationDatabase:
    """Handle all database operations for storing translation transcripts."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database with configuration.
        
        Args:
            config: DatabaseConfig instance. If None, uses defaults.
        """
        self.config = config or DatabaseConfig()
        self.db_path = self.config.db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.config.timeout)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source_language TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    duration_seconds REAL,
                    confidence REAL,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audio_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    translation_id INTEGER NOT NULL,
                    audio_path TEXT,
                    sample_rate INTEGER,
                    duration_seconds REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (translation_id) REFERENCES translations(id)
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    def insert_translation(self, record: TranslationRecord) -> int:
        """
        Insert a translation record into the database.
        
        Args:
            record: TranslationRecord instance
            
        Returns:
            translation_id
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.config.timeout)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO translations 
                (source_language, target_language, source_text, translated_text, duration_seconds, confidence, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.source_language,
                record.target_language,
                record.source_text,
                record.translated_text,
                record.duration_seconds,
                record.confidence,
                record.status
            ))
            
            translation_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Translation {translation_id} inserted successfully")
            return translation_id
        except Exception as e:
            logger.error(f"Error inserting translation: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_translations(self) -> List[TranslationRecord]:
        """Retrieve all translations from database."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.config.timeout)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM translations ORDER BY timestamp DESC
            ''')
            
            results = []
            for row in cursor.fetchall():
                record = TranslationRecord(
                    id=row['id'],
                    timestamp=row['timestamp'],
                    source_language=row['source_language'],
                    target_language=row['target_language'],
                    source_text=row['source_text'],
                    translated_text=row['translated_text'],
                    duration_seconds=row['duration_seconds'],
                    confidence=row['confidence'],
                    status=row['status']
                )
                results.append(record)
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving translations: {e}")
            raise
        finally:
            conn.close()
    
    def get_translation_by_id(self, translation_id: int) -> Optional[TranslationRecord]:
        """Retrieve a specific translation by ID."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.config.timeout)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM translations WHERE id = ?
            ''', (translation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            record = TranslationRecord(
                id=row['id'],
                timestamp=row['timestamp'],
                source_language=row['source_language'],
                target_language=row['target_language'],
                source_text=row['source_text'],
                translated_text=row['translated_text'],
                duration_seconds=row['duration_seconds'],
                confidence=row['confidence'],
                status=row['status']
            )
            
            return record
        except Exception as e:
            logger.error(f"Error retrieving translation {translation_id}: {e}")
            raise
        finally:
            conn.close()
    
    def get_translations_by_language_pair(
        self,
        source_lang: str,
        target_lang: str
    ) -> List[TranslationRecord]:
        """Retrieve translations for a specific language pair."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.config.timeout)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM translations 
                WHERE source_language = ? AND target_language = ?
                ORDER BY timestamp DESC
            ''', (source_lang, target_lang))
            
            results = []
            for row in cursor.fetchall():
                record = TranslationRecord(
                    id=row['id'],
                    timestamp=row['timestamp'],
                    source_language=row['source_language'],
                    target_language=row['target_language'],
                    source_text=row['source_text'],
                    translated_text=row['translated_text'],
                    duration_seconds=row['duration_seconds'],
                    confidence=row['confidence'],
                    status=row['status']
                )
                results.append(record)
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving translations: {e}")
            raise
        finally:
            conn.close()
