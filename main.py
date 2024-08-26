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

@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students)

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

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Student WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Student deleted successfully!'})

@app.route('/students/view', methods=['GET'])
def view_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('students.html', students=students)


if __name__ == '__main__':
   app.run(debug=True)
