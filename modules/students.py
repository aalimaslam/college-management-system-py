from database import Database
import datetime

class Student:
    def __init__(self, db):
        """Initialize Student class with database connection"""
        self.db = db
    
    def add_student(self, name, age, gender, contact, email, address, course, semester):
        """Add a new student to the database"""
        enrollment_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if email already exists
        exists = self.db.fetch_one("SELECT email FROM students WHERE email = ?", (email,))
        if exists:
            print(f"Error: Student with email {email} already exists.")
            return False
        
        query = """
        INSERT INTO students (name, age, gender, contact, email, address, course, enrollment_date, semester)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (name, age, gender, contact, email, address, course, enrollment_date, semester)
        
        if self.db.execute_query(query, params):
            print(f"Student {name} added successfully.")
            return True
        return False
    
    def update_student(self, student_id, **kwargs):
        """Update student information"""
        valid_fields = ['name', 'age', 'gender', 'contact', 'email', 'address', 'course', 'semester']
        
        # Filter out invalid fields
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            print("No valid fields to update.")
            return False

        # Check if student_id exists before trying to update
        check_exists = self.db.fetch_one("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if not check_exists:
            print(f"Error: Student with ID {student_id} does not exist. Cannot update.")
            return False
        
        # Construct update query
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE students SET {set_clause} WHERE student_id = ?"
        
        # Parameters for the query
        params = list(updates.values()) + [student_id]
        
        if self.db.execute_query(query, tuple(params)):
            print(f"Student ID {student_id} updated successfully.")
            return True
        return False
    
    def delete_student(self, student_id):
        """Delete a student from the database"""
        # Check if student exists
        exists = self.db.fetch_one("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if not exists:
            print(f"Error: Student with ID {student_id} does not exist.")
            return False
        
        query = "DELETE FROM students WHERE student_id = ?"
        if self.db.execute_query(query, (student_id,)):
            print(f"Student ID {student_id} deleted successfully.")
            return True
        return False
    
    def get_student(self, student_id):
        """Get student details by ID"""
        query = "SELECT * FROM students WHERE student_id = ?"
        student = self.db.fetch_one(query, (student_id,))
        
        if not student:
            print(f"No student found with ID {student_id}.")
            return None
        
        # Convert to dictionary for easier access
        columns = ["student_id", "name", "age", "gender", "contact", "email", 
                   "address", "course", "enrollment_date", "semester"]
        return dict(zip(columns, student))
    
    def get_all_students(self):
        """Get all students"""
        query = "SELECT * FROM students ORDER BY name"
        students = self.db.fetch_all(query)
        
        if not students:
            print("No students found.")
            return []
        
        # Convert to list of dictionaries
        columns = ["student_id", "name", "age", "gender", "contact", "email", 
                   "address", "course", "enrollment_date", "semester"]
        return [dict(zip(columns, student)) for student in students]
    
    def search_students(self, search_term):
        """Search for students by name, email, or course"""
        query = """
        SELECT * FROM students 
        WHERE LOWER(name) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?) OR LOWER(course) LIKE LOWER(?)
        ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern)
        students = self.db.fetch_all(query, params)
        
        if not students:
            print(f"No students found matching '{search_term}'.")
            return []
        
        # Convert to list of dictionaries
        columns = ["student_id", "name", "age", "gender", "contact", "email", 
                   "address", "course", "enrollment_date", "semester"]
        return [dict(zip(columns, student)) for student in students]
    
    def display_student(self, student_data):
        """Display student information in a formatted way"""
        if not student_data:
            return
        
        print("\n" + "="*50)
        print(f"STUDENT ID: {student_data['student_id']}")
        print(f"Name: {student_data['name']}")
        print(f"Age: {student_data['age']}")
        print(f"Gender: {student_data['gender']}")
        print(f"Contact: {student_data['contact']}")
        print(f"Email: {student_data['email']}")
        print(f"Address: {student_data['address']}")
        print(f"Course: {student_data['course']}")
        print(f"Enrollment Date: {student_data['enrollment_date']}")
        print(f"Semester: {student_data['semester']}")
        print("="*50 + "\n")