from database import Database
import datetime

class Event:
    def __init__(self, db):
        """Initialize Event class with database connection"""
        self.db = db
    
    def add_event(self, name, description, date, time, venue, organizer):
        """Add a new event to the database"""
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Error: Date must be in YYYY-MM-DD format.")
            return False
            
        # Default status is 'upcoming'
        query = """
        INSERT INTO events (name, description, date, time, venue, organizer, status)
        VALUES (?, ?, ?, ?, ?, ?, 'upcoming')
        """
        params = (name, description, date, time, venue, organizer)
        
        if self.db.execute_query(query, params):
            print(f"Event '{name}' added successfully.")
            return True
        return False

    def update_event(self, event_id, **kwargs):
        """Update event information"""
        self.get_all_events()
        valid_fields = ['name', 'description', 'date', 'time', 'venue', 'organizer', 'status']

        if 'organizer' in kwargs:
            org = kwargs['organizer']
            if org is None or str(org).strip() == '':
                kwargs['organizer'] = None

        updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}

        if not updates:
            print("No valid fields to update.")
            return False

        # Validate date format if provided
        if 'date' in updates:
            try:
                datetime.datetime.strptime(updates['date'], "%Y-%m-%d")
            except ValueError:
                print("Error: Date must be in YYYY-MM-DD format.")
                return False

        # Validate status if provided
        if 'status' in updates and updates['status'] not in ['upcoming', 'ongoing', 'completed', 'cancelled']:
            print("Error: Status must be one of 'upcoming', 'ongoing', 'completed', or 'cancelled'.")
            return False

        # Construct update query
        set_clause = ", ".join([f"{field} = ?" for field in updates.keys()])
        query = f"UPDATE events SET {set_clause} WHERE event_id = ?"

        # Parameters for the query
        params = list(updates.values()) + [event_id]


        if self.db.execute_query(query, tuple(params)):
            print(f"Event ID {event_id} updated successfully.")
            return True
        return False  
    def cancel_event(self, event_id):
        """Cancel an event"""
        self.get_all_events()
        event = self.get_event(event_id)
        if not event:
            return False
        
        if event['status'] == 'completed':
            print("Cannot cancel an event that has already completed.")
            return False
        
        if event['status'] == 'cancelled':
            print("This event is already cancelled.")
            return True
        
        query = "UPDATE events SET status = 'cancelled' WHERE event_id = ?"
        if self.db.execute_query(query, (event_id,)):
            print(f"Event '{event['name']}' cancelled successfully.")
            return True
        return False
    
    def delete_event(self, event_id):
        """Delete an event from the database"""
        # Check if event exists
        self.get_all_events()

        exists = self.db.fetch_one("SELECT event_id FROM events WHERE event_id = ?", (event_id,))
        if not exists:
            print(f"Error: Event with ID {event_id} does not exist.")
            return False
        
        query = "DELETE FROM events WHERE event_id = ?"
        if self.db.execute_query(query, (event_id,)):
            print(f"Event ID {event_id} deleted successfully.")
            return True
        return False
    
    def get_event(self, event_id):
        """Get event details by ID"""
        query = "SELECT * FROM events WHERE event_id = ?"
        event = self.db.fetch_one(query, (event_id,))
        
        if not event:
            print(f"No event found with ID {event_id}.")
            return None
        
        # Convert to dictionary for easier access
        columns = ["event_id", "name", "description", "date", "time", "venue", "organizer", "status"]
        return dict(zip(columns, event))
    
    def get_all_events(self, status=None):
        """Get all events, optionally filtered by status"""
        if status:
            if status not in ['upcoming', 'ongoing', 'completed', 'cancelled', 'all']:
                print("Invalid status. Must be 'upcoming', 'ongoing', 'completed', 'cancelled', or 'all'.")
                return []
                
            if status == 'all':
                query = "SELECT * FROM events ORDER BY date"
                params = ()
            else:
                query = "SELECT * FROM events WHERE status = ? ORDER BY date"
                params = (status,)
        else:
            # Default to showing non-cancelled events
            query = "SELECT * FROM events WHERE status != 'cancelled' ORDER BY date"
            params = ()
            
        events = self.db.fetch_all(query, params)
        
        if not events:
            status_msg = f" with status '{status}'" if status and status != 'all' else ""
            print(f"No events found{status_msg}.")
            return []
        
        # Convert to list of dictionaries
        columns = ["event_id", "name", "description", "date", "time", "venue", "organizer", "status"]
        return [dict(zip(columns, event)) for event in events]
    
    def search_events(self, search_term):
        """Search for events by name, description, venue, or organizer"""
        query = """
        SELECT * FROM events 
        WHERE name ILIKE ? OR description ILIKE ? OR venue ILIKE ? OR organizer ILIKE ?
        ORDER BY date
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern)
        events = self.db.fetch_all(query, params)
        
        if not events:
            print(f"No events found matching '{search_term}'.")
            return []
        
        # Convert to list of dictionaries
        columns = ["event_id", "name", "description", "date", "time", "venue", "organizer", "status"]
        return [dict(zip(columns, event)) for event in events]
    
    def display_event(self, event_data):
        """Display event information in a formatted way"""
        if not event_data:
            return

        print("\n" + "="*50)
        print(f"EVENT ID: {event_data['event_id']}")
        print(f"Name: {event_data['name']}")
        print(f"Description: {event_data['description']}")
        print(f"Date: {event_data['date']}")
        print(f"Time: {event_data['time']}")
        print(f"Venue: {event_data['venue']}")
        # Fix: Handle missing or None organizer gracefully
        organizer = event_data.get('organizer', '')
        if organizer is None or str(organizer).strip() == '':
            print("Organizer: Not specified")
        else:
            print(f"Organizer: {organizer}")
        print(f"Status: {event_data['status']}")
        print("="*50 + "\n")
    
    def update_event_statuses(self):
        """
        Update event statuses based on the current date
        - Events with past dates are marked as 'completed'
        - Events with current date are marked as 'ongoing'
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Update past events to completed
        past_query = """
        UPDATE events 
        SET status = 'completed' 
        WHERE date < ? AND status = 'upcoming'
        """
        self.db.execute_query(past_query, (today,))
        
        # Update current events to ongoing
        current_query = """
        UPDATE events 
        SET status = 'ongoing' 
        WHERE date = ? AND status = 'upcoming'
        """
        self.db.execute_query(current_query, (today,))
        
        return True