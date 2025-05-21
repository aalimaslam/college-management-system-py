from database import Database
import datetime

class Library:
    def __init__(self, db):
        """Initialize Library class with database connection"""
        self.db = db
    
    def add_book(self, title, author, isbn, publisher, year_published, total_copies):
        """Add a new book to the library"""
        # Check if ISBN already exists
        exists = self.db.fetch_one("SELECT isbn FROM books WHERE isbn = ?", (isbn,))
        if exists:
            print(f"Error: Book with ISBN {isbn} already exists.")
            return False
        
        query = """
        INSERT INTO books (title, author, isbn, publisher, year_published, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # Initially, available copies equals total copies
        params = (title, author, isbn, publisher, year_published, total_copies, total_copies)
        
        if self.db.execute_query(query, params):
            print(f"Book '{title}' added successfully.")
            return True
        return False
    
    def update_book(self, book_id, **kwargs):
        """Update book information"""
        valid_fields = ['title', 'author', 'isbn', 'publisher', 'year_published', 'total_copies']
        
        # Filter out invalid fields
        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
        
        if not updates:
            print("No valid fields to update.")
            return False
        
        # Special handling for total_copies to adjust available_copies accordingly
        if 'total_copies' in updates:
            book = self.get_book(book_id)
            if book:
                current_total = book['total_copies']
                current_available = book['available_copies']
                new_total = updates['total_copies']
                
                # Calculate books currently issued
                issued = current_total - current_available
                
                # Ensure the new total is not less than books currently issued
                if new_total < issued:
                    print(f"Error: Cannot set total copies to {new_total} as {issued} books are currently issued.")
                    return False
                
                # Update available copies accordingly
                new_available = new_total - issued
                updates['available_copies'] = new_available
        
        # Construct update query
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE books SET {set_clause} WHERE book_id = ?"
        
        # Parameters for the query
        params = list(updates.values()) + [book_id]
        
        if self.db.execute_query(query, tuple(params)):
            print(f"Book ID {book_id} updated successfully.")
            return True
        return False
    
    def delete_book(self, book_id):
        """Delete a book from the library"""
        # Check if book exists and if it has any issues
        book = self.get_book(book_id)
        if not book:
            print(f"Error: Book with ID {book_id} does not exist.")
            return False
        
        # Check if book is currently issued
        if book['total_copies'] != book['available_copies']:
            print(f"Error: Cannot delete book ID {book_id} as it has issues pending.")
            return False
        
        query = "DELETE FROM books WHERE book_id = ?"
        if self.db.execute_query(query, (book_id,)):
            print(f"Book ID {book_id} deleted successfully.")
            return True
        return False
    
    def get_book(self, book_id):
        """Get book details by ID"""
        query = "SELECT * FROM books WHERE book_id = ?"
        book = self.db.fetch_one(query, (book_id,))
        
        if not book:
            print(f"No book found with ID {book_id}.")
            return None
        
        # Convert to dictionary for easier access
        columns = ["book_id", "title", "author", "isbn", "publisher", 
                  "year_published", "total_copies", "available_copies"]
        return dict(zip(columns, book))
    
    def get_all_books(self):
        """Get all books in the library"""
        query = "SELECT * FROM books ORDER BY title"
        books = self.db.fetch_all(query)
        
        if not books:
            print("No books found in the library.")
            return []
        
        # Convert to list of dictionaries
        columns = ["book_id", "title", "author", "isbn", "publisher", 
                  "year_published", "total_copies", "available_copies"]
        return [dict(zip(columns, book)) for book in books]
    
    def search_books(self, search_term):
        """Search for books by title, author, or ISBN"""
        query = """
        SELECT * FROM books 
        WHERE title ILIKE ? OR author ILIKE ? OR isbn ILIKE ? OR publisher ILIKE ?
        ORDER BY title
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern)
        books = self.db.fetch_all(query, params)
        
        if not books:
            print(f"No books found matching '{search_term}'.")
            return []
        
        # Convert to list of dictionaries
        columns = ["book_id", "title", "author", "isbn", "publisher", 
                  "year_published", "total_copies", "available_copies"]
        return [dict(zip(columns, book)) for book in books]
    
    def issue_book(self, book_id, student_id):
        """Issue a book to a student"""
        # Check if book exists and is available
        book = self.get_book(book_id)
        if not book:
            return False
        
        if book['available_copies'] <= 0:
            print(f"Error: No copies of book '{book['title']}' are available.")
            return False
        
        # Check if student exists
        student_exists = self.db.fetch_one("SELECT student_id FROM students WHERE student_id = ?", (student_id,))
        if not student_exists:
            print(f"Error: Student with ID {student_id} does not exist.")
            return False
        
        # Check if student already has this book
        already_issued = self.db.fetch_one("""
            SELECT issue_id FROM book_issues 
            WHERE book_id = ? AND student_id = ? AND status = 'issued'
        """, (book_id, student_id))
        
        if already_issued:
            print(f"Error: This book is already issued to this student.")
            return False
        
        # Issue the book
        issue_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
        
        query = """
        INSERT INTO book_issues (book_id, student_id, issue_date, return_date, status)
        VALUES (?, ?, ?, ?, 'issued')
        """
        params = (book_id, student_id, issue_date, return_date)
        
        if self.db.execute_query(query, params):
            # Update available copies
            update_query = "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?"
            if self.db.execute_query(update_query, (book_id,)):
                print(f"Book '{book['title']}' issued to student ID {student_id} successfully.")
                print(f"Return Date: {return_date}")
                return True
        
        return False
    
    def return_book(self, issue_id):
        """Process a book return"""
        # Get issue details
        query = "SELECT * FROM book_issues WHERE issue_id = ?"
        issue = self.db.fetch_one(query, (issue_id,))
        
        if not issue:
            print(f"Error: Issue ID {issue_id} not found.")
            return False
        
        # Convert to dictionary for easier access
        issue_columns = ["issue_id", "book_id", "student_id", "issue_date", 
                         "return_date", "actual_return_date", "fine_amount", "status"]
        issue_data = dict(zip(issue_columns, issue))
        
        if issue_data['status'] == 'returned':
            print("This book has already been returned.")
            return False
        
        # Process return
        actual_return_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Calculate fine if late
        fine_amount = 0
        if issue_data['return_date']:
            return_date = datetime.datetime.strptime(issue_data['return_date'], "%Y-%m-%d")
            actual_date = datetime.datetime.strptime(actual_return_date, "%Y-%m-%d")
            
            if actual_date > return_date:
                days_late = (actual_date - return_date).days
                fine_amount = days_late * 2  # $2 per day

        # Update issue record
        update_issue_query = """
        UPDATE book_issues 
        SET actual_return_date = ?, fine_amount = ?, status = 'returned'
        WHERE issue_id = ?
        """
        if self.db.execute_query(update_issue_query, (actual_return_date, fine_amount, issue_id)):
            # Update book availability
            update_book_query = "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?"
            if self.db.execute_query(update_book_query, (issue_data['book_id'],)):
                print(f"Book ID {issue_data['book_id']} returned successfully.")
                if fine_amount > 0:
                    print(f"Fine: ${fine_amount}")
                return True
        
        return False

