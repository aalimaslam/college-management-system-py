from database import Database
import datetime

class Teacher:
    def __init__(self, db):
        """Initialize Teacher class with database connection"""
        self.db = db

    def add_teacher(self, name, gender, contact, email, department, qualification):
        """Add a new teacher to the database"""
        date_joined = datetime.datetime.now().strftime("%Y-%m-%d")

        # Check if email already exists
        exists = self.db.fetch_one("SELECT email FROM teachers WHERE email = ?", (email,))
        if exists:
            print(f"❌ Error: Teacher with email {email} already exists.")
            return False

        query = """
        INSERT INTO teachers (name, gender, contact, email, department, qualification, date_joined)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (name, gender, contact, email, department, qualification, date_joined)

        if self.db.execute_query(query, params):
            print(f"✅ Teacher '{name}' added successfully!")
            return True
        print("❌ Failed to add teacher.")
        return False

    def update_teacher(self, teacher_id, **kwargs):
        """Update teacher information"""
        valid_fields = ['name', 'gender', 'contact', 'email', 'department', 'qualification']

        # Filter out invalid fields
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        if not updates:
            print("⚠️  No valid fields to update.")
            return False

        # Check if teacher_id exists before trying to update
        check_exists = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
        if not check_exists:
            print(f"❌ Error: Teacher with ID {teacher_id} does not exist. Cannot update.")
            return False

        # Construct update query
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE teachers SET {set_clause} WHERE teacher_id = ?"

        # Parameters for the query
        params = list(updates.values()) + [teacher_id]

        if self.db.execute_query(query, tuple(params)):
            print(f"✅ Teacher ID {teacher_id} updated successfully!")
            return True
        print("❌ Failed to update teacher.")
        return False

    def delete_teacher(self, teacher_id):
        """Delete a teacher from the database"""
        # Check if teacher exists
        exists = self.db.fetch_one("SELECT teacher_id FROM teachers WHERE teacher_id = ?", (teacher_id,))
        if not exists:
            print(f"❌ Error: Teacher with ID {teacher_id} does not exist.")
            return False

        query = "DELETE FROM teachers WHERE teacher_id = ?"
        if self.db.execute_query(query, (teacher_id,)):
            print(f"🗑️  Teacher ID {teacher_id} deleted successfully.")
            return True
        print("❌ Failed to delete teacher.")
        return False

    def get_teacher(self, teacher_id):
        """Get teacher details by ID"""
        query = "SELECT * FROM teachers WHERE teacher_id = ?"
        teacher = self.db.fetch_one(query, (teacher_id,))

        if not teacher:
            print(f"⚠️  No teacher found with ID {teacher_id}.")
            return None

        # Convert to dictionary for easier access
        columns = ["teacher_id", "name", "gender", "contact", "email",
                  "department", "qualification", "date_joined"]
        return dict(zip(columns, teacher))

    def get_all_teachers(self):
        """Get all teachers"""
        query = "SELECT * FROM teachers ORDER BY name"
        teachers = self.db.fetch_all(query)

        if not teachers:
            print("⚠️  No teachers found.")
            return []

        # Convert to list of dictionaries
        columns = ["teacher_id", "name", "gender", "contact", "email",
                  "department", "qualification", "date_joined"]
        return [dict(zip(columns, teacher)) for teacher in teachers]

    def search_teachers(self, search_term):
        """Search for teachers by name, email, department, or qualification"""
        query = """
        SELECT * FROM teachers 
        WHERE LOWER(name) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?) OR LOWER(department) LIKE LOWER(?) OR LOWER(qualification) LIKE LOWER(?)
        ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern)
        teachers = self.db.fetch_all(query, params)

        if not teachers:
            print(f"⚠️  No teachers found matching '{search_term}'.")
            return []

        # Convert to list of dictionaries
        columns = ["teacher_id", "name", "gender", "contact", "email",
                  "department", "qualification", "date_joined"]
        return [dict(zip(columns, teacher)) for teacher in teachers]

    def display_teacher(self, teacher_data):
        """Display teacher information in a formatted way"""
        if not teacher_data:
            print("⚠️  No teacher data to display.")
            return

        print("\n" + "="*55)
        print(f"🆔 TEACHER ID: {teacher_data['teacher_id']}")
        print(f"👤 Name      : {teacher_data['name']}")
        print(f"🚻 Gender    : {teacher_data['gender']}")
        print(f"📞 Contact   : {teacher_data['contact']}")
        print(f"✉️  Email     : {teacher_data['email']}")
        print(f"🏢 Department: {teacher_data['department']}")
        print(f"🎓 Qualification: {teacher_data['qualification']}")
        print(f"📅 Date Joined: {teacher_data['date_joined']}")
        print("="*55 + "\n")