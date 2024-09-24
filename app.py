from flask import Flask, render_template, request, redirect, url_for, jsonify, session,get_flashed_messages,flash
import smtplib,math
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
            consultation_type VARCHAR(100),
            FOREIGN KEY (username) REFERENCES login(username) ON DELETE CASCADE
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
    print("Session data:", session)  # Debugging statement
    is_logged_in = 'username' in session
    return render_template('index.html', logged_in=is_logged_in)

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

        # Check if the user already exists in the database
        c1.execute("SELECT * FROM login WHERE username = %s", (username,))
        existing_user = c1.fetchone()

        if existing_user:
            return jsonify({'success': False, 'message': 'User already exists!'}), 400  # User exists

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Save the new user to the database
        c1.execute("INSERT INTO login (username, password, name, phone_no) VALUES (%s, %s, %s, %s)",
                   (username, hashed_password, name, phone_no))
        mydb.commit()

        return jsonify({'success': True})
        # Successful registration

    return render_template('register.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Replace this with your actual database query
        c1.execute("SELECT * FROM login WHERE username = %s", (username,))
        login_user = c1.fetchone()
        
        if login_user and bcrypt.checkpw(password.encode('utf-8'), login_user[1].encode('utf-8')):
            session['username'] = username
            return jsonify({'success': True})  # Return success response
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401  # Return failure response
    else:
        return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' in session:
        username=session['username']
        c1.execute("SELECT phone_no,name FROM login WHERE username = %s", (username,))
        data = c1.fetchone()
        return render_template('profile.html', username=session['username'],phone=data[0],name=data[1])
    return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        flash('You need to log in to access your profile.', 'error')
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Get the updated data from the form
    email = request.form['email']
    phone_no = request.form['phone_no']

    # Update the user's information in the database
    c1.execute("UPDATE login SET email = %s, phone_no = %s WHERE username = %s", (email, phone_no, session['username']))
    mydb.commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    if request.method == 'POST':
        username = session['username']  # Safely access username from session
        appointment_date = request.form.get('appointment_date')  # Use .get() to avoid KeyError
        appointment_time = request.form.get('appointment_time')  # Use .get() to avoid KeyError
        consultation = request.form.get('consultation')  # Use .get() to avoid KeyError

        if not appointment_date or not appointment_time or not consultation:
            return "All fields are required.", 400  # Return error if fields are missing

        # Combine date and time into a single datetime string
        appointment_datetime = f"{appointment_date} {appointment_time}"

        # Insert appointment into the database
        c1.execute("INSERT INTO appointments (username, appointment_date, consultation_type) VALUES (%s, %s, %s)", 
                   (username, appointment_datetime, consultation))
        mydb.commit()
        
        message ="Subject:  Appointment Scheduled\n\n"+f"hi {username},\n\nI hope this message finds you well.\n\nYour appointment has been scheduled\n Date and time:{appointment_datetime}. \nIf you have any questions or need to reschedule, please feel free to contact us at Ai-healthcare app.\n\nWe kindly ask that you arrive 10-15 minutes early to complete any necessary paperwork or preparations.\n\nWe look forward to seeing you!\n\nBest regards,\nAi-healthcare"
    
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()

        emailid = "officialpriyansh23@gmail.com"
        s.login("test1471email@gmail.com", "drsi saoy yhhl deam")
        s.sendmail('&&&&&&',emailid,message)

        # Redirect to the index page
        return redirect(url_for('index'))

    return render_template('appointment.html')



@app.route('/medical-records')
def medical_records():
    if 'username' not in session:
        flash('You need to log in to access your medical records.', 'error')
        return redirect(url_for('login'))

    # Fetch medical records from the database
    c1.execute("SELECT * FROM medical_records WHERE username = %s", (session['username'],))
    records = c1.fetchall()

    if records:
        return render_template('medical_records.html', records=records)
    else:
        flash('No medical records found.', 'info')
        return render_template('medical_records.html', records=[])

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
