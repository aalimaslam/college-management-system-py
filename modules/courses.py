from database import Database

class Course:
    def __init__(self, db):
        """Initialize Course class with database connection"""
        self.db = db

    def add_course(self, title, description, duration):
        """Add a new course"""
        # Check if course already exists
        existing = self.db.fetch_one("SELECT course_id FROM courses WHERE title = ?", (title,))
        if existing:
            print(f"Error: Course '{title}' already exists.")
            return False

        query = "INSERT INTO courses (title, description, duration) VALUES (?, ?, ?)"
        if self.db.execute_query(query, (title, description, duration)):
            print(f"Course '{title}' added successfully.")
            return True
        return False

    def update_course(self, course_id, title=None, description=None, duration=None):
        """Update course details"""
        existing = self.db.fetch_one("SELECT * FROM courses WHERE course_id = ?", (course_id,))
        if not existing:
            print(f"Error: Course with ID {course_id} does not exist.")
            return False

        updates = {}
        if title:
            updates['title'] = title
        if description:
            updates['description'] = description
        if duration:
            updates['duration'] = duration


        if not updates:
            print("No valid fields to update.")
            return False

        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE courses SET {set_clause} WHERE course_id = ?"
        params = list(updates.values()) + [course_id]

        if self.db.execute_query(query, tuple(params)):
            print(f"Course ID {course_id} updated successfully.")
            return True
        return False

    def delete_course(self, course_id):
        """Delete a course"""
        existing = self.db.fetch_one("SELECT * FROM courses WHERE course_id = ?", (course_id,))
        if not existing:
            print(f"Error: Course with ID {course_id} does not exist.")
            return False

        query = "DELETE FROM courses WHERE course_id = ?"
        if self.db.execute_query(query, (course_id,)):
            print(f"Course ID {course_id} deleted successfully.")
            return True
        return False

    def get_course(self, course_id):
        """Retrieve course details by ID"""
        query = "SELECT * FROM courses WHERE course_id = ?"
        course = self.db.fetch_one(query, (course_id,))
        if not course:
            print(f"No course found with ID {course_id}.")
            return None

        columns = ["course_id", "course_name", "description"]
        return dict(zip(columns, course))

    def get_all_courses(self):
        """List all courses"""
        query = "SELECT * FROM courses ORDER BY course_id"
        return self.db.fetch_all(query)

    def display_course(self, course):
        """Display a single course in formatted output"""
        if not course:
            return
        print("\n" + "=" * 40)
        print(f"Course ID   : {course['course_id']}")
        print(f"Course Name : {course['course_name']}")
        print(f"Description : {course['description']}")
        print("=" * 40 + "\n")
