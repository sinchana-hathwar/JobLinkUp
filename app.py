import os
import sqlite3
import random 
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
conn.commit()
conn.close()

def get_db_connection():
    conn = sqlite3.connect("./database.db")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/", methods = ('GET', 'POST'))
def index():
    if "current_user" in session:
        if request.method == 'POST':
            job_title = request.form.get('job_title')
            location = request.form.get('location')
            company_name = request.form.get('company_name')

            search_filter = {'job_title': job_title , 'location': location, 'company_name': company_name }
            print(search_filter)
            return redirect(url_for('jobs',search_filter=json.dumps(search_filter)))
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


@app.route("/premium")
def premium():
    if "current_user" in session:
        return render_template("premium.html", userdata=session["current_user"])
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# @app.route('/upload/<int:job_id>', methods=['GET', 'POST'])
# def upload_file(job_id):
#     if 'current_user' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         file = request.files['resume']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             # Update the database to associate the uploaded file with the job listing
#             conn = sqlite3.connect('database.db')
#             cursor = conn.cursor()
#             cursor.execute('UPDATE Jobs SET File_path = ? WHERE ID = ?', (file_path, job_id))
#             conn.commit()
#             conn.close()

#             flash('File uploaded successfully.')
#             return redirect(url_for('job_details', job_id=job_id))
#         else:
#             flash('Invalid file format. Allowed formats: pdf, doc, docx.')

#     return render_template('upload.html', job_id=job_id)

def populate_job_listings():
    conn = sqlite3.connect("./database.db")
    cur = conn.cursor()

    companies = ["TCS", "IBM", "Infosys", "Wipro", "Accenture", "Dell", "ABB", "Microsoft", "Google", "Amazon"]
    job_titles = ["Software Engineer", "Data Analyst", "Web Developer", "Database Administrator", "Network Engineer",
                  "UX Designer", "Digital Marketing Specialist", "Business Analyst", "AI/ML Engineer", "DevOps Engineer"]
    locations = ["Bangalore", "Pune", "Chennai", "Hyderabad", "Mumbai"]

    job_data = {
        "Software Engineer": {
            "qualification": "Bachelor's degree in Computer Science or related field",
            "description": "Join our team as a Software Engineer and work on cutting-edge software projects.",
            "responsibilities": "Develop and maintain software applications."
        },
        "Data Analyst": {
            "qualification": "Bachelor's degree in Statistics, Data Science, or related field",
            "description": "Become a Data Analyst and analyze data to provide valuable insights.",
            "responsibilities": "Collect, clean, and analyze data to support business decisions."
        },
        "Web Developer": {
            "qualification": "Bachelor's degree in Web Development or related field",
            "description": "Join us as a Web Developer and create stunning websites and web applications.",
            "responsibilities": "Design and develop web solutions for clients."
        },
        "Database Administrator": {
            "qualification": "Bachelor's degree in Database Management or related field",
            "description": "Work as a Database Administrator and manage databases for optimal performance.",
            "responsibilities": "Ensure data security and efficient database operations."
        },
        "Network Engineer": {
            "qualification": "Bachelor's degree in Network Engineering or related field",
            "description": "Join our team as a Network Engineer and build and maintain network infrastructure.",
            "responsibilities": "Design and implement network solutions to meet business needs."
        },
        "UX Designer": {
            "qualification": "Bachelor's degree in UX/UI Design or related field",
            "description": "Become a UX Designer and create user-centered designs for web and mobile applications.",
            "responsibilities": "Design intuitive and visually appealing user interfaces."
        },
        "Digital Marketing Specialist": {
            "qualification": "Bachelor's degree in Marketing or related field",
            "description": "Join as a Digital Marketing Specialist and drive online marketing campaigns.",
            "responsibilities": "Plan and execute digital marketing strategies."
        },
        "Business Analyst": {
            "qualification": "Bachelor's degree in Business Administration or related field",
            "description": "Work as a Business Analyst and analyze business processes.",
            "responsibilities": "Gather and document business requirements."
        },
        "AI/ML Engineer": {
            "qualification": "Bachelor's degree in Computer Science or AI/ML",
            "description": "Join as an AI/ML Engineer and develop machine learning models.",
            "responsibilities": "Design and train AI/ML algorithms."
        },
        "DevOps Engineer": {
            "qualification": "Bachelor's degree in Computer Science or related field",
            "description": "Join as a DevOps Engineer and automate software development processes.",
            "responsibilities": "Build and maintain CI/CD pipelines."
        }
    }
    
    for company in companies:
        for _ in range(5):  # Insert 5 job listings per company (adjust as needed)
            title = random.choice(job_titles)
            salary = random.randint(50000, 150000)
            location = random.choice(locations)
            duration = random.choice(["Full-time", "Part-time", "Contract"])
            company_description = job_data.get(title, {}).get("description", "Description not available")
            company_responsibilities = job_data.get(title, {}).get("responsibilities", "Responsibilities not available")
            qualification = job_data.get(title, {}).get("qualification", "Qualification not available")

            # Replace this with your actual data insertion logic into your database table
            insert_sql = '''
            INSERT INTO Jobs (Company_name, Title, Salary, Location, Duration, Description, Responsibilities, Qualification)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''

            job_data_tuple = (company, title, salary, location, duration, company_description, company_responsibilities, qualification)

            cur.execute(insert_sql, job_data_tuple)

    conn.commit()
    conn.close()

# Call the function to populate job listings
populate_job_listings()

@app.route('/jobs', methods = ['GET'])
def jobs():
    search_filter = request.args.get('search_filter', default=json.dumps({}), type=str)
    search_filter = json.loads(search_filter)
    print(search_filter,'are the search filters')
    conn = sqlite3.connect("./database.db")
    cursor = conn.cursor()
    
    # Execute a query to fetch job listings from the database
    if (search_filter == {}) or  ((search_filter['job_title'] == 'All') and (search_filter['company_name']== '') and (search_filter['location']=='All Locations')):
        cursor.execute('SELECT * FROM Jobs')

    elif (search_filter['job_title'] == 'All') and (search_filter['company_name']!= '') and (search_filter['location']!='All Locations'):
        cursor.execute('SELECT * FROM Jobs where Company_name like ? and Location = ? ',('%'+search_filter['company_name']+'%',search_filter['location']))
        
    elif (search_filter['job_title'] != 'All') and (search_filter['company_name']== '') and (search_filter['location']!='All Locations'):
        cursor.execute('SELECT * FROM Jobs where Title = ? and Location = ? ',(search_filter['job_title'],search_filter['location']))

    elif (search_filter['job_title'] != 'All') and (search_filter['company_name']!= '') and (search_filter['location']=='All Locations'):
        cursor.execute('SELECT * FROM Jobs where Company_name like ? and Title = ? ',('%'+search_filter['company_name']+'%',search_filter['job_title']))    

    elif (search_filter['job_title'] != 'All') and (search_filter['company_name']!= '') and (search_filter['location']!='All Locations'):
        cursor.execute('SELECT * FROM Jobs where Company_name like ? and Title = ? and Location = ?',('%'+search_filter['company_name']+'%',search_filter['job_title'], search_filter['location']))
    
    elif (search_filter['job_title'] != 'All') and (search_filter['company_name']== '') and (search_filter['location']=='All Locations'):
        cursor.execute('SELECT * FROM Jobs where Title = ? ',(search_filter['job_title'],))
    elif (search_filter['job_title'] == 'All') and (search_filter['company_name']!= '') and (search_filter['location']=='All Locations'):
        cursor.execute("SELECT * FROM Jobs where Company_name like ?",('%'+search_filter['company_name']+'%',))
    elif (search_filter['job_title'] == 'All') and (search_filter['company_name']== '') and (search_filter['location']!='All Locations'):
        cursor.execute('SELECT * FROM Jobs where Location = ? ',(search_filter['location'],))    

    # Fetch all job listings as a list of dictionaries
    job_listings = []
    for row in cursor.fetchall():
        job_id, company_name, title, salary, location, duration, description, responsibilities, qualification = row
        job = {
            'ID': job_id,
            'company': company_name,
            'title': title,
            'salary': salary,
            'location': location,
            'duration': duration,
            'description': description,
            'responsibilities': responsibilities,
            'qualification': qualification
        }
        job_listings.append(job)
    conn.commit()
    conn.close()

    return render_template('job.html', job_listings=job_listings)

# Rest of your routes and code...
# ... (Previous code)

@app.route('/job_details/<int:job_id>')
def job_details(job_id):
    conn = sqlite3.connect('./database.db')
    cursor = conn.cursor()
    job_id = int(job_id)

    cursor.execute('SELECT * FROM Jobs WHERE ID = ?', (job_id,))
    job = cursor.fetchone()
    conn.commit()
    conn.close()

    return render_template('job_details.html', job=job)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# @app.route('/upload/<int:job_id>', methods=['GET', 'POST'])
# def upload_file(job_id):
#     if 'current_user' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         file = request.files['resume']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             conn = sqlite3.connect("./database.db")
#             cursor = conn.cursor()
#             cursor.execute('UPDATE Jobs SET File_path = ? WHERE ID = ?', (file_path, job_id))
#             conn.commit()
#             conn.close()

#             flash('File uploaded successfully.')
#             return redirect(url_for('job_details', job_id=job_id))
#         else:
#             flash('Invalid file format. Allowed formats: pdf, doc, docx.')

#     return render_template('upload.html', job_id=job_id)
@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/subscribe")
def subscribe():
    return render_template("subscribe.html")

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/interviewhelper")
def interviewhelper():
    return render_template("interviewhelper.html")

@app.route("/business_analyst")
def business_analyst():
    return render_template("business_analyst.html")

@app.route("/data_scientist")
def data_scientist():
    return render_template("data_scientist.html")

@app.route("/softwareEngineer")
def softwareEngineer():
    return render_template("softwareEngineer.html")

@app.route("/project_manager")
def project_manager():
    return render_template("project_manager.html")

@app.route("/data_engineer")
def data_engineer():
    return render_template("data_engineer.html")


@app.route("/uiux")
def uiux():
    return render_template("uiux.html")

@app.route("/data_analyst")
def data_analyst():
    return render_template("data_analyst.html")

@app.route("/DevOps")
def DevOps():
    return render_template("DevOps.html")

@app.route("/DMM")
def DMM():
    return render_template("DMM.html")

@app.route("/AIML")
def AIML():
    return render_template("AIML.html")

@app.route('/resume')
def resume_templates():
    # Define a list of templates with their URLs
    # templates = [
    #     {'name': 'New York Resume Template Creative', 'url': 'static/pdf/New-York-Resume-Template-Creative.pdf'},
    #     {'name': 'Moscow-Creative-Resume-Template', 'url': 'static/pdf/Moscow-Creative-Resume-Template.pdf'},
    #     {'name': 'Sydney-Resume-Template-Modern', 'url': 'static/pdf/Sydney-Resume-Template-Modern (1).pdf'},
    #     # Add more templates as needed
    # ]
    
    return render_template('resume.html')
@app.route("/subscribers")
def subscribers():
    return render_template("subscribers.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0' , port=80,debug=True)

