from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

conn = sqlite3.connect("database.db")
print("Opened database successfully")

conn.execute(
    "CREATE TABLE if not exists User (name TEXT,email TEXT, password TEXT, phone_no INT, DoB date, addr TEXT, city TEXT, pin TEXT, Qualification TEXT, About TEXT)"
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
    if "email" in session:
        return render_template("index.html")
    print("email not in session")
    return redirect(url_for("login"))


@app.route("/about")
def about():
    print(session)
    if "email" in session:
        return render_template("about.html")
    print("email not in session")
    return redirect(url_for("login"))


@app.route("/jobs")
def jobs():
    if "email" in session:
        return render_template("job.html")
    print("email not in session")
    return redirect(url_for("login"))


@app.route("/premium")
def premium():
    if "email" in session:
        return render_template("premium.html")
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
            # print("login_email", login_email)
            login_password = request.form["login_password"]
            # print("login_password", login_password)
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                user = cur.execute(
                    "SELECT * FROM User WHERE email = ?", (login_email,)
                ).fetchall()
                print("Users are", user)
                if len(user) == 0:
                    flash("Invalid Email")
                    print("Invalid Email")
                    return redirect(url_for("login"))
                elif user[0][2] != login_password:
                    flash("Invalid Password")
                    print("Invalid Password")
                    return redirect(url_for("login"))

                session["email"] = login_email
                session["name"] = user[0][0]
                session["password"] = user[0][2]

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
    session.pop("username", None)
    session.pop("email", None)
    session.pop("password", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
