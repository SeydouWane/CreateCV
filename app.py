from flask import Flask, render_template, request, session, redirect, url_for, send_file
from datetime import datetime
import os
import io

# --- 🚨 DÉPENDANCE WEASYPRINT ---
# Nous utilisons WeasyPrint pour générer le PDF. 
# Si vous ne l'avez pas encore installé: pip install weasyprint
try:
    from weasyprint import HTML
except ImportError:
    print("ATTENTION: La librairie 'weasyprint' n'est pas installée. Le CV sera renvoyé en HTML brut.")
    # On définit une fonction de substitution si WeasyPrint manque
    def generate_pdf_substitute(html_content):
        return io.BytesIO(html_content.encode('utf-8'))


app = Flask(__name__)
# 🚨 IMPORTANT : CLÉ SECRÈTE OBLIGATOIRE POUR LES SESSIONS FLASK
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key_a_changer_en_production_98765') 

# Définition des chemins de redirection pour la navigation
STEP_REDIRECTS = {
    'step1': 'step1a',
    'step1a': 'step2',
    'step2': 'step3',
    'step3': 'step4',
    'step4': 'step5',
    'step5': 'step6',
    'step6': 'template_select',
    'template_select': 'review'
}

# --- FONCTIONS UTILITAIRES DE SAUVEGARDE ---

def save_single_entry_data(fields_list):
    """Sauvegarde des données de champs simples (step1)."""
    data = {}
    for field in fields_list:
        data[field] = request.form.get(field)
    return data

def save_list_data(fields_map):
    """Sauvegarde des données de listes dynamiques (expériences, formations, etc.)."""
    
    # 1. Récupérer les listes de tous les champs
    form_data = {}
    for field in fields_map.keys():
        # Pour les listes dynamiques, Flask nomme les champs "field[]"
        form_data[field] = request.form.getlist(field + '[]')

    # 2. Déterminer la longueur de la liste (basé sur le premier champ)
    first_field = list(fields_map.keys())[0]
    if not form_data or not form_data.get(first_field):
        return []
    
    list_length = len(form_data[first_field])
    
    # 3. Construire la liste d'objets (dictionnaires)
    data_list = []
    
    # Récupérer les index des cases cochées (pour 'current', 'speak', etc.)
    checked_fields = {
        field: request.form.getlist(field + '[]')
        for field in fields_map if fields_map[field] == bool
    }

    for i in range(list_length):
        # Vérification si l'entrée principale (le premier champ) n'est pas vide
        if not form_data[first_field][i].strip():
            continue
            
        entry = {}
        for field, type_conversion in fields_map.items():
            if type_conversion == bool:
                # Vérifie si l'index 'i' est dans la liste des index cochés pour ce champ
                entry[field] = str(i) in checked_fields[field]
            else:
                entry[field] = form_data[field][i]
        
        data_list.append(entry)
        
    return data_list

# --- ROUTES DES FORMULAIRES ---

@app.route('/')
def index():
    """Redirection vers la première étape."""
    return redirect(url_for('step1'))

@app.route('/step1', methods=['GET', 'POST'])
def step1():
    """Infos Personnelles."""
    if request.method == 'POST':
        session['personal_info'] = save_single_entry_data(
            ['name', 'email', 'phone', 'linkedin', 'photo_path'])
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step1']))
    
    return render_template('form_step1.html', personal_info=session.get('personal_info', {}))

@app.route('/step1a', methods=['GET', 'POST'])
def step1a():
    """Langues."""
    fields = {'name': str, 'speak': bool, 'read': bool, 'write': bool}
    if request.method == 'POST':
        session['languages'] = save_list_data(fields)
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step1a']))
        
    return render_template('form_step1a.html', languages=session.get('languages', []))

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    """Formations."""
    fields = {
        'degree': str, 'school': str, 'location': str, 
        'start_year': str, 'end_year': str, 'in_progress': bool,
        'thesis_subject': str, 'thesis_supervisors': str, 'courses': str
    }
    if request.method == 'POST':
        education_list = save_list_data(fields)
        
        # Traitement des cours (conversion de la chaîne multiligne en liste)
        for entry in education_list:
            if 'courses' in entry and entry['courses']:
                entry['courses'] = [c.strip() for c in entry['courses'].split('\n') if c.strip()]
            else:
                entry['courses'] = []
                
        session['education'] = education_list
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step2']))

    return render_template('form_step2.html', education=session.get('education', []))

@app.route('/step3', methods=['GET', 'POST'])
def step3():
    """Compétences."""
    if request.method == 'POST':
        # Les compétences sont un cas spécial : une liste de chaînes simples
        skills_list = [skill.strip() for skill in request.form.getlist('skills[]') if skill.strip()]
        session['skills'] = skills_list
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step3']))
        
    return render_template('form_step3.html', skills=session.get('skills', []))

@app.route('/step4', methods=['GET', 'POST'])
def step4():
    """Expériences Professionnelles."""
    fields = {
        'title': str, 'company': str, 'location': str, 'type': str,
        'start_date': str, 'end_date': str, 'current': bool,
        'description': str, 'ref_name': str, 'ref_contact': str
    }
    if request.method == 'POST':
        session['experiences'] = save_list_data(fields)
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step4']))
        
    return render_template('form_step4.html', experiences=session.get('experiences', []))

@app.route('/step5', methods=['GET', 'POST'])
def step5():
    """Projets & Distinctions."""
    fields = {'title': str, 'year': str, 'type': str, 'description': str}
    if request.method == 'POST':
        session['distinctions'] = save_list_data(fields)
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step5']))
        
    return render_template('form_step5.html', distinctions=session.get('distinctions', []))

@app.route('/step6', methods=['GET', 'POST'])
def step6():
    """Certifications."""
    fields = {'title': str, 'issuer': str, 'year': str, 'url': str}
    if request.method == 'POST':
        session['certifications'] = save_list_data(fields)
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['step6']))
        
    return render_template('form_step6.html', certifications=session.get('certifications', []))

@app.route('/template_select', methods=['GET', 'POST'])
def template_select():
    """Choix du Template."""
    if request.method == 'POST':
        # Sauvegarde le choix du template, par défaut à 'classic'
        session['template_choice'] = request.form.get('template_choice', 'classic')
        session.modified = True
        return redirect(url_for(STEP_REDIRECTS['template_select'])) # Redirection vers 'review'
    
    return render_template('form_template_select.html', 
                           template_choice=session.get('template_choice', 'classic'))


@app.route('/review')
def review():
    """Revue finale avant génération."""
    # Assurer qu'il y a des données minimales pour éviter une erreur
    if not session.get('personal_info'):
        return redirect(url_for('step1'))
        
    return render_template('review.html', data=session)

# --- ROUTE DE GÉNÉRATION FINALE ---

@app.route('/generate_cv')
def generate_cv():
    """
    Génère le CV final en PDF en utilisant le template choisi dans la session.
    """
    # 1. Déterminer le template à utiliser (par défaut: classic)
    template_choice = session.get('template_choice', 'classic')
    template_name = f'cv_templates_{template_choice}.html'

    # Si l'utilisateur n'a pas rempli le formulaire step1, on le renvoie
    if not session.get('personal_info'):
        return redirect(url_for('step1'))

    # 2. Rendu du template HTML
    html_out = render_template(template_name, 
                               data=session, 
                               today=datetime.now().strftime('%d/%m/%Y'))

    # 3. Conversion en PDF
    try:
        # Tente d'utiliser WeasyPrint
        pdf_bytes = HTML(string=html_out, base_url=request.base_url).write_pdf()
        pdf_file = io.BytesIO(pdf_bytes)
    except NameError:
        # Si WeasyPrint n'a pas pu être importé (non installé)
        # Pour le débogage, on renvoie le HTML brut
        return html_out, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        app.logger.error(f"Erreur de conversion PDF : {e}")
        return f"Erreur lors de la conversion PDF : {e}", 500

    # 4. Envoi du fichier PDF
    name = session.get('personal_info', {}).get('name', 'CV_Anonyme').replace(' ', '_')
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{name}_CV_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

if __name__ == '__main__':
    # Le mode debug doit être désactivé en production
    # Si debug=True, les changements de session sont persistants (utile pour le développement)
    app.run(host='0.0.0.0', port=5000, debug=True)