import unittest
import sys
import os

# Add the root directory to the Python path to allow importing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from modules.admin import Administrator

class TestAdministrator(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        self.db_name = ":memory:"  # Use in-memory SQLite database
        self.db = Database(self.db_name) 
        self.admin_manager = Administrator(self.db)
        # Database.__init__ should call create_tables if connection is successful.
        # If self.db.conn is None here, Database init failed.
        if not self.db.conn:
            self.fail("Database connection failed in setUp.")
        # Forcing table creation again just in case, though ideally not needed.
        # self.db.create_tables() 

    def tearDown(self):
        """Tear down after each test method."""
        if self.db and self.db.conn:
            self.db.close()

    # --- Test methods for Administrator ---

    def test_add_admin_successful(self):
        """Test successful addition of a new administrator."""
        name = "John Doe"
        email = "john.doe@example.com"
        add_result = self.admin_manager.add_admin(name, "1234567890", email, "Manager", "HR")
        # This assertion checks the return value of add_admin
        self.assertTrue(add_result, f"add_admin returned False, but True was expected. Log output from add_admin might indicate why.")
        
        # Verify by fetching the admin directly from the DB (returns a tuple)
        admin_data_tuple = self.db.fetch_one("SELECT admin_id, name, contact, email, position, department FROM administrators WHERE email=?", (email,))
        self.assertIsNotNone(admin_data_tuple, f"Admin with email '{email}' should be found in DB after successful add, but fetch_one returned None.")
        self.assertEqual(admin_data_tuple[1], name, "Stored admin name does not match.")
        self.assertEqual(admin_data_tuple[3], email, "Stored admin email does not match.")

    def test_add_admin_duplicate_email(self):
        """Test attempting to add an administrator with an email that already exists."""
        name1 = "Jane Doe"
        email = "common.email@example.com"
        contact1 = "0987654321"
        position1 = "Coordinator"
        department1 = "Operations"
        
        # Add initial admin
        initial_add_result = self.admin_manager.add_admin(name1, contact1, email, position1, department1)
        self.assertTrue(initial_add_result, f"Initial admin addition failed for {email}, cannot test duplicate.")
        
        # Attempt to add another admin with the same email
        name2 = "John Smith"
        add_result_duplicate = self.admin_manager.add_admin(name2, "1122334455", email, "Assistant", "Operations")
        self.assertFalse(add_result_duplicate, "add_admin should return False for a duplicate email, but it returned True.")

        # Verify that only the first admin exists
        all_admins_with_email = self.db.fetch_all("SELECT name FROM administrators WHERE email=?", (email,))
        self.assertEqual(len(all_admins_with_email), 1, "Only one admin with the specified email should exist in the DB.")
        self.assertEqual(all_admins_with_email[0][0], name1, "The admin in DB should be the first one added (Jane Doe).")

    # --- Tests for update_admin ---
    def test_update_admin_successful(self):
        """Test successful update of an administrator's details."""
        email = "update.me@example.com"
        self.admin_manager.add_admin("Initial Name", "111222", email, "OldPos", "OldDept")
        
        # Fetch admin_id directly (returns a tuple)
        admin_row = self.db.fetch_one("SELECT admin_id FROM administrators WHERE email=?", (email,))
        self.assertIsNotNone(admin_row, "Admin to be updated should exist in DB.")
        admin_id = admin_row[0]

        update_kwargs = {"name": "Updated Name", "contact": "333444", "position": "NewPos"}
        update_result = self.admin_manager.update_admin(admin_id, **update_kwargs)
        self.assertTrue(update_result, "update_admin should return True for a successful update.")

        # Verify using the Administrator's get_admin method (returns a dict)
        updated_admin_data = self.admin_manager.get_admin(admin_id)
        self.assertIsNotNone(updated_admin_data, "get_admin should find the updated admin.")
        self.assertEqual(updated_admin_data['name'], "Updated Name")
        self.assertEqual(updated_admin_data['contact'], "333444")
        self.assertEqual(updated_admin_data['position'], "NewPos")
        self.assertEqual(updated_admin_data['department'], "OldDept") # This field was not updated

    def test_update_admin_no_valid_fields(self):
        """Test updating with no valid fields provided (empty kwargs or non-matching kwargs)."""
        email = "no.update@example.com"
        self.admin_manager.add_admin("No Update User", "000", email, "Tester", "QA")
        admin_row = self.db.fetch_one("SELECT admin_id FROM administrators WHERE email=?", (email,))
        self.assertIsNotNone(admin_row, "Admin must be added to test update with no valid fields.")
        admin_id = admin_row[0]

        # Attempt to update with no keyword arguments
        update_result_no_kwargs = self.admin_manager.update_admin(admin_id)
        self.assertFalse(update_result_no_kwargs, "update_admin should return False if no kwargs are provided.")

        # Attempt to update with keyword arguments that don't match valid fields
        update_result_invalid_kwargs = self.admin_manager.update_admin(admin_id, non_existent_field="value", another_bad="data")
        self.assertFalse(update_result_invalid_kwargs, "update_admin should return False if only invalid fields are provided.")
        
        # Ensure data hasn't changed
        admin_data_after = self.admin_manager.get_admin(admin_id)
        self.assertEqual(admin_data_after['name'], "No Update User", "Name should not have changed.")

    def test_update_admin_non_existent_id(self):
        """Test attempting to update a non-existent admin_id."""
        non_existent_id = 99999
        update_result = self.admin_manager.update_admin(non_existent_id, name="Ghost User")
        # This relies on the fix in admin.py to check for admin existence first
        self.assertFalse(update_result, "update_admin should return False for a non-existent admin_id.")

    # --- Tests for delete_admin ---
    def test_delete_admin_successful(self):
        """Test successful deletion of an administrator."""
        email = "delete.me@example.com"
        self.admin_manager.add_admin("Delete User", "121212", email, "TempPos", "TempDept")
        admin_row = self.db.fetch_one("SELECT admin_id FROM administrators WHERE email=?", (email,))
        self.assertIsNotNone(admin_row, "Admin to be deleted must exist.")
        admin_id = admin_row[0]

        delete_result = self.admin_manager.delete_admin(admin_id)
        self.assertTrue(delete_result, "delete_admin should return True for successful deletion.")

        # Verify admin is no longer found by get_admin
        deleted_admin_data = self.admin_manager.get_admin(admin_id)
        self.assertIsNone(deleted_admin_data, "get_admin should return None for a deleted admin_id.")
        
        # Also verify directly from DB
        deleted_admin_db_check = self.db.fetch_one("SELECT * FROM administrators WHERE admin_id=?",(admin_id,))
        self.assertIsNone(deleted_admin_db_check, "Admin should not be found in DB after deletion.")


    def test_delete_admin_non_existent_id(self):
        """Test attempting to delete a non-existent admin_id."""
        non_existent_id = 88888
        delete_result = self.admin_manager.delete_admin(non_existent_id)
        self.assertFalse(delete_result, "delete_admin should return False for a non-existent admin_id.")

    # --- Tests for get_admin ---
    def test_get_admin_successful(self):
        """Test retrieving an existing administrator by ID."""
        name = "Alice Wonderland"
        email = "alice.get@example.com"
        self.admin_manager.add_admin(name, "111222333", email, "Reader", "Fantasy")
        
        admin_row = self.db.fetch_one("SELECT admin_id FROM administrators WHERE email=?", (email,))
        self.assertIsNotNone(admin_row, "Admin to be fetched must exist.")
        admin_id = admin_row[0]

        admin_data = self.admin_manager.get_admin(admin_id) # Returns a dict
        self.assertIsNotNone(admin_data, "get_admin should return data for an existing admin.")
        self.assertEqual(admin_data['admin_id'], admin_id)
        self.assertEqual(admin_data['name'], name)
        self.assertEqual(admin_data['email'], email)

    def test_get_admin_non_existent_id(self):
        """Test attempting to retrieve a non-existent admin_id."""
        non_existent_id = 77777
        admin_data = self.admin_manager.get_admin(non_existent_id)
        self.assertIsNone(admin_data, "get_admin should return None for a non-existent admin_id.")

    # --- Tests for get_all_admins ---
    def test_get_all_admins_when_present(self):
        """Test retrieving all administrators when there are admins in the database."""
        self.admin_manager.add_admin("Admin One", "one@example.com", "1", "Pos1", "Dept1")
        self.admin_manager.add_admin("Admin Two", "two@example.com", "2", "Pos2", "Dept2")
        
        all_admins = self.admin_manager.get_all_admins() # Returns a list of dicts
        self.assertIsNotNone(all_admins)
        self.assertEqual(len(all_admins), 2, "get_all_admins should return all added administrators.")
        
        # Check for names (order might vary, so check for presence or sort)
        names_retrieved = sorted([admin['name'] for admin in all_admins])
        self.assertListEqual(names_retrieved, ["Admin One", "Admin Two"])

    def test_get_all_admins_when_empty(self):
        """Test retrieving all administrators when the table is empty."""
        all_admins = self.admin_manager.get_all_admins()
        self.assertIsNotNone(all_admins, "get_all_admins should return an empty list, not None.")
        self.assertEqual(len(all_admins), 0, "get_all_admins should return an empty list when no admins exist.")

    # --- Tests for search_admins ---
    def test_search_admins_by_name(self):
        """Test searching administrators by name (case-insensitive)."""
        name_to_search = "Search Name"
        self.admin_manager.add_admin(name_to_search, "s1@example.com", "S1", "SPos", "SDept")
        self.admin_manager.add_admin("Another Person", "a1@example.com", "A1", "APos", "ADept")
        
        results = self.admin_manager.search_admins(search_term=name_to_search.lower()) # Search with lowercase
        self.assertEqual(len(results), 1, "Should find one admin by name.")
        self.assertEqual(results[0]['name'], name_to_search)

    def test_search_admins_by_email(self):
        """Test searching administrators by email (case-insensitive)."""
        email_to_search = "Search.Email@Example.Com"
        self.admin_manager.add_admin("Email User", "e1@example.com", email_to_search, "EPos", "EDept")
        results = self.admin_manager.search_admins(search_term=email_to_search.upper()) # Search with uppercase
        self.assertEqual(len(results), 1, "Should find one admin by email.")
        self.assertEqual(results[0]['email'], email_to_search)

    def test_search_admins_by_position(self):
        """Test searching administrators by position (case-insensitive)."""
        pos_to_search = "SearchPosition"
        self.admin_manager.add_admin("Position User", "p1@example.com", "P1", pos_to_search, "PDept")
        results = self.admin_manager.search_admins(search_term=pos_to_search.lower())
        self.assertEqual(len(results), 1, "Should find one admin by position.")
        self.assertEqual(results[0]['position'], pos_to_search)

    def test_search_admins_by_department(self):
        """Test searching administrators by department (case-insensitive)."""
        dept_to_search = "SearchDepartment"
        self.admin_manager.add_admin("Dept User", "d1@example.com", "D1", "DPos", dept_to_search)
        results = self.admin_manager.search_admins(search_term=dept_to_search.upper())
        self.assertEqual(len(results), 1, "Should find one admin by department.")
        self.assertEqual(results[0]['department'], dept_to_search)
        
    def test_search_admins_partial_match(self):
        """Test searching with a partial term (e.g., part of name, case-insensitive)."""
        self.admin_manager.add_admin("Match Test One", "partial1@example.com", "PT1", "PTPos", "PTDept")
        self.admin_manager.add_admin("Another User", "partial2@example.com", "PT2", "PTPos2", "PTDept2")
        
        results = self.admin_manager.search_admins(search_term="match test") # Partial and different case
        self.assertEqual(len(results), 1, "Should find one admin with partial name match.")
        self.assertEqual(results[0]['name'], "Match Test One")

    def test_search_admins_multiple_fields_match_single_term(self):
        """Test searching with a term that could match multiple fields but returns distinct admins."""
        # Admin1 matches search_term in name
        self.admin_manager.add_admin("Searchable Term", "admin1@example.com", "C1", "Pos1", "Dept1")
        # Admin2 matches search_term in department
        self.admin_manager.add_admin("Admin Two", "admin2@example.com", "C2", "Pos2", "Searchable Term")
        # Admin3 matches search_term in position
        self.admin_manager.add_admin("Admin Three", "admin3@example.com", "C3", "Searchable Term", "Dept3")

        results = self.admin_manager.search_admins(search_term="Searchable Term")
        self.assertEqual(len(results), 3, "Should find all admins matching 'Searchable Term' in various fields.")
        
        names_found = sorted([admin['name'] for admin in results])
        self.assertListEqual(names_found, ["Admin Three", "Admin Two", "Searchable Term"])

    def test_search_admins_no_results(self):
        """Test searching with a term that matches no administrators."""
        self.admin_manager.add_admin("Existing User", "exists@example.com", "E1", "EPos", "EDept")
        results = self.admin_manager.search_admins(search_term="NonExistentTermXYZ")
        self.assertIsNotNone(results, "Search results should be an empty list, not None.")
        self.assertEqual(len(results), 0, "Search should return an empty list for no matches.")

if __name__ == '__main__':
    unittest.main()
