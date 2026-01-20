from flask import Blueprint, render_template, request, redirect, url_for
from database import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/add_pulication', methods=['GET', 'POST'])
def add_pulication():
    data = db.load()
    
    publications = list(data.keys())
    subjects = set()
    classes = set()
    chapters = set()
    
    for pub, pub_data in data.items():
        for subject, subject_data in pub_data.items():
            subjects.add(subject)
            for class_name, class_data in subject_data.items():
                classes.add(class_name)
                for chapter in class_data.keys():
                    chapters.add(chapter)
    
    if request.method == 'POST':
        publication = request.form['publication']
        subject = request.form['subject']
        class_name = request.form['class_name']
        chapter = request.form['chapter']

        if publication not in data:
            data[publication] = {}
        if subject not in data[publication]:
            data[publication][subject] = {}
        if class_name not in data[publication][subject]:
            data[publication][subject][class_name] = {}
        if chapter not in data[publication][subject][class_name]:
            data[publication][subject][class_name][chapter] = {}

        db.save(data)
        return redirect(url_for('questions.add_question'))

    return render_template('add_pulication.html',
                         publications=sorted(publications),
                         subjects=sorted(subjects),
                         classes=sorted(classes),
                         chapters=sorted(chapters))

def rename_key_in_json(publication, subject=None, class_name=None, chapter=None,
                       new_publication=None, new_subject=None, new_class=None, new_chapter=None):
    data = db.load()

    if new_publication and publication in data:
        data[new_publication] = data.pop(publication)
        publication = new_publication

    if subject and new_subject and subject in data[publication]:
        data[publication][new_subject] = data[publication].pop(subject)
        subject = new_subject

    if class_name and new_class and class_name in data[publication][subject]:
        data[publication][subject][new_class] = data[publication][subject].pop(class_name)
        class_name = new_class

    if chapter and new_chapter and chapter in data[publication][subject][class_name]:
        data[publication][subject][class_name][new_chapter] = \
            data[publication][subject][class_name].pop(chapter)

    db.save(data)

@admin_bp.route('/rename', methods=['GET', 'POST'])
def rename_page():
    data = db.load()
    publications = list(data.keys())

    if request.method == 'POST':
        old_pub = request.form.get('old_publication')
        new_pub = request.form.get('new_publication', '').strip()
        old_sub = request.form.get('old_subject') or None
        new_sub = request.form.get('new_subject', '').strip()
        old_class = request.form.get('old_class_name') or None
        new_class = request.form.get('new_class_name', '').strip()
        old_chap = request.form.get('old_chapter') or None
        new_chap = request.form.get('new_chapter', '').strip()

        rename_key_in_json(
            publication=old_pub,
            subject=old_sub,
            class_name=old_class,
            chapter=old_chap,
            new_publication=new_pub if new_pub else None,
            new_subject=new_sub if new_sub else None,
            new_class=new_class if new_class else None,
            new_chapter=new_chap if new_chap else None
        )
        return redirect(url_for('admin.rename_page'))

    return render_template('rename.html', publications=publications, data=data)

@admin_bp.route('/delete', methods=['GET', 'POST'])
def delete_page():
    data = db.load()

    if request.method == 'POST':
        publication = request.form.get('publication')
        subject = request.form.get('subject')
        class_name = request.form.get('class_name')
        chapter = request.form.get('chapter')

        try:
            if publication and not subject:  
                if publication in data:
                    del data[publication]
            elif publication and subject and not class_name:  
                if subject in data[publication]:
                    del data[publication][subject]
            elif publication and subject and class_name and not chapter:  
                if class_name in data[publication][subject]:
                    del data[publication][subject][class_name]
            elif publication and subject and class_name and chapter:  
                if chapter in data[publication][subject][class_name]:
                    del data[publication][subject][class_name][chapter]

            db.save(data)
            return redirect(url_for('admin.delete_page'))

        except Exception as e:
            return f"❌ Error: {e}"

    publications = list(data.keys())
    return render_template("delete.html", data=data, publications=publications)