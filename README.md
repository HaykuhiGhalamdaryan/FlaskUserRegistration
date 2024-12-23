# Flask Application for User Registration and Data Analysis

This project is a Flask web application designed for user registration, email verification, and data analysis. Users can register with their details, verify their email via a code, and view or analyze the data.

---

## Features

1. **User Registration**
   - Users can register by providing their name, surname, phone, email, and profession.
   - Data validation for email and phone number ensures accurate input.

2. **Email Verification**
   - A verification code is sent to the user's email.
   - Users must input the code to complete their registration.

3. **View Registered Data**
   - Displays all registered user data from the database.

4. **Most Common Profession Analysis**
   - Identifies the most common professions among registered users using text analysis.

5. **Error Handling**
   - Handles database errors, email sending issues, and invalid input gracefully.

---

## Technologies Used

- **Backend:** Flask, Python
- **Frontend:** HTML, CSS (via templates)
- **Database:** MySQL
- **Email Service:** SMTP (Mail.ru)
- **Data Analysis:** Pandas, Scikit-learn (CountVectorizer)

---

## Prerequisites

1. **Python**: Install Python 3.8 or higher.
2. **MySQL**: Ensure MySQL is installed and running.
3. **Environment Variables**: Configure `.env` with the following:
   - `db_user`: Database username
   - `db_password`: Database password
   - `host`: Database host (e.g., localhost)
   - `db_name`: Database name
   - `SMTP_EMAIL`: SMTP email address (Mail.ru)
   - `SMTP__PASSWORD`: SMTP email password

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HaykuhiGhalamdaryan/FlaskUserRegistration.git
   cd FlaskUserRegistration
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the database and required table:
   ```sql
   CREATE DATABASE your_database_name;
   USE your_database_name;
   CREATE TABLE profession (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(255),
       surname VARCHAR(255),
       phone VARCHAR(255),
       email VARCHAR(255),
       profession TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

4. Set up the `.env` file with the required credentials (refer to **Prerequisites**).

5. Run the application:
   ```bash
   python app.py
   ```

---

## Routes

### 1. `/`
**Method:** GET
- Renders the registration form.

### 2. `/upload`
**Method:** POST
- Processes user registration.
- Sends a verification code to the user's email.
- Redirects to the `/verify` route.

### 3. `/verify`
**Methods:** GET, POST
- Verifies the code sent to the user's email.
- Saves the user data to the database upon successful verification.

### 4. `/view-data`
**Method:** GET
- Displays all registered user data.

### 5. `/most-common-profession`
**Method:** GET
- Analyzes and displays the most common professions among registered users.

---

## Usage

1. Open the application in your browser (default: `http://127.0.0.1:5000`).
2. Register by filling out the form.
3. Check your email for the verification code and input it on the verification page.
4. Explore registered user data and analyze professions using the provided links/buttons.

---

## Error Handling

- Invalid email or phone number: Displays a meaningful error message and retains the entered data.
- Database errors: Displays a generic error message and logs the issue.
- Email sending issues: Alerts the user to check their email settings.

---

## License

This project is licensed under the MIT License.

