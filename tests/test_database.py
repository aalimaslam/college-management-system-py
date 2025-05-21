import unittest
import sqlite3
import sys
import os

# Add the root directory to the Python path to allow importing 'database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.db_name = ":memory:"
        self.db = Database(self.db_name)

    def tearDown(self):
        """Tear down after each test method."""
        if self.db and self.db.conn:
            self.db.close()

    def test_successful_connection(self):
        """Test successful connection to an in-memory database."""
        self.assertIsNotNone(self.db.conn, "Database connection should not be None.")
        self.assertIsInstance(self.db.conn, sqlite3.Connection, "Should be a sqlite3.Connection instance.")

    def test_successful_closing(self):
        """Test successful closing of the database connection."""
        self.db.close()
        self.assertIsNone(self.db.conn, "Database connection should be None after closing.")

    def test_create_tables(self):
        """Test the create_tables method."""
        self.db.create_tables()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'students', 'administrators', 'teachers', 'books', 
            'book_issues', 'events', 'feedback', 'courses'
        ]
        
        for table_name in expected_tables:
            self.assertIn(table_name, tables, f"Table '{table_name}' should be created.")

    def test_execute_query_insert(self):
        """Test execute_query for INSERT operations."""
        self.db.create_tables() # Ensure tables exist
        # Corrected columns for students table
        insert_query = "INSERT INTO students (name, email, age, course) VALUES (?, ?, ?, ?)"
        params = ('Test Student', 'test@example.com', 22, 'Computer Science')
        result = self.db.execute_query(insert_query, params)
        self.assertTrue(result, "INSERT operation should return True on success.")
        
        # Verify the data was inserted
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM students WHERE email='test@example.com'")
        self.assertIsNotNone(cursor.fetchone(), "Data should be inserted into students table.")

    def test_execute_query_update(self):
        """Test execute_query for UPDATE operations."""
        self.db.create_tables()
        # First, insert a row to update
        # Corrected columns for students table
        insert_query = "INSERT INTO students (name, email, age, course) VALUES (?, ?, ?, ?)"
        params_insert = ('Update Me', 'update@example.com', 25, 'Information Technology')
        self.db.execute_query(insert_query, params_insert)
        
        update_query = "UPDATE students SET name = ?, age = ? WHERE email = ?"
        params_update = ('Updated Name', 26, 'update@example.com')
        result = self.db.execute_query(update_query, params_update)
        self.assertTrue(result, "UPDATE operation should return True on success.")
        
        # Verify the data was updated
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name, age FROM students WHERE email='update@example.com'")
        updated_data = cursor.fetchone()
        self.assertIsNotNone(updated_data, "Updated data should not be None.")
        self.assertEqual(updated_data[0], 'Updated Name', "Student name should be updated.")
        self.assertEqual(updated_data[1], 26, "Student age should be updated.")


    def test_fetch_all(self):
        """Test fetch_all to retrieve multiple rows."""
        self.db.create_tables()
        # Insert multiple records - Corrected columns
        students_data = [
            ('Alice', 'alice@example.com', 21, 'CSE'),
            ('Bob', 'bob@example.com', 22, 'ECE')
        ]
        for data in students_data:
            self.db.execute_query("INSERT INTO students (name, email, age, course) VALUES (?, ?, ?, ?)", data)
            
        rows = self.db.fetch_all("SELECT student_id, name, email, age, course FROM students ORDER BY name ASC")
        self.assertEqual(len(rows), 2, "fetch_all should retrieve all inserted students.")
        # student_id is at index 0, name is at index 1
        self.assertEqual(rows[0][1], 'Alice', "First student's name should be Alice.") 
        self.assertEqual(rows[1][1], 'Bob', "Second student's name should be Bob.")

    def test_fetch_one(self):
        """Test fetch_one to retrieve a single row."""
        self.db.create_tables()
        # Corrected columns
        insert_query = "INSERT INTO students (name, email, age, course) VALUES (?, ?, ?, ?)"
        params = ('Single Student', 'single@example.com', 24, 'Mechanical')
        self.db.execute_query(insert_query, params)
        
        row = self.db.fetch_one("SELECT student_id, name, email, age, course FROM students WHERE email='single@example.com'")
        self.assertIsNotNone(row, "fetch_one should retrieve the student.")
        self.assertEqual(row[1], 'Single Student', "Student's name should be 'Single Student'.") # name is at index 1

    def test_fetch_one_no_row(self):
        """Test fetch_one when no row is found."""
        self.db.create_tables() # Ensure tables are created
        row = self.db.fetch_one("SELECT * FROM students WHERE email='nonexistent@example.com'")
        self.assertIsNone(row, "fetch_one should return None when no row is found.")

    def test_connection_error(self):
        """Test connection to an invalid database path."""
        # Attempt to connect to a read-only path that typically cannot be written to
        invalid_db = Database("/invalid_path/test.db")
        self.assertIsNone(invalid_db.conn, "Connection should be None for an invalid path.")

    def test_execute_query_error(self):
        """Test execute_query with an invalid SQL query."""
        self.db.create_tables() # Ensure tables exist for other operations, though this one will fail
        invalid_query = "INSERT INTO non_existent_table (column) VALUES (?)"
        params = ('some_value',)
        # execute_query is expected to return False on error, not raise an exception
        result = self.db.execute_query(invalid_query, params)
        self.assertFalse(result, "execute_query should return False for an invalid query.")


if __name__ == '__main__':
    unittest.main()
