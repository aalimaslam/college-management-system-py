from database import Database

class Administrator:
    def __init__(self, db):
        """Initialize Administrator class with database connection"""
        self.db = db
    
    def add_admin(self, name, contact, email, position, department):
        """Add a new administrator to the database"""
        # Check if email already exists
        exists = self.db.fetch_one("SELECT email FROM administrators WHERE email = ?", (email,))
        if exists:
            print(f"Error: Administrator with email {email} already exists.")
            return False
        
        query = """
        INSERT INTO administrators (name, contact, email, position, department)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (name, contact, email, position, department)
        
        if self.db.execute_query(query, params):
            print(f"Administrator {name} added successfully.")
            return True
        return False
    
    def update_admin(self, admin_id, **kwargs):
        """Update administrator information"""
        valid_fields = ['name', 'contact', 'email', 'position', 'department']
        
        # Filter out invalid fields
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            print("No valid fields to update.")
            return False
        
        # Construct update query
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE administrators SET {set_clause} WHERE admin_id = ?"
        
        # Parameters for the query
        params = list(updates.values()) + [admin_id]
        
        if self.db.execute_query(query, tuple(params)):
            print(f"Administrator ID {admin_id} updated successfully.")
            return True
        return False
    
    def delete_admin(self, admin_id):
        """Delete an administrator from the database"""
        # Check if admin exists
        exists = self.db.fetch_one("SELECT admin_id FROM administrators WHERE admin_id = ?", (admin_id,))
        if not exists:
            print(f"Error: Administrator with ID {admin_id} does not exist.")
            return False
        
        query = "DELETE FROM administrators WHERE admin_id = ?"
        if self.db.execute_query(query, (admin_id,)):
            print(f"Administrator ID {admin_id} deleted successfully.")
            return True
        return False
    
    def get_admin(self, admin_id):
        """Get administrator details by ID"""
        query = "SELECT * FROM administrators WHERE admin_id = ?"
        admin = self.db.fetch_one(query, (admin_id,))
        
        if not admin:
            print(f"No administrator found with ID {admin_id}.")
            return None
        
        # Convert to dictionary for easier access
        columns = ["admin_id", "name", "contact", "email", "position", "department"]
        return dict(zip(columns, admin))
    
    def get_all_admins(self):
        """Get all administrators"""
        query = "SELECT * FROM administrators ORDER BY name"
        admins = self.db.fetch_all(query)
        
        if not admins:
            print("No administrators found.")
            return []
        
        # Convert to list of dictionaries
        columns = ["admin_id", "name", "contact", "email", "position", "department"]
        return [dict(zip(columns, admin)) for admin in admins]
    
    def search_admins(self, search_term):
        """Search for administrators by name, email, position, or department"""
        query = """
        SELECT * FROM administrators 
        WHERE name ILIKE ? OR email ILIKE ? OR position ILIKE ? OR department ILIKE ?
        ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern)
        admins = self.db.fetch_all(query, params)
        
        if not admins:
            print(f"No administrators found matching '{search_term}'.")
            return []
        
        # Convert to list of dictionaries
        columns = ["admin_id", "name", "contact", "email", "position", "department"]
        return [dict(zip(columns, admin)) for admin in admins]
    
    def display_admin(self, admin_data):
        """Display administrator information in a formatted way"""
        if not admin_data:
            return
        
        print("\n" + "="*50)
        print(f"ADMINISTRATOR ID: {admin_data['admin_id']}")
        print(f"Name: {admin_data['name']}")
        print(f"Contact: {admin_data['contact']}")
        print(f"Email: {admin_data['email']}")
        print(f"Position: {admin_data['position']}")
        print(f"Department: {admin_data['department']}")
        print("="*50 + "\n")