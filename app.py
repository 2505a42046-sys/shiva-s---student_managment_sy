import streamlit as st
import pandas as pd
import os
from pathlib import Path

# ================= CONFIGURATION =================

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

FILE_NAME = Path(__file__).parent / "students.csv"

FIELDS = [
    "student_id",
    "name",
    "age",
    "course",
    "marks",
    "grade"
]

USERNAME = "admin"
PASSWORD = "admin123"


# ================= SESSION STATE =================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(columns=FIELDS)


# ================= GRADE CALCULATION =================

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
    return "F"


# ================= LOAD DATA =================

def load_data():
    if not FILE_NAME.exists():
        return pd.DataFrame(columns=FIELDS)

    try:
        df = pd.read_csv(FILE_NAME, dtype={"student_id": str})

        if not set(FIELDS).issubset(df.columns):
            st.error("CSV file has an invalid format.")
            return pd.DataFrame(columns=FIELDS)

        df = df[FIELDS].copy()

        df["student_id"] = df["student_id"].fillna("").astype(str).str.strip()
        df["name"] = df["name"].fillna("").astype(str).str.strip()
        df["course"] = df["course"].fillna("").astype(str).str.strip()
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df["marks"] = pd.to_numeric(df["marks"], errors="coerce")

        valid = (
            df["student_id"].ne("")
            & df["name"].ne("")
            & df["course"].ne("")
            & df["age"].notna()
            & df["marks"].notna()
            & df["age"].gt(0)
            & df["age"].eq(df["age"].astype("Int64"))
            & df["marks"].between(0, 100)
        )

        df = df.loc[valid].copy()

        if df["student_id"].duplicated().any():
            st.error("CSV contains duplicate student IDs.")
            return pd.DataFrame(columns=FIELDS)

        df["age"] = df["age"].astype(int)
        df["grade"] = df["marks"].apply(calculate_grade)

        return df.reset_index(drop=True)

    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Unable to load CSV: {error}")
        return pd.DataFrame(columns=FIELDS)


def save_data():
    try:
        st.session_state.students.to_csv(
            FILE_NAME,
            index=False,
            columns=FIELDS
        )
        return True

    except OSError as error:
        st.error(f"Unable to save data: {error}")
        return False


# ================= LOGIN =================

def login_page():
    st.title("🎓 Student Management System")
    st.write("Please log in to continue.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

        if submitted:
            if username == USERNAME and password == PASSWORD:
                st.session_state.logged_in = True
                st.session_state.students = load_data()
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ================= ADD STUDENT =================

def add_student():
    st.subheader("➕ Add Student")

    with st.form("add_student_form"):
        student_id = st.text_input("Student ID").strip()
        name = st.text_input("Student Name").strip()
        age = st.number_input(
            "Age", min_value=1, max_value=120, value=18
        )
        course = st.text_input("Course").strip()
        marks = st.number_input(
            "Marks", min_value=0.0, max_value=100.0, value=0.0
        )

        submitted = st.form_submit_button("Add Student")

        if submitted:
            df = st.session_state.students

            if not student_id or not name or not course:
                st.error("All fields are required.")

            elif df["student_id"].astype(str).eq(student_id).any():
                st.error("Student ID already exists.")

            else:
                new_student = pd.DataFrame([{
                    "student_id": student_id,
                    "name": name,
                    "age": int(age),
                    "course": course,
                    "marks": float(marks),
                    "grade": calculate_grade(marks)
                }])

                st.session_state.students = pd.concat(
                    [df, new_student],
                    ignore_index=True
                )

                if save_data():
                    st.success("Student added and saved successfully!")


# ================= DISPLAY STUDENTS =================

def display_students():
    st.subheader("📋 All Students")

    df = st.session_state.students

    if df.empty:
        st.info("No student records available.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.write(f"**Total Students:** {len(df)}")


# ================= SEARCH STUDENT =================

def search_student():
    st.subheader("🔎 Search Student")

    student_id = st.text_input(
        "Enter Student ID",
        key="search_student_id"
    ).strip()

    if st.button("Search"):
        df = st.session_state.students

        result = df[df["student_id"].astype(str) == student_id]

        if result.empty:
            st.warning("Student not found.")
        else:
            st.dataframe(result, use_container_width=True, hide_index=True)


# ================= UPDATE STUDENT =================

def update_student():
    st.subheader("✏️ Update Student")

    df = st.session_state.students

    if df.empty:
        st.info("No students available to update.")
        return

    student_id = st.selectbox(
        "Select Student ID",
        df["student_id"].astype(str).tolist(),
        key="update_student_id"
    )

    student = df[df["student_id"].astype(str) == student_id].iloc[0]

    with st.form("update_student_form"):
        name = st.text_input("Name", value=str(student["name"]))
        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=int(student["age"])
        )
        course = st.text_input("Course", value=str(student["course"]))
        marks = st.number_input(
            "Marks",
            min_value=0.0,
            max_value=100.0,
            value=float(student["marks"])
        )

        submitted = st.form_submit_button("Update Student")

        if submitted:
            if not name.strip() or not course.strip():
                st.error("Name and course cannot be empty.")
                return

            idx = df.index[df["student_id"].astype(str) == student_id][0]

            st.session_state.students.loc[idx, "name"] = name.strip()
            st.session_state.students.loc[idx, "age"] = int(age)
            st.session_state.students.loc[idx, "course"] = course.strip()
            st.session_state.students.loc[idx, "marks"] = float(marks)
            st.session_state.students.loc[idx, "grade"] = calculate_grade(marks)

            if save_data():
                st.success("Student updated successfully!")


# ================= DELETE STUDENT =================

def delete_student():
    st.subheader("🗑️ Delete Student")

    df = st.session_state.students

    if df.empty:
        st.info("No students available to delete.")
        return

    student_id = st.selectbox(
        "Select Student ID to delete",
        df["student_id"].astype(str).tolist(),
        key="delete_student_id"
    )

    student = df[df["student_id"].astype(str) == student_id].iloc[0]

    st.write(f"**Student Name:** {student['name']}")

    confirm = st.checkbox("I confirm that I want to delete this student.")

    if st.button("Delete Student", type="primary"):
        if not confirm:
            st.warning("Please confirm before deleting.")
        else:
            st.session_state.students = df[
                df["student_id"].astype(str) != student_id
            ].reset_index(drop=True)

            if save_data():
                st.success("Student deleted successfully!")


# ================= CALCULATE GRADE =================

def grade_page():
    st.subheader("📊 Calculate Grade")

    df = st.session_state.students

    if df.empty:
        st.info("No student records available.")
        return

    student_id = st.selectbox(
        "Select Student",
        df["student_id"].astype(str).tolist(),
        key="grade_student_id"
    )

    student = df[df["student_id"].astype(str) == student_id].iloc[0]

    grade = calculate_grade(float(student["marks"]))

    st.metric("Student Marks", f"{student['marks']:.2f}")
    st.metric("Grade", grade)
    st.write(f"**Student:** {student['name']}")


# ================= SAVE TO CSV =================

def save_csv_page():
    st.subheader("💾 Save to CSV")

    df = st.session_state.students

    if st.button("Save Student Records"):
        if save_data():
            st.success(f"Records saved to {FILE_NAME.name}.")

    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="students.csv",
        mime="text/csv"
    )


# ================= LOAD CSV =================

def load_csv_page():
    st.subheader("📂 Load CSV")

    uploaded_file = st.file_uploader(
        "Upload a student CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(
                uploaded_file,
                dtype={"student_id": str}
            )

            if not set(FIELDS).issubset(df.columns):
                st.error("CSV must contain all required columns.")
                return

            df = df[FIELDS].copy()
            df["student_id"] = df["student_id"].fillna("").astype(str).str.strip()
            df["name"] = df["name"].fillna("").astype(str).str.strip()
            df["course"] = df["course"].fillna("").astype(str).str.strip()
            df["age"] = pd.to_numeric(df["age"], errors="coerce")
            df["marks"] = pd.to_numeric(df["marks"], errors="coerce")

            valid = (
                df["student_id"].ne("")
                & df["name"].ne("")
                & df["course"].ne("")
                & df["age"].notna()
                & df["marks"].notna()
                & df["age"].gt(0)
                & df["age"].eq(df["age"].astype("Int64"))
                & df["marks"].between(0, 100)
            )

            if not valid.all():
                st.error("CSV contains invalid student records.")
                return

            if df["student_id"].duplicated().any():
                st.error("CSV contains duplicate student IDs.")
                return

            df["age"] = df["age"].astype(int)
            df["grade"] = df["marks"].apply(calculate_grade)

            st.dataframe(df, use_container_width=True, hide_index=True)

            if st.button("Import Student Records"):
                st.session_state.students = df.reset_index(drop=True)

                if save_data():
                    st.success("CSV records imported and saved successfully!")

        except (ValueError, TypeError, pd.errors.ParserError) as error:
            st.error(f"Unable to process CSV: {error}")


# ================= REPORTS =================

def reports_page():
    st.subheader("📈 Student Performance Reports")

    df = st.session_state.students

    if df.empty:
        st.info("No student records available for reports.")
        return

    total = len(df)
    average = df["marks"].mean()
    passed = int((df["marks"] >= 50).sum())
    failed = total - passed

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total)
    col2.metric("Average Marks", f"{average:.2f}")
    col3.metric("Passed", passed)
    col4.metric("Failed", failed)

    highest = df.loc[df["marks"].idxmax()]
    lowest = df.loc[df["marks"].idxmin()]

    st.write(f"**Highest Marks:** {highest['name']} ({highest['marks']})")
    st.write(f"**Lowest Marks:** {lowest['name']} ({lowest['marks']})")

    st.subheader("Grade Distribution")

    grade_order = ["A+", "A", "B", "C", "D", "F"]

    grade_counts = (
        df["grade"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
    )

    st.bar_chart(grade_counts)


# ================= MAIN APPLICATION =================

def main():
    if not st.session_state.logged_in:
        login_page()
        return

    st.title("🎓 Student Management System")
    st.caption("Manage student records and academic performance.")

    with st.sidebar:
        st.header("Navigation")

        option = st.radio(
            "Choose an option",
            [
                "Add Student",
                "Display Students",
                "Search Student",
                "Update Student",
                "Delete Student",
                "Calculate Grade",
                "Save to CSV",
                "Load CSV",
                "Reports"
            ]
        )

        st.divider()

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.students = pd.DataFrame(columns=FIELDS)
            st.rerun()

    if option == "Add Student":
        add_student()

    elif option == "Display Students":
        display_students()

    elif option == "Search Student":
        search_student()

    elif option == "Update Student":
        update_student()

    elif option == "Delete Student":
        delete_student()

    elif option == "Calculate Grade":
        grade_page()

    elif option == "Save to CSV":
        save_csv_page()

    elif option == "Load CSV":
        load_csv_page()

    elif option == "Reports":
        reports_page()


if __name__ == "__main__":
    main()