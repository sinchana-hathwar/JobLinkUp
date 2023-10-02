from flask import Flask
from flask import render_template, request, redirect, url_for
import sqlite3 
app = Flask(__name__)

conn = sqlite3.connect('database.db')
print ("Opened database successfully")

conn.execute('CREATE TABLE if not exists User (name TEXT,email TEXT, password TEXT, phone_no INT, DoB date, addr TEXT, city TEXT, pin TEXT, Qualification TEXT, About TEXT)')
conn.execute('CREATE TABLE if not exists Jobs (Company_name TEXT,Title TEXT, JD TEXT, Salary INT, Location TEXT, Duration TEXT)')
conn.execute('CREATE TABLE if not exists Templates (Template_name TEXT,Template_link TEXT)')

print ("Table created successfully")
conn.close()

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/jobs")
def jobs():
    return render_template('job.html')

@app.route("/premium")
def premium():
    return render_template('premium.html')

@app.route("/login")
def login():
    return render_template('loginpage.html')
@app.route('/adduser',methods = ['POST', 'GET'])
def adduser():
   if request.method == 'POST':
      try:
         uname = request.form['signup-username']
         email = request.form['signup-email']
         password = request.form['signup-password']


         with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO User (name,email,password) VALUES(?,?,?)",(uname, email, password) )
            #cur.execute("INSERT INTO Templates (Template_name) VALUES(?)", (email))
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"
         print(msg)
      
      finally: 
         return redirect(url_for("index"))
         con.close()
         
if __name__ == '__main__':
    app.run(debug= True)