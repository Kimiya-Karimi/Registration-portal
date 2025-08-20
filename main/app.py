from flask import Flask , render_template , url_for , request , redirect , session, flash, jsonify, g
import os , json , re, logging, uuid, time 
from werkzeug.security import generate_password_hash, check_password_hash
from logging.handlers import RotatingFileHandler
app = Flask(__name__)
app.secret_key = "kimiakarimipanteagholampour"
os.makedirs("logs", exist_ok=True)

app_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
)
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
))
app.logger.setLevel(logging.INFO)
app.logger.addHandler(app_handler)
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
<<<<<<< Updated upstream
@app.before_request
def _start_timer():
    g._start_time = time.time()
    g._rid = str(uuid.uuid4())[:8]  
@app.after_request
def _log_request(response):
    try:
        duration_ms = int((time.time() - g._start_time) * 1000)
    except Exception:
        duration_ms = -1
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "-")
    app.logger.info(
        f"REQ {g._rid} | {ip} | {request.method} {request.path} "
        f"| {response.status_code} | {duration_ms}ms | UA={ua}"
    )
    return response
@app.errorhandler(Exception)
def _handle_exception(e):
    app.logger.exception(f"ERR {getattr(g, '_rid', '-')}: Unhandled exception")
    return "Internal Server Error", 500
def log_event(event, **fields):
    app.logger.info("EVENT | %s | %s", event, fields)
=======

>>>>>>> Stashed changes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/AdminDashboard")
def AdminDashboard():
    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)
    courses_path = os.path.join(app.root_path, 'data' , 'students.json')
    courses = DataManager.load_data(courses_path)

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
        log_event(
            "course_added",
            course_name=name,
            credit=credit,
            capacity=capacity,
            occupied=occupied,
            prerequisites=prerequisites,
            price=price,
            classes=classes,
            day=day,
            time=time
        )
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
            log_event("admin_login_success", email=email)
            return redirect(url_for('AdminDashboard'))
        else:
            log_event("admin_login_failed", email=email)
            error = "incorrect email or password!"
            return render_template("AdminLogin.html", error=error)
    
    return render_template("AdminLogin.html")


@app.route("/StudentLogin", methods=["GET", "POST"])
def StudentLogin():
    if request.method == "POST":
        StudentID = request.form.get('StudentID', '').strip()
        password = request.form.get('password', '').strip()

        if not StudentID or not password:
            log_event("student_login_failed", reason="missing_fields", student_id=StudentID)
            return render_template("StudentLogin.html", error="Please enter both ID and password.")

        if len(StudentID) != 13:
            log_event("student_login_failed", reason="invalid_id_length", student_id=StudentID)
            return render_template("StudentLogin.html", error="Student ID must be 13 digits long.")

        students_path = os.path.join(app.root_path, 'data', 'students.json')
        students = DataManager.load_data(students_path)

        if StudentID not in students:
            log_event("student_login_failed", reason="invalid_student_id", student_id=StudentID)
            return render_template("StudentLogin.html", error="Student ID not found.")

        stored_hashed_password = students[StudentID]['password']

        if check_password_hash(stored_hashed_password, password):
            log_event("student_login_success", student_id=StudentID)
            session["student_id"] = StudentID
            return redirect(url_for('StudentDashboard'))
        else:
            log_event("student_login_failed",reason="wrong_password",student_id=StudentID)
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
        fname = request.form.get('fname', '').strip()
        lname = request.form.get('lname', '').strip()
        password = request.form.get('password', '').strip()
        dob_day = request.form.get('dob_day')
        dob_month = request.form.get('dob_month')
        dob_year = request.form.get('dob_year')
        if not (dob_day and dob_month and dob_year):
            log_event("student_signup_failed", reason="missing_dob", sid=None)
            return render_template("StudentSignup.html", error="Please enter your complete date of birth.")
        dob = f"{dob_year.zfill(4)}/{dob_month.zfill(2)}/{dob_day.zfill(2)}"
        gender = request.form.get('gender', '').strip()
        nid = request.form.get('nid', '').strip()
        semester=request.form.get('semester')
        sid = request.form.get('sid', '').strip()
        student_path = os.path.join(app.root_path, 'data', 'students.json')
        data = DataManager.load_data(student_path)

        if not all([fname, lname, password, dob, gender, nid, sid,semester]):
            log_event("student_signup_failed", reason="missing_fields", sid=sid)
            return render_template("StudentSignup.html", error="Please fill out all the fields.")

        if len(sid) != 13:
            log_event("student_signup_failed", reason="invalid_id_length", sid=sid)
            return render_template("StudentSignup.html", error="Student ID must be 13 digits long.")

        def is_valid_password(password):
            has_number = any(char.isdigit() for char in password)
            has_letter = any(char.isalpha() for char in password)
            return len(password) >= 6 and has_number and has_letter
        
        if not is_valid_password(password):
            log_event("student_signup_failed", reason="weak_password", sid=sid)
            return render_template("StudentSignup.html", error="Password must be at least 6 characters and include both letters and numbers.")

        if sid in data:
            log_event("student_signup_failed", reason="user_exists", sid=sid)
            return render_template("StudentLogin.html", error="User already exists. Please log in.")

        hashed_password = generate_password_hash(password)
        student_data = {
            'first name': fname,
            'last name': lname,
            'password': hashed_password,
            'date of birth': dob,
            'gender': gender,
            'national ID': nid,
            'student ID': sid,
            'semester' : semester,
            'course list': [],
            'registered_courses': [],
            'paid_courses': [],
            'quizzes': {
                'python quiz': None,
                'C++ quiz': None
            }
        }

        data[sid] = student_data
        DataManager.save_data(data, student_path)

        session["student_id"] = sid
        log_event("student_signup_success", sid=sid)
        return redirect(url_for("StudentDashboard"))

    return render_template("StudentSignup.html")


@app.route("/StudentDashboard",methods=["GET", "POST"])
def StudentDashboard():
    student_id = session.get("student_id")
    if not student_id:
        log_event("student_dashboard_access_failed", reason="no_session", student_id=student_id)
        return redirect(url_for("StudentLogin"))
    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)
    student_data = students.get(student_id)
    if not student_data:
        log_event("student_dashboard_access_failed", reason="student_not_found", student_id=student_id)
        return redirect(url_for("StudentLogin"))
    log_event("student_dashboard_access_success", student_id=student_id)
    return render_template("StudentDashboard.html", student= student_data)


@app.route("/SeptemberTermCalender")
def SeptemberTermCalender():
    timetable = DataManager.load_data("main/data/timetable.json")
    courses = DataManager.load_data("main/data/courses.json")
    return render_template("SeptemberTermCalender.html", timetable=timetable, courses=courses)


@app.route("/FAQ", methods=["GET"])
def FAQ():
    return render_template("FAQ.html")


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
            log_event("course_register_failed", reason="student_not_found", student_id=student_id, course=course_name)
            flash("Student data not found.", "danger")
            return redirect(url_for("registercourse"))

        total_credit = sum(courses[c]["credit"] for c in student.get("paid_courses", []) if c in courses)
        if total_credit + courses[course_name]["credit"] > 20:
            log_event("course_register_failed", reason="credit_limit_exceeded", student_id=student_id, course=course_name)
            flash("Cannot register more than 20 credits.", "danger")
            return redirect(url_for("registercourse"))
        
        if course_name in student.get("course list", []):
            log_event("course_register_failed", reason="course_already_exists", student_id=student_id, course=course_name)
            flash("you have already registered this course.", "danger")
            return redirect(url_for("registercourse"))
        
        prereqs_raw = courses[course_name].get("prequisites", "")
        prereqs = [p.strip() for p in prereqs_raw.split(",")] if prereqs_raw else []
        prereqs = [p for p in prereqs if p] 
        if not all(p in student.get("paid_courses", []) for p in prereqs):
            log_event("course_register_failed", reason="prerequisites_not_met", student_id=student_id, course=course_name, missing=prereqs)
            flash(f"Prerequisites not met: {', '.join(prereqs)}", "danger")
            return redirect(url_for("registercourse"))

        
        if courses[course_name]["occupied"] >= courses[course_name]["capacity"]:
            log_event("course_register_failed", reason="capacity_full", student_id=student_id, course=course_name)
            flash("Course is full.", "danger")
            return redirect(url_for("registercourse"))

        
        student_courses = student.get("paid_courses", [])
        for day, slots in timetable.items():
            for time_slot, slot_courses in slots.items():
                if course_name in slot_courses:
                    if any(c in slot_courses for c in student_courses):
                        log_event("course_register_failed", reason="time_conflict", student_id=student_id, course=course_name, conflict_with=slot_courses)
                        flash("Time conflict detected with another registered course.", "danger")
                        return redirect(url_for("registercourse"))


        
        if course_name not in student.get("registered_courses", []):
            log_event("course_register_success", student_id=student_id, course=course_name)
            student["registered_courses"].append(course_name)
            DataManager.save_data(students, students_path)

        return redirect(url_for("payment"))

    return render_template("registercourse.html", courses=courses)


@app.route('/payment', methods=["GET"])
def payment():
    student_id = session.get("student_id")
    if not student_id or student_id not in students:
        log_event("payment_page_denied", reason="not_logged_in", student_id=student_id)
        return redirect(url_for("StudentLogin"))
    courses_path = os.path.join(app.root_path, 'data', 'courses.json')
    students_path = os.path.join(app.root_path, 'data', 'students.json')

    all_courses = DataManager.load_data(courses_path)
    students = DataManager.load_data(students_path)
    student = students.get(student_id, {})

    registered_courses = student.get("registered_courses", [])
    paid_courses = student.get("paid_courses", [])

    selected_courses = []
    for name in registered_courses:
        if name in all_courses:
            course_data = all_courses[name].copy()
            course_data["name"] = name
            course_data["paid"] = name in paid_courses
            selected_courses.append(course_data)
    log_event(
        "payment_page_viewed",
        student_id=student_id,
        registered_count=len(registered_courses),
        paid_count=len(paid_courses)
    )
    return render_template("payment.html", selected_courses=selected_courses)


@app.route("/checkout", methods=["POST"])
def checkout():
    student_id = session.get("student_id")
    if not student_id:
        log_event("checkout_page_denied", reason="not_logged_in", student_id=student_id)
        return redirect(url_for("StudentLogin"))

    course_name = request.form.get("course_name")
    if not course_name:
        return "Course name is missing", 400

    students_path = os.path.join(app.root_path, 'data', 'students.json')
    courses_path = os.path.join(app.root_path, 'data', 'courses.json')

    students = DataManager.load_data(students_path)
    courses = DataManager.load_data(courses_path)

    if student_id not in students:
        return "Student not found", 404

    student = students[student_id]

    if course_name not in student.get("registered_courses", []):
        student["registered_courses"].append(course_name)

    if course_name not in student.get("paid_courses", []):
        student["paid_courses"].append(course_name)

    if course_name not in student.get("course list", []):
        student["course list"].append(course_name)

    if course_name in courses:
        courses[course_name]["occupied"] += 1
        courses[course_name]["capacity"] -= 1

    DataManager.save_data(students, students_path)
    DataManager.save_data(courses, courses_path)

    flash(f'Payment successful. {course_name} is now added to your course list.', 'success')
    log_event("checkout_success", student_id=student_id, course_name=course_name)
    return redirect(url_for("payment"))


@app.route('/payment_success', methods=["POST"])
def payment_success():
    return redirect(url_for("payment"))


@app.route('/payment_failed', methods=["POST"])
def payment_failed():
    return redirect(url_for("payment"))


@app.route("/mycourses")
def mycourses():
    student_id = session.get("student_id")
    if not student_id:
        log_event("student_not_found", student_id=student_id)
        return redirect(url_for("StudentLogin"))
    students_path = os.path.join(app.root_path, "data", "students.json")
    courses_path = os.path.join(app.root_path, "data", "courses.json")
    students = DataManager.load_data(students_path)
    courses = DataManager.load_data(courses_path)
    student = students.get(student_id)
    paid_courses = student.get("paid_courses", [])
    paid_courses_info = {course: courses.get(course, {}) for course in paid_courses}
    log_event("student_not_found", student_id=student_id)
    return render_template("mycourses.html", courses=paid_courses_info)


@app.route('/query', methods=["GET", "POST"])
def query():
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("StudentLogin"))

    student_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(student_path)
    student = students.get(student_id)

    python_answers = {
        "q1": "print",
        "q2": "int",
        "q3": "for",
        "q4": "def",
        "q5": "2",
        "q6": "555",
        "q7": "Lists are mutable, tuples are immutable",
        "q8": "5",
        "q9": "from math import sqrt",
        "q10": "4",
    }

    cpp_answers = {
        "q1": "cout",
        "q2": "int x;",
        "q3": "do-while",
        "q4": "const",
        "q5": "A",
        "q6": "2",
        "q7": "iostream",
        "q8": "2",
        "q9": "real",
        "q10": "6",
    }

    message = None
    results = {}

    if request.method == "POST":
        form = request.form
        if "pythonForm" in form:
            score = 0
            question_results = {}
            for q, ans in python_answers.items():
                user_ans = form.get(q)
                correct = user_ans == ans
                question_results[q] = {"user": user_ans, "correct": ans, "is_correct": correct}
                if correct:
                    score += 1
            student['quizzes']['python quiz'] = score
            results = question_results
            message = f"Python exam submitted! Score: {score}/10"

        elif "cppForm" in form:
            score = 0
            question_results = {}
            for q, ans in cpp_answers.items():
                user_ans = form.get(q)
                correct = user_ans == ans
                question_results[q] = {"user": user_ans, "correct": ans, "is_correct": correct}
                if correct:
                    score += 1
            student['quizzes']['C++ quiz'] = score
            results = question_results
            message = f"C++ exam submitted! Score: {score}/10"

        students[student_id] = student
        DataManager.save_data(students, student_path)

    return render_template("query.html", student=student, message=message, results=results)




@app.route('/project', methods=["GET"])
def project():
    return render_template("project.html")


@app.route('/administrator', methods=["GET"])
def administrator():
    return render_template("administrator.html")


@app.route('/coursecontent/<course_name>')
def coursecontent(course_name):
    import urllib.parse
    course_name_decoded = urllib.parse.unquote(course_name)

    courses_content_path = os.path.join(app.root_path, 'data', 'coursecontent.json')
    courses_content = DataManager.load_data(courses_content_path)

    course = courses_content.get(course_name_decoded)

    return render_template('coursecontent.html', course_name=course_name_decoded, course=course,  enumerate=enumerate)


@app.route("/professor",methods=["GET", "POST"])
def professor():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        admins_path = os.path.join(app.root_path, 'data', 'professor.json')
        admins = DataManager.load_data(admins_path)
        if email.endswith('@paia.com') and email in admins and admins[email] == password:
            return redirect(url_for('professorDashboard'))
        else:
            error = "incorrect email or password!"
            return render_template("professor.html", error=error)
    return render_template("professor.html")


@app.route("/professorDashboard",methods=["GET", "POST"])
def professorDashboard():
    return render_template("professorDashboard.html")


@app.route("/courses",methods=["GET", "POST"])
def courses():
    course_path=os.path.join(app.root_path, 'data', 'courses.json')
    courses=DataManager.load_data(course_path)
    return render_template("courses.html" , courses=courses)


@app.route("/studentsinfo",methods=["GET", "POST"])
def studentsinfo():
    students_path=os.path.join(app.root_path, 'data', 'students.json')
    students=DataManager.load_data(students_path)
    allowed_courses = ["Programming", "Advanced Programming", "Data Structures And Algorithms", "Computer Workshop", "Database"]
    return render_template("studentsinfo.html" , students=students , allowed_courses=allowed_courses)


@app.route("/exams")
def exams():
    students_path = os.path.join(app.root_path, 'data', 'students.json')
    students = DataManager.load_data(students_path)

    student_scores = {}
    for sid, data in students.items():
        student_scores[sid] = {
            "name": f"{data['first name']} {data['last name']}",
            "quizzes": data.get("quizzes", {})
        }
    return render_template("exams.html", student_scores=student_scores)


@app.route("/submit_exam", methods=["POST"])
def submit_exam():
    STUDENT_JSON = "data/student.json"
    data = request.json
    username = data.get("username")  
    exam_type = data.get("exam")     
    score = data.get("score")

    students = DataManager.load_data(STUDENT_JSON)
    
    for student in students:
        if student["username"] == username:
            if "exams" not in student:
                student["exams"] = {}
            student["exams"][exam_type] = {
                "score": score,
            }
            break
    else:
        return jsonify({"status": "error", "msg": "student not found"}), 404

    DataManager.save_data(STUDENT_JSON, students)
    return jsonify({"status": "success"})
if __name__ == "__main__":
    app.run(debug=True)
    