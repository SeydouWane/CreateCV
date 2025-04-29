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


@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        skills = request.form.getlist('skills[]')
        session['skills'] = skills
        return redirect('/step4')
    return render_template('form_step3.html')


@app.route('/step4', methods=['GET', 'POST'])
def step4():
    if request.method == 'POST':
        experiences = []

        titles = request.form.getlist('title[]')
        companies = request.form.getlist('company[]')
        locations = request.form.getlist('location[]')
        types = request.form.getlist('type[]')
        start_dates = request.form.getlist('start_date[]')
        end_dates = request.form.getlist('end_date[]')
        currents = request.form.getlist('current[]')
        descriptions = request.form.getlist('description[]')
        ref_names = request.form.getlist('ref_name[]')
        ref_contacts = request.form.getlist('ref_contact[]')

        for i in range(len(titles)):
            # On ignore les lignes vides
            if not titles[i].strip() and not companies[i].strip():
                continue

            experiences.append({
                'title': titles[i],
                'company': companies[i],
                'location': locations[i],
                'type': types[i],
                'start_date': start_dates[i],
                'end_date': end_dates[i] if end_dates[i] else None,
                'current': True if i < len(currents) else False,
                'description': descriptions[i],
                'ref_name': ref_names[i],
                'ref_contact': ref_contacts[i]
            })

        session['experiences'] = experiences
        return redirect('/review')
    return render_template('form_step4.html')


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

from flask import render_template, session, make_response
from deep_translator import GoogleTranslator
import pdfkit

@app.route('/generate_cv_en')
def generate_cv_en():
    # Cloner les données depuis la session
    data = session.copy()
    translator = GoogleTranslator(source='fr', target='en')

    def t(text):
        return translator.translate(text) if text else ''

    # Traduction des compétences
    if 'skills' in data:
        data['skills'] = [t(s) for s in data['skills']]

    # Traduction de l’éducation
    if 'education' in data:
        for edu in data['education']:
            edu['degree'] = t(edu.get('degree'))
            edu['school'] = t(edu.get('school'))
            edu['courses'] = [t(c) for c in edu.get('courses', [])]

    # Traduction des expériences professionnelles
    if 'experiences' in data:
        for exp in data['experiences']:
            exp['title'] = t(exp.get('title'))
            exp['company'] = t(exp.get('company'))
            exp['location'] = t(exp.get('location'))
            exp['description'] = t(exp.get('description'))
            exp['type'] = t(exp.get('type'))
            exp['ref_name'] = t(exp.get('ref_name'))
            exp['ref_contact'] = exp.get('ref_contact')  # Ne pas traduire email/téléphone

    # Traduction des langues
    if 'languages' in data:
        for lang in data['languages']:
            lang['name'] = t(lang.get('name'))

    # Traduction partielle des infos perso
    if 'personal_info' in data:
        data['personal_info']['name'] = data['personal_info'].get('name')
        data['personal_info']['linkedin'] = data['personal_info'].get('linkedin')

    # Générer le PDF à partir du template anglais
    rendered = render_template('cv_template_en.html', data=data)
    pdf = pdfkit.from_string(rendered, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=cv_en.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True)
