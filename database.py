
import sqlite3

class Database:
    def __init__(self, db_name="college_management.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        if self.conn: # Only create tables if connection was successful
            self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None      # Set conn to None after closing
            self.cursor = None    # Set cursor to None after closing
            print("Database connection closed.")
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Students table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                contact TEXT,
                email TEXT UNIQUE,
                address TEXT,
                course TEXT,
                enrollment_date TEXT,
                semester INTEGER
            )
            ''')
            
            # Administrators table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS administrators (
                admin_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                contact TEXT,
                email TEXT UNIQUE,
                position TEXT,
                department TEXT
            )
            ''')
            
            # Teachers table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT,
                contact TEXT,
                email TEXT UNIQUE,
                department TEXT,
                qualification TEXT,
                date_joined TEXT
            )
            ''')
            
            # Library table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT UNIQUE,
                publisher TEXT,
                year_published INTEGER,
                total_copies INTEGER,
                available_copies INTEGER
            )
            ''')
            
            # Book issues table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_issues (
                issue_id INTEGER PRIMARY KEY,
                book_id INTEGER,
                student_id INTEGER,
                issue_date TEXT,
                return_date TEXT,
                actual_return_date TEXT,
                fine_amount REAL,
                status TEXT,
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
            ''')
            
            # Events table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                date TEXT,
                time TEXT,
                venue TEXT,
                organizer TEXT,
                status TEXT
            )
            ''')
            
            # Feedback table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY,
                student_id INTEGER,
                teacher_id INTEGER,
                course TEXT,
                rating INTEGER,
                comments TEXT,
                date_submitted TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers (teacher_id)
            )
            ''')

            # Courses table
            self.cursor.execute('''
            create table if not exists courses (
                                course_id INTEGER PRIMARY KEY,
                                title text,
                                description text,
                                duration text
            )
            

            ''')
            
            self.conn.commit()
            print("All tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
    
    def execute_query(self, query, parameters=()):
        """Execute a query with optional parameters"""
        try:
            self.cursor.execute(query, parameters)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return False
    
    def fetch_all(self, query, parameters=()):
        """Execute a query and fetch all results"""
        try:
            self.cursor.execute(query, parameters)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fetch error: {e}")
            return []
    
    def fetch_one(self, query, parameters=()):
        """Execute a query and fetch one result"""
        try:
            self.cursor.execute(query, parameters)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Fetch error: {e}")
            return None