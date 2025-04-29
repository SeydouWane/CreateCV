from flask import Flask, render_template, request, redirect, session, make_response
import pdfkit
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'

@app.route('/')
def index():
    return redirect('/step1')


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        personal_info = request.form.to_dict()

        # Gestion de la photo
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                personal_info['photo_filename'] = filename
            else:
                personal_info['photo_filename'] = None
        else:
            personal_info['photo_filename'] = None

        session['personal_info'] = personal_info
        return redirect('/step1a')
    return render_template('form_step1.html', personal_info=session.get('personal_info', {}))

@app.route('/step1a', methods=['GET', 'POST'])
def step1a():
    if request.method == 'POST':
        languages = []
        language_names = request.form.getlist('language_name[]')

        for i, name in enumerate(language_names):
            language_info = {
                'name': name,
                'speak': True if f'speak_{i}' in request.form else False,
                'read': True if f'read_{i}' in request.form else False,
                'write': True if f'write_{i}' in request.form else False,
            }
            languages.append(language_info)

        session['languages'] = languages
        return redirect('/step2')  

    return render_template('form_step1a.html')

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    if request.method == 'POST':
        education_list = []
        degrees = request.form.getlist('degree[]')
        schools = request.form.getlist('school[]')
        start_years = request.form.getlist('start_year[]')
        end_years = request.form.getlist('end_year[]')
        in_progress_list = request.form.getlist('in_progress[]')
        courses1 = request.form.getlist('course1[]')
        courses2 = request.form.getlist('course2[]')
        courses3 = request.form.getlist('course3[]')
        courses4 = request.form.getlist('course4[]')

        for i in range(len(degrees)):
            education_list.append({
                'degree': degrees[i],
                'school': schools[i],
                'start_year': start_years[i],
                'end_year': end_years[i] if end_years[i] else None,
                'in_progress': True if i < len(in_progress_list) else False,
                'courses': [
                    courses1[i], 
                    courses2[i], 
                    courses3[i], 
                    courses4[i]
                ]
            })
        session['education'] = education_list
        return redirect('/step3')   # ← ← ← ici tu corriges !
    return render_template('form_step2.html')


@app.route('/review')
def review():
    return render_template('review.html', data=session)

@app.route('/generate_cv')
def generate_cv():
    rendered = render_template('cv_template.html', data=session)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=cv.pdf'
    return response


@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        skills = request.form.getlist('skills[]')
        session['skills'] = skills
        return redirect('/review')
    return render_template('form_step3.html')


if __name__ == '__main__':
    app.run(debug=True)
