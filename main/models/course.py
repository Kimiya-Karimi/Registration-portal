def signup_student():
        fname = input('enter your first name: ')
        lname = input('enter your last name: ')
        uid= input("enter your user id: ")
        password = input("enter a strong password:" )
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
