"""
Tests for database service functions.
"""
import unittest
import tempfile
import sqlite3
import os
from services.database import DatabaseService


class TestDatabaseService(unittest.TestCase):
    """Test cases for DatabaseService."""
    
    def setUp(self):
        """Create a temporary test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Create test tables
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                total REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        cursor.execute("""
            INSERT INTO users (name, email) VALUES 
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com')
        """)
        
        cursor.execute("""
            INSERT INTO orders (user_id, total) VALUES 
            (1, 99.99),
            (1, 149.99),
            (2, 79.99)
        """)
        
        conn.commit()
        conn.close()
    
    def tearDown(self):
        """Clean up test database."""
        try:
            os.unlink(self.test_db_path)
        except:
            pass
    
    def test_load_schema_from_sqlite(self):
        """Test schema generation from SQLite database."""
        schema = DatabaseService.load_schema_from_sqlite(self.test_db_path)
        
        self.assertIsInstance(schema, str)
        self.assertIn("users", schema)
        self.assertIn("orders", schema)
        self.assertIn("INTEGER PK", schema)
        self.assertIn("FKs[", schema)
    
    def test_execute_query_success(self):
        """Test successful query execution."""
        # Save original SQLITE_PATH and replace with test DB
        original_path = DatabaseService.__dict__.get('config')
        
        # Mock config for this test
        import config.settings
        original_sqlite_path = config.settings.config.SQLITE_PATH
        config.settings.config.SQLITE_PATH = self.test_db_path
        
        try:
            result = DatabaseService.execute_query("SELECT * FROM users")
            
            self.assertIn("data", result)
            self.assertNotIn("error", result)
            self.assertEqual(len(result["data"]), 2)
            self.assertEqual(result["data"][0]["name"], "John Doe")
            
        finally:
            # Restore original config
            config.settings.config.SQLITE_PATH = original_sqlite_path
    
    def test_execute_query_error(self):
        """Test query execution with SQL error."""
        import config.settings
        original_sqlite_path = config.settings.config.SQLITE_PATH
        config.settings.config.SQLITE_PATH = self.test_db_path
        
        try:
            result = DatabaseService.execute_query("SELECT * FROM nonexistent_table")
            
            self.assertIn("error", result)
            self.assertNotIn("data", result)
            
        finally:
            config.settings.config.SQLITE_PATH = original_sqlite_path
    
    def test_load_schema_nonexistent_db(self):
        """Test schema loading from nonexistent database."""
        schema = DatabaseService.load_schema_from_sqlite("/nonexistent/database.db")
        
        self.assertEqual(schema, "Database file not found.")


if __name__ == '__main__':
    unittest.main()