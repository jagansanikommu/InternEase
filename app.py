from flask import Flask, render_template, request, redirect, url_for, flash, session , abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///internships.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'jagan'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class CompanyOfficial(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)


class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

skills = db.Table('skills',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.Boolean, nullable=False, default=True)
    skills = db.relationship('Skill', secondary=skills, lazy='subquery', backref=db.backref('students', lazy=True))
    

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')

    student = db.relationship('Student', backref=db.backref('applications', lazy=True))
    internship = db.relationship('Internship', backref=db.backref('applications', lazy=True))





@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.')

    return render_template('admin_login.html')


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not current_user.email=='j@gmail.com':  # Assuming you have an 'is_admin' field in your User model
        abort(403)
    officials = CompanyOfficial.query.all()
    internships = Internship.query.all()

    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        location = request.form['location']
        duration = request.form['duration']
        description = request.form['description']
        internship = Internship(title=title, company=company, location=location, duration=duration, description=description)
        db.session.add(internship)
        db.session.commit()
        flash('The internship has been added.')
    return render_template('admin_dashboard.html', internships=internships, officials=officials)

@app.route('/admin/internship/update/<int:internship_id>', methods=['GET', 'POST'])
@login_required
def update_internship(internship_id):
    if not current_user.email=='j@gmail.com':  # Assuming you have an 'is_admin' field in your User model
        abort(403)
    internship = Internship.query.get(internship_id)
    if internship is None:
        flash('The internship does not exist.')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        internship.title = request.form['title']
        internship.company = request.form['company']
        internship.location = request.form['location']
        internship.duration = request.form['duration']
        internship.description = request.form['description']
        db.session.commit()
        flash('The internship has been updated.')
        return redirect(url_for('admin_dashboard'))
    return render_template('update_internship.html', internship=internship)

@app.route('/admin/internship/delete/<int:internship_id>', methods=['POST'])
@login_required
def delete_internship(internship_id):
    if not current_user.email=='j@gmail.com':  # Assuming you have an 'is_admin' field in your User model
        abort(403)
    internship = Internship.query.get(internship_id)
    if internship is None:
        flash('The internship does not exist.')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(internship)
    db.session.commit()
    flash('The internship has been deleted.')
    return redirect(url_for('admin_dashboard'))

#---------------------------
@app.route('/admin/company_official/create', methods=['GET', 'POST'])
@login_required
def create_company_official():
    # Check if the current user is an admin
    # Add your logic here
    if not current_user.email=='j@gmail.com':  # Assuming you have an 'is_admin' field in your User model
        abort(403)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        company = request.form['company']

        official = CompanyOfficial(username=username, password=password, company=company)
        db.session.add(official)
        db.session.commit()
        flash('The company official has been created.')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_company_official.html')

@app.route('/admin/company_official/update/<int:official_id>', methods=['GET', 'POST'])
@login_required
def update_company_official(official_id):
    # Check if the current user is an admin
    # Add your logic here
    if not current_user.email=='j@gmail.com':  # Assuming you have an 'is_admin' field in your User model
        abort(403)

    official = CompanyOfficial.query.get(official_id)
    if official is None:
        flash('The company official does not exist.')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        official.username = request.form['username']
        official.password = request.form['password']
        official.company = request.form['company']
        db.session.commit()
        flash('The company official has been updated.')
        return redirect(url_for('admin_dashboard'))

    return render_template('update_company_official.html', official=official)

@app.route('/admin/company_official/delete/<int:official_id>', methods=['POST'])
@login_required
def delete_company_official(official_id):
    # Check if the current user is an admin
    # Add your logic here
    if not current_user.email=='j@gmail.com':  # Assuming you have an 'is_admin' field in your User model
        abort(403)

    official = CompanyOfficial.query.get(official_id)
    if official is None:
        flash('The company official does not exist.')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(official)
    db.session.commit()
    flash('The company official has been deleted.')
    return redirect(url_for('admin_dashboard'))






@app.route('/')
def home():
    return render_template('home.html')


@app.route('/internships')
def internships():
    internships = Internship.query.all()
    return render_template('internships.html', internships=internships)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        college = request.form['college']
        course = request.form['course']
        year = request.form['year']
        skill_ids = request.form.getlist('skills')  # get list of skill ids from form
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        availability = request.form.get('availability', False)
        
        student = Student(name=name, email=email, password=password, college=college, course=course, year=year, availability=availability)
        db.session.add(student)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    skills = Skill.query.all()
    return render_template('register.html', skills=skills)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Try to authenticate as a Student
        student = Student.query.filter_by(email=email).first()
        if student and student.password == password:
            login_user(student)
            return redirect(url_for('profile'))

        # Try to authenticate as a CompanyOfficial
        official = CompanyOfficial.query.filter_by(username=email).first()
        if official and official.password == password:
            login_user(official)
            return redirect(url_for('company_dashboard'))  # Redirect to company dashboard

        flash('Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    edit = request.args.get('edit', type=bool, default=False)

    if request.method == 'POST' and edit:
        # existing code...
        skill_ids = request.form.getlist('skills')  # get list of skill ids from form
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()

        current_user.skills = skills
        availability = request.form.get('availability', False)
        current_user.availability = availability
        db.session.commit()

        flash('Profile updated successfully.')
        return redirect(url_for('profile'))

    skills = Skill.query.all()
    return render_template('profile.html', skills=skills, edit=edit)

@app.route('/internships/<int:internship_id>/apply', methods=['GET', 'POST'])
@login_required
def apply(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    if request.method == 'POST':
        application = Application(student_id=current_user.id, internship_id=internship_id)
        db.session.add(application)
        db.session.commit()
        flash('Your application has been submitted.')
        return redirect(url_for('internships'))
    return render_template('apply.html', internship=internship)

@app.route('/company/dashboard', methods=['GET', 'POST'])
@login_required
def company_dashboard():
    #
    skills = Skill.query.all()  # get all skills
    skill_ids = request.form.getlist('skills')  # get the selected skills from the form
    students = None

    if skill_ids:
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        students = set(skills[0].students) if skills else None
        for skill in skills[1:]:
            students &= set(skill.students)

    return render_template('company_dashboard.html', students=students, skills=skills)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
