from flask import Flask , render_template , url_for , request , redirect , session, flash
import os , json , re 
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict
app = Flask(__name__)
app.secret_key = "kimiakarimipanteagholampour"
class DataManager:
    @staticmethod
    def load_data(file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

    @staticmethod
    def save_data(data, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
def calculate_distribution(registrations):
    distribution = {}
    for r in registrations:
        course = r.get("course")
        if course:
            distribution[course] = distribution.get(course, 0) + 1
    return distribution

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/AdminDashboard")
def AdminDashboard():
    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)
    courses_path = os.path.join(app.root_path, 'data' , 'students.json')
    courses = DataManager.load_data(courses_path)

    # distribution = {}
    # for student in students:
    #     for course in student.get("courses", []):
    #         distribution[course] = distribution.get(course, 0) + 1

    # chart_data = {
    #     "labels": [for course in distribution],
    #     "data": list(distribution.values())
    # }

    return render_template("AdminDashboard.html")

@app.route("/Addcourse", methods=["GET", "POST"])
def Addcourse():
    courses_path = os.path.join(app.root_path, 'data', 'courses.json')
    timetable_path = os.path.join(app.root_path, 'data', 'timetable.json')

    courses = DataManager.load_data(courses_path)
    timetable = DataManager.load_data(timetable_path)

    if request.method == "POST":
        name = request.form['name'].title()
        if name in courses:
            return render_template("Addcourse.html", error="Course already exists.")

        credit = request.form['credit']
        capacity = request.form['capacity']
        occupied = request.form['occupied']
        prerequisites = request.form.get('prerequisites', '').title()
        price = request.form['price']
        classes = request.form['classes']  

        day = request.form.get('day')
        time = request.form.get('time')

        new_course = {
            name: {
                "credit": credit,
                "capacity": capacity,
                "occupied": occupied,
                "prerequisites": prerequisites,
                "price": price,
                "classes": classes
            }
        }

        courses.update(new_course)
        DataManager.save_data(courses, courses_path)

        if day and time:
            if day not in timetable:
                timetable[day] = {}
            if time not in timetable[day]:
                timetable[day][time] = []
    return render_template("Addcourse.html")            

@app.route("/report")
def report():
    students_path = os.path.join(app.root_path, "data", "students.json")
    students = DataManager.load_data(students_path)
    courses_path= os.path.join(app.root_path, 'data', 'courses.json')
    courses = DataManager.load_data(courses_path)
    return render_template("report.html" , courses=courses ,students=students)

@app.route("/AdminLogin",methods=["GET", "POST"])
def AdminLogin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        admins_path = os.path.join(app.root_path, 'data', 'admins.json')
        admins = DataManager.load_data(admins_path)
        if email.endswith('@paia.com') and email in admins and admins[email] == password:
            return redirect(url_for('AdminDashboard'))
        else:
            error = "incorrect email or password!"
            return render_template("AdminLogin.html", error=error)
    return render_template("AdminLogin.html")

@app.route("/StudentLogin", methods=["GET", "POST"])
def StudentLogin():
    if request.method == "POST":
        StudentID = request.form.get('StudentID', '').strip()
        password = request.form.get('password', '').strip()

        if not StudentID or not password:
            return render_template("StudentLogin.html", error="Please enter both ID and password.")

        if len(StudentID) != 13:
            return render_template("StudentLogin.html", error="Student ID must be 13 digits long.")

        students_path = os.path.join(app.root_path, 'data', 'students.json')
        students = DataManager.load_data(students_path)

        if StudentID not in students:
            return render_template("StudentLogin.html", error="Student ID not found.")

        stored_hashed_password = students[StudentID]['password']

        if check_password_hash(stored_hashed_password, password):
            session["student_id"] = StudentID
            return redirect(url_for('StudentDashboard'))
        else:
            return render_template("StudentLogin.html", error="Incorrect password.")

    return render_template("StudentLogin.html")

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
@app.route("/StudentSignup", methods=["GET", "POST"])
def StudentSignup():
    if request.method == "POST":
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        password = request.form.get('password')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        nid = request.form.get('nid')
        sid = request.form.get('sid')

        student_path = os.path.join(app.root_path, 'data', 'students.json')
        data = DataManager.load_data(student_path)

        
        if not all([fname, lname, password, dob, gender, nid, sid]):
            return render_template("StudentSignup.html", error="Please fill out all the fields.")

        
        def is_valid_password(password):
            return len(password) >= 6 and any(char.isdigit() for char in password)

        if not is_valid_password(password):
            return render_template("StudentSignup.html", error="Password must be at least 6 characters and include numbers.")

        
        if sid in data:
            return render_template("StudentLogin.html", message="User already exists. Please log in.")

        
        hashed_password = generate_password_hash(password)
        student_data = {
            'first name': fname,
            'last name': lname,
            'password': hashed_password,
            'date of birth': dob,
            'gender': gender,
            'national ID': nid,
            'student ID': sid,
            'course list': [],
            'registered_courses': [],
            'paid_courses': [],
            'courses': {
                "Saturday": {"8-10": [], "10-12": [], "12-14": [], "14-16": [], "16-18": []},
                "Sunday": {"8-10": [], "10-12": [], "12-14": [], "14-16": [], "16-18": []},
                "Monday": {"8-10": [], "10-12": [], "12-14": [], "14-16": [], "16-18": []},
                "Tuesday": {"8-10": [], "10-12": [], "12-14": [], "14-16": [], "16-18": []},
                "Wednesday": {"8-10": [], "10-12": [], "12-14": [], "14-16": [], "16-18": []}
            }
        }

        
        data[sid] = student_data
        DataManager.save_data(data, student_path)

        
        session["student_id"] = sid
        return redirect(url_for("StudentDashboard"))

    
    return render_template("StudentSignup.html")

@app.route("/StudentDashboard",methods=["GET", "POST"])
def StudentDashboard():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("StudentLogin"))
    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)
    student_data = students.get(student_id)
    if not student_data:
        return redirect(url_for("StudentLogin"))
    return render_template("StudentDashboard.html", student= student_data)

@app.route("/SeptemberTermCalender")
def SeptemberTermCalender():
    timetable = DataManager.load_data("main/data/timetable.json")
    courses = DataManager.load_data("main/data/courses.json")
    return render_template("SeptemberTermCalender.html", timetable=timetable, courses=courses)
@app.route("/registercourse", methods=["GET", "POST"])
def registercourse():
    courses_path = os.path.join(app.root_path, "data", "courses.json")
    courses = DataManager.load_data(courses_path)

    if request.method == "POST":
        student_id = session.get("student_id")
        
        students_path = os.path.join(app.root_path, "data", "students.json")
        timetable_path = os.path.join(app.root_path, "data", "timetable.json")

        students = DataManager.load_data(students_path)
        timetable = DataManager.load_data(timetable_path)

        course_name = request.form.get("course")

        student = students.get(student_id)
        if not student:
            flash("Student data not found.", "danger")
            return redirect(url_for("registercourse"))

        
        total_credit = sum(courses[c]["credit"] for c in student.get("registered_courses", []) if c in courses)
        if total_credit + courses[course_name]["credit"] > 20:
            flash("Cannot register more than 20 credits.", "danger")
            return redirect(url_for("registercourse"))

        
        prereqs_raw = courses[course_name].get("prequisites", "")
        prereqs = [p.strip() for p in prereqs_raw.split(",")] if prereqs_raw else []
        prereqs = [p for p in prereqs if p] 

        if not all(p in student.get("registered_courses", []) for p in prereqs):
            flash(f"Prerequisites not met: {', '.join(prereqs)}", "danger")
            return redirect(url_for("registercourse"))

        
        if courses[course_name]["occupied"] >= courses[course_name]["capacity"]:
            flash("Course is full.", "danger")
            return redirect(url_for("registercourse"))

        student_courses = student.get("registered_courses", [])
        for day, slots in timetable.items():
            for time_slot, slot_courses in slots.items():
                if course_name in slot_courses:
                    if any(c in slot_courses for c in student_courses):
                        flash("Time conflict detected with another registered course.", "danger")
                        return redirect(url_for("registercourse"))
        session["pending_course"] = course_name
        return redirect(url_for("payment"))

    return render_template("registercourse.html", courses=courses)

@app.route("/FAQ", methods=["GET"])
def FAQ():
    return render_template("FAQ.html")
@app.route('/payment', methods=["GET"])
def payment():
    student_id = session.get("student_id")
    courses_path = os.path.join(app.root_path, 'data', 'courses.json')
    all_courses = DataManager.load_data(courses_path)
    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)
    student = students.get(student_id, {})
    paid_courses = student.get("paid_courses", [])
    selected_courses = []
    for name, course_data in all_courses.items():
        course_data = course_data.copy() 
        course_data["name"] = name
        course_data["paid"] = name in paid_courses
        selected_courses.append(course_data)

    return render_template("payment.html", selected_courses=selected_courses)
 

@app.route("/checkout", methods=["POST"])
def checkout():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("StudentLogin"))  
    course_name = request.form.get("course_name")
    if not course_name:
        return "Course name is missing", 400

    students_path = os.path.join(app.root_path, 'data', 'students.json')
    student_data = DataManager.load_data(students_path)

    if student_id not in student_data:
        return "Student ID not found in data", 404

    
    if course_name not in student_data[student_id].get("registered_courses", []):
        student_data[student_id]["registered_courses"].append(course_name)

    
    if course_name not in student_data[student_id].get("paid_courses", []):
        student_data[student_id]["paid_courses"].append(course_name)

    DataManager.save_data(student_data, students_path)

    return redirect(url_for("payment"))


@app.route('/payment_success', methods=["POST"])
def payment_success():
    course_name = request.form.get("course_name")
    student_id = session.get("student_id")

    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)

    if student_id in students and course_name:
        student = students[student_id]
        paid_courses = student.get("paid_courses", [])
        if course_name not in paid_courses:
            paid_courses.append(course_name)
            student["paid_courses"] = paid_courses
            students[student_id] = student
            DataManager.save_data(students_path, students)

    return redirect(url_for("payment"))
@app.route('/payment_failed', methods=["POST"])
def payment_failed():
    return redirect(url_for("payment"))
@app.route("/coursecontent/<course_name>")
def coursecontent(course_name):
    pass

@app.route("/mycourses")
def mycourses():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("StudentLogin"))
    students_path = os.path.join(app.root_path, "data", "students.json")
    courses_path = os.path.join(app.root_path, "data", "courses.json")
    students = DataManager.load_data(students_path)
    courses = DataManager.load_data(courses_path)
    student = students.get(student_id)
    registered_courses = student.get("registered_courses", [])
    registered_courses_info = {course: courses.get(course, {}) for course in registered_courses}
    return render_template("mycourses.html", courses=registered_courses_info)

@app.route('/query', methods=["GET","POST"])
def query():
    return render_template("query.html")
@app.route('/project', methods=["GET"])
def project():
    return render_template("project.html")
@app.route('/administrator', methods=["GET"])
def administrator():
    return render_template("administrator.html")

if __name__ == "__main__":
    app.run(debug=True)
    