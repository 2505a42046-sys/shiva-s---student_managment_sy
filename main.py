import csv
import os

# ================= CONFIGURATION =================

FILE_NAME = "students.csv"

FIELDS = ["student_id", "name", "age", "course", "marks", "grade"]

USERNAME = "admin"
PASSWORD = "admin123"

students = []


# ================= LOGIN =================

def login():
    print("\n========== STUDENT MANAGEMENT SYSTEM ==========")

    for attempt in range(3):
        username = input("Username: ").strip()
        password = input("Password: ")

        if username == USERNAME and password == PASSWORD:
            print("\nLogin successful!")
            return True

        print("Invalid username or password.")

    print("Maximum login attempts exceeded.")
    return False


# ================= CALCULATE GRADE =================

def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"


# ================= FIND STUDENT =================

def find_student(student_id):
    for student in students:
        if student["student_id"] == student_id:
            return student

    return None


# ================= ADD STUDENT =================

def add_student():
    print("\n========== ADD STUDENT ==========")

    student_id = input("Enter Student ID: ").strip()

    if not student_id:
        print("Student ID cannot be empty.")
        return

    if find_student(student_id):
        print("Student ID already exists.")
        return

    name = input("Enter Name: ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    try:
        age = int(input("Enter Age: "))

        if age <= 0:
            print("Age must be positive.")
            return

        course = input("Enter Course: ").strip()

        if not course:
            print("Course cannot be empty.")
            return

        marks = float(input("Enter Marks (0-100): "))

        if not 0 <= marks <= 100:
            print("Marks must be between 0 and 100.")
            return

        student = {
            "student_id": student_id,
            "name": name,
            "age": age,
            "course": course,
            "marks": marks,
            "grade": calculate_grade(marks)
        }

        students.append(student)

        print("\nStudent added successfully!")
        print(f"Grade: {student['grade']}")
        print("Remember to save your changes using the Save to CSV option.")

    except ValueError:
        print("Invalid input. Age must be an integer and marks must be numeric.")


# ================= DISPLAY STUDENTS =================

def display_students():
    print("\n========== STUDENT RECORDS ==========")

    if not students:
        print("No student records found.")
        return

    print("-" * 100)
    print(
        f"{'ID':<12}"
        f"{'Name':<22}"
        f"{'Age':<8}"
        f"{'Course':<20}"
        f"{'Marks':<12}"
        f"{'Grade':<10}"
    )
    print("-" * 100)

    for student in students:
        print(
            f"{student['student_id']:<12}"
            f"{student['name']:<22}"
            f"{student['age']:<8}"
            f"{student['course']:<20}"
            f"{float(student['marks']):<12.2f}"
            f"{student['grade']:<10}"
        )

    print("-" * 100)
    print(f"Total Students: {len(students)}")


# ================= SEARCH STUDENT =================

def search_student():
    print("\n========== SEARCH STUDENT ==========")

    student_id = input("Enter Student ID: ").strip()

    student = find_student(student_id)

    if student:
        print("\nStudent Found!")
        print(f"Student ID : {student['student_id']}")
        print(f"Name       : {student['name']}")
        print(f"Age        : {student['age']}")
        print(f"Course     : {student['course']}")
        print(f"Marks      : {float(student['marks']):.2f}")
        print(f"Grade      : {student['grade']}")
    else:
        print("Student not found.")


# ================= UPDATE STUDENT =================

def update_student():
    print("\n========== UPDATE STUDENT ==========")

    student_id = input("Enter Student ID: ").strip()

    student = find_student(student_id)

    if not student:
        print("Student not found.")
        return

    print("\nLeave a field empty to keep its current value.")

    new_name = input(f"Name [{student['name']}]: ").strip()

    if new_name:
        student["name"] = new_name

    new_age = input(f"Age [{student['age']}]: ").strip()

    if new_age:
        try:
            age = int(new_age)

            if age <= 0:
                print("Age must be positive.")
                return

            student["age"] = age

        except ValueError:
            print("Invalid age.")
            return

    new_course = input(f"Course [{student['course']}]: ").strip()

    if new_course:
        student["course"] = new_course

    new_marks = input(f"Marks [{student['marks']}]: ").strip()

    if new_marks:
        try:
            marks = float(new_marks)

            if not 0 <= marks <= 100:
                print("Marks must be between 0 and 100.")
                return

            student["marks"] = marks
            student["grade"] = calculate_grade(marks)

        except ValueError:
            print("Invalid marks.")
            return

    print("Student updated successfully!")
    print("Remember to save your changes using the Save to CSV option.")


# ================= DELETE STUDENT =================

def delete_student():
    print("\n========== DELETE STUDENT ==========")

    student_id = input("Enter Student ID: ").strip()

    student = find_student(student_id)

    if not student:
        print("Student not found.")
        return

    print(f"Student Name: {student['name']}")

    confirm = input("Are you sure you want to delete? (y/n): ").strip().lower()

    if confirm == "y":
        students.remove(student)
        print("Student deleted successfully!")
        print("Remember to save your changes using the Save to CSV option.")
    else:
        print("Deletion cancelled.")


# ================= SAVE TO CSV =================

def save_to_csv():
    print("\n========== SAVE TO CSV ==========")

    try:
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)

            writer.writeheader()
            writer.writerows(students)

        print(f"Records saved successfully to {FILE_NAME}.")

    except OSError as error:
        print(f"Error saving file: {error}")


# ================= LOAD CSV =================

def load_from_csv():
    global students

    print("\n========== LOAD CSV ==========")

    if not os.path.exists(FILE_NAME):
        print("CSV file does not exist. A new file will be created when you save.")
        return

    try:
        loaded_students = []
        seen_ids = set()

        with open(FILE_NAME, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None or not set(FIELDS).issubset(reader.fieldnames):
                print("Invalid CSV format. Required columns are missing.")
                return

            for row_number, row in enumerate(reader, start=2):
                try:
                    student_id = row["student_id"].strip()
                    name = row["name"].strip()
                    age = int(row["age"])
                    course = row["course"].strip()
                    marks = float(row["marks"])

                    if not student_id or not name or not course:
                        raise ValueError("Required fields are empty.")

                    if student_id in seen_ids:
                        raise ValueError("Duplicate student ID.")

                    if age <= 0:
                        raise ValueError("Age must be positive.")

                    if not 0 <= marks <= 100:
                        raise ValueError("Marks must be between 0 and 100.")

                    student = {
                        "student_id": student_id,
                        "name": name,
                        "age": age,
                        "course": course,
                        "marks": marks,
                        "grade": calculate_grade(marks)
                    }

                    loaded_students.append(student)
                    seen_ids.add(student_id)

                except (ValueError, TypeError, AttributeError, KeyError) as error:
                    print(f"Skipping invalid row {row_number}: {error}")

        # Replace current records only after processing the file.
        students = loaded_students

        print(f"Loaded {len(students)} student records.")

    except (OSError, csv.Error) as error:
        print(f"Error loading CSV: {error}")


# ================= REPORTS =================

def reports():
    print("\n========== STUDENT REPORTS ==========")

    if not students:
        print("No student records available.")
        return

    total_students = len(students)

    marks_list = [float(student["marks"]) for student in students]

    average_marks = sum(marks_list) / total_students

    highest_student = max(students, key=lambda student: float(student["marks"]))
    lowest_student = min(students, key=lambda student: float(student["marks"]))

    passed_students = sum(1 for mark in marks_list if mark >= 50)
    failed_students = total_students - passed_students

    print(f"Total Students : {total_students}")
    print(f"Average Marks  : {average_marks:.2f}")
    print(f"Passed         : {passed_students}")
    print(f"Failed         : {failed_students}")

    print(
        f"Highest Marks  : {highest_student['name']} "
        f"({highest_student['marks']})"
    )

    print(
        f"Lowest Marks   : {lowest_student['name']} "
        f"({lowest_student['marks']})"
    )

    print("\nGrade Distribution:")

    grade_counts = {}

    for student in students:
        grade = student["grade"]
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    for grade in ["A+", "A", "B", "C", "D", "F"]:
        print(f"Grade {grade}: {grade_counts.get(grade, 0)} student(s)")


# ================= MAIN MENU =================

def main_menu():
    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Add Student")
        print("2. Display Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Calculate Grade")
        print("7. Save to CSV")
        print("8. Load CSV")
        print("9. Reports")
        print("10. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_student()

        elif choice == "2":
            display_students()

        elif choice == "3":
            search_student()

        elif choice == "4":
            update_student()

        elif choice == "5":
            delete_student()

        elif choice == "6":
            calculate_grade_for_student()

        elif choice == "7":
            save_to_csv()

        elif choice == "8":
            load_from_csv()

        elif choice == "9":
            reports()

        elif choice == "10":
            print("\nSave changes before exiting if you haven't already.")
            confirm = input("Exit application? (y/n): ").strip().lower()

            if confirm == "y":
                print("Thank you for using Student Management System!")
                break

        else:
            print("Invalid choice. Please enter a number from 1 to 10.")


# ================= CALCULATE GRADE MENU =================

def calculate_grade_for_student():
    print("\n========== CALCULATE GRADE ==========")

    student_id = input("Enter Student ID: ").strip()

    student = find_student(student_id)

    if not student:
        print("Student not found.")
        return

    marks = float(student["marks"])
    grade = calculate_grade(marks)

    student["grade"] = grade

    print(f"Student Name: {student['name']}")
    print(f"Marks       : {marks:.2f}")
    print(f"Grade       : {grade}")


# ================= MAIN PROGRAM =================

def main():
    if not login():
        return

    # Load saved records when the application starts.
    load_from_csv()

    main_menu()


if __name__ == "__main__":
    main()
