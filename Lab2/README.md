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

## Part 3: Creating the Flask Application

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

     @app.route('/')
     def hello():
        return '<h1>Hello, World!</h1>'
     ```

   - In order to run the Flask server when the script is executed add the following code at the end of the file:
      ```python
      if __name__ == '__main__':
         app.run(debug=True)
      ```

3. **Implement CRUD API Endpoints**:
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
### Optional Task:
- Use a helper function to execute SQL queries to reduce code redundancy similar to the one in Lab 1.
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
   - The render_template function in Flask is used to generate HTML output by combining a template file (in this case, students.html) with data passed to it. The students data, which is a list of tuples representing rows from the Student table, is passed to the template. The template uses Jinja2 syntax to iterate over the students list and dynamically generate a table displaying the student information. This separates the presentation layer from the application logic, making the code more modular and maintainable.
---

## Part 5: Testing and Validation

### Instructions:
- Test each API endpoint using Postman or curl.
- Access the `students/view` URL in your browser to see the list of students rendered using the Flask template.

### Task:
- **Test the Application using `curl`**:
  - **Add a Student**:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"name":"Darsh","age":24,"grade":"A"}' http://127.0.0.1:5000/students
    ```
    - This command sends a POST request to add a new student named "Darsh" with age 24 and grade "A".
  
  - **Get All Students**:
    ```bash
    curl http://127.0.0.1:5000/students
    ```
    - This command sends a GET request to retrieve all students from the database.

  - **Update a Student**:
    ```bash
    curl -X PUT -H "Content-Type: application/json" -d '{"name":"Akshit","age":21,"grade":"A+"}' http://127.0.0.1:5000/students/1
    ```
    - This command sends a PUT request to update the student with ID 1, changing Akshit's age to 21 and grade to "A+".
  
  - **Delete a Student**:
    ```bash
    curl -X DELETE http://127.0.0.1:5000/students/2
    ```
    - This command sends a DELETE request to remove the student with ID 2 from the database.

- **Accessing the Template**:
  - Open a browser and go to `http://127.0.0.1:5000/students/view` to view the student list rendered in an HTML table.

---

## Helpful Resources

For further reading and additional help, you can refer to the following resources:

- **[API Integration in Python](https://realpython.com/api-integration-in-python/):** A comprehensive guide on integrating APIs in Python, helpful for understanding REST APIs.
  
- **[How to Build a Web Application Using Flask and Deploy It to the Cloud](https://www.freecodecamp.org/news/how-to-build-a-web-application-using-flask-and-deploy-it-to-the-cloud-3551c985e492/):** This article walks you through building and deploying a Flask web application step by step.

- **[How to Make a Web Application Using Flask in Python 3](https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-3-using-html-templates):** A detailed tutorial on creating a Flask web application, with a focus on using HTML templates.
  
- **[Flask RESTful CRUD API](https://medium.com/@dennisivy/flask-restful-crud-api-c13c7d82c6e5):** This tutorial covers creating a RESTful CRUD API using Flask, which aligns closely with the CRUD operations in this lab.
