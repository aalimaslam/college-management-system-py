import unittest
from unittest.mock import patch
import sys
import os
import datetime # Import the original datetime module for creating real datetime objects

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from modules.library import Library

class TestLibrary(unittest.TestCase):

    def setUp(self):
        self.db_name = ":memory:"
        self.db = Database(self.db_name)
        self.library_manager = Library(self.db)
        if not self.db.conn:
            self.fail("Database connection failed in setUp.")
        self.db.create_tables() 

        self.dummy_student_id = 1
        student_exists = self.db.fetch_one("SELECT student_id FROM students WHERE student_id = ?", (self.dummy_student_id,))
        if not student_exists: 
            self.db.execute_query(
                "INSERT INTO students (student_id, name, age, gender, contact, email, address, course, enrollment_date, semester) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.dummy_student_id, "Test Student", 20, "Male", "123000", "test.student@example.com", "123 Test St", "CS", "2023-01-01", 1)
            )

    def tearDown(self):
        if self.db and self.db.conn:
            self.db.close()

    # --- Book Management Tests (selected) ---
    def test_add_book_successful(self):
        add_result = self.library_manager.add_book("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Scribner", 1925, 10)
        self.assertTrue(add_result)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("9780743273565",))
        self.assertIsNotNone(book_id_row)
        book = self.library_manager.get_book(book_id_row[0])
        self.assertEqual(book['title'], "The Great Gatsby")

    def test_search_books(self): 
        self.library_manager.add_book("Python Basics", "Author P", "py123", "PubPy", 2020, 1)
        self.library_manager.add_book("Java Advanced", "Author J", "java123", "PubJava", 2021, 1)
        self.assertEqual(len(self.library_manager.search_books("python")), 1)
        self.assertEqual(len(self.library_manager.search_books("AUTHOR J")), 1)

    # --- Test methods for Book Issuing and Returning ---
    @patch('modules.library.datetime') 
    def test_issue_book_successful(self, mock_datetime_module):
        fixed_now = datetime.datetime(2024, 1, 1, 10, 0, 0) # real datetime object
        mock_datetime_module.datetime.now.return_value = fixed_now
        # Ensure strptime calls on the mocked datetime class use the real strptime
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta # Ensure timedelta is the real one

        expected_issue_date = fixed_now.strftime("%Y-%m-%d")
        expected_return_date = (fixed_now + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

        self.library_manager.add_book("Issuable", "I. Author", "issue1", "PubI", 2023, 1)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("issue1",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        
        self.assertTrue(self.library_manager.issue_book(book_id, self.dummy_student_id), "issue_book should succeed.")
        book = self.library_manager.get_book(book_id)
        self.assertEqual(book['available_copies'], 0)
        issue_info = self.db.fetch_one("SELECT issue_date, return_date, status FROM book_issues WHERE book_id=?", (book_id,))
        self.assertIsNotNone(issue_info, "Issue record should be created.")
        self.assertEqual(issue_info[0], expected_issue_date)
        self.assertEqual(issue_info[1], expected_return_date)
        self.assertEqual(issue_info[2], "issued")

    def test_issue_book_no_available_copies(self):
        self.library_manager.add_book("No Copies", "N. Author", "no_copy_isbn", "PubN", 2023, 0)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("no_copy_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.assertFalse(self.library_manager.issue_book(book_id, self.dummy_student_id))

    def test_issue_book_to_non_existent_student(self):
        self.library_manager.add_book("For Ghost Student", "G. Author", "ghost_isbn", "PubG", 2023, 1)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("ghost_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.assertFalse(self.library_manager.issue_book(book_id, 999)) # Non-existent student

    @patch('modules.library.datetime')
    def test_issue_book_already_issued_to_student(self, mock_datetime_module):
        fixed_now = datetime.datetime(2024, 1, 1)
        mock_datetime_module.datetime.now.return_value = fixed_now
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta

        self.library_manager.add_book("Double Issue Test", "D. Author", "double_isbn", "PubD", 2023, 2)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("double_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.library_manager.issue_book(book_id, self.dummy_student_id) 
        self.assertFalse(self.library_manager.issue_book(book_id, self.dummy_student_id))
        book = self.library_manager.get_book(book_id)
        self.assertEqual(book['available_copies'], 1)


    @patch('modules.library.datetime')
    def test_return_book_successful_on_time(self, mock_datetime_module):
        issue_time = datetime.datetime(2024, 1, 1)
        mock_datetime_module.datetime.now.return_value = issue_time
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta
        
        self.library_manager.add_book("Return Test Book", "R. Author", "ret_isbn", "PubR", 2023, 1)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("ret_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.library_manager.issue_book(book_id, self.dummy_student_id)
        issue_id_row = self.db.fetch_one("SELECT issue_id FROM book_issues WHERE book_id=?", (book_id,))
        self.assertIsNotNone(issue_id_row)
        issue_id = issue_id_row[0]
        
        return_time = datetime.datetime(2024, 1, 10) 
        mock_datetime_module.datetime.now.return_value = return_time
        
        self.assertTrue(self.library_manager.return_book(issue_id))
        returned_issue = self.db.fetch_one("SELECT status, fine_amount, actual_return_date FROM book_issues WHERE issue_id=?",(issue_id,))
        self.assertEqual(returned_issue[0], "returned")
        self.assertEqual(returned_issue[1], 0) 
        self.assertEqual(returned_issue[2], "2024-01-10")


    @patch('modules.library.datetime')
    def test_return_book_late_with_fine(self, mock_datetime_module):
        issue_time = datetime.datetime(2024, 1, 1)
        mock_datetime_module.datetime.now.return_value = issue_time
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta

        self.library_manager.add_book("Late Book", "L. Author", "late_isbn", "PubL", 2023, 1)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("late_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.library_manager.issue_book(book_id, self.dummy_student_id) 
        issue_id_row = self.db.fetch_one("SELECT issue_id FROM book_issues WHERE book_id=?", (book_id,))
        self.assertIsNotNone(issue_id_row)
        issue_id = issue_id_row[0]

        return_time_late = datetime.datetime(2024, 1, 20) 
        mock_datetime_module.datetime.now.return_value = return_time_late
        self.assertTrue(self.library_manager.return_book(issue_id))
        returned_issue = self.db.fetch_one("SELECT fine_amount FROM book_issues WHERE issue_id=?", (issue_id,))
        self.assertEqual(returned_issue[0], 10)

    def test_return_book_non_existent_issue_id(self):
        self.assertFalse(self.library_manager.return_book(9999))

    @patch('modules.library.datetime')
    def test_return_book_already_returned(self, mock_datetime_module):
        first_fixed_time = datetime.datetime(2024, 1, 1)
        mock_datetime_module.datetime.now.return_value = first_fixed_time
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta

        self.library_manager.add_book("Double Return", "D. Author", "double_ret_isbn", "PubDR", 2023, 1)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("double_ret_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.library_manager.issue_book(book_id, self.dummy_student_id)
        issue_id_row = self.db.fetch_one("SELECT issue_id FROM book_issues WHERE book_id=?", (book_id,))
        self.assertIsNotNone(issue_id_row)
        issue_id = issue_id_row[0]
        
        second_fixed_time = datetime.datetime(2024, 1, 5)
        mock_datetime_module.datetime.now.return_value = second_fixed_time
        self.library_manager.return_book(issue_id) 
        self.assertFalse(self.library_manager.return_book(issue_id))

    @patch('modules.library.datetime')
    def test_update_book_total_copies_less_than_issued(self, mock_datetime_module):
        fixed_now = datetime.datetime(2024, 1, 1)
        mock_datetime_module.datetime.now.return_value = fixed_now
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta

        self.library_manager.add_book("Issue Check", "IC. Author", "ic_isbn", "PubIC", 2023, 3)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("ic_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.library_manager.issue_book(book_id, self.dummy_student_id) 
        self.assertFalse(self.library_manager.update_book(book_id, total_copies=0))

    @patch('modules.library.datetime')
    def test_delete_book_with_pending_issues(self, mock_datetime_module):
        fixed_now = datetime.datetime(2024, 1, 1)
        mock_datetime_module.datetime.now.return_value = fixed_now
        mock_datetime_module.datetime.strptime.side_effect = lambda date_string, fmt: datetime.datetime.strptime(date_string, fmt)
        mock_datetime_module.timedelta = datetime.timedelta

        self.library_manager.add_book("Issued Delete", "ID. Author", "id_isbn", "PubID", 2023, 1)
        book_id_row = self.db.fetch_one("SELECT book_id FROM books WHERE isbn=?", ("id_isbn",))
        self.assertIsNotNone(book_id_row)
        book_id = book_id_row[0]
        self.library_manager.issue_book(book_id, self.dummy_student_id)
        self.assertFalse(self.library_manager.delete_book(book_id))

if __name__ == '__main__':
    unittest.main()
