"""
Tests for SQL guardrails and security functions.
"""
import unittest
from core.guardrails import sanitize_sql, validate_table_name


class TestGuardrails(unittest.TestCase):
    """Test cases for SQL guardrails."""
    
    def test_valid_select_queries(self):
        """Test that valid SELECT queries pass validation."""
        valid_queries = [
            "SELECT * FROM users",
            "SELECT name, email FROM customers WHERE id = 1",
            "SELECT COUNT(*) FROM orders",
            "WITH top_customers AS (SELECT * FROM customers ORDER BY total_spent DESC) SELECT * FROM top_customers",
            "select name from products where price > 100",  # Case insensitive
        ]
        
        for query in valid_queries:
            with self.subTest(query=query):
                is_safe, sanitized, reason = sanitize_sql(query)
                self.assertTrue(is_safe, f"Query should be safe: {query}. Reason: {reason}")
                self.assertIn("LIMIT", sanitized.upper())
    
    def test_forbidden_queries(self):
        """Test that dangerous queries are rejected."""
        forbidden_queries = [
            "DROP TABLE users",
            "INSERT INTO users (name) VALUES ('test')",
            "UPDATE users SET name = 'hacker'",
            "DELETE FROM users",
            "CREATE TABLE test (id INT)",
            "ALTER TABLE users ADD COLUMN test VARCHAR(100)",
            "TRUNCATE TABLE users",
            "PRAGMA table_info(users)",
            "SELECT * FROM users; DROP TABLE users",
            "SELECT * FROM users -- comment",
            "SELECT * FROM users /* comment */",
        ]
        
        for query in forbidden_queries:
            with self.subTest(query=query):
                is_safe, _, reason = sanitize_sql(query)
                self.assertFalse(is_safe, f"Query should be rejected: {query}")
                # Accept either 'forbidden' or 'non_select_or_unsafe' as rejection reasons
                self.assertTrue(
                    "forbidden" in reason.lower() or "non_select_or_unsafe" in reason.lower(),
                    f"Query should be rejected for security reasons: {query}. Reason: {reason}"
                )
    
    def test_empty_queries(self):
        """Test handling of empty or invalid queries."""
        invalid_queries = [
            "",
            None,
            "   ",
            "```sql\n\n```",
            123,  # Non-string input
        ]
        
        for query in invalid_queries:
            with self.subTest(query=query):
                is_safe, _, reason = sanitize_sql(query)
                self.assertFalse(is_safe, f"Invalid query should be rejected: {query}")
                self.assertIn("empty", reason.lower())
    
    def test_limit_addition(self):
        """Test that LIMIT is added when missing."""
        query = "SELECT * FROM users"
        is_safe, sanitized, _ = sanitize_sql(query, default_limit=100)
        
        self.assertTrue(is_safe)
        self.assertIn("LIMIT 100", sanitized)
    
    def test_existing_limit_preserved(self):
        """Test that existing LIMIT is preserved."""
        query = "SELECT * FROM users LIMIT 50"
        is_safe, sanitized, _ = sanitize_sql(query)
        
        self.assertTrue(is_safe)
        self.assertIn("LIMIT 50", sanitized)
    
    def test_excessive_limit_rejected(self):
        """Test that excessive LIMIT values are rejected."""
        query = "SELECT * FROM users LIMIT 50000"
        is_safe, _, reason = sanitize_sql(query)
        
        self.assertFalse(is_safe)
        self.assertIn("excessive_limit", reason)
    
    def test_table_name_validation(self):
        """Test table name validation."""
        valid_names = [
            "users",
            "user_accounts",
            "Products",
            "table123",
            "T1",
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(validate_table_name(name), f"Valid table name rejected: {name}")
        
        invalid_names = [
            "",
            None,
            "123table",  # Starts with number
            "user-accounts",  # Contains hyphen
            "sqlite_master",  # System table
            "pg_tables",  # PostgreSQL system table
            "information_schema",  # System schema
            "user accounts",  # Contains space
            "user.accounts",  # Contains dot
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_table_name(name), f"Invalid table name accepted: {name}")


if __name__ == '__main__':
    unittest.main()