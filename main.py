from modules.college import College
from database import Database

if __name__ == "__main__":
    college = College()
    db = Database()
    db.connect()
    db.create_tables()
    db.close()

    while True:
        try:
            print("\n" + "="*60)
            print(" " * 13 + "🎓 COLLEGE MANAGEMENT SYSTEM 🎓")
            print("="*60)
            print(" 1. 👨‍🎓 Student Management")
            print(" 2. 👨‍💼 Administrator Management")
            print(" 3. 👩‍🏫 Teacher Management")
            print(" 4. 📚 Library Management")
            print(" 5. 🎉 Event Management")
            print(" 6. 📝 Feedback Management")
            print(" 7. 📖 Course Management")
            print(" 8. 🤖 AI Space")
            print(" 9. 📊 Analytics")
            print(" 0. 🚪 Exit")
            print("="*60)

            choice = input("Enter your choice (0-9): ")

            if choice == '1':
                college.run_student_module()
            elif choice == '2':
                college.run_admin_module()
            elif choice == '3':
                college.run_teacher_module()
            elif choice == '4':
                college.run_library_module()
            elif choice == '5':
                college.run_event_module()
            elif choice == '6':
                college.run_feedback_module()
            elif choice == '7':
                college.run_course_module()
            elif choice == '8':
                college.run_ai_module()
            elif choice == '9':
                college.run_analytics_module()
            elif choice == '0':
                print("\n🚪 Exiting system... Goodbye!\n")
                college.close()
                break
            else:
                print("❌ Invalid choice. Please try again.")
        except Exception as e:
            print(f"\n⚠️  An error occurred: {e}\nReturning to main menu...")