import unittest
from unittest.mock import patch
import sys
import os
import datetime

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from modules.students import Student

class TestStudent(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.db_name = ":memory:"
        self.db = Database(self.db_name)
        self.student_manager = Student(self.db)
        if not self.db.conn:
            self.fail("Database connection failed in setUp.")
        # Ensure students table exists
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students';")
        if cursor.fetchone() is None:
            self.fail("Students table does not exist in the database after setup.")

    def tearDown(self):
        """Tear down after each test method."""
        if self.db and self.db.conn:
            self.db.close()

    # --- Test methods for add_student ---
    @patch('modules.students.datetime') # Mocking datetime in the students module
    def test_add_student_successful(self, mock_datetime):
        """Test successful addition of a new student."""
        # Setup mock for datetime.now()
        mock_now = datetime.datetime(2024, 1, 15, 10, 30, 0) # Example fixed date
        mock_datetime.datetime.now.return_value = mock_now
        expected_enrollment_date = mock_now.strftime("%Y-%m-%d")

        name = "Alice Smith"
        email = "alice.smith@example.com"
        add_result = self.student_manager.add_student(
            name, 20, "Female", "1234567890", email, 
            "123 Main St", "Computer Science", 1
        )
        self.assertTrue(add_result, "add_student should return True for successful addition.")
        
        # Verify by fetching the student using the manager's get_student method
        # First, get the student_id (since it's auto-incremented)
        student_row_for_id = self.db.fetch_one("SELECT student_id FROM students WHERE email=?", (email,))
        self.assertIsNotNone(student_row_for_id, "Student should be in DB to get ID.")
        student_id = student_row_for_id[0]
        
        student_data = self.student_manager.get_student(student_id) # Returns a dict
        self.assertIsNotNone(student_data, "get_student should retrieve the added student.")
        self.assertEqual(student_data['name'], name)
        self.assertEqual(student_data['email'], email)
        self.assertEqual(student_data['age'], 20)
        self.assertEqual(student_data['course'], "Computer Science")
        self.assertEqual(student_data['enrollment_date'], expected_enrollment_date)
        self.assertEqual(student_data['semester'], 1)

    def test_add_student_duplicate_email(self):
        """Test attempting to add a student with an email that already exists."""
        email = "bob.brown@example.com"
        # Add initial student
        self.student_manager.add_student(
            "Bob Brown", 22, "Male", "0987654321", email,
            "456 Oak St", "Data Science", 3
        )
        
        # Attempt to add another student with the same email
        add_result_duplicate = self.student_manager.add_student(
            "Bobby Brown", 23, "Male", "1122334455", email,
            "789 Pine St", "Cyber Security", 1
        )
        self.assertFalse(add_result_duplicate, "add_student should return False for a duplicate email.")

        # Verify only one student with that email (check by count)
        count_tuple = self.db.fetch_one("SELECT COUNT(*) FROM students WHERE email=?",(email,))
        self.assertEqual(count_tuple[0], 1, "Only one student with the duplicate email should exist.")

    # --- Tests for update_student ---
    def test_update_student_successful_full(self):
        """Test successful full update of a student's details."""
        email = "update.full@example.com"
        self.student_manager.add_student("Original Name", 21, "Other", "111", email, "Addr1", "Course1", 2)
        student_row = self.db.fetch_one("SELECT student_id FROM students WHERE email=?", (email,))
        self.assertIsNotNone(student_row, "Student to be updated must exist.")
        student_id = student_row[0]

        update_kwargs = {
            "name": "Updated Name", "age": 22, "gender": "Male", "contact": "222333",
            "email": "updated.full@example.com", "address": "Addr2 Updated", 
            "course": "Course2 Updated", "semester": 3
        }
        update_result = self.student_manager.update_student(student_id, **update_kwargs)
        self.assertTrue(update_result, "update_student should return True for a successful full update.")

        updated_student = self.student_manager.get_student(student_id)
        self.assertIsNotNone(updated_student)
        for key, value in update_kwargs.items():
            self.assertEqual(updated_student[key], value, f"Field {key} was not updated correctly.")

    def test_update_student_partial(self):
        """Test partial update (e.g., only updating contact and course)."""
        email = "update.partial@example.com"
        original_name = "Partial Original"
        self.student_manager.add_student(original_name, 25, "Female", "555", email, "AddrP", "CourseP", 4)
        student_row = self.db.fetch_one("SELECT student_id FROM students WHERE email=?", (email,))
        self.assertIsNotNone(student_row)
        student_id = student_row[0]

        update_result = self.student_manager.update_student(student_id, contact="666777", course="CourseP Updated")
        self.assertTrue(update_result, "Partial update should be successful.")

        updated_student = self.student_manager.get_student(student_id)
        self.assertIsNotNone(updated_student)
        self.assertEqual(updated_student['contact'], "666777")
        self.assertEqual(updated_student['course'], "CourseP Updated")
        self.assertEqual(updated_student['name'], original_name) # Should remain unchanged

    def test_update_student_non_existent_id(self):
        """Test attempting to update a non-existent student_id."""
        non_existent_id = 99999
        update_result = self.student_manager.update_student(non_existent_id, name="Ghost Student")
        # This relies on the fix in students.py to check for student existence first
        self.assertFalse(update_result, "update_student should return False for a non-existent student_id.")

    def test_update_student_no_valid_fields(self):
        """Test updating with no valid fields provided."""
        email = "no.updatefields@example.com"
        self.student_manager.add_student("NoUpdate User", 30, "Male", "000", email, "AddrN", "CourseN", 5)
        student_row = self.db.fetch_one("SELECT student_id FROM students WHERE email=?", (email,))
        self.assertIsNotNone(student_row)
        student_id = student_row[0]

        update_result_no_kwargs = self.student_manager.update_student(student_id)
        self.assertFalse(update_result_no_kwargs, "update_student should return False if no kwargs are provided.")
        
        update_result_invalid_kwargs = self.student_manager.update_student(student_id, invalid_field="xyz")
        self.assertFalse(update_result_invalid_kwargs, "update_student should return False if only invalid fields are provided.")

    # --- Tests for delete_student ---
    def test_delete_student_successful(self):
        """Test successful deletion of a student."""
        email = "delete.me@example.com"
        self.student_manager.add_student("Delete User", 20, "Male", "del123", email, "Del Addr", "Del Course", 1)
        student_row = self.db.fetch_one("SELECT student_id FROM students WHERE email=?", (email,))
        self.assertIsNotNone(student_row, "Student to be deleted must exist.")
        student_id = student_row[0]

        delete_result = self.student_manager.delete_student(student_id)
        self.assertTrue(delete_result, "delete_student should return True for successful deletion.")

        deleted_student_data = self.student_manager.get_student(student_id)
        self.assertIsNone(deleted_student_data, "get_student should return None for a deleted student_id.")
        
        # Also verify directly from DB
        deleted_student_db_check = self.db.fetch_one("SELECT * FROM students WHERE student_id=?", (student_id,))
        self.assertIsNone(deleted_student_db_check, "Student should not be found in DB after deletion.")

    def test_delete_student_non_existent_id(self):
        """Test attempting to delete a non-existent student_id."""
        non_existent_id = 88888
        delete_result = self.student_manager.delete_student(non_existent_id)
        self.assertFalse(delete_result, "delete_student should return False for a non-existent student_id.")

    # --- Tests for get_student ---
    @patch('modules.students.datetime')
    def test_get_student_successful(self, mock_datetime):
        """Test retrieving an existing student by ID."""
        mock_now = datetime.datetime(2024, 3, 10) # Fixed date for consistent enrollment_date
        mock_datetime.datetime.now.return_value = mock_now
        expected_enrollment_date = mock_now.strftime("%Y-%m-%d")

        name = "Get Student"
        email = "get.student@example.com"
        self.student_manager.add_student(name, 23, "Female", "get123", email, "Get Addr", "Get Course", 2)
        
        student_row = self.db.fetch_one("SELECT student_id FROM students WHERE email=?", (email,))
        self.assertIsNotNone(student_row, "Student to be fetched must exist.")
        student_id = student_row[0]

        student_data = self.student_manager.get_student(student_id) # Returns a dict
        self.assertIsNotNone(student_data, "get_student should return data for an existing student.")
        self.assertEqual(student_data['student_id'], student_id)
        self.assertEqual(student_data['name'], name)
        self.assertEqual(student_data['email'], email)
        self.assertEqual(student_data['enrollment_date'], expected_enrollment_date)

    def test_get_student_non_existent_id(self):
        """Test attempting to retrieve a non-existent student_id."""
        non_existent_id = 77777
        student_data = self.student_manager.get_student(non_existent_id)
        self.assertIsNone(student_data, "get_student should return None for a non-existent student_id.")

    # --- Tests for get_all_students ---
    def test_get_all_students_when_present(self):
        """Test retrieving all students when data exists."""
        self.student_manager.add_student("Student Uno", 20, "Male", "s1", "s1@example.com", "Addr S1", "CS", 1)
        self.student_manager.add_student("Student Dos", 21, "Female", "s2", "s2@example.com", "Addr S2", "IT", 2)
        
        all_students = self.student_manager.get_all_students() # Returns a list of dicts
        self.assertIsNotNone(all_students)
        self.assertEqual(len(all_students), 2, "get_all_students should return all added students.")
        
        # Check for names (order is by name as per students.py get_all_students query)
        self.assertEqual(all_students[0]['name'], "Student Dos") 
        self.assertEqual(all_students[1]['name'], "Student Uno")

    def test_get_all_students_when_empty(self):
        """Test retrieving all students when the table is empty."""
        all_students = self.student_manager.get_all_students()
        self.assertIsNotNone(all_students, "get_all_students should return an empty list, not None.")
        self.assertEqual(len(all_students), 0, "get_all_students should return an empty list when no students exist.")

    # --- Tests for search_students ---
    def test_search_students_by_name(self):
        """Test searching students by name (case-insensitive)."""
        name_to_search = "Searchable Name"
        self.student_manager.add_student(name_to_search, 20, "Male", "sfn1", "sfn1@example.com", "Addr SFN1", "CS", 1)
        self.student_manager.add_student("Another Student", 21, "Female", "sfn2", "sfn2@example.com", "Addr SFN2", "IT", 2)
        
        results = self.student_manager.search_students(search_term=name_to_search.lower()) # Search with lowercase
        self.assertEqual(len(results), 1, "Should find one student by name.")
        self.assertEqual(results[0]['name'], name_to_search)

    def test_search_students_by_email(self):
        """Test searching students by email (case-insensitive)."""
        email_to_search = "Search.Email.Student@Example.Com"
        self.student_manager.add_student("Email Search User", 22, "Other", "sfe1", email_to_search, "Addr SFE1", "Business", 3)
        results = self.student_manager.search_students(search_term=email_to_search.upper()) # Search with uppercase
        self.assertEqual(len(results), 1, "Should find one student by email.")
        self.assertEqual(results[0]['email'], email_to_search)

    def test_search_students_by_course(self):
        """Test searching students by course (case-insensitive)."""
        course_to_search = "Data Analytics"
        self.student_manager.add_student("Course Search User", 23, "Male", "sfc1", "sfc1@example.com", "Addr SFC1", course_to_search, 4)
        self.student_manager.add_student("Different Course User", 24, "Female", "sfc2", "sfc2@example.com", "Addr SFC2", "Robotics", 1)
        results = self.student_manager.search_students(search_term=course_to_search.lower())
        self.assertEqual(len(results), 1, "Should find one student by course.")
        self.assertEqual(results[0]['course'], course_to_search)
        
    def test_search_students_partial_match_name(self):
        """Test searching with a partial term for name (case-insensitive)."""
        self.student_manager.add_student("Student Alpha Beta", 20, "Male", "spa1", "spa1@example.com", "Addr SPA1", "CS", 1)
        self.student_manager.add_student("Gamma Student Delta", 21, "Female", "spa2", "spa2@example.com", "Addr SPA2", "IT", 2)
        
        results = self.student_manager.search_students(search_term="alpha beta") # Partial and different case
        self.assertEqual(len(results), 1, "Should find one student with partial name match.")
        self.assertEqual(results[0]['name'], "Student Alpha Beta")

    def test_search_students_multiple_results(self):
        """Test searching with a term that matches multiple students."""
        common_course = "Common Course"
        self.student_manager.add_student("Student X", 20, "Male", "smr1", "smr1@example.com", "Addr SMR1", common_course, 1)
        self.student_manager.add_student("Student Y", 21, "Female", "smr2", "smr2@example.com", "Addr SMR2", common_course, 2)
        self.student_manager.add_student("Student Z (Different)", 22, "Male", "smr3", "smr3@example.com", "Addr SMR3", "Other Course", 1)

        results = self.student_manager.search_students(search_term=common_course)
        self.assertEqual(len(results), 2, "Should find all students in the 'Common Course'.")
        
        # Check names of found students (order by name)
        names_found = sorted([s['name'] for s in results])
        self.assertListEqual(names_found, ["Student X", "Student Y"])

    def test_search_students_no_results(self):
        """Test searching with a term that matches no students."""
        self.student_manager.add_student("Existing Student", 20, "Male", "snr1", "snr1@example.com", "Addr SNR1", "Maths", 1)
        results = self.student_manager.search_students(search_term="NonExistentSearchTermXYZ")
        self.assertIsNotNone(results, "Search results should be an empty list, not None.")
        self.assertEqual(len(results), 0, "Search should return an empty list for no matches.")

if __name__ == '__main__':
    unittest.main()
