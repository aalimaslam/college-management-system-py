from database import Database
from modules.students import Student
from modules.admin import Administrator
from modules.teachers import Teacher
from modules.library import Library
from modules.events import Event
from modules.feedback import Feedback
from modules.ai import generateResponse
from modules.courses import Course

class College:
    def __init__(self, db_name="college_management.db"):
        """Initialize the College Management System"""
        self.db = Database(db_name)
        self.student = Student(self.db)
        self.admin = Administrator(self.db)
        self.teacher = Teacher(self.db)
        self.library = Library(self.db)
        self.event = Event(self.db)
        self.feedback = Feedback(self.db)
        self.course = Course(self.db)
        
    def close(self):
        """Close database connection"""
        self.db.close()

    def run_student_module(self):
        """Run the student management module"""
        while True:
            print("\n===== STUDENT MANAGEMENT =====")
            print("1. Add New Student")
            print("2. Update Student")
            print("3. Delete Student")
            print("4. View Student")
            print("5. View All Students")
            print("6. Search Students")
            print("0. Return to Main Menu")
            
            choice = input("Enter your choice (0-6): ")
            
            if choice == '1':
                name = input("Enter student name: ")
                age = int(input("Enter age: "))
                gender = input("Enter gender: ")
                contact = input("Enter contact number: ")
                email = input("Enter email: ")
                address = input("Enter address: ")
                course = input("Enter course: ")
                semester = int(input("Enter semester: "))
                
                self.student.add_student(name, age, gender, contact, email, address, course, semester)
                
            elif choice == '2':
                student_id = int(input("Enter student ID to update: "))
                student_data = self.student.get_student(student_id)
                
                if student_data:
                    self.student.display_student(student_data)
                    print("\nEnter new details (leave blank to keep current value):")
                    
                    name = input(f"Name [{student_data['name']}]: ") or None
                    age_str = input(f"Age [{student_data['age']}]: ") or None
                    age = int(age_str) if age_str else None
                    gender = input(f"Gender [{student_data['gender']}]: ") or None
                    contact = input(f"Contact [{student_data['contact']}]: ") or None
                    email = input(f"Email [{student_data['email']}]: ") or None
                    address = input(f"Address [{student_data['address']}]: ") or None
                    course = input(f"Course [{student_data['course']}]: ") or None
                    semester_str = input(f"Semester [{student_data['semester']}]: ") or None
                    semester = int(semester_str) if semester_str else None
                    
                    self.student.update_student(
                        student_id, name=name, age=age, gender=gender, 
                        contact=contact, email=email, address=address, 
                        course=course, semester=semester
                    )
            
            elif choice == '3':
                student_id = int(input("Enter student ID to delete: "))
                confirm = input(f"Are you sure you want to delete student ID {student_id}? (y/n): ")
                if confirm.lower() == 'y':
                    self.student.delete_student(student_id)
            
            elif choice == '4':
                student_id = int(input("Enter student ID to view: "))
                student_data = self.student.get_student(student_id)
                if student_data:
                    self.student.display_student(student_data)
            
            elif choice == '5':
                students = self.student.get_all_students()
                for student in students:
                    self.student.display_student(student)
            
            elif choice == '6':
                search_term = input("Enter search term: ")
                students = self.student.search_students(search_term)
                for student in students:
                    self.student.display_student(student)
            
            elif choice == '0':
                break
            
            else:
                print("Invalid choice. Please try again.")

    def run_admin_module(self):
        """Run the administrator management module"""
        while True:
            print("\n===== ADMINISTRATOR MANAGEMENT =====")
            print("1. Add New Administrator")
            print("2. Update Administrator")
            print("3. Delete Administrator")
            print("4. View Administrator")
            print("5. View All Administrators")
            print("6. Search Administrators")
            print("0. Return to Main Menu")
            
            choice = input("Enter your choice (0-6): ")
            
            if choice == '1':
                name = input("Enter administrator name: ")
                contact = input("Enter contact number: ")
                email = input("Enter email: ")
                position = input("Enter position: ")
                department = input("Enter department: ")
                
                self.admin.add_admin(name, contact, email, position, department)
            
            elif choice == '2':
                admin_id = int(input("Enter administrator ID to update: "))
                admin_data = self.admin.get_admin(admin_id)
                
                if admin_data:
                    self.admin.display_admin(admin_data)
                    print("\nEnter new details (leave blank to keep current value):")
                    
                    name = input(f"Name [{admin_data['name']}]: ") or None
                    contact = input(f"Contact [{admin_data['contact']}]: ") or None
                    email = input(f"Email [{admin_data['email']}]: ") or None
                    position = input(f"Position [{admin_data['position']}]: ") or None
                    department = input(f"Department [{admin_data['department']}]: ") or None
                    
                    self.admin.update_admin(
                        admin_id, name=name, contact=contact, email=email,
                        position=position, department=department
                    )
            
            elif choice == '3':
                admin_id = int(input("Enter administrator ID to delete: "))
                confirm = input(f"Are you sure you want to delete administrator ID {admin_id}? (y/n): ")
                if confirm.lower() == 'y':
                    self.admin.delete_admin(admin_id)
            
            elif choice == '4':
                admin_id = int(input("Enter administrator ID to view: "))
                admin_data = self.admin.get_admin(admin_id)
                if admin_data:
                    self.admin.display_admin(admin_data)
            
            elif choice == '5':
                admins = self.admin.get_all_admins()
                for admin in admins:
                    self.admin.display_admin(admin)
            
            elif choice == '6':
                search_term = input("Enter search term: ")
                admins = self.admin.search_admins(search_term)
                for admin in admins:
                    self.admin.display_admin(admin)
            
            elif choice == '0':
                break
            
            else:
                print("Invalid choice. Please try again.")

    def run_teacher_module(self):
        """Run the teacher management module"""
        while True:
            print("\n===== TEACHER MANAGEMENT =====")
            print("1. Add New Teacher")
            print("2. Update Teacher")
            print("3. Delete Teacher")
            print("4. View Teacher")
            print("5. View All Teachers")
            print("6. Search Teachers")
            print("0. Return to Main Menu")
            
            choice = input("Enter your choice (0-6): ")
            
            if choice == '1':
                name = input("Enter teacher name: ")
                gender = input("Enter gender: ")
                contact = input("Enter contact number: ")
                email = input("Enter email: ")
                department = input("Enter department: ")
                qualification = input("Enter qualification: ")
                
                self.teacher.add_teacher(name, gender, contact, email, department, qualification)
            
            elif choice == '2':
                teacher_id = int(input("Enter teacher ID to update: "))
                teacher_data = self.teacher.get_teacher(teacher_id)
                
                if teacher_data:
                    self.teacher.display_teacher(teacher_data)
                    print("\nEnter new details (leave blank to keep current value):")
                    
                    name = input(f"Name [{teacher_data['name']}]: ") or None
                    gender = input(f"Gender [{teacher_data['gender']}]: ") or None
                    contact = input(f"Contact [{teacher_data['contact']}]: ") or None
                    email = input(f"Email [{teacher_data['email']}]: ") or None
                    department = input(f"Department [{teacher_data['department']}]: ") or None
                    qualification = input(f"Qualification [{teacher_data['qualification']}]: ") or None
                    
                    self.teacher.update_teacher(
                        teacher_id, name=name, gender=gender, contact=contact,
                        email=email, department=department, qualification=qualification
                    )
            
            elif choice == '3':
                teacher_id = int(input("Enter teacher ID to delete: "))
                confirm = input(f"Are you sure you want to delete teacher ID {teacher_id}? (y/n): ")
                if confirm.lower() == 'y':
                    self.teacher.delete_teacher(teacher_id)
            
            elif choice == '4':
                teacher_id = int(input("Enter teacher ID to view: "))
                teacher_data = self.teacher.get_teacher(teacher_id)
                if teacher_data:
                    self.teacher.display_teacher(teacher_data)
            
            elif choice == '5':
                teachers = self.teacher.get_all_teachers()
                for teacher in teachers:
                    self.teacher.display_teacher(teacher)
            
            elif choice == '6':
                search_term = input("Enter search term: ")
                teachers = self.teacher.search_teachers(search_term)
                for teacher in teachers:
                    self.teacher.display_teacher(teacher)
            
            elif choice == '0':
                break
            
            else:
                print("Invalid choice. Please try again.")

    def run_library_module(self):
        """Run the library management module"""
        while True:
            print("\n===== LIBRARY MANAGEMENT =====")
            print("1. Add New Book")
            print("2. Update Book")
            print("3. Delete Book")
            print("4. View Book")
            print("5. View All Books")
            print("6. Search Books")
            print("7. Issue Book")
            print("8. Return Book")
            print("0. Return to Main Menu")
            
            choice = input("Enter your choice (0-8): ")

            if choice == '1':
                title = input("Enter book title: ")
                author = input("Enter author name: ")
                isbn = input("Enter ISBN: ")
                publisher = input("Enter publisher: ")
                year = input("Enter publication year: ")
                quantity = int(input("Enter quantity: "))

                self.library.add_book(title, author, isbn, publisher, year, quantity)

            elif choice == '2':
                book_id = int(input("Enter book ID to update: "))
                book_data = self.library.get_book(book_id)

                if book_data:
                    self.library.display_book(book_data)
                    print("\nEnter new details (leave blank to keep current value):")

                    title = input(f"Title [{book_data['title']}]: ") or None
                    author = input(f"Author [{book_data['author']}]: ") or None
                    isbn = input(f"ISBN [{book_data['isbn']}]: ") or None
                    publisher = input(f"Publisher [{book_data['publisher']}]: ") or None
                    year = input(f"Year [{book_data['year']}]: ") or None
                    quantity_str = input(f"Quantity [{book_data['quantity']}]: ") or None
                    quantity = int(quantity_str) if quantity_str else None

                    self.library.update_book(
                        book_id, title=title, author=author, isbn=isbn,
                        publisher=publisher, year=year, quantity=quantity
                    )

            elif choice == '3':
                book_id = int(input("Enter book ID to delete: "))
                confirm = input(f"Are you sure you want to delete book ID {book_id}? (y/n): ")
                if confirm.lower() == 'y':
                    self.library.delete_book(book_id)

            elif choice == '4':
                book_id = int(input("Enter book ID to view: "))
                book_data = self.library.get_book(book_id)
                if book_data:
                    self.library.display_book(book_data)

            elif choice == '5':
                books = self.library.get_all_books()
                for book in books:
                    self.library.display_book(book)

            elif choice == '6':
                search_term = input("Enter search term: ")
                books = self.library.search_books(search_term)
                for book in books:
                    self.library.display_book(book)

            elif choice == '7':
                book_id = int(input("Enter book ID to issue: "))
                student_id = int(input("Enter student ID to issue to: "))
                self.library.issue_book(book_id, student_id)

            elif choice == '8':
                book_id = int(input("Enter book ID to return: "))
                student_id = int(input("Enter student ID returning the book: "))
                self.library.return_book(book_id, student_id)

            elif choice == '0':
                break

            else:
                print("Invalid choice. Please try again.")

    def run_ai_module(self):
        """Run the AI module"""
        while True:
            print("\n===== AI SPACE =====")
            print("1. Run the AI Space")
            print("0. Go Back")
            choice  = input("Enter your choice (0-1) ")

            if choice == '1':
                global response
                prompt = input("Enter the details you want to know : ")
                if(len(prompt) < 5):
                    print('Enter more comprehensive prompt')
                else : 
                    response = generateResponse(prompt)
                print(response)
            elif choice == '0':
                break
            else :
                print("Invalid choice. Please try again.")
    
    def run_event_module(self):
        """Run the event management module"""
        while True:
            print("\n===== EVENT MANAGEMENT =====")
            print("1. Add New Event")
            print("2. Update Event")
            print("3. Delete Event")
            print("4. View Event")
            print("5. View All Events")
            print("6. Search Events")
            print("0. Return to Main Menu")
            
            choice = input("Enter your choice (0-6): ")
            
            if choice == '1':
                name = input("Enter event name: ")
                date = input("Enter event date (YYYY-MM-DD): ")
                time = input("Enter event time (HH:MM): ")
                venue = input("Enter venue: ")
                description = input("Enter event description: ")
                self.event.add_event(name, date, time, venue, description)

            elif choice == '2':
                event_id = int(input("Enter event ID to update: "))
                event_data = self.event.get_event(event_id)

                if event_data:
                    self.event.display_event(event_data)
                    print("\nEnter new details (leave blank to keep current value):")

                    name = input(f"Name [{event_data['name']}]: ") or None
                    date = input(f"Date [{event_data['date']}]: ") or None
                    time = input(f"Time [{event_data['time']}]: ") or None
                    venue = input(f"Venue [{event_data['venue']}]: ") or None
                    description = input(f"Description [{event_data['description']}]: ") or None
                    
                    self.event.update_event(
                        event_id, name=name, date=date, time=time,
                        venue=venue, description=description
                    )

            elif choice == '3':
                event_id = int(input("Enter event ID to delete: "))
                confirm = input(f"Are you sure you want to delete event ID {event_id}? (y/n): ")
                if confirm.lower() == 'y':
                    self.event.delete_event(event_id)

            elif choice == '4':
                event_id = int(input("Enter event ID to view: "))
                event_data = self.event.get_event(event_id)
                if event_data:
                    self.event.display_event(event_data)

            elif choice == '5':
                events = self.event.get_all_events()
                for event in events:
                    self.event.display_event(event)

            elif choice == '6':
                search_term = input("Enter search term: ")
                events = self.event.search_events(search_term)
                for event in events:
                    self.event.display_event(event)

            elif choice == '0':
                break

            else:
                print("Invalid choice. Please try again.")

    def run_feedback_module(self):
        """Run the feedback management module"""
        while True:
            print("\n===== FEEDBACK MANAGEMENT =====")
            print("1. Submit Feedback")
            print("2. Update Feedback")
            print("3. Delete Feedback")
            print("4. View Feedback by ID")
            print("5. View Feedback for a Teacher")
            print("6. View Feedback by a Student")
            print("7. View Feedback for a Course")
            print("8. Calculate Average Rating for Teacher")
            print("0. Return to Main Menu")

            choice = input("Enter your choice (0-8): ")

            if choice == '1':
                student_id = int(input("Enter student ID: "))
                teacher_id = int(input("Enter teacher ID: "))
                course = input("Enter course name: ")
                try:
                    rating = int(input("Enter rating (1-5): "))
                except ValueError:
                    print("Invalid rating. Must be an integer.")
                    continue
                comments = input("Enter comments: ")
                self.feedback.submit_feedback(student_id, teacher_id, course, rating, comments)

            elif choice == '2':
                feedback_id = int(input("Enter feedback ID to update: "))
                try:
                    rating = input("Enter new rating (1-5, or leave blank): ")
                    rating = int(rating) if rating else None
                except ValueError:
                    print("Invalid rating.")
                    continue
                comments = input("Enter new comments (or leave blank): ")
                comments = comments if comments else None
                self.feedback.update_feedback(feedback_id, rating=rating, comments=comments)

            elif choice == '3':
                feedback_id = int(input("Enter feedback ID to delete: "))
                confirm = input("Are you sure you want to delete this feedback? (y/n): ")
                if confirm.lower() == 'y':
                    self.feedback.delete_feedback(feedback_id)

            elif choice == '4':
                feedback_id = int(input("Enter feedback ID to view: "))
                data = self.feedback.get_feedback(feedback_id)
                self.feedback.display_feedback(data)

            elif choice == '5':
                teacher_id = int(input("Enter teacher ID: "))
                feedbacks = self.feedback.get_teacher_feedback(teacher_id)
                for fb in feedbacks:
                    print(f"\nFeedback ID: {fb[0]}")
                    print(f"Student: {fb[1]}")
                    print(f"Course: {fb[2]}")
                    print(f"Rating: {fb[3]}/5")
                    print(f"Comments: {fb[4]}")
                    print(f"Date: {fb[5]}")
                    print("-" * 40)

            elif choice == '6':
                student_id = int(input("Enter student ID: "))
                feedbacks = self.feedback.get_student_feedback(student_id)
                for fb in feedbacks:
                    print(f"\nFeedback ID: {fb[0]}")
                    print(f"Teacher: {fb[1]}")
                    print(f"Course: {fb[2]}")
                    print(f"Rating: {fb[3]}/5")
                    print(f"Comments: {fb[4]}")
                    print(f"Date: {fb[5]}")
                    print("-" * 40)

            elif choice == '7':
                course = input("Enter course name: ")
                feedbacks = self.feedback.get_course_feedback(course)
                for fb in feedbacks:
                    print(f"\nFeedback ID: {fb[0]}")
                    print(f"Student: {fb[1]}")
                    print(f"Teacher: {fb[2]}")
                    print(f"Rating: {fb[3]}/5")
                    print(f"Comments: {fb[4]}")
                    print(f"Date: {fb[5]}")
                    print("-" * 40)

            elif choice == '8':
                teacher_id = int(input("Enter teacher ID: "))
                avg = self.feedback.calculate_teacher_rating(teacher_id)
                print(f"Average Rating for Teacher {teacher_id}: {avg}/5")

            elif choice == '0':
                break

            else:
                print("Invalid choice. Please try again.")
    
    def run_course_module(self):
        """Run the course management module"""
        while True:
            print("\n===== COURSE MANAGEMENT =====")
            print("1. Add Course")
            print("2. Update Course")
            print("3. Delete Course")
            print("4. View Course by ID")
            print("5. View All Courses")
            print("0. Return to Main Menu")

            choice = input("Enter your choice (0-5): ")

            if choice == '1':
                name = input("Enter course name: ")
                description = input("Enter course description: ")
                duration = input("Enter course duration: ")
                self.course.add_course(name, description, duration)

            elif choice == '2':
                try:
                    course_id = int(input("Enter course ID to update: "))
                    name = input("Enter new course name (or leave blank): ")
                    description = input("Enter new description (or leave blank): ")
                    name = name if name.strip() else None
                    description = description if description.strip() else None
                    self.course.update_course(course_id, name, description)
                except ValueError:
                    print("Invalid input. Course ID must be an integer.")

            elif choice == '3':
                try:
                    print(self.course.get_all_courses())
                    course_id = int(input("Enter course ID to delete: "))
                    confirm = input("Are you sure you want to delete this course? (y/n): ")
                    if confirm.lower() == 'y':
                        self.course.delete_course(course_id)
                except ValueError:
                    print("Invalid input. Course ID must be an integer.")

            elif choice == '4':
                try:
                    course_id = int(input("Enter course ID to view: "))
                    course = self.course.get_course(course_id)
                    self.course.display_course(course)
                except ValueError:
                    print("Invalid input. Course ID must be an integer.")

            elif choice == '5':
                all_courses = self.course.get_all_courses()
                if not all_courses:
                    print("No courses found.")
                for c in all_courses:
                    course_dict = {
                        "course_id": c[0],
                        "course_name": c[1],
                        "description": c[2]
                    }
                    self.course.display_course(course_dict)

            elif choice == '0':
                break
            else:
                print("Invalid choice. Please try again.")            