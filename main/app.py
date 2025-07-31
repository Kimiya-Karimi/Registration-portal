from flask import Flask , render_template , url_for , request , redirect
import os , json , re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
class DataManager:
    @staticmethod
    def load_data(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    @staticmethod
    def save_data(data, file_path):
        with open (file_path, "w") as f:
            json.dump(data, f, indent=4)
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/AdminDashboard")
def AdminDashboard():
    return render_template("AdminDashboard.html")  
@app.route("/AdminLogin",methods=["GET", "POST"])
def AdminLogin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        admins_path = os.path.join(app.root_path, 'data', 'admins.json')
        admins = DataManager.load_data(admins_path)
        if email.endswith('@paia.ir') and email in admins and admins[email] == password:
            return redirect(url_for('AdminDashboard'))
        else:
            error = "incorrect email or password!"
            return render_template("AdminLogin.html", error=error)
    return render_template("AdminLogin.html")
@app.route("/StudentLogin",methods=["GET", "POST"])
def StudentLogin():
    if request.method == "POST":
        StudentID = request.form['StudentID']
        password = request.form['password']
        students_path = os.path.join(app.root_path, 'data', 'students.json')
        students = DataManager.load_data(students_path)
        if not StudentID or not password:
            return render_template("StudentLogin.html", error="Please enter both ID and password.")
        if StudentID in students:
            stored_hashed_password = students[StudentID]['password']

            if not len(StudentID) == 13:
                return render_template("StudentLogin.html", error="Student ID must be 13 digits long.")

            if check_password_hash(stored_hashed_password, password):
                return redirect(url_for('StudentDashboard'))
            else:
                return render_template("StudentLogin.html", error="Incorrect password.")
        else:
            return render_template("StudentLogin.html", error="Student ID not found.")
        
    return render_template("StudentLogin.html")    
@app.route("/SeptemberTermCalender")
def SeptemberTermCalender():
    return render_template("SeptemberTermCalender.html")
@app.route("/AvailableCourses")
def AvailableCourses():
    courses_path= os.path.join(app.root_path, 'data', 'courses.json')
    courses = DataManager.load_data(courses_path)
    return render_template("AvailableCourses.html" , courses=courses)
@app.route("/students")
def students():
    students_path= os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)
    return render_template("students.html" , students=students)
@app.route("/StudentSignup",methods=["GET","POST"])
def StudentSignup():
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        dob =request.form['dob']
        gender = request.form['gender']
        nid = request.form['nid']
        sid =request.form['sid']  
        student_path = os.path.join(app.root_path, 'data', 'students.json')
        data = DataManager.load_data(student_path)  
        if not fname or not lname or not password or not dob or not gender or not nid or not sid:
            return render_template("StudentSignup.html", error="Please fill out all the fields.")
        def is_valid_password(password):
            return len(password) >= 6 and any(char.isdigit() for char in password)
        if not is_valid_password(password):
            return render_template("StudentSignup.html", error="Password must be at least 6 characters and include numbers.")
        if sid in data :
            return render_template("StudentLogin.html",message = "User already exists. Please log in.")
        else:
            student_data={
                'first name':fname,
                'last name':lname,
                'password': hashed_password,
                'date of birth':dob,
                'gender':gender,
                'national ID':nid,
                'student ID':sid,
                'course list':[],
                'courses':{
                "Saturday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
                "Sunday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
                "Monday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
                "Tuesday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
                "Wednesday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]}}
            }
        data[sid]= student_data
        DataManager.save_data(data, student_path)
    return render_template("StudentSignup.html")
@app.route("/StudentDashboard")
def StudentDashboard():
    return render_template("StudentDashboard.html")
if __name__ == "__main__":
    app.run(debug=True)
    