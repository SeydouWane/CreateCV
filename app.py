from flask import Flask, render_template, request, redirect, session, make_response
import os
from werkzeug.utils import secure_filename
from xhtml2pdf import pisa
from io import BytesIO

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
                'speak': f'speak_{i}' in request.form,
                'read': f'read_{i}' in request.form,
                'write': f'write_{i}' in request.form
            }
            languages.append(language_info)
        session['languages'] = languages
        return redirect('/step2')

    # GET : on récupère les valeurs stockées
    languages = session.get('languages', [{'name': '', 'speak': False, 'read': False, 'write': False}])
    return render_template('form_step1a.html', languages=languages)


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
        thesis_subjects = request.form.getlist('thesis_subject[]')
        thesis_supervisors = request.form.getlist('thesis_supervisors[]')

        for i in range(len(degrees)):
            education = {
                'degree': degrees[i],
                'school': schools[i],
                'start_year': start_years[i],
                'end_year': end_years[i],
                'in_progress': i < len(in_progress_list),
                'courses': [courses1[i], courses2[i], courses3[i], courses4[i]],
                'thesis_subject': thesis_subjects[i] if i < len(thesis_subjects) else '',
                'thesis_supervisors': thesis_supervisors[i] if i < len(thesis_supervisors) else ''
            }
            education_list.append(education)

        session['education'] = education_list
        return redirect('/step3')

    # 🧠 Passer les données précédentes à la vue
    education = session.get('education', [{}])
    return render_template('form_step2.html', education=education)


@app.route('/step3', methods=['GET', 'POST'])
def step3():
    if request.method == 'POST':
        skills = request.form.getlist('skills[]')
        session['skills'] = skills
        return redirect('/step4')  # ou la page suivante

    # Charger les données existantes si présentes
    skills = session.get('skills', [''])
    return render_template('form_step3.html', skills=skills)


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
        currents = request.form.getlist('current[]')  # seulement cochés
        descriptions = request.form.getlist('description[]')
        ref_names = request.form.getlist('ref_name[]')
        ref_contacts = request.form.getlist('ref_contact[]')

        for i in range(len(titles)):
            experiences.append({
                'title': titles[i],
                'company': companies[i],
                'location': locations[i],
                'type': types[i],
                'start_date': start_dates[i],
                'end_date': end_dates[i],
                'current': str(i) in currents,  # coché si son index figure
                'description': descriptions[i],
                'ref_name': ref_names[i],
                'ref_contact': ref_contacts[i]
            })

        session['experiences'] = experiences
        return redirect('/step5')

    # GET : on récupère les expériences mémorisées
    experiences = session.get('experiences', [{}])
    return render_template('form_step4.html', experiences=experiences)


@app.route('/step5', methods=['GET', 'POST'])
def step5():
    if request.method == 'POST':
        distinctions = []
        titles = request.form.getlist('title[]')
        descriptions = request.form.getlist('description[]')
        years = request.form.getlist('year[]')
        types = request.form.getlist('type[]')

        for i in range(len(titles)):
            if not titles[i].strip():
                continue
            distinctions.append({
                'title': titles[i],
                'description': descriptions[i],
                'year': years[i],
                'type': types[i]
            })

        session['distinctions'] = distinctions
        return redirect('/step6')

    # GET : on récupère les valeurs mémorisées
    distinctions = session.get('distinctions', [{}])
    return render_template('form_step5.html', distinctions=distinctions)


@app.route('/step6', methods=['GET', 'POST'])
def step6():
    if request.method == 'POST':
        certifications = []
        names = request.form.getlist('name[]')
        issuers = request.form.getlist('issuer[]')
        years = request.form.getlist('year[]')
        links = request.form.getlist('link[]')

        for i in range(len(names)):
            if not names[i].strip():
                continue
            certifications.append({
                'name': names[i],
                'issuer': issuers[i],
                'year': years[i],
                'link': links[i]
            })

        session['certifications'] = certifications
        return redirect('/review')

    # GET
    certifications = session.get('certifications', [{}])
    return render_template('form_step6.html', certifications=certifications)


@app.route('/review')
def review():
    return render_template('review.html', data=session)


from datetime import datetime

@app.route('/generate_cv')
def generate_cv():
    data = session.copy()

    # Traitement de l'image
    if 'photo_filename' in data.get('personal_info', {}) and data['personal_info']['photo_filename']:
        filename = data['personal_info']['photo_filename']
        full_path = os.path.join(app.root_path, 'static', 'uploads', filename)
        data['personal_info']['photo_path'] = full_path
    else:
        data['personal_info']['photo_path'] = None

    # ✅ Nouvelle ligne : ajouter la date du jour
    today = datetime.now().strftime('%d/%m/%Y')

    # Rendu HTML
    rendered = render_template('cv_template.html', data=data, today=today)

    # Conversion PDF
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(rendered, dest=pdf)

    if pisa_status.err:
        return "Erreur lors de la génération du PDF", 500

    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=cv.pdf'
    return response


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # PORT fourni par Render (sinon 5000 localement)
    app.run(host='0.0.0.0', port=port)
