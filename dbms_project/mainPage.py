from os import name
from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,logout_user,login_manager,LoginManager,login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import text

local_server=True

app=Flask(__name__)
app.secret_key='samarth'

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:samarth@localhost/project31'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)

viewthing='signinInstructor'
k=1  #instructor  0->student

login_manager=LoginManager(app)
login_manager.login_view=viewthing

@login_manager.user_loader
def load_user(user_id):
    if(k==1):
        return instructor.query.get(int(user_id))
    elif (k==2):
        return admin.query.get(int(user_id))
    return student.query.get(int(user_id))



# all tables -->
class instructor(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    username=db.Column(db.String(150),nullable=False,unique=True)
    email=db.Column(db.String(150),nullable=False)
    password=db.Column(db.String(1000),nullable=False)
    v1=db.relationship('course', backref='instructor', lazy=True)
    def __init__(self,name,username,email,password):
        self.name=name
        self.username=username
        self.email=email
        self.password=password

class student(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(150),nullable=False)
    username=db.Column(db.String(150),nullable=False,unique=True)
    email=db.Column(db.String(150),nullable=False)
    password=db.Column(db.String(1000),nullable=False)
    v1=db.relationship('comment', backref='student', lazy=True)
    def __init__(self,name,username,email,password):
        self.name=name
        self.username=username
        self.email=email
        self.password=password

class comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    student_id=db.Column(db.Integer,db.ForeignKey('student.id'),nullable=False)
    comment=db.Column(db.String(1000),nullable=False)

    def __init__(self,student_id,comment):
        self.student_id=student_id
        self.comment=comment

class admin(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(150),nullable=False)
    password=db.Column(db.String(1000),nullable=False)

    def __init__(self,username,password):
        self.username=username
        self.password=password

class course(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    course_name=db.Column(db.String(150),nullable=False,unique=True)
    duration=db.Column(db.String(150),nullable=False)
    difficulty=db.Column(db.Integer,nullable=False)
    fee=db.Column(db.Integer,nullable=False)
    university_name=db.Column(db.String(150),nullable=False)
    instructor_id=db.Column(db.Integer,db.ForeignKey('instructor.id'),nullable=False)
    instructor_username=db.Column(db.String(200),nullable=False)


    def __init__(self,course_name,duration,difficulty,fee,university_name,instructor_id,instructor_username):
        self.course_name=course_name
        self.duration=duration
        self.difficulty=difficulty
        self.fee=fee
        self.university_name=university_name
        self.instructor_id=instructor_id
        self.instructor_username=instructor_username

class enroll(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    course_id=db.Column(db.Integer,nullable=False)
    student_id=db.Column(db.Integer,nullable=False)

    def __init__(self,course_id,student_id):
        self.course_id=course_id
        self.student_id=student_id


# all routing -->
@app.route('/')
def startPage():
    p1=text("SELECT s.name,c.comment from student as s,comment as c WHERE c.student_id=s.id")
    p2=db.engine.execute(p1)
    return render_template("signPage.html",p2=p2)

@app.route('/signupInstructor',methods=['POST','GET'])
def signupInstructor():
    if request.method=="POST":
        name=request.form.get('ISUname')
        username=request.form.get('ISUusername')
        email=request.form.get('ISUemail')
        password=request.form.get('ISUpass')
        print(name,username)
        ins = instructor.query.filter_by(username=username).first()
        if ins:
            print("Already a member")
            return render_template('/signinInstructor.html')

        entry=instructor(name,username,email,password=generate_password_hash(password))
        db.session.add(entry)
        db.session.commit()
    return render_template("signupInstructor.html")

@app.route('/signupStudent',methods=['POST','GET'])
def signupStudent():
    if request.method=="POST":
        name=request.form.get('SSUname')
        username=request.form.get('SSUusername')
        email=request.form.get('SSUemail')
        password=request.form.get('SSUpass')
        # print(name,username)
        stu = student.query.filter_by(username=username).first()
        if stu:
            print("Already a member")
            return render_template('/signinStudent.html')
        
        entry=student(name,username,email,password=generate_password_hash(password))
        db.session.add(entry)
        db.session.commit()
    return render_template("signupStudent.html")

@app.route('/signinAdmin',methods=['POST','GET'])
def signinAdmin():
    if request.method=="POST":
        username=request.form.get('Ausername')
        password=request.form.get('Apass')
        print(username,password)
        adm=admin.query.filter_by(username=username).first()

        if(adm):
            global k
            k=2
            global viewthing
            viewthing='signinAdmin'
            login_user(adm)
            return redirect(url_for('admin1'))
        else:
            print('invalid')
            return render_template('signinAdmin.html')
    return render_template("signinAdmin.html")

@app.route('/signinInstructor',methods=['POST','GET'])
def signinInstructor():
    if request.method=="POST":
        username=request.form.get('ISIusername'
        )
        password=request.form.get('ISIpass')
        print(username,password)
        ins=instructor.query.filter_by(username=username).first()

        if(ins and check_password_hash(ins.password,password)):
            global k
            k=1
            global viewthing
            viewthing='signinInstructor'
            login_user(ins)
            flash("Login Successful","primary")
            return redirect(url_for('instructor1'))
        else:
            flash("Invalid credentials","danger")
            print('invalid credentials')
            return render_template('signinInstructor.html')
    return render_template("signinInstructor.html")

@app.route('/signinStudent',methods=['POST','GET'])
def signinStudent():
    if request.method=="POST":
        username=request.form.get('SSIusername')
        password=request.form.get('SSIpass')
        print(username,password)
        std=student.query.filter_by(username=username).first()

        if(std and check_password_hash(std.password,password)):
            global k
            k=0
            global viewthing
            viewthing='signinStudent'
            login_user(std)
            flash("Login Successful","primary")
            return redirect(url_for('student1'))
        else:
            flash("Invalid credentials","danger")
            print('invalid credentials')
            return render_template('signinStudent.html')
    return render_template("signinStudent.html")

@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
    return render_template('signPage.html')

@app.route('/admin1',methods=['POST','GET'])
def admin1():
    p1=text("SELECT * FROM student")
    p2=text("SELECT * FROM instructor")
    p3=text("SELECT * FROM course")
    s1=db.engine.execute(p2)
    s2=db.engine.execute(p1)
    s3=db.engine.execute(p3)
    flash("Login Successful","primary")
    return render_template("admin1.html",s1=s1,s2=s2,s3=s3)

@app.route('/adminCourseDelete/<string:cid>',methods=['POST','GET'])
def adminCourseDelete(cid):
    p1=text(f"DELETE FROM course WHERE course.cid='{cid}'")
    db.engine.execute(p1)
    flash("Deleted Successfully","danger")
    return redirect(url_for('admin1'))

@app.route('/adminCourseEdit/<string:cid>',methods=['POST','GET'])
def adminCourseEdit(cid):
    posts=course.query.filter_by(cid=cid).first()
    if request.method=="POST":
        course_name=request.form.get('Coursename')
        duration=request.form.get('Duration')
        difficulty=request.form.get('Difficulty')
        fee=request.form.get('Fee')
        university_name=request.form.get('Universityname')
        p1=text(f"UPDATE course SET course_name='{course_name}',duration='{duration}',difficulty='{difficulty}',fee='{fee}',university_name='{university_name}' WHERE '{cid}'=course.cid")
        db.engine.execute(p1)
        flash("Courses is Updated Successfully","success")
        return redirect(url_for('admin1'))

    return render_template('adminCourseEdit.html',posts=posts)

@app.route('/adminInstructorEdit/<string:id>',methods=['POST','GET'])
def adminInstructorEdit(id):
    posts=instructor.query.filter_by(id=id).first()
    if request.method=="POST":
        name=request.form.get('Instructorname')
        email=request.form.get('Instructoremail')
        print(name,email)
        p1=text(f"UPDATE instructor SET name='{name}',email='{email}' WHERE '{id}'=instructor.id")
        db.engine.execute(p1)
        flash("Courses is Updated Successfully","success")
        return redirect(url_for('admin1'))

    return render_template('adminInstructorEdit.html',posts=posts)

@app.route('/adminStudentEdit/<string:id>',methods=['POST','GET'])
def adminStudentEdit(id):
    posts=student.query.filter_by(id=id).first()
    if request.method=="POST":
        name=request.form.get('Studentname')
        email=request.form.get('Studentemail')
        print(name,email)
        p1=text(f"UPDATE student SET name='{name}',email='{email}' WHERE '{id}'=student.id")
        db.engine.execute(p1)
        flash("Courses is Updated Successfully","success")
        return redirect(url_for('admin1'))

    return render_template('adminStudentEdit.html',posts=posts)

@app.route('/instructor1',methods=['POST','GET'])
def instructor1():
    if request.method=="POST":
        course_name=request.form.get('insCoursename')
        duration=request.form.get('insDuration')
        difficulty=request.form.get('insDifficulty')
        fee=request.form.get('insFee')
        university_name=request.form.get('insUniversityname')
        instructor_username=request.form.get('insUsername')
        instructor_id=current_user.id
        entry=course(course_name,duration,difficulty,fee,university_name,instructor_id,instructor_username)
        db.session.add(entry)
        db.session.commit()

        flash("Insert data successful","success")
    return render_template("instructor1.html")

@app.route('/course11',methods=['POST','GET'])
def course11():
    us=current_user.id
    p2=text(f"SELECT * FROM course WHERE '{us}'=instructor_id")
    query=db.engine.execute(p2)
    return render_template('course11.html',query=query)

@app.route("/courseEdit/<string:cid>",methods=['POST','GET'])
def courseEdit(cid):
    posts=course.query.filter_by(cid=cid).first()
    if request.method=="POST":
        course_name=request.form.get('Coursename')
        duration=request.form.get('Duration')
        difficulty=request.form.get('Difficulty')
        fee=request.form.get('Fee')
        university_name=request.form.get('Universityname')
        p1=text(f"UPDATE course SET course_name='{course_name}',duration='{duration}',difficulty='{difficulty}',fee='{fee}',university_name='{university_name}' WHERE '{cid}'=course.cid")
        db.engine.execute(p1)
        flash("Courses is Updated Successfully","success")
        return redirect(url_for('course11'))
    
    return render_template('courseEdit.html',posts=posts)   

@app.route('/deleteCourse/<string:cid>',methods=['POST','GET'])
def delete(cid):
    p1=text(f"DELETE FROM course WHERE course.cid='{cid}'")
    db.engine.execute(p1)
    flash("Deleted Successfully","danger")
    return redirect(url_for('course11'))

@app.route('/courseHave',methods=['POST','GET'])
def courseHave():
    v1=current_user.id
    p3=text(f"SELECT course_name,university_name,instructor_username FROM enroll INNER JOIN course on  course_id=cid WHERE enroll.student_id='{v1}'")
    stu4=db.engine.execute(p3)
    return render_template("courseHave.html",stu4=stu4)    

@app.route('/student1',methods=['POST','GET'])
def student1():
    p2=text('SELECT course.course_name,course.university_name,course.duration,course.difficulty,course.fee,instructor.name FROM course LEFT JOIN instructor on instructor.id=course.instructor_id')
    stu1=db.engine.execute(p2)
    if request.method=="POST":
        course_name=request.form.get('Coursename')
        stu2=course.query.filter_by(course_name=course_name).first()
        stu3=int(stu2.cid)
        entry=enroll(stu3,current_user.id)   
        db.session.add(entry)
        db.session.commit()       
        print(stu2.cid,current_user.id)
    return render_template("student1.html",stu1=stu1)

@app.route('/comment1',methods=['POST','GET'])
def comment1():
    if request.method=="POST":
        username=request.form.get('username')
        comment1=request.form.get('comment')
        stu1=student.query.filter_by(username=username).first()
        stu2=int(stu1.id)
        print(stu1)
        entry=comment(stu2,comment1)
        db.session.add(entry)
        db.session.commit()
        print(username,comment1)
    return render_template("comment1.html")

if __name__=='__main__':
    db.create_all()
    app.run(debug=True)
