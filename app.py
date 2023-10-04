import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

conn = sqlite3.connect("database.db")
print("Opened database successfully")

conn.execute(
    "CREATE TABLE if not exists User (name TEXT,email TEXT, password TEXT, phone_no INT, DoB date, addr TEXT,  pin TEXT, Qualification TEXT, Subject Text, About TEXT, IsSubscribed BOOLEAN DEFAULT 0, role TEXT DEFAULT 'job_seeker' )"
)
conn.execute(
    "CREATE TABLE if not exists Jobs (Company_name TEXT,Title TEXT, JD TEXT, Salary INT, Location TEXT, Duration TEXT)"
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


@app.route("/jobs")
def jobs():
    if "current_user" in session:
        return render_template("job.html")
    print("email not in session")
    return redirect(url_for("login"))


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


if __name__ == "__main__":
    app.run(debug=True)
