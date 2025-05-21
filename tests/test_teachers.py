import unittest
from unittest.mock import patch
import sys
import os
import datetime

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from modules.teachers import Teacher

class TestTeacher(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.db_name = ":memory:"
        self.db = Database(self.db_name)
        self.teacher_manager = Teacher(self.db)
        if not self.db.conn:
            self.fail("Database connection failed in setUp.")
        # Ensure teachers table exists
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teachers';")
        if cursor.fetchone() is None:
            self.fail("Teachers table does not exist in the database after setup.")

    def tearDown(self):
        """Tear down after each test method."""
        if self.db and self.db.conn:
            self.db.close()

    # --- Test methods for add_teacher ---
    @patch('modules.teachers.datetime') # Mocking datetime in the teachers module
    def test_add_teacher_successful(self, mock_datetime):
        """Test successful addition of a new teacher."""
        mock_now = datetime.datetime(2024, 2, 10, 11, 0, 0) # Example fixed date
        mock_datetime.datetime.now.return_value = mock_now
        expected_date_joined = mock_now.strftime("%Y-%m-%d")

        name = "Dr. Jane Smith"
        email = "jane.smith@example.edu"
        add_result = self.teacher_manager.add_teacher(
            name, "Female", "9876543210", email, 
            "Computer Science", "PhD in AI"
        )
        self.assertTrue(add_result, "add_teacher should return True for successful addition.")
        
        # Verify by fetching the teacher using the manager's get_teacher method
        teacher_row_for_id = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE email=?", (email,))
        self.assertIsNotNone(teacher_row_for_id, "Teacher should be in DB to get ID.")
        teacher_id = teacher_row_for_id[0]
        
        teacher_data = self.teacher_manager.get_teacher(teacher_id) # Returns a dict
        self.assertIsNotNone(teacher_data, "get_teacher should retrieve the added teacher.")
        self.assertEqual(teacher_data['name'], name)
        self.assertEqual(teacher_data['email'], email)
        self.assertEqual(teacher_data['gender'], "Female")
        self.assertEqual(teacher_data['department'], "Computer Science")
        self.assertEqual(teacher_data['qualification'], "PhD in AI")
        self.assertEqual(teacher_data['date_joined'], expected_date_joined)

    def test_add_teacher_duplicate_email(self):
        """Test attempting to add a teacher with an email that already exists."""
        email = "john.doe@example.edu"
        # Add initial teacher
        self.teacher_manager.add_teacher(
            "Dr. John Doe", "Male", "1234567890", email,
            "Physics", "PhD in Quantum Physics"
        )
        
        # Attempt to add another teacher with the same email
        add_result_duplicate = self.teacher_manager.add_teacher(
            "Dr. Johnny Doe", "Male", "1122334455", email,
            "Chemistry", "MSc in Organic Chemistry"
        )
        self.assertFalse(add_result_duplicate, "add_teacher should return False for a duplicate email.")

        # Verify only one teacher with that email (check by count)
        count_tuple = self.db.fetch_one("SELECT COUNT(*) FROM teachers WHERE email=?",(email,))
        self.assertEqual(count_tuple[0], 1, "Only one teacher with the duplicate email should exist.")

    # --- Tests for update_teacher ---
    def test_update_teacher_successful_full(self):
        """Test successful full update of a teacher's details."""
        email = "update.full.teacher@example.edu"
        self.teacher_manager.add_teacher("Original Teacher", "Other", "t111", email, "Dept1", "Qual1")
        teacher_row = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE email=?", (email,))
        self.assertIsNotNone(teacher_row, "Teacher to be updated must exist.")
        teacher_id = teacher_row[0]

        update_kwargs = {
            "name": "Updated Teacher Name", "gender": "Male", "contact": "t222333",
            "email": "updated.full.teacher@example.edu", "department": "Dept2 Updated", 
            "qualification": "Qual2 Updated"
        }
        update_result = self.teacher_manager.update_teacher(teacher_id, **update_kwargs)
        self.assertTrue(update_result, "update_teacher should return True for a successful full update.")

        updated_teacher = self.teacher_manager.get_teacher(teacher_id)
        self.assertIsNotNone(updated_teacher)
        for key, value in update_kwargs.items():
            self.assertEqual(updated_teacher[key], value, f"Field {key} was not updated correctly.")

    def test_update_teacher_partial(self):
        """Test partial update (e.g., only updating department and qualification)."""
        email = "update.partial.teacher@example.edu"
        original_name = "Partial Original Teacher"
        self.teacher_manager.add_teacher(original_name, "Female", "t555", email, "DeptP", "QualP")
        teacher_row = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE email=?", (email,))
        self.assertIsNotNone(teacher_row)
        teacher_id = teacher_row[0]

        update_result = self.teacher_manager.update_teacher(teacher_id, department="DeptP Updated", qualification="QualP Updated")
        self.assertTrue(update_result, "Partial update should be successful.")

        updated_teacher = self.teacher_manager.get_teacher(teacher_id)
        self.assertIsNotNone(updated_teacher)
        self.assertEqual(updated_teacher['department'], "DeptP Updated")
        self.assertEqual(updated_teacher['qualification'], "QualP Updated")
        self.assertEqual(updated_teacher['name'], original_name) # Should remain unchanged

    def test_update_teacher_non_existent_id(self):
        """Test attempting to update a non-existent teacher_id."""
        non_existent_id = 99999
        update_result = self.teacher_manager.update_teacher(non_existent_id, name="Ghost Teacher")
        # This relies on the fix in teachers.py to check for teacher existence first
        self.assertFalse(update_result, "update_teacher should return False for a non-existent teacher_id.")

    def test_update_teacher_no_valid_fields(self):
        """Test updating with no valid fields provided."""
        email = "no.updatefields.teacher@example.edu"
        self.teacher_manager.add_teacher("NoUpdate Teacher", "Male", "t000", email, "DeptN", "QualN")
        teacher_row = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE email=?", (email,))
        self.assertIsNotNone(teacher_row)
        teacher_id = teacher_row[0]

        update_result_no_kwargs = self.teacher_manager.update_teacher(teacher_id)
        self.assertFalse(update_result_no_kwargs, "update_teacher should return False if no kwargs are provided.")
        
        update_result_invalid_kwargs = self.teacher_manager.update_teacher(teacher_id, invalid_field="xyz")
        self.assertFalse(update_result_invalid_kwargs, "update_teacher should return False if only invalid fields are provided.")

    # --- Tests for delete_teacher ---
    def test_delete_teacher_successful(self):
        """Test successful deletion of a teacher."""
        email = "delete.me.teacher@example.edu"
        self.teacher_manager.add_teacher("Delete Teacher", "Male", "del123t", email, "Del Dept", "Del Qual")
        teacher_row = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE email=?", (email,))
        self.assertIsNotNone(teacher_row, "Teacher to be deleted must exist.")
        teacher_id = teacher_row[0]

        delete_result = self.teacher_manager.delete_teacher(teacher_id)
        self.assertTrue(delete_result, "delete_teacher should return True for successful deletion.")

        deleted_teacher_data = self.teacher_manager.get_teacher(teacher_id)
        self.assertIsNone(deleted_teacher_data, "get_teacher should return None for a deleted teacher_id.")
        
        deleted_teacher_db_check = self.db.fetch_one("SELECT * FROM teachers WHERE teacher_id=?", (teacher_id,))
        self.assertIsNone(deleted_teacher_db_check, "Teacher should not be found in DB after deletion.")

    def test_delete_teacher_non_existent_id(self):
        """Test attempting to delete a non-existent teacher_id."""
        non_existent_id = 88888
        delete_result = self.teacher_manager.delete_teacher(non_existent_id)
        self.assertFalse(delete_result, "delete_teacher should return False for a non-existent teacher_id.")

    # --- Tests for get_teacher ---
    @patch('modules.teachers.datetime')
    def test_get_teacher_successful(self, mock_datetime):
        """Test retrieving an existing teacher by ID."""
        mock_now = datetime.datetime(2024, 3, 15) # Fixed date for consistent date_joined
        mock_datetime.datetime.now.return_value = mock_now
        expected_date_joined = mock_now.strftime("%Y-%m-%d")

        name = "Get Teacher Example"
        email = "get.teacher@example.edu"
        self.teacher_manager.add_teacher(name, "Female", "get123t", email, "Get Dept", "Get Qual")
        
        teacher_row = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE email=?", (email,))
        self.assertIsNotNone(teacher_row, "Teacher to be fetched must exist.")
        teacher_id = teacher_row[0]

        teacher_data = self.teacher_manager.get_teacher(teacher_id) # Returns a dict
        self.assertIsNotNone(teacher_data, "get_teacher should return data for an existing teacher.")
        self.assertEqual(teacher_data['teacher_id'], teacher_id)
        self.assertEqual(teacher_data['name'], name)
        self.assertEqual(teacher_data['email'], email)
        self.assertEqual(teacher_data['date_joined'], expected_date_joined)

    def test_get_teacher_non_existent_id(self):
        """Test attempting to retrieve a non-existent teacher_id."""
        non_existent_id = 77777
        teacher_data = self.teacher_manager.get_teacher(non_existent_id)
        self.assertIsNone(teacher_data, "get_teacher should return None for a non-existent teacher_id.")

    # --- Tests for get_all_teachers ---
    def test_get_all_teachers_when_present(self):
        """Test retrieving all teachers when data exists."""
        self.teacher_manager.add_teacher("Teacher Alpha", "Male", "ta1", "ta1@example.edu", "Dept A", "PhD")
        self.teacher_manager.add_teacher("Teacher Beta", "Female", "tb1", "tb1@example.edu", "Dept B", "MSc")
        
        all_teachers = self.teacher_manager.get_all_teachers() # Returns a list of dicts
        self.assertIsNotNone(all_teachers)
        self.assertEqual(len(all_teachers), 2, "get_all_teachers should return all added teachers.")
        
        # Check for names (order is by name as per teachers.py get_all_teachers query)
        self.assertEqual(all_teachers[0]['name'], "Teacher Alpha") 
        self.assertEqual(all_teachers[1]['name'], "Teacher Beta")

    def test_get_all_teachers_when_empty(self):
        """Test retrieving all teachers when the table is empty."""
        all_teachers = self.teacher_manager.get_all_teachers()
        self.assertIsNotNone(all_teachers, "get_all_teachers should return an empty list, not None.")
        self.assertEqual(len(all_teachers), 0, "get_all_teachers should return an empty list when no teachers exist.")

    # --- Tests for search_teachers ---
    def test_search_teachers_by_name(self):
        """Test searching teachers by name (case-insensitive)."""
        name_to_search = "Prof. Searchable"
        self.teacher_manager.add_teacher(name_to_search, "Male", "sfn1t", "sfn1t@example.edu", "CS", "PhD")
        self.teacher_manager.add_teacher("Another Teacher", "Female", "sfn2t", "sfn2t@example.edu", "IT", "MSc")
        
        results = self.teacher_manager.search_teachers(search_term=name_to_search.lower())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], name_to_search)

    def test_search_teachers_by_email(self):
        """Test searching teachers by email (case-insensitive)."""
        email_to_search = "Search.Email.Teacher@Example.Edu"
        self.teacher_manager.add_teacher("Email Search Teacher", "Other", "sfe1t", email_to_search, "Business", "MBA")
        results = self.teacher_manager.search_teachers(search_term=email_to_search.upper())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['email'], email_to_search)

    def test_search_teachers_by_department(self):
        """Test searching teachers by department (case-insensitive)."""
        dept_to_search = "Quantum Mechanics"
        self.teacher_manager.add_teacher("Dept Search Teacher", "Male", "sfd1t", "sfd1t@example.edu", dept_to_search, "PhD")
        results = self.teacher_manager.search_teachers(search_term=dept_to_search.lower())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['department'], dept_to_search)

    def test_search_teachers_by_qualification(self):
        """Test searching teachers by qualification (case-insensitive)."""
        qual_to_search = "Rocket Science Expert"
        self.teacher_manager.add_teacher("Qual Search Teacher", "Female", "sfq1t", "sfq1t@example.edu", "Aerospace", qual_to_search)
        results = self.teacher_manager.search_teachers(search_term=qual_to_search.upper())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['qualification'], qual_to_search)
        
    def test_search_teachers_partial_match_name(self):
        """Test searching with a partial term for name (case-insensitive)."""
        self.teacher_manager.add_teacher("Teacher Alpha Beta Gamma", "Male", "spat1", "spat1@example.edu", "CS", "PhD")
        self.teacher_manager.add_teacher("Delta Epsilon Teacher", "Female", "spat2", "spat2@example.edu", "IT", "MSc")
        
        results = self.teacher_manager.search_teachers(search_term="alpha beta") 
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Teacher Alpha Beta Gamma")

    def test_search_teachers_multiple_results(self):
        """Test searching with a term that matches multiple teachers by different fields."""
        common_qual = "Expert Coder"
        self.teacher_manager.add_teacher("Teacher X", "Male", "smrt1", "smrt1@example.edu", "Software Eng", common_qual)
        self.teacher_manager.add_teacher("Teacher Y", "Female", "smrt2", "smrt2@example.edu", "Game Dev", common_qual)
        self.teacher_manager.add_teacher("Teacher Z (Different)", "Male", "smrt3", "smrt3@example.edu", "AI", "PhD AI")

        results = self.teacher_manager.search_teachers(search_term=common_qual)
        self.assertEqual(len(results), 2)
        names_found = sorted([t['name'] for t in results])
        self.assertListEqual(names_found, ["Teacher X", "Teacher Y"])

    def test_search_teachers_no_results(self):
        """Test searching with a term that matches no teachers."""
        self.teacher_manager.add_teacher("Existing Teacher", "Male", "snrt1", "snrt1@example.edu", "Maths", "PhD")
        results = self.teacher_manager.search_teachers(search_term="NonExistentSearchTermXYZ")
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
