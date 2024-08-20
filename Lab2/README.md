# Lab Sheet 2: 3-Tier Architecture using Python, Flask, and MySQL

**Objective**: By the end of this lab, you will be able to design and implement a 3-tier architecture, where Flask templates render the frontend, Flask handles REST API endpoints, and MySQL for persistent data storage.

---

## Overview

In this lab, you will create a web application that implements a 3-tier architecture:

- **Presentation Layer (Tier 1)**: Uses Flask templates to render the frontend.
- **Application Layer (Tier 2)**: Flask handles REST API endpoints and business logic.
- **Data Layer (Tier 3)**: MySQL serves as the database for persistent data storage.

---

## Part 1: Setting Up the Environment

### Instructions:
1. **Install Flask and MySQL connector for Python**:
   - Ensure you have Python installed (version 3.x).
   - Install Flask:
     ```bash
     pip install Flask
     ```
   - Install MySQL connector:
     ```bash
     pip install mysql-connector-python
     ```

2. **Set Up MySQL Database**:
   - Install MySQL server if not already installed.
   - Log into MySQL and create a new database called `school`.
   - Create a user with permissions to access this database.

### Task:
- Connect to MySQL:
  ```bash
  mysql -u your_username -p
  ```
- Create the `school` database:
  ```sql
  CREATE DATABASE school;
  USE school;
  ```

---

## Part 2: Database Design

### Instructions:
- Create a table called `Student` within the `school` database with the following fields:
  - `id` (INT, Primary Key, AutoIncrement)
  - `name` (VARCHAR(100), Not Null)
  - `age` (INT, Not Null)
  - `grade` (VARCHAR(5), Not Null)

### Task:
- Execute the following SQL commands in MySQL to create the `Student` table:

  ```sql
  CREATE TABLE Student (
      id INT PRIMARY KEY AUTO_INCREMENT,
      name VARCHAR(100) NOT NULL,
      age INT NOT NULL,
      grade VARCHAR(5) NOT NULL
  );
  ```

- Insert 3 records into the `Student` table:
  ```sql
  INSERT INTO Student (name, age, grade) VALUES ('Akshit', 20, 'A');
  INSERT INTO Student (name, age, grade) VALUES ('Pratish', 21, 'B');
  INSERT INTO Student (name, age, grade) VALUES ('Rahul', 22, 'A');
  ```

---

## Part 3: Creating the Flask Application (50 minutes)

### Instructions:
- Create a Flask application named `app.py`.
- Configure the MySQL connection using Flask and MySQL connector.
- Implement REST API endpoints to handle CRUD operations (Create, Read, Update, Delete) for `Student` data.

### Task:
1. **Set Up Flask and MySQL Connection**:
   - In `app.py`, set up Flask and configure the MySQL connection:

     ```python
     from flask import Flask, request, jsonify, render_template
     import mysql.connector

     app = Flask(__name__)

     def get_db_connection():
         conn = mysql.connector.connect(
             host="localhost",
             user="your_username",
             password="your_password",
             database="school"
         )
         return conn
     ```

2. **Implement CRUD API Endpoints**:
   - Implement the following REST API endpoints:

     - **Create a new student (POST)**:
       ```python
       @app.route('/students', methods=['POST'])
       def add_student():
           data = request.get_json()
           name = data['name']
           age = data['age']
           grade = data['grade']
           conn = get_db_connection()
           cursor = conn.cursor()
           cursor.execute("INSERT INTO Student (name, age, grade) VALUES (%s, %s, %s)", (name, age, grade))
           conn.commit()
           cursor.close()
           conn.close()
           return jsonify({'message': 'Student added successfully!'}), 201
       ```

     - **Retrieve all students (GET)**:
       ```python
       @app.route('/students', methods=['GET'])
       def get_students():
           conn = get_db_connection()
           cursor = conn.cursor()
           cursor.execute("SELECT * FROM Student")
           students = cursor.fetchall()
           cursor.close()
           conn.close()
           return jsonify(students)
       ```

     - **Update a student (PUT)**:
       ```python
       @app.route('/students/<int:id>', methods=['PUT'])
       def update_student(id):
           data = request.get_json()
           name = data['name']
           age = data['age']
           grade = data['grade']
           conn = get_db_connection()
           cursor = conn.cursor()
           cursor.execute("UPDATE Student SET name = %s, age = %s, grade = %s WHERE id = %s", (name, age, grade, id))
           conn.commit()
           cursor.close()
           conn.close()
           return jsonify({'message': 'Student updated successfully!'})
       ```

     - **Delete a student (DELETE)**:
       ```python
       @app.route('/students/<int:id>', methods=['DELETE'])
       def delete_student(id):
           conn = get_db_connection()
           cursor = conn.cursor()
           cursor.execute("DELETE FROM Student WHERE id = %s", (id,))
           conn.commit()
           cursor.close()
           conn.close()
           return jsonify({'message': 'Student deleted successfully!'})
       ```

---

## Part 4: Creating Flask Templates

### Instructions:
- Create a basic HTML template to display the list of students.
- Render the student data in the template using Flask.

### Task:
1. **Create a `templates` folder**:
   - In your project directory, create a folder named `templates`.

2. **Create `students.html` Template**:
   - Inside the `templates` folder, create an `students.html` file:

     ```html
     <!DOCTYPE html>
     <html lang="en">
     <head>
         <meta charset="UTF-8">
         <meta name="viewport" content="width=device-width, initial-scale=1.0">
         <title>Student List</title>
     </head>
     <body>
         <h1>Students</h1>
         <table>
             <tr>
                 <th>ID</th>
                 <th>Name</th>
                 <th>Age</th>
                 <th>Grade</th>
             </tr>
             {% for student in students %}
             <tr>
                 <td>{{ student[0] }}</td>
                 <td>{{ student[1] }}</td>
                 <td>{{ student[2] }}</td>
                 <td>{{ student[3] }}</td>
             </tr>
             {% endfor %}
         </table>
     </body>
     </html>
     ```

3. **Render the Template in Flask**:
   - Add an endpoint in `app.py` to render the student list:

     ```python
     @app.route('/students/view', methods=['GET'])
     def view_students():
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute("SELECT * FROM Student")
         students = cursor.fetchall()
         cursor.close()
         conn.close()
         return render_template('students.html', students=students)
     ```

---

## Part 5: Testing and Validation

### Instructions:
- Test each API endpoint using Postman or curl.
- Access the `students/view` URL in your browser to see the list of students rendered using the Flask template.

### Task:
- **Test the Application**:
  - Use Postman to test the CRUD operations (POST, GET, PUT, DELETE) on the `/students` endpoints.
  - Visit `http://127.0.0.1:5000/students/view` in your browser to see the rendered list of students.
