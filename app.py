from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import secrets
import mysql.connector
import bcrypt
import ollama_response as chatbot

# Connect to MySQL
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1471",
        database="healthcare"
    )
except mysql.connector.Error as err:
    print(f"Error: {err}")
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1471"
    )
    c2 = mydb.cursor()
    c2.execute("CREATE DATABASE healthcare")
    print("Database created successfully.")
    mydb.database = 'healthcare'

# Create cursor
c1 = mydb.cursor()
# Create tables if they do not exist
def create_tables():
    # Create login table
    c1.execute("""
        CREATE TABLE IF NOT EXISTS login (
            username VARCHAR(100) PRIMARY KEY,
            password VARCHAR(255),
            name VARCHAR(100),
            phone_no VARCHAR(15)
        )
    """)
    print("Login table checked/created successfully.")

    # Create appointments table
    c1.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            appointment_date DATETIME,
            details TEXT
        )
    """)
    print("Appointments table checked/created successfully.")
    
c1.execute("""
    CREATE TABLE IF NOT EXISTS medical_records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100),
        record_date DATE,
        record_type VARCHAR(100),
        details TEXT
    )
""")

create_tables()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get('user_question')

    response = chatbot.chat_with_bot(user_question)
    if response:
        return response 
    else:
        default_response = "I'm sorry, I don't have enough information to answer your question. Please try asking something else."
        return default_response  # Return plain text response
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        phone_no = request.form['phone_no']

        # Check if the user already exists
        c1.execute("SELECT * FROM login WHERE username = %s", (username,))
        existing_user = c1.fetchone()

        if existing_user is None:
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            c1.execute("INSERT INTO login (username, password, name, phone_no) VALUES (%s, %s, %s, %s)", 
                       (username, hashpass, name, phone_no))
            mydb.commit()
            session['username'] = username
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        c1.execute("SELECT * FROM login WHERE username = %s", (username,))
        login_user = c1.fetchone()

        if login_user:
            if bcrypt.checkpw(password.encode('utf-8'), login_user[1].encode('utf-8')):  # login_user[1] is the password
                session['username'] = username
                return jsonify({"success": True})  # Return success response as JSON

        return jsonify({"success": False, "message": "Invalid username/password combination"})

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        username = session['username']
        appointment_date = request.form['appointment_date']
        details = request.form['details']

        # Insert appointment into the database
        c1.execute("INSERT INTO appointments (username, appointment_date, details) VALUES (%s, %s, %s)", 
                   (username, appointment_date, details))
        mydb.commit()

        # Redirect to the index page
        return redirect(url_for('index'))

    return render_template('appointment.html')



@app.route('/medical-records')
def medical_records():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    username = session['username']
    
    # Fetch medical records for the logged-in user
    c1.execute("SELECT * FROM appointments WHERE username = %s", (username,))
    records = c1.fetchall()

    return render_template('medical-records.html', records=records)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    # Fetch doctor information from a database or API
    doctors = [
        {'name': 'Dr. John Doe', 'specialty': 'Cardiology', 'bio': 'Education and Experience'},
        # Add more doctors here
    ]
    return render_template('doctors.html', doctors=doctors)

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=True)