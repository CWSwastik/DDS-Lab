#  Labsheet 1: 2 tier architecture using Python and SQLite

## 1. CREATE a Student table 
```sql
CREATE TABLE Student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL
);
```

## 2. Insert some records
```sql
INSERT INTO Student (name, age, grade) VALUES ('Akshit', 20, 'A');
INSERT INTO Student (name, age, grade) VALUES ('Pratish', 21, 'B');
INSERT INTO Student (name, age, grade) VALUES ('Rahul', 22, 'A');
```

## 3. CREATE a main.py file
```py
import sqlite3

def execute_query(query, params):
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
