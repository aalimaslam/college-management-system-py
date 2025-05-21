from database import Database
import datetime

class Feedback:
    def __init__(self, db):
        """Initialize Feedback class with database connection"""
        self.db = db
    
    def submit_feedback(self, student_id, teacher_id, course, rating, comments):
        """Submit feedback from a student for a teacher"""
        # Validate student exists
        student_exists = self.db.fetch_one("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if not student_exists:
            print(f"Error: Student with ID {student_id} does not exist.")
            return False
        
        # Validate teacher exists
        teacher_exists = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
        if not teacher_exists:
            print(f"Error: Teacher with ID {teacher_id} does not exist.")
            return False
        
        # Validate rating (1-5)
        if not (1 <= rating <= 5):
            print("Error: Rating must be between 1 and 5.")
            return False
        
        # Check if feedback already exists for this combination
        existing = self.db.fetch_one("""
            SELECT feedback_id FROM feedback 
            WHERE student_id = ? AND teacher_id = ? AND course = ?
        """, (student_id, teacher_id, course))
        
        if existing:
            print(f"Feedback already exists for this student-teacher-course combination.")
            print("Please use update_feedback method to modify existing feedback.")
            return False
        
        date_submitted = datetime.datetime.now().strftime("%Y-%m-%d")
        
        query = """
        INSERT INTO feedback (student_id, teacher_id, course, rating, comments, date_submitted)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (student_id, teacher_id, course, rating, comments, date_submitted)
        
        if self.db.execute_query(query, params):
            print(f"Feedback submitted successfully.")
            return True
        return False
    
    def update_feedback(self, feedback_id, rating=None, comments=None):
        """Update existing feedback"""
        # Check if feedback exists
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            return False
        
        updates = {}
        
        if rating is not None:
            # Validate rating (1-5)
            if not (1 <= rating <= 5):
                print("Error: Rating must be between 1 and 5.")
                return False
            updates['rating'] = rating
            
        if comments is not None:
            updates['comments'] = comments
            
        if not updates:
            print("No valid fields to update.")
            return False
        
        # Update date_submitted to current date
        updates['date_submitted'] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Construct update query
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE feedback SET {set_clause} WHERE feedback_id = ?"
        
        # Parameters for the query
        params = list(updates.values()) + [feedback_id]
        
        if self.db.execute_query(query, tuple(params)):
            print(f"Feedback ID {feedback_id} updated successfully.")
            return True
        return False
    
    def delete_feedback(self, feedback_id):
        """Delete feedback"""
        # Check if feedback exists
        exists = self.db.fetch_one("SELECT feedback_id FROM feedback WHERE feedback_id = ?", (feedback_id,))
        if not exists:
            print(f"Error: Feedback with ID {feedback_id} does not exist.")
            return False
        
        query = "DELETE FROM feedback WHERE feedback_id = ?"
        if self.db.execute_query(query, (feedback_id,)):
            print(f"Feedback ID {feedback_id} deleted successfully.")
            return True
        return False
    
    def get_feedback(self, feedback_id):
        """Get feedback details by ID"""
        query = "SELECT * FROM feedback WHERE feedback_id = ?"
        feedback = self.db.fetch_one(query, (feedback_id,))
        
        if not feedback:
            print(f"No feedback found with ID {feedback_id}.")
            return None
        
        # Convert to dictionary for easier access
        columns = ["feedback_id", "student_id", "teacher_id", "course", 
                  "rating", "comments", "date_submitted"]
        return dict(zip(columns, feedback))
    
    def get_teacher_feedback(self, teacher_id):
        """Get all feedback for a specific teacher"""
        # Validate teacher exists
        teacher_exists = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
        if not teacher_exists:
            print(f"Error: Teacher with ID {teacher_id} does not exist.")
            return []
        
        query = """
        SELECT f.feedback_id, s.name as student_name, f.course, f.rating, 
               f.comments, f.date_submitted
        FROM feedback f
        JOIN students s ON f.student_id = s.student_id
        WHERE f.teacher_id = ?
        ORDER BY f.date_submitted DESC
        """
        feedback_list = self.db.fetch_all(query, (teacher_id,))
        
        if not feedback_list:
            print(f"No feedback found for teacher ID {teacher_id}.")
            return []
            
        return feedback_list
    
    def get_student_feedback(self, student_id):
        """Get all feedback submitted by a specific student"""
        # Validate student exists
        student_exists = self.db.fetch_one("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if not student_exists:
            print(f"Error: Student with ID {student_id} does not exist.")
            return []
        
        query = """
        SELECT f.feedback_id, t.name as teacher_name, f.course, f.rating, 
               f.comments, f.date_submitted
        FROM feedback f
        JOIN teachers t ON f.teacher_id = t.teacher_id
        WHERE f.student_id = ?
        ORDER BY f.date_submitted DESC
        """
        feedback_list = self.db.fetch_all(query, (student_id,))
        
        if not feedback_list:
            print(f"No feedback found for student ID {student_id}.")
            return []
            
        return feedback_list
    
    def get_course_feedback(self, course):
        """Get all feedback for a specific course"""
        query = """
        SELECT f.feedback_id, s.name as student_name, t.name as teacher_name, 
               f.rating, f.comments, f.date_submitted
        FROM feedback f
        JOIN students s ON f.student_id = s.student_id
        JOIN teachers t ON f.teacher_id = t.teacher_id
        WHERE f.course = ?
        ORDER BY f.date_submitted DESC
        """
        feedback_list = self.db.fetch_all(query, (course,))
        
        if not feedback_list:
            print(f"No feedback found for course '{course}'.")
            return []
            
        return feedback_list
    
    def calculate_teacher_rating(self, teacher_id):
        """Calculate average rating for a teacher"""
        query = "SELECT AVG(rating) FROM feedback WHERE teacher_id = ?"
        result = self.db.fetch_one(query, (teacher_id,))
        
        if not result or result[0] is None:
            print(f"No ratings found for teacher ID {teacher_id}.")
            return 0
            
        # Format to 2 decimal places
        avg_rating = round(result[0], 2)
        return avg_rating
    
    def display_feedback(self, feedback_data):
        """Display feedback information in a formatted way"""
        if not feedback_data:
            return
        
        print("\n" + "="*50)
        print(f"FEEDBACK ID: {feedback_data['feedback_id']}")
        print(f"Student ID: {feedback_data['student_id']}")
        print(f"Teacher ID: {feedback_data['teacher_id']}")
        print(f"Course: {feedback_data['course']}")
        print(f"Rating: {feedback_data['rating']}/5")
        print(f"Comments: {feedback_data['comments']}")
        print(f"Date Submitted: {feedback_data['date_submitted']}")
        print("="*50 + "\n")