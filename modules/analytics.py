from database import Database

class Analytics:
    def __init__(self, db_name="college_management.db"):
        self.db = db_name
        print("Analytics module initialized.")

    def get_total_students(self):
        """Queries the students table to count the total number of students."""
        result = self.db.fetch_one("SELECT COUNT(*) FROM students")
        return result[0] if result else 0

    def get_students_by_course(self):
        """Queries the students table and groups by the course column."""
        results = self.db.fetch_all("SELECT course, COUNT(*) FROM students GROUP BY course")
        return {course: count for course, count in results} if results else {}

    def get_students_by_gender(self):
        """Queries the students table and groups by the gender column."""
        results = self.db.fetch_all("SELECT gender, COUNT(*) FROM students GROUP BY gender")
        return {gender: count for gender, count in results} if results else {}

    def get_student_enrollment_trends(self):
        """Queries the students table and groups by enrollment year-month."""
        results = self.db.fetch_all("SELECT SUBSTR(enrollment_date, 1, 7), COUNT(*) FROM students GROUP BY SUBSTR(enrollment_date, 1, 7) ORDER BY SUBSTR(enrollment_date, 1, 7)")
        return {period: count for period, count in results} if results else {}

    def get_total_courses(self):
        """Queries the courses table to count the total number of courses."""
        result = self.db.fetch_one("SELECT COUNT(*) FROM courses")
        return result[0] if result else 0

    def get_course_popularity(self):
        """Queries the students table to count students per course."""
        # This method reuses the logic from get_students_by_course
        results = self.db.fetch_all("SELECT course, COUNT(*) FROM students GROUP BY course")
        return {course: count for course, count in results} if results else {}

    def get_total_teachers(self):
        """Queries the teachers table to count the total number of teachers."""
        result = self.db.fetch_one("SELECT COUNT(*) FROM teachers")
        return result[0] if result else 0

    def get_teachers_by_department(self):
        """Queries the teachers table and groups by the department column."""
        results = self.db.fetch_all("SELECT department, COUNT(*) FROM teachers GROUP BY department")
        return {department: count for department, count in results} if results else {}

    def get_total_books(self):
        """Queries the books table to count the total number of unique book entries."""
        result = self.db.fetch_one("SELECT COUNT(DISTINCT book_id) FROM books")
        return result[0] if result else 0

    def get_total_borrowed_books(self):
        """Queries the book_issues table to count books that are currently borrowed."""
        result = self.db.fetch_one("SELECT COUNT(*) FROM book_issues WHERE status = 'Issued'")
        return result[0] if result else 0

    def get_most_borrowed_books(self, limit=5):
        """Queries book_issues and books tables for most borrowed books."""
        query = """
            SELECT b.title, COUNT(bi.book_id) AS borrow_count
            FROM book_issues bi
            JOIN books b ON bi.book_id = b.book_id
            GROUP BY bi.book_id, b.title
            ORDER BY borrow_count DESC
            LIMIT ?
        """
        results = self.db.fetch_all(query, (limit,))
        return results if results else []

    def get_total_events(self):
        """Queries the events table to count the total number of events."""
        result = self.db.fetch_one("SELECT COUNT(*) FROM events")
        return result[0] if result else 0

    def get_upcoming_events(self):
        """Queries the events table for upcoming events."""
        query = "SELECT name, date, venue FROM events WHERE date >= date('now') ORDER BY date ASC"
        results = self.db.fetch_all(query)
        return results if results else []

    def get_average_feedback_rating_by_course(self):
        """Queries the feedback table for average rating by course."""
        query = "SELECT course, AVG(rating) FROM feedback GROUP BY course"
        results = self.db.fetch_all(query)
        # Filter out courses where AVG(rating) might be None
        return {course: avg_rating for course, avg_rating in results if avg_rating is not None} if results else {}

    def get_average_feedback_rating_by_teacher(self):
        """Queries feedback and teachers tables for average rating by teacher."""
        query = """
            SELECT t.name, AVG(f.rating)
            FROM feedback f
            JOIN teachers t ON f.teacher_id = t.teacher_id
            GROUP BY t.teacher_id, t.name
        """
        results = self.db.fetch_all(query)
        # Filter out teachers where AVG(rating) might be None
        return {name: avg_rating for name, avg_rating in results if avg_rating is not None} if results else {}
