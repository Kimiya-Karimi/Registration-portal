from flask import Flask , render_template , url_for , request , redirect
import os , json
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

    @staticmethod
    def save_student(student_data, file_path= os.path.join(app.root_path, 'data', 'students.json')):
        data= DataManager.load_data(file_path)
        sid= student_data['student ID']
        if sid in data:
            return('this student alredy exists.')
        data[sid]= student_data
        DataManager.save_data(data, file_path)
        return('student saved successfully!')
class User:
    def __init__(self, uid, password, nid):
        self.user_id = uid
        self.password = password
        self.national_id = nid


class Student(User):
    def __init__(self, fn, ln, uid, password, dob, gn, sid, nid):
        super().__init__(uid, password, nid)
        self.first_name= fn
        self.last_name= ln
        self.date_of_birth= dob
        self.gender = gn
        self.student_id = sid

    def __str__(self):
        return f' First Name: {self.first_name}, Last Name : {self.last_name}, Date of Birthday: {self.date_of_birth}, National ID: {self.national_id}, Student Number: {self.student_id}'

    def show_profile(self):
        students = DataManager.load_data("E:/python/project main/json trash/students.json")
        student = students[self.student_id]
        print(f'\nfirst name: {student['first name']}\n last name: {student['last name']}\ndate of birth:{student['date of birth']}\n')

    def add_course_to_student(self, course_name):
        student_path="E:/python/project main/json trash/students.json"
        course_path='E:/python/project main/json trash/courses.json'
        timetable_path='E:/python/project main/json trash/timetable.json'
        course_data=DataManager.load_data(course_path)
        student_data=DataManager.load_data(student_path)
        timetable_data=DataManager.load_data(timetable_path)
        sid = self.student_id
        for day, slots in timetable_data.items():
            for time_slot in slots:
                if course_name in slots[time_slot]:
                    student_data[sid]['courses'][day][time_slot].append(course_name)
        student_data[sid]['course list'].append(course_name)
        DataManager.save_data(student_data, student_path)
        print(f"{course_name} added to student {sid}'s course list successfully!")
        return True
@staticmethod
def signup_student():
        fname = input('enter your first name: ')
        lname = input('enter your last name: ')
        uid= input("enter your user id: ")
        password = input("enter a strong password:" )
        #repeat password,if
        DoB = input('enter your date of birth (YYYY/MM/DD): ')
        gender = input('enter your gender (female/male): ')
        national_id = input('enter your national ID: ')
        student_id = input('enter your student ID: ')
        while len(student_id)!=13:
            print('invalid student ID.')
            student_id=input('please enter your student ID correctly: ')
        new_student = Student(fname,lname,uid,password,DoB,gender,student_id,national_id)
        student_data={
            'first name':new_student.first_name,
            'last name':new_student.last_name,
            'user ID':new_student.user_id,
            'password':new_student.password,
            'date of birth':new_student.date_of_birth,
            'gender':new_student.gender,
            'national ID': new_student.national_id,
            'student ID':new_student.student_id,
            'course list':[],
            'courses':{
            "Saturday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
            "Sunday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
            "Monday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
            "Tuesday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]},
            "Wednesday" : {"8-10":[], "10-12":[], "12-14":[], "14-16":[], "16-18":[]}}
        }
        DataManager.save_student(student_data)
        student_dashboard(new_student)
class Course:
    def __init__(self, cname, day, time, credit, capacity, prequisites):
        self.course_name = cname 
        self.course_day = day
        self.course_time = time
        self.credit = credit
        self.capacity = capacity
        self.prequisites=prequisites

class CourseManager(Course):
    def __init__(self, cname, day, time, credit, capacity, prequisites):
            super().__init__(cname, day, time, credit, capacity, prequisites)        
class Registration:

    @staticmethod
    def course_register(student):
        student_path="E:/python/project main/json trash/students.json"
        course_path='E:/python/project main/json trash/courses.json'
        timetable_path='E:/python/project main/json trash/timetable.json'
        course_data=DataManager.load_data(course_path)
        student_data=DataManager.load_data(student_path)
        timetable_data=DataManager.load_data(timetable_path)
        sid = student.student_id
        total_credit=0
        # for course_day, course_time in student_data[sid]['courses']:
        #         for time_slot, course_name in course_time.items():
        #             course_info=[course_name]
        #             total_credit+=course_info['credit']
        while total_credit<=20:
            course=input('enter the course you would like to register: ').title()
            if Registration.has_time_conflict(student, course):
                print('time conflict detected. cannot register this course.')
                choice=input('would you like to register another course? (yes/no) ').lower()
                if choice=='yes':
                    Registration.course_register(student)
                else:
                    student_dashboard(student)
                    break
            else:
                if course_data[course]['prequisites']=='None' or course_data[course]['prequisites'] in student_data[sid]['course list']:
                    if course_data[course]['capacity']!=course_data[course]['occupied']:
                        course_data[course]['occupied']+=1
                        total_credit+=int(course_data[course]['credit'])
                        DataManager.save_data(course_data, course_path)
                        Student.add_course_to_student(student, course)
                        choice=input('would you like to register another course? (yes/no) ').lower()
                        if choice=='yes':
                            Registration.course_register(student)
                        else:
                            student_dashboard(student)
                            break
                    else:
                        print('this course is full. cannot add the course.\n')
                        choice=input('would you like to register another course? (yes/no) ').lower()
                        if choice=='yes':
                            Registration.course_register(student)
                        else:
                            student_dashboard(student)
                            break
                else:
                    print('prequisites not met. cannot add course.\n')
                    choice=input('would you like to register another course? (yes/no) ').lower()
                    if choice=='yes':
                        Registration.course_register(student)
                    else:
                        student_dashboard(student)
                        break

    @staticmethod
    def has_time_conflict(student, new_course):
        student_path = "E:/python/project main/json trash/students.json"
        timetable_path='E:/python/project main/json trash/timetable.json'
        student_data = DataManager.load_data(student_path)
        timetable_data=DataManager.load_data(timetable_path)
        sid = student.student_id
        student_courses = student_data[sid].get('courses', [])
        new_course_day=None
        new_course_time=None
        for day, slots in timetable_data.items():
            for time_slot, courses in slots.items():
                if new_course in courses:
                    student_day=student_courses.get(day, {})
                    #student_time=
                    break
        for course in student_courses:
            for day, slots in timetable_data.items():
                for time_slot, courses in slots.items():
                    if course in courses:
                        if day==new_course_day and time_slot==new_course_time:
                            return True
        return False
def student_dashboard(student):
    while True:
        print("1. profile \n2. course registration \n3. Available courses\n")
        choice= input()
        if choice=='1':
            student.show_profile()
        elif choice=='2':
            CourseManager.show_courses()
            Registration.course_register(student)
        else:
            CourseManager.show_courses()            
             
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
@app.route("/StudentSignup",methods=["GET", "POST"])
def StudentSignup():
    return render_template("StudentSignup.html")
@app.route("/StudentDashboard")
def StudentDashboard():
    return render_template("StudentDashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
    