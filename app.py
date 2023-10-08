import sqlite3
import random 
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

conn = sqlite3.connect("./database.db")
print("Opened database successfully")

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Fetch all the table names
tables = cursor.fetchall()

# Print the table names
for table in tables:
    print(table[0])
conn.execute(
    "CREATE TABLE if not exists User (name TEXT,email TEXT, password TEXT, phone_no INT, DoB date, addr TEXT,  pin TEXT, Qualification TEXT, Subject Text, About TEXT, IsSubscribed BOOLEAN DEFAULT 0, role TEXT DEFAULT 'job_seeker' )"
)
conn.execute(
    "CREATE TABLE if not exists Jobs (ID INTEGER PRIMARY KEY AUTOINCREMENT,Company_name TEXT NOT NULL,Title TEXT NOT NULL,Salary INTEGER,Location TEXT,Duration TEXT,Description TEXT,Responsibilities TEXT,Qualification TEXT)"
)
conn.execute(
    "CREATE TABLE if not exists Templates (Template_name TEXT,Template_link TEXT)"
)

print("Table created successfully")
conn.close()


@app.route("/")
def index():
    if "current_user" in session:
        return render_template("index.html")
    print("email not in session")
    return redirect(url_for("login"))


@app.route("/about")
def about():
    print(session)
    if "current_user" in session:
        return render_template("about.html")
    print("email not in session")
    return redirect(url_for("login"))


# @app.route("/jobs")
# def jobs():
#     job_listings = [] 
#     if "current_user" in session:
#         return render_template("job.html")
#     print("email not in session")
#     return redirect(url_for("login"))


@app.route("/premium")
def premium():
    if "current_user" in session:
        return render_template("premium.html")
    print("email not in session")
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if "current_user" in session:
        return render_template("profile.html")
    print("email not in session")
    return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("loginpage.html")


@app.route("/loginuser", methods=["POST", "GET"])
def loginuser():
    if request.method == "POST":
        try:
            print("entered try")
            login_email = request.form["login_email"]
            print("login_email", login_email)
            login_password = request.form["login_password"]
            print("login_password", login_password)
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                user = cur.execute(
                    "SELECT * FROM User WHERE email = ?", (login_email,)
                ).fetchall()

                if len(user) == 0:
                    flash("Invalid Email")
                    print("Invalid Email")
                    return redirect(url_for("login"))
                elif user[0][2] != login_password:
                    flash("Invalid Password")
                    print("Invalid Password")
                    return redirect(url_for("login"))

                # session["email"] = login_email
                # session["name"] = user[0][0]
                # session["password"] = user[0][2]
                session["current_user"] = user[0]
                print("current_user", session["current_user"])

        except:
            print("login failed")
            flash("Something went wrong, please try again")
            return redirect(url_for("login"))

        return redirect(url_for("index"))


@app.route("/adduser", methods=["POST", "GET"])
def adduser():
    if request.method == "POST":
        try:
            uname = request.form["signup-username"]
            email = request.form["signup-email"]
            password = request.form["signup-password"]

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                user = cur.execute(
                    "SELECT * FROM User WHERE email = ?", (email,)
                ).fetchall()
                if len(user) > 0:
                    flash("Email already exists")
                    return redirect(url_for("login"))

                cur.execute(
                    "INSERT INTO User (name,email,password) VALUES(?,?,?)",
                    (uname, email, password),
                )

                con.commit()
                flash("Account created successfully")
                print("Account created successfully")

        except:
            con.rollback()
            flash("Something went wrong, please try again")

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove the username from the session if it's there
    # session.pop("username", None)
    # session.pop("email", None)
    # session.pop("password", None)
    session.pop("current_user", None)
    return redirect(url_for("login"))


@app.route("/updateuser", methods=["POST", "GET"])
def updateuser():
    if request.method == "POST":
        try:
            uname = request.form["user_name"]
            phone = request.form["phone"]
            role = request.form["joblinkup-usage"]
            pin = request.form["pincode"]
            location = request.form["location"]
            degree = request.form["degree"]
            subject = request.form["subject"]
            email = request.form["email"]
            dob = request.form["birthday"]
            desc = "none"

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE User SET name = ?, phone_no = ?, DoB = ?, addr = ?, pin = ?, Qualification = ?, Subject = ?, About = ?, role = ? WHERE email = ?",
                    (
                        uname,
                        phone,
                        dob,
                        location,
                        pin,
                        degree,
                        subject,
                        desc,
                        role,
                        email,
                    ),
                )

        except:
            pass

        finally:
            return redirect(url_for("index"))
        
def populate_job_listings():
    conn = sqlite3.connect('database.db')

    cur = conn.cursor()

    companies = ["TCS", "IBM", "Infosys", "Wipro", "Accenture", "Dell", "ABB", "Microsoft", "Google", "Amazon"]
    job_titles = ["Software Engineer", "Data Analyst", "Web Developer", "Database Administrator", "Network Engineer",
                  "UX Designer", "Digital Marketing Specialist", "Business Analyst", "AI/ML Engineer", "DevOps Engineer"]
    locations = ["Bangalore", "Pune", "Chennai", "Hyderabad", "Mumbai"]

    job_data = {
        "TCS": {
            "Description": "TCS is a multinational IT services and consulting company.",
            "responsibilities": "TCS employees work on various IT projects for clients worldwide."
        },
        "IBM": {
            "Description": "IBM is a global technology company that provides hardware, software, and services.",
            "responsibilities": "IBM employees are involved in cutting-edge technology and innovation."
        },
        # Add descriptions and responsibilities for other companies here...
    }
    # ...
    for company in companies:
        for _ in range(5):  # Insert 5 job listings per company (adjust as needed)
            title = random.choice(job_titles)
            salary = random.randint(50000, 150000)
            location = random.choice(locations)
            duration = random.choice(["Full-time", "Part-time", "Contract"])
            company_description = job_data.get(company, {}).get("Description", "Description not available")
            company_responsibilities = job_data.get(company, {}).get("responsibilities", "Responsibilities not available")

            # Replace this with your actual data insertion logic into your database table
            insert_sql = '''
            INSERT INTO Jobs (Company_name, Title, Salary, Location, Duration, Description, Responsibilities)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''

            # Correct the variable names here
            job_data_tuple = (company, title, salary, location, duration, company_description, company_responsibilities)

            cur.execute(insert_sql, job_data_tuple)  # Use the corrected variable name
    # ...
             
            # # Replace this with your actual data insertion logic into your database table
            # insert_sql = '''
            # INSERT INTO Jobs (Company_name, Title, Salary, Location, Duration, Description, Responsibilities)
            # VALUES (?, ?, ?, ?, ?, ?, ?)
            # '''

            # job_data = (company, title, salary, location, duration, company_description, company_responsibilities)

            # cur.execute(insert_sql, job_data)

    conn.commit()
    conn.close()

# Call the function to populate job listings
populate_job_listings()


@app.route('/jobs')
def jobs():
    # Replace this with your logic to fetch job listings from your database
    job_listings = []  # Fetch job listings here
    return render_template('jobb.html', job_listings=job_listings)

@app.route('/job_details/<int:job_id>')
def job_details(job_id):
    # Replace this with your logic to fetch job details from your database based on the job_id
    job = {}  # Fetch job details here
    return render_template('job_details.html', job=job)
if __name__ == "__main__":
    app.run(debug=True)
