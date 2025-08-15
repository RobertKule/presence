from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here_12345'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///presences.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèles de données
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    students = db.relationship('Student', backref='course', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Course {self.name}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    matricule = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Student {self.full_name}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present', 'absent', 'late'
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    def __repr__(self):
        return f'<Attendance {self.date} {self.status}>'

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, 'Rapport de Présence des Étudiants', 
                 new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 
                 new_x="LMARGIN", new_y="NEXT", align='C')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def dashboard():
    courses = Course.query.order_by(Course.name).all()
    return render_template('dashboard.html', courses=courses, now=datetime.now())
from datetime import datetime

@app.template_filter('format_date')
def format_date_filter(date_obj):
    """Format a date object to French format (DD/MM/YYYY)"""
    if isinstance(date_obj, (date, datetime)):
        return date_obj.strftime("%d/%m/%Y")
    return str(date_obj)  # fallback for non-date objects
# @app.template_filter('format_date')
# def format_date_filter(date_obj):
#     if isinstance(date_obj, date):
#         return date_obj.strftime("%d/%m/%Y")
#     return date_obj

@app.route('/add_course', methods=['POST'])
def add_course():
    course_name = request.form.get('course_name')
    if course_name and course_name.strip():
        try:
            course = Course(name=course_name)
            db.session.add(course)
            db.session.commit()
            flash(f'Cours "{course_name}" ajouté avec succès!', 'success')
        except:
            db.session.rollback()
            flash('Ce cours existe déjà', 'error')
    else:
        flash('Nom de cours invalide', 'error')
    return redirect(url_for('dashboard'))

@app.route('/course/<course_name>')
def course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        flash('Cours non trouvé', 'error')
        return redirect(url_for('dashboard'))
    
    # Récupérer les dates distinctes des séances
    dates = db.session.query(Attendance.date)\
             .filter_by(course_id=course.id)\
             .distinct()\
             .order_by(Attendance.date.desc())\
             .all()
    
    dates = [d[0] for d in dates]  # Extraire les dates du résultat
    
    return render_template('course.html', 
                         course=course,
                         dates=dates,
                         now=datetime.now())

@app.route('/upload_students/<course_name>', methods=['GET', 'POST'])
def upload_students(course_name):
    course = Course.query.filter_by(name=course_name).first_or_404()
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Type de fichier non autorisé (.xlsx, .xls uniquement)', 'error')
            return redirect(request.url)

        try:
            # Lire le fichier directement sans sauvegarde temporaire
            df = pd.read_excel(file.stream)
            
            if 'Nom complet' not in df.columns:
                flash("La colonne 'Nom complet' est obligatoire", 'error')
                return redirect(request.url)
            
            # Préparer les nouveaux étudiants
            new_students = []
            for _, row in df.iterrows():
                new_students.append(Student(
                    full_name=str(row['Nom complet']).strip(),
                    matricule=str(row.get('Matricule', '')).strip() or None,
                    course_id=course.id
                ))
            
            # Transaction unique
            db.session.begin_nested()  # Pour les opérations de suppression/ajout
            
            # Supprimer les anciens étudiants
            Student.query.filter_by(course_id=course.id).delete()
            
            # Ajouter les nouveaux
            db.session.bulk_save_objects(new_students)
            
            db.session.commit()
            flash(f'{len(new_students)} étudiants importés avec succès!', 'success')
            return redirect(url_for('course', course_name=course.name))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erreur import: {str(e)}", exc_info=True)
            flash(f"Erreur lors de l'import: {str(e)}", 'error')
            return redirect(request.url)
    
    # GET Request
    students = Student.query.filter_by(course_id=course.id).order_by(Student.full_name).all()
    return render_template('upload.html', 
                         course=course,
                         students=students,
                         now=datetime.now())

@app.route('/take_attendance/<course_name>', methods=['GET', 'POST'])
def take_attendance(course_name):
    course = Course.query.filter_by(name=course_name).first()
    if not course:
        flash('Cours non trouvé', 'error')
        return redirect(url_for('dashboard'))
    
    students = Student.query.filter_by(course_id=course.id).order_by(Student.full_name).all()
    
    if request.method == 'POST':
        date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Supprimer les anciennes entrées pour cette date
            Attendance.query.filter_by(course_id=course.id, date=attendance_date).delete()
            
            for student in students:
                status = request.form.get(f'status_{student.id}', 'absent')
                attendance = Attendance(
                    date=attendance_date,
                    status=status,
                    student_id=student.id,
                    course_id=course.id
                )
                db.session.add(attendance)
            
            db.session.commit()
            flash(f'Présence enregistrée pour le {attendance_date}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'error')
        
        return redirect(url_for('course', course_name=course_name))
    
    return render_template('attendance.html',
                         course=course,
                         students=students,
                         today=datetime.now().strftime('%Y-%m-%d'),
                         now=datetime.now())

@app.route('/statistics/<course_name>')
def statistics(course_name):
    course = Course.query.filter_by(name=course_name).first_or_404()
    
    # Récupérer les dates des séances
    session_dates = db.session.query(Attendance.date).filter_by(course_id=course.id).distinct().all()
    
    if not session_dates:
        flash('Aucune donnée de présence disponible', 'warning')
        return redirect(url_for('course', course_name=course.name))
    
    total_days = len(session_dates)
    students = Student.query.filter_by(course_id=course.id).all()
    
    # Préparer les statistiques
    stats = []
    for student in students:
        present_count = Attendance.query.filter_by(
            student_id=student.id,
            status='present',
            course_id=course.id
        ).count()
        
        attendance_rate = round((present_count / total_days * 100), 2) if total_days > 0 else 0
        
        stats.append({
            'student': student,
            'present_count': present_count,
            'attendance_rate': attendance_rate
        })

    # Générer le graphique
    try:
        plt.switch_backend('Agg')  # Important pour Flask
        
        names = [s.full_name for s in students]
        rates = [s['attendance_rate'] for s in stats]
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(names) * 0.4)))
        bars = ax.barh(names, rates, color='#4e73df')
        ax.bar_label(bars, fmt='%.1f%%', padding=3)
        ax.set_xlabel('Taux de présence (%)')
        ax.set_title(f'Taux de présence - {course.name}\nTotal séances: {total_days}')
        ax.set_xlim(0, 100)
        plt.tight_layout()
        
        # Convertir en image base64
        img = BytesIO()
        plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
        plt.close()  # Fermer la figure pour libérer la mémoire
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        
    except Exception as e:
        app.logger.error(f"Erreur génération graphique: {str(e)}")
        plot_url = None

    return render_template('statistics.html',
                         course=course,
                         stats=stats,
                         total_days=total_days,
                         plot_url=plot_url,
                         now=datetime.now())

@app.route('/export_pdf/<course_name>')
def export_pdf(course_name):
    course = Course.query.filter_by(name=course_name).first_or_404()
    
    # Récupérer les données
    session_dates = db.session.query(Attendance.date).filter_by(course_id=course.id).distinct().all()
    
    if not session_dates:
        flash('Aucune donnée à exporter', 'warning')
        return redirect(url_for('statistics', course_name=course.name))
    
    total_days = len(session_dates)
    students = Student.query.filter_by(course_id=course.id).all()
    
    # Préparer les statistiques
    stats = []
    for student in students:
        present_count = Attendance.query.filter_by(
            student_id=student.id,
            status='present',
            course_id=course.id
        ).count()
        
        attendance_rate = round((present_count / total_days * 100), 2) if total_days > 0 else 0
        
        stats.append({
            'student': student,
            'present_count': present_count,
            'attendance_rate': attendance_rate
        })

    # Création du PDF
    try:
        pdf = PDF()
        pdf.add_page()
        
        # En-tête
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'Statistiques de présence - {course.name}', 0, 1, 'C')
        pdf.ln(10)
        
        # Métadonnées
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Date du rapport: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1)
        pdf.cell(0, 10, f'Nombre de séances: {total_days}', 0, 1)
        pdf.ln(10)
        
        # Tableau
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(20, 10, 'ID', 1)
        pdf.cell(60, 10, 'Nom complet', 1)
        pdf.cell(30, 10, 'Matricule', 1)
        pdf.cell(30, 10, 'Présences', 1, 0, 'C')
        pdf.cell(30, 10, 'Taux (%)', 1, 0, 'C')
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        for stat in sorted(stats, key=lambda x: (-x['attendance_rate'], x['student'].full_name)):
            student = stat['student']
            pdf.cell(20, 10, str(student.id), 1)
            pdf.cell(60, 10, student.full_name, 1)
            pdf.cell(30, 10, student.matricule if student.matricule else '-', 1)
            pdf.cell(30, 10, f"{stat['present_count']}/{total_days}", 1, 0, 'C')
            pdf.cell(30, 10, f"{stat['attendance_rate']}%", 1, 0, 'C')
            pdf.ln()
        
        # Sauvegarde en mémoire
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        
        return send_file(
            pdf_output,
            as_attachment=True,
            download_name=f'presence_{course_name}_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        app.logger.error(f"Erreur génération PDF: {str(e)}")
        flash("Erreur lors de la génération du PDF", 'error')
        return redirect(url_for('statistics', course_name=course.name))

@app.route('/favicon.ico')
def favicon():
    return '', 404

# Créer les tables si elles n'existent pas
with app.app_context():
    db.create_all()

# if __name__ == '__main__':
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#     app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changer le port si nécessaire