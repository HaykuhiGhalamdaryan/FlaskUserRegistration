from flask import Flask, request, render_template, session, redirect, url_for
import mysql.connector
import random
import re
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)
app.secret_key = os.urandom(24)

email_val = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

load_dotenv()

db_config = {
    'user': os.getenv("db_user"),
    'password': os.getenv("db_password"),
    'host': os.getenv("host"),
    'database': os.getenv("db_name")
}

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP__PASSWORD")
SMTP_SERVER = "smtp.mail.ru"
SMTP_PORT = 587

existing_data = []

@app.route('/', methods=['GET'])
def index():
    return render_template('form.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    surname = request.form['surname']
    phone = request.form['phone']
    email = request.form['email']
    profession = request.form['profession']

    if not re.match(email_val, email):
        return render_template('form.html', message="Invalid email. Please try again.", name=name, surname=surname, phone=phone, email=email, profession=profession)
    
    if not re.findall('^[+]', phone) or len(phone) > 12 or not phone[1:].isdigit():
        return render_template('form.html', message="Invalid phone number. Please try again.", name=name, surname=surname, phone=phone, email=email, profession=profession)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        check_query = "SELECT * FROM profession WHERE email = %s OR phone = %s"
        cursor.execute(check_query, (email, phone))
        result = cursor.fetchone()
        
        if result:
            return render_template('form.html', message="This user is already registered with this email or phone number.", name=name, surname=surname, phone=phone, email=email, profession=profession)
        
        session['user_data'] = {
            'name': name,
            'surname': surname,
            'phone': phone,
            'email': email,
            'profession': profession
        }
        
        verification_code = str(random.randint(100000, 999999))
        session['verification_code'] = verification_code
        
        try:
            send_verification_email(email, name, verification_code)
            
        except ValueError as email_error:
            return render_template('error.html', message=str(email_error))
        
        return redirect(url_for('verify'))
    
    except mysql.connector.Error as err:
        return render_template('error.html', message="A database error occurred. Please try again later.")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        input_code = request.form['code']
        
        if input_code == session.get('verification_code'):
            user_data = session.get('user_data')
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                
                query = "INSERT INTO profession (name, surname, phone, email, profession) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (user_data['name'], user_data['surname'], user_data['phone'], user_data['email'], user_data['profession']))
                conn.commit()
                
                session.pop('verification_code', None)
                session.pop('user_data', None)
                
                return render_template('result.html', message="Your data has been verified and saved successfully!")
            
            except mysql.connector.Error as err:
                return render_template('error.html', message="A database error occurred while saving your data. Please try again.")
            
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        else:
            return render_template('verify.html', message="Incorrect code. Please try again.")
    
    return render_template('verify.html')
            
def send_verification_email(to_email, name, verification_code):
    if SMTP_EMAIL is None or SMTP_PASSWORD is None:
        raise ValueError("SMTP configuration is missing. Please check your settings.")
        
    subject = "Your Verification Code"
    body = f"Hello {name},\n\nYour verification code is: {verification_code}\n\nPlease enter this code to complete your registration."

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        print("Verification email sent successfully!")

    except smtplib.SMTPAuthenticationError:
        raise ValueError("Failed to send email. Authentication error occurred.")
    
    except Exception as e:
        raise ValueError("An error occurred while sending the email. Please try again later.")   

@app.route('/view-data', methods=['GET'])
def view_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM profession")
        data = cursor.fetchall()

        return render_template('view_data.html', data=data)

    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/most-common-profession', methods=['GET'])
def most_common_profession():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT profession FROM profession"
        cursor.execute(query)
        results = cursor.fetchall()
        
        professions = [profession[0] for profession in results]
                
        all_professions = existing_data + professions
        
        profession_list = [prof.strip() for entry in all_professions for prof in entry.split(',')]
        
        vectorizer = CountVectorizer(tokenizer=lambda x: x.split(', '))
        X = vectorizer.fit_transform([', '.join(profession_list)])
        
        profession_counts = pd.DataFrame(
            data=X.toarray().flatten(),
            index=vectorizer.get_feature_names_out(),
            columns=['Count']
        )
        
        most_common_professions = profession_counts.sort_values(by='Count', ascending=False).reset_index()
        most_common_professions.columns = ['Profession', 'Count']
        
        return render_template('most_common_profession.html', professions=most_common_professions.to_dict(orient='records'))

    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
