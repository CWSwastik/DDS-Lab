# Lab Sheet 1: 2-Tier Architecture using Python and SQLite

## Objective
In this lab, you will create a simple 2-tier architecture where the application logic is handled by Python and the data is managed using an SQLite database. You will create a `Student` table, insert some records, and implement basic CRUD operations using Python.


## 1. Create a Student Table

Start by creating a `Student` table in the `students.db` database. This table will store basic student information such as their ID, name, age, and grade.

```sql
CREATE TABLE Student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL
);
```

- `id`: This is the primary key that uniquely identifies each student. It is an integer that automatically increments with each new entry.
- `name`: Stores the name of the student as text and cannot be null.
- `age`: Stores the age of the student as an integer and cannot be null.
- `grade`: Stores the grade of the student as text and cannot be null.


## 2. Insert Some Records

Next, populate the `Student` table with some initial data. You can insert the following records:

```sql
INSERT INTO Student (name, age, grade) VALUES ('Akshit', 20, 'A');
INSERT INTO Student (name, age, grade) VALUES ('Pratish', 21, 'B');
INSERT INTO Student (name, age, grade) VALUES ('Rahul', 22, 'A');
```

- These SQL commands insert three students into the `Student` table with the names 'Akshit', 'Pratish', and 'Rahul', along with their respective ages and grades.



## 3. Create a `main.py` File

Now, you'll create a Python script named `main.py` that will connect to the SQLite database and perform CRUD operations. The script will include a utility function `execute_query` that simplifies executing SQL commands by managing the database connection and cursor.

```python
import sqlite3

def execute_query(query, params=()):
    with sqlite3.connect('students.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        conn.commit()

def add_student(name, age, grade):
    execute_query("INSERT INTO Student (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))

def get_students():
    return execute_query("SELECT * FROM Student")

def update_student(id, name, age, grade):
    execute_query("UPDATE Student SET name = ?, age = ?, grade = ? WHERE id = ?", (name, age, grade, id))

def delete_student(id):
    execute_query("DELETE FROM Student WHERE id = ?", (id,))

if __name__ == "__main__":
    # Example usage
    add_student('Darsh', 23, 'B')
    print(get_students())
    update_student(1, 'Akshit', 20, 'A+')
    delete_student(2)
    print(get_students())
```

- **`execute_query(query, params=())`**: This function handles the connection to the database and executes the given SQL query. It uses a context manager to ensure the connection is properly closed after the operation. For `SELECT` queries, it returns the results.
- **CRUD Functions**: 
  - `add_student`: Adds a new student to the database.
  - `get_students`: Retrieves all students from the database.
  - `update_student`: Updates an existing student's details.
  - `delete_student`: Deletes a student from the database.
- **Example Usage**: The script demonstrates adding, retrieving, updating, and deleting records.
