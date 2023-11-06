import os
import sqlite3
import random
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)
from werkzeug.utils import secure_filename
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "doc", "docx"}
app.config["MAX_CONTENT_PATH"] = 5 * 1000 * 1000

# Ensure the upload folder exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    "CREATE TABLE if not exists User (name TEXT,email TEXT, password TEXT, phone_no INT, DoB date, addr TEXT,  pin TEXT, Qualification TEXT, Subject Text, About TEXT, IsSubscribed BOOLEAN DEFAULT 0, role TEXT DEFAULT 'job_seeker', resume TEXT, pfp TEXT )"
)

conn.execute(
    "CREATE TABLE if not exists Jobs (ID INTEGER PRIMARY KEY AUTOINCREMENT,Company_name TEXT NOT NULL,Title TEXT NOT NULL,Salary INTEGER,Location TEXT,Duration TEXT,Description TEXT,Responsibilities TEXT,Qualification TEXT)"
)
conn.execute(
    "CREATE TABLE if not exists Templates (Template_name TEXT,Template_link TEXT)"
)
conn.execute(
    "CREATE TABLE if not exists JobsApplied (email Text NOT NULL, JobID TEXT NOT NULL)"
    #add make them foreign keys if required later
)

print("Table created successfully")
conn.commit()
conn.close()


def get_db_connection():
    conn = sqlite3.connect("./database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=("GET", "POST"))
def index():
    if "current_user" in session:
        if request.method == "POST":
            job_title = request.form.get("job_title")
            location = request.form.get("location")
            company_name = request.form.get("company_name")

            search_filter = {
                "job_title": job_title,
                "location": location,
                "company_name": company_name,
            }
            print(search_filter)
            return redirect(url_for("jobs", search_filter=json.dumps(search_filter)))
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


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "current_user" not in session:
        print("email not in session")
        return redirect(url_for("login"))

    email = session["current_user"][1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE email=?", (email,))
    user = cursor.fetchone()

    try:
        if request.method == "POST":
            name = request.form.get("user_name")
            phone = request.form.get("phone")
            pincode = request.form.get("pincode")
            location = request.form.get("location")
            dob = request.form.get("birthday")
            qualification = request.form.get("degree")
            subject = request.form.get("subject")
            role = request.form.get("joblinkup-usage")
            about = request.form.get("aboutuser")

            cursor.execute(
                """
                UPDATE User SET name = ?, phone_no=?, pin=?, addr=?, DoB=?, Qualification=?, 
                Subject=?, role=?, about = ? WHERE email=?
                """,
                (
                    name,
                    phone,
                    pincode,
                    location,
                    dob,
                    qualification,
                    subject,
                    role,
                    about,
                    email,
                ),
            )
            print("updated")

            conn.commit()

            flash("Profile updated successfully!", "success")

            if "resume" in request.files:
                print("entered if resume")
                f = request.files["resume"]
                if f.filename != "" and allowed_file(f.filename):
                    print("entered if")
                    query = conn.execute(
                        "SELECT resume FROM User WHERE email = ?", (email,)
                    )
                    data = query.fetchone()
                    old_filename = data[0]
                    if old_filename != None:
                        old_filepath = os.path.join(
                            app.config["UPLOAD_FOLDER"], old_filename
                        )
                        if os.path.exists(old_filepath):
                            os.remove(old_filepath)
                    filename = secure_filename(f.filename)
                    filepath = os.path.join(
                        app.config["UPLOAD_FOLDER"], secure_filename(f.filename)
                    )
                    print("filepath", filepath)
                    f.save(os.path.join("uploads", secure_filename(f.filename)))
                    flash("Upload successful")
                    cursor.execute(
                        "UPDATE User SET resume = ? WHERE email = ?",
                        (secure_filename(f.filename), email),
                    )
                    conn.commit()
                    print("updated")
                    cursor.execute("SELECT * FROM User WHERE email=?", (email,))
                    user = cursor.fetchone()
                    #session["current_user"] = user

            if "pfp" in request.files:
                f = request.files["pfp"]
                
                if f.filename != "":
                    
                    allowed_filetype = ["png", "jpg", "jpeg"]
                    if f.filename.split('.')[1] in allowed_filetype:
                        
                        ext = f.filename.split(".")[1]
                        print("pfp passed checks")
                        filename = secure_filename(f.filename)
                        filepath = os.path.join("profilePictures/", email + "." + ext)
                        print("filepath", filepath)
                        f.save(os.path.join("static/profilePictures/", email + "." + ext))
                        flash("Upload successful")
                        cursor.execute(
                            "UPDATE User SET pfp = ? WHERE email = ?",
                            (filepath, email),
                        )
                        conn.commit()
                        print("updated")
                        cursor.execute("SELECT * FROM User WHERE email=?", (email,))
                        user = cursor.fetchone()
                        # session["current_user"] = user

                print(f)

            return redirect(url_for("profile"))
    except Exception as e:
        print("proof",str(e))
        flash("An error occurred while updating your profile.", "error")
    finally:
        conn.close()
    return render_template("profile.html", user=user)


@app.route("/login")
def login():
    return render_template("loginpage.html")


@app.route("/loginuser", methods=["POST", "GET"])
def loginuser():
    if request.method == "POST":
        try:
            print("entered try")
            login_email = request.form.get("login_email")
            login_password = request.form.get("login_password")
            print("login_email", login_email)
            print("login_password", login_password)

            if not login_email or not login_password:
                flash("Please enter email and password")
                print("Please enter email and password")
                return redirect(url_for("login") + "#0")

            print("login_email", login_email)
            print("login_password", login_password)

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                user = cur.execute(
                    "SELECT * FROM User WHERE email = ?", (login_email,)
                ).fetchall()

                if len(user) == 0:
                    # flash("Invalid Email")
                    print("Invalid Email")
                    return redirect(url_for("login"))
                elif user[0][2] != login_password:
                    # flash("Invalid Password")
                    print("Invalid Password")
                    return redirect(url_for("login"))

                # session["email"] = login_email
                # session["name"] = user[0][0]
                # session["password"] = user[0][2]
                session["current_user"] = user[0]
                print("current_user", session["current_user"])

        except:
            print("login failed")
            # flash("Something went wrong, please try again")
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
                return redirect(url_for("profile"))
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
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


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

    companies = [
        "TCS",
        "IBM",
        "Infosys",
        "Wipro",
        "Accenture",
        "Dell",
        "ABB",
        "Microsoft",
        "Google",
        "Amazon",
    ]
    job_titles = [
        "Software Engineer",
        "Data Analyst",
        "Web Developer",
        "Database Administrator",
        "Network Engineer",
        "UX Designer",
        "Digital Marketing Specialist",
        "Business Analyst",
        "AI/ML Engineer",
        "DevOps Engineer",
    ]
    locations = ["Bangalore", "Pune", "Chennai", "Hyderabad", "Mumbai"]

    job_data = {
        "Software Engineer": {
            "qualification": 
            """Bachelor's degree in Computer Science or related field
            Proficiency in programming languages (e.g., Java, Python, C++) and software development methodologies.
            Problem-solving skills and strong analytical thinking.""",
            "description":
            """Software engineers design, develop, test, and maintain software applications and systems. They collaborate with cross-functional teams to create high-quality software solutions
            Join our team as a Software Engineer and work on cutting-edge software projects.""",
            "responsibilities":
            """Develop and maintain software applications.
            Writing and debugging code.
            Collaborating with other engineers and product managers.
            Maintaining code quality and documentation.
            Solving technical challenges and implementing software enhancements.""",
        },
        "Data Analyst": {
            "qualification":
            """Bachelor's degree in Statistics, Data Science, or related field
            Proficiency in data analysis and data visualization tools (e.g., Excel, SQL, Tableau, Power BI).
            Strong analytical and problem-solving skills""",
            "description": 
            """Data analysts are responsible for collecting, processing, and analyzing data to support data-driven decision-making within an organization. 
            They help extract insights from data to drive business growth and efficiency.
            Become a Data Analyst and analyze data to provide valuable insights.""",
            "responsibilities":
            """Collect, clean, and analyze data to support business decisions.
            Create data visualizations, reports, and dashboards to present findings to non-technical stakeholders.
            Work with cross-functional teams to understand business needs and provide actionable data insights.
            Effectively communicate findings and recommendations to both technical and non-technical audiences.""",
        },
        "Web Developer": {
            "qualification": 
            """Bachelor's degree in Web Development or related field
            Proficiency in web development languages and technologies, including HTML, CSS, JavaScript, and frameworks like React or Angular.
            Strong problem-solving and critical-thinking skills.""",
            "description": 
            """Web developers are responsible for designing, building, and maintaining websites and web applications.
             They work on the front-end (user interface) and/or back-end (server-side) aspects of websites.
             Join us as a Web Developer and create stunning websites and web applications.""",
            "responsibilities": """Design and develop web solutions for clients.
            Creating user-friendly and visually appealing website interfaces.
            Implementing responsive web design to ensure compatibility across various devices and screen sizes.
            Collaborating with UI/UX designers to turn design mockups into functional web pages.
            Conducting testing and quality assurance to identify and resolve issues.
             Debugging and troubleshooting web application errors.
             Staying up-to-date with the latest web development trends, technologies, and best practices.""",
        },
        "Database Administrator": {
            "qualification": 
            """Strong knowledge of database management systems (e.g., Oracle, SQL Server, MySQL, PostgreSQL).
             Proficiency in SQL (Structured Query Language).
            Problem-solving and analytical skills.
            Bachelor's degree in Database Management or related field""",
            "description": 
            """Database administrators are responsible for managing and maintaining databases to ensure data integrity, availability, and security. 
            They work with database management systems (DBMS) and collaborate with development and IT teams.
            Work as a Database Administrator and manage databases for optimal performance.""",
            "responsibilities": 
            """Database Design and Implementation
            Data Security and Access Control
            Backup and Recovery
            Performance Tuning and Monitoring
            Data Migration and Integration
            Ensure data security and efficient database operations.""",
        },
        "Network Engineer": {
            "qualification": 
            """Bachelor's degree in Network Engineering or related field
            Strong knowledge of networking technologies and protocols.
            Certifications such as Cisco CCNA/CCNP, CompTIA Network+, or relevant industry-specific certifications.
            Problem-solving skills and analytical thinking.""",
            "description":
             """Network engineers design, implement, maintain, and manage an organization's network infrastructure.
             They ensure that network systems are secure, reliable, and efficient, enabling data communication and connectivity.
            Join our team as a Network Engineer and build and maintain network infrastructure.""",
            "responsibilities": 
            """Network Design and Planning
            Network Implementation
            Network Upgrades and Expansion
            Network Monitoring and Alerts
            Network Security
            Design and implement network solutions to meet business needs.""",
        },
        "UX Designer": {
            "qualification":
            """Bachelor's degree in UX/UI Design or related field
            Proficiency in design tools (e.g., Adobe XD, Sketch, Figma).
            Strong understanding of user-centered design principles.""",
            "description": 
            """UI/UX designers create user-friendly and visually appealing interfaces for web and mobile applications.
             They focus on user experience, interaction design, and usability.
            Become a UX Designer and create user-centered designs for web and mobile applications.""",
            "responsibilities":
            """Conducting user research and testing.
            Creating wireframes, prototypes, and mockups.
            Collaborating with developers to implement designs.
            Ensuring a seamless and intuitive user experience.
            Design intuitive and visually appealing user interfaces.""",
        },
        "Digital Marketing Specialist": {
            "qualification": 
            """Bachelor's degree in Marketing or related field
            Proficiency in digital marketing tools and platforms, including Google Ads, social media advertising, email marketing, and SEO (Search Engine Optimization).
            Strong analytical and data-driven decision-making skills.""",
            "description":
            """Digital marketing specialists are responsible for planning and executing online marketing strategies to drive brand awareness, engagement, and lead generation.
             They leverage various digital channels to reach target audiences and achieve marketing goals.
            Join as a Digital Marketing Specialist and drive online marketing campaigns.""",
            "responsibilities":
            """Digital Marketing Strategy
            Search Engine Optimization (SEO)
            Online Advertising and Remarketing
            Budget Management
            Plan and execute digital marketing strategies.""",
        },
        "Business Analyst": {
            "qualification": 
            """Bachelor's degree in Business Administration or related field
            Strong analytical and problem-solving skills.
            Business analysis certification (e.g., CBAP).""",
            "description": 
            """Business analysts bridge the gap between business needs and technology solutions.
             They identify business requirements and propose system improvements.
            Work as a Business Analyst and analyze business processes.""",
            "responsibilities":
            """Gathering and documenting business requirements.
            Analyzing data and processes to identify opportunities for improvement.
            Collaborating with stakeholders to define project scope and objectives.
            Developing business cases and recommending solutions.
            Gather and document business requirements.""",
        },
        "AI/ML Engineer": {
            "qualification":
             """Proficiency in programming languages (e.g., Python) and machine learning frameworks (e.g., TensorFlow, PyTorch).
            Strong problem-solving and critical-thinking skills
            Bachelor's degree in Computer Science or AI/ML""",
            "description":
            """AI/ML engineers design, develop, and deploy machine learning models and AI systems. 
            They work with large datasets, develop algorithms, and create predictive models. 
            Join as an AI/ML Engineer and develop machine learning models.""",
            "responsibilities":
            """ Developing and implementing machine learning models and algorithms.
            Collaborating with data scientists and domain experts to understand industry-specific problems and solutions.
            Building, testing, and deploying machine learning models in production environments.
            Optimizing models for performance, scalability, and efficiency.
            Staying up-to-date with the latest AI and ML technologies and best practices.
            Design and train AI/ML algorithms.""",
        },
        "DevOps Engineer": {
            "qualification": 
            """Bachelor's degree in Computer Science or related field
            Proficiency in scripting and automation tools (e.g., Bash, Python).
            Knowledge of DevOps practices, CI/CD (Continuous Integration/Continuous Deployment), and cloud platforms (e.g., AWS, Azure).""",
            "description": 
            """DevOps engineers focus on automating and streamlining software development and IT operations. 
            They aim to shorten the software development lifecycle and improve the quality of code.
            Join as a DevOps Engineer and automate software development processes.""",
            "responsibilities": 
            """Implementing and maintaining CI/CD pipelines.
            Automating manual tasks and processes.
           Ensuring system stability, scalability, and security.
           Collaborating with development and operations teams.
            Build and maintain CI/CD pipelines.""",
        },
    }

    for company in companies:
        for _ in range(5):  # Insert 5 job listings per company (adjust as needed)
            title = random.choice(job_titles)
            salary = random.randint(50000, 150000)
            location = random.choice(locations)
            duration = random.choice(["Full-time", "Part-time", "Contract"])
            company_description = job_data.get(title, {}).get(
                "description", "Description not available"
            )
            company_responsibilities = job_data.get(title, {}).get(
                "responsibilities", "Responsibilities not available"
            )
            qualification = job_data.get(title, {}).get(
                "qualification", "Qualification not available"
            )

            # Replace this with your actual data insertion logic into your database table
            insert_sql = """
            INSERT INTO Jobs (Company_name, Title, Salary, Location, Duration, Description, Responsibilities, Qualification)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            job_data_tuple = (
                company,
                title,
                salary,
                location,
                duration,
                company_description,
                company_responsibilities,
                qualification,
            )

            cur.execute(insert_sql, job_data_tuple)

    conn.commit()
    conn.close()


# Call the function to populate job listings
populate_job_listings()


@app.route("/jobs", methods=["GET"])
def jobs():
    search_filter = request.args.get("search_filter", default=json.dumps({}), type=str)
    search_filter = json.loads(search_filter)
    print(search_filter, "are the search filters")
    conn = sqlite3.connect("./database.db")
    cursor = conn.cursor()

    # Execute a query to fetch job listings from the database
    if (search_filter == {}) or (
        (search_filter["job_title"] == "All")
        and (search_filter["company_name"] == "")
        and (search_filter["location"] == "All Locations")
    ):
        cursor.execute("SELECT * FROM Jobs")

    elif (
        (search_filter["job_title"] == "All")
        and (search_filter["company_name"] != "")
        and (search_filter["location"] != "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Company_name like ? and Location = ? ",
            ("%" + search_filter["company_name"] + "%", search_filter["location"]),
        )

    elif (
        (search_filter["job_title"] != "All")
        and (search_filter["company_name"] == "")
        and (search_filter["location"] != "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Title = ? and Location = ? ",
            (search_filter["job_title"], search_filter["location"]),
        )

    elif (
        (search_filter["job_title"] != "All")
        and (search_filter["company_name"] != "")
        and (search_filter["location"] == "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Company_name like ? and Title = ? ",
            ("%" + search_filter["company_name"] + "%", search_filter["job_title"]),
        )

    elif (
        (search_filter["job_title"] != "All")
        and (search_filter["company_name"] != "")
        and (search_filter["location"] != "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Company_name like ? and Title = ? and Location = ?",
            (
                "%" + search_filter["company_name"] + "%",
                search_filter["job_title"],
                search_filter["location"],
            ),
        )

    elif (
        (search_filter["job_title"] != "All")
        and (search_filter["company_name"] == "")
        and (search_filter["location"] == "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Title = ? ", (search_filter["job_title"],)
        )
    elif (
        (search_filter["job_title"] == "All")
        and (search_filter["company_name"] != "")
        and (search_filter["location"] == "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Company_name like ?",
            ("%" + search_filter["company_name"] + "%",),
        )
    elif (
        (search_filter["job_title"] == "All")
        and (search_filter["company_name"] == "")
        and (search_filter["location"] != "All Locations")
    ):
        cursor.execute(
            "SELECT * FROM Jobs where Location = ? ", (search_filter["location"],)
        )

    # Fetch all job listings as a list of dictionaries
    job_listings = []
    for row in cursor.fetchall():
        (
            job_id,
            company_name,
            title,
            salary,
            location,
            duration,
            description,
            responsibilities,
            qualification,
        ) = row
        job = {
            "ID": job_id,
            "company": company_name,
            "title": title,
            "salary": salary,
            "location": location,
            "duration": duration,
            "description": description,
            "responsibilities": responsibilities,
            "qualification": qualification,
        }
        job_listings.append(job)

    no_results = False
    if not job_listings:
        no_results = True
        cursor.execute("SELECT * FROM Jobs")
        for row in cursor.fetchall():
            (
                job_id,
                company_name,
                title,
                salary,
                location,
                duration,
                description,
                responsibilities,
                qualification,
            ) = row
            job = {
                "ID": job_id,
                "company": company_name,
                "title": title,
                "salary": salary,
                "location": location,
                "duration": duration,
                "description": description,
                "responsibilities": responsibilities,
                "qualification": qualification,
            }
            job_listings.append(job)
    conn.commit()
    conn.close()

    return render_template("job.html", job_listings=job_listings, no_results=no_results)


# Rest of your routes and code...
# ... (Previous code)


@app.route("/job_details/<int:job_id>")
def job_details(job_id):
    conn = sqlite3.connect("./database.db")
    cursor = conn.cursor()
    job_id = int(job_id)
    applied = False
    job = cursor.execute("SELECT * FROM Jobs WHERE ID = ?", (job_id,)).fetchone()
    print("binding passed are", session["current_user"][1])

    applied_jobs = cursor.execute("SELECT * FROM JobsApplied WHERE email = ?", (session["current_user"][1],)).fetchall()
   
    if(len(applied_jobs)>0):
        applied_jobs = applied_jobs[0][1].split(",")
        print("applied jobs are ", applied_jobs)
        if str(job_id) in applied_jobs:
            applied = True
    # job = cursor.fetchone()
    conn.commit()
    conn.close()
    rendered_job = {"job":job,"applied":applied}
    print("job details: ", rendered_job)
    return render_template("job_details.html", rendered_job = rendered_job)

@app.route("/add_job", methods=["GET", "POST"])
def add_job():
    
    if request.method == "POST":
        conn = sqlite3.connect("./database.db")
        cur = conn.cursor()
        jobId = request.form["job_id"]
        print("applied job id: ", jobId, session["current_user"][1])
        applied_jobs = cur.execute(
            "SELECT * FROM JobsApplied WHERE email = ?", (session["current_user"][1],)
        ).fetchall()
        if not applied_jobs:
            cur.execute("INSERT INTO JobsApplied values (?,?)", (session["current_user"][1], jobId))
        else:
            current_jobs = str(applied_jobs[0][1])
            current_jobs_arr = current_jobs.split(",")
            if jobId in current_jobs_arr:
                return redirect(url_for("jobs"))
            cur.execute("UPDATE JobsApplied SET JobID = ? WHERE email = ?", (current_jobs + "," + str(jobId), session["current_user"][1]))
        conn.commit()           

        conn.close()
        return redirect(url_for("jobs"))
   


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


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


@app.route("/uploader", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "resume" not in request.files:
            flash("File not found")
            return redirect(url_for("profile"))
        f = request.files.get("resume")
        if f is None or f.filename == "" or not allowed_file(f.filename):
            flash("Invalid file")
            return redirect(request.url)
        if f.filename != "":
            email = session["current_user"][1]
            print(email)
            # Fetch the old filename from the database
            query = conn.execute("SELECT resume FROM users WHERE email = ?", (email,))
            data = query.fetchone()
            old_filename = data[0]
            # Delete the old file in the folder
            # if old_filename == None:
            #     filename = secure_filename(f.filename)
            #     filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
            #     f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            #     flash('Upload successful')
            #     conn.execute('UPDATE users SET resume = ? WHERE email = ?', (secure_filename(f.filename),email))
            if old_filename != None:
                old_filepath = os.path.join(app.config["UPLOAD_FOLDER"], old_filename)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            # Save the new file
            filename = secure_filename(f.filename)
            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"], secure_filename(f.filename)
            )
            f.save(
                os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename))
            )
            flash("Upload successful")
            # Update the new filename in the database
            conn.execute(
                "UPDATE users SET resume = ? WHERE email = ?",
                (secure_filename(f.filename), email),
            )
            print("updated")
            # else:
            #     conn.execute('UPDATE users SET resume = ? WHERE email = ?', (secure_filename(f.filename),email))
            conn.commit()
            return redirect(url_for("profile"))
        conn.close()


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


@app.route("/resume")
def resume_templates():
    # Define a list of templates with their URLs
    # templates = [
    #     {'name': 'New York Resume Template Creative', 'url': 'static/pdf/New-York-Resume-Template-Creative.pdf'},
    #     {'name': 'Moscow-Creative-Resume-Template', 'url': 'static/pdf/Moscow-Creative-Resume-Template.pdf'},
    #     {'name': 'Sydney-Resume-Template-Modern', 'url': 'static/pdf/Sydney-Resume-Template-Modern (1).pdf'},
    #     # Add more templates as needed
    # ]

    return render_template("resume.html")


@app.route("/subscribers")
def subscribers():
    return render_template("subscribers.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
