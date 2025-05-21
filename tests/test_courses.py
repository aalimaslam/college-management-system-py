import unittest
import sys
import os

# Add the root directory to the Python path to allow importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from modules.courses import Course

class TestCourse(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.db_name = ":memory:"  # Use in-memory SQLite database
        self.db = Database(self.db_name)
        self.course_manager = Course(self.db)
        if not self.db.conn:
            self.fail("Database connection failed in setUp.")
        # Ensure courses table exists (created by Database's create_tables)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses';")
        if cursor.fetchone() is None:
            self.fail("Courses table does not exist in the database after setup.")


    def tearDown(self):
        """Tear down after each test method."""
        if self.db and self.db.conn:
            self.db.close()

    # --- Test methods for Course ---

    def test_add_course_successful(self):
        """Test successful addition of a new course."""
        title = "Introduction to Python"
        description = "A beginner-friendly course on Python programming."
        duration = "10 weeks"
        
        add_result = self.course_manager.add_course(title, description, duration)
        self.assertTrue(add_result, "add_course should return True for successful addition.")
        
        # Verify by fetching the course directly from the DB (returns a tuple)
        # Schema: course_id, title, description, duration
        course_data_tuple = self.db.fetch_one("SELECT * FROM courses WHERE title=?", (title,))
        self.assertIsNotNone(course_data_tuple, "Course should be found in DB after successful add.")
        self.assertEqual(course_data_tuple[1], title, "Stored course title does not match.")
        self.assertEqual(course_data_tuple[2], description, "Stored course description does not match.")
        self.assertEqual(course_data_tuple[3], duration, "Stored course duration does not match.")

    def test_add_course_duplicate_title(self):
        """Test attempting to add a course with a title that already exists."""
        title = "Advanced Algorithms"
        description1 = "An in-depth look at algorithms."
        duration1 = "12 weeks"
        
        # Add initial course
        initial_add_result = self.course_manager.add_course(title, description1, duration1)
        self.assertTrue(initial_add_result, f"Initial course addition failed for '{title}', cannot test duplicate.")
        
        # Attempt to add another course with the same title
        description2 = "A different take on advanced algorithms."
        duration2 = "8 weeks"
        add_result_duplicate = self.course_manager.add_course(title, description2, duration2)
        self.assertFalse(add_result_duplicate, "add_course should return False for a duplicate title, but it returned True.")

        # Verify that only the first course exists (or that the second one wasn't added)
        all_courses_with_title = self.db.fetch_all("SELECT description FROM courses WHERE title=?", (title,))
        self.assertEqual(len(all_courses_with_title), 1, "Only one course with the specified title should exist in the DB.")
        self.assertEqual(all_courses_with_title[0][0], description1, "The course in DB should be the first one added.")

    # --- Tests for update_course ---
    def test_update_course_successful(self):
        """Test successful update of a course's details."""
        title = "Original Course Title"
        self.course_manager.add_course(title, "Original Desc", "5 weeks")
        
        # Fetch course_id directly from DB (returns a tuple)
        course_row = self.db.fetch_one("SELECT course_id FROM courses WHERE title=?", (title,))
        self.assertIsNotNone(course_row, "Course to be updated should exist in DB.")
        course_id = course_row[0]

        update_kwargs = {
            "title": "Updated Course Title",
            "description": "Updated Description",
            "duration": "7 weeks"
        }
        update_result = self.course_manager.update_course(course_id, **update_kwargs)
        self.assertTrue(update_result, "update_course should return True for a successful update.")

        # Verify using direct DB check (returns a tuple)
        # Schema: course_id, title, description, duration
        updated_course_tuple = self.db.fetch_one("SELECT * FROM courses WHERE course_id=?", (course_id,))
        self.assertIsNotNone(updated_course_tuple, "Updated course data should not be None.")
        self.assertEqual(updated_course_tuple[1], "Updated Course Title", "Title was not updated correctly.")
        self.assertEqual(updated_course_tuple[2], "Updated Description", "Description was not updated correctly.")
        self.assertEqual(updated_course_tuple[3], "7 weeks", "Duration was not updated correctly.")

    def test_update_course_partial_update(self):
        """Test updating only some fields of a course."""
        title = "Partial Update Course"
        original_desc = "Original Description for Partial"
        original_duration = "3 months"
        self.course_manager.add_course(title, original_desc, original_duration)
        
        course_row = self.db.fetch_one("SELECT course_id FROM courses WHERE title=?", (title,))
        self.assertIsNotNone(course_row)
        course_id = course_row[0]

        update_result = self.course_manager.update_course(course_id, description="New Description for Partial")
        self.assertTrue(update_result, "Partial update should be successful.")

        updated_course_tuple = self.db.fetch_one("SELECT * FROM courses WHERE course_id=?", (course_id,))
        self.assertEqual(updated_course_tuple[1], title, "Title should remain unchanged.")
        self.assertEqual(updated_course_tuple[2], "New Description for Partial", "Description should be updated.")
        self.assertEqual(updated_course_tuple[3], original_duration, "Duration should remain unchanged.")
        
    def test_update_course_no_valid_fields(self):
        """Test updating with no valid fields provided."""
        title = "No Update Fields Course"
        self.course_manager.add_course(title, "Desc", "1 week")
        course_row = self.db.fetch_one("SELECT course_id FROM courses WHERE title=?", (title,))
        self.assertIsNotNone(course_row)
        course_id = course_row[0]

        update_result_no_kwargs = self.course_manager.update_course(course_id) # No actual update kwargs
        self.assertFalse(update_result_no_kwargs, "update_course should return False if no valid fields are provided.")
        
        update_result_none_values = self.course_manager.update_course(course_id, title=None, description=None, duration=None)
        self.assertFalse(update_result_none_values, "update_course should return False if all provided fields are None.")

        # Ensure data hasn't changed
        course_data_after = self.db.fetch_one("SELECT title FROM courses WHERE course_id=?", (course_id,))
        self.assertEqual(course_data_after[0], title, "Title should not have changed.")

    def test_update_course_non_existent_id(self):
        """Test attempting to update a non-existent course_id."""
        non_existent_id = 99999
        update_result = self.course_manager.update_course(non_existent_id, title="Ghost Course")
        self.assertFalse(update_result, "update_course should return False for a non-existent course_id.")

    # --- Tests for delete_course ---
    def test_delete_course_successful(self):
        """Test successful deletion of a course."""
        title = "Course to Delete"
        self.course_manager.add_course(title, "Desc", "1 week")
        course_row = self.db.fetch_one("SELECT course_id FROM courses WHERE title=?", (title,))
        self.assertIsNotNone(course_row, "Course to be deleted must exist.")
        course_id = course_row[0]

        delete_result = self.course_manager.delete_course(course_id)
        self.assertTrue(delete_result, "delete_course should return True for successful deletion.")

        # Verify course is no longer found by get_course (which returns dict or None)
        deleted_course_data = self.course_manager.get_course(course_id)
        self.assertIsNone(deleted_course_data, "get_course should return None for a deleted course_id.")
        
        # Also verify directly from DB (fetch_one returns tuple or None)
        deleted_course_db_check = self.db.fetch_one("SELECT * FROM courses WHERE course_id=?", (course_id,))
        self.assertIsNone(deleted_course_db_check, "Course should not be found in DB after deletion.")

    def test_delete_course_non_existent_id(self):
        """Test attempting to delete a non-existent course_id."""
        non_existent_id = 88888
        delete_result = self.course_manager.delete_course(non_existent_id)
        self.assertFalse(delete_result, "delete_course should return False for a non-existent course_id.")

    # --- Tests for get_course ---
    def test_get_course_successful(self):
        """Test retrieving an existing course by ID."""
        title = "Gettable Course"
        description = "Details for gettable course."
        duration = "3 weeks"
        self.course_manager.add_course(title, description, duration)
        
        course_row = self.db.fetch_one("SELECT course_id FROM courses WHERE title=?", (title,))
        self.assertIsNotNone(course_row, "Course to be fetched must exist.")
        course_id = course_row[0]

        # get_course in courses.py returns a dict.
        # It has a bug: uses 'course_name' for 'title' and misses 'duration'.
        # Testing for actual schema adherence, which might require courses.py to be fixed.
        course_data = self.course_manager.get_course(course_id) 
        self.assertIsNotNone(course_data, "get_course should return data for an existing course.")
        self.assertEqual(course_data.get('course_id'), course_id)
        self.assertEqual(course_data.get('title'), title, "Expected 'title' key based on schema.") # Will fail if courses.py uses 'course_name'
        self.assertEqual(course_data.get('description'), description)
        self.assertEqual(course_data.get('duration'), duration, "Expected 'duration' key based on schema.") # Will fail if courses.py omits it

    def test_get_course_non_existent_id(self):
        """Test attempting to retrieve a non-existent course_id."""
        non_existent_id = 77777
        course_data = self.course_manager.get_course(non_existent_id)
        self.assertIsNone(course_data, "get_course should return None for a non-existent course_id.")

    # --- Tests for get_all_courses ---
    def test_get_all_courses_when_present(self):
        """Test retrieving all courses when there are courses in the database."""
        self.course_manager.add_course("Course Alpha", "Desc A", "1 month")
        self.course_manager.add_course("Course Beta", "Desc B", "2 months")
        
        # get_all_courses in courses.py returns a list of tuples.
        all_courses_tuples = self.course_manager.get_all_courses() 
        self.assertIsNotNone(all_courses_tuples)
        self.assertEqual(len(all_courses_tuples), 2, "get_all_courses should return all added courses.")
        
        # Verify content (expecting tuples: course_id, title, description, duration)
        # Order is by course_id as per courses.py's get_all_courses query
        self.assertEqual(all_courses_tuples[0][1], "Course Alpha") # title of first course
        self.assertEqual(all_courses_tuples[1][1], "Course Beta")  # title of second course
        self.assertEqual(all_courses_tuples[0][3], "1 month")     # duration of first course

    def test_get_all_courses_when_empty(self):
        """Test retrieving all courses when the table is empty."""
        all_courses = self.course_manager.get_all_courses()
        self.assertIsNotNone(all_courses, "get_all_courses should return an empty list, not None.")
        self.assertEqual(len(all_courses), 0, "get_all_courses should return an empty list when no courses exist.")

if __name__ == '__main__':
    unittest.main()
