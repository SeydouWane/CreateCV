from flask import Flask, render_template, request, redirect, session, make_response
import pdfkit

app = Flask(__name__)
app.secret_key = 'super_secret_key'

@app.route('/')
def index():
    return redirect('/step1')

@app.route('/step1', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        session['personal_info'] = request.form.to_dict()
        return redirect('/step2')
    return render_template('form_step1.html', personal_info=session.get('personal_info', {}))

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
        return redirect('/review')
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

if __name__ == '__main__':
    app.run(debug=True)
