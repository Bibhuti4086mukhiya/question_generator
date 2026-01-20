from flask import Blueprint, render_template, request, redirect, url_for
from database import db

questions_bp = Blueprint('questions', __name__)

# Show form to add a question (Legacy route, kept for compatibility)
@questions_bp.route('/add')
def show_form():
    return render_template('add_question.html')

# Save a question (Legacy route)
@questions_bp.route('/save_question', methods=['POST'])
def save_question():
    pub = request.form['publication']
    sub = request.form['subject']
    cls = request.form['class']
    ch = request.form['chapter']
    qtype = request.form['qtype']
    question = request.form.get('question', '').strip()
    match_key = request.form.get('match_key', '').strip()
    match_value = request.form.get('match_value', '').strip()

    data = db.load()
    data.setdefault(pub, {}).setdefault(sub, {}).setdefault(cls, {}).setdefault(ch, {}).setdefault(qtype, [])

    if qtype == "Match the Following" and match_key and match_value:
        data[pub][sub][cls][ch][qtype].append({match_key: match_value})
    elif question:
        data[pub][sub][cls][ch][qtype].append(question)

    db.save(data)
    return redirect(url_for('questions.show_form'))

@questions_bp.route('/add_question', methods=['GET', 'POST'])
def add_question():
    data = db.load()
    publications = list(data.keys())
    
    # Initialize selected values
    selected_pub = ''
    selected_sub = ''
    selected_cls = ''
    selected_chapter = ''
    selected_qtype = ''
    
    if request.method == 'POST':
        try:
            # Get form data with defaults
            publication = request.form.get('publication', '').strip()
            subject = request.form.get('subject', '').strip()
            class_name = request.form.get('class', '').strip()
            chapter = request.form.get('chapter', '').strip()
            qtype = request.form.get('qtype', '').strip()
            
            # Store selections for persistence
            selected_pub = publication
            selected_sub = subject
            selected_cls = class_name
            selected_chapter = chapter
            selected_qtype = qtype
            
            # Validate required fields
            if not all([publication, subject, class_name, chapter, qtype]):
                return render_template('add_question.html', 
                                    publications=publications,
                                    selected_pub=selected_pub,
                                    selected_sub=selected_sub,
                                    selected_cls=selected_cls,
                                    selected_chapter=selected_chapter,
                                    selected_qtype=selected_qtype,
                                    data=data)
            
            # Initialize data structure
            data.setdefault(publication, {}) \
                .setdefault(subject, {}) \
                .setdefault(class_name, {}) \
                .setdefault(chapter, {}) \
                .setdefault(qtype, [])
            
            if qtype == "Match the Following":
                match_key = request.form.get("match_key", "").strip()
                match_value = request.form.get("match_value", "").strip()
                if match_key and match_value:
                    data[publication][subject][class_name][chapter][qtype].append({match_key: match_value})
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)
            
            elif qtype == "Fill in the Blanks":
                question_text = request.form.get("fib_question", "").strip()
                answer_text = request.form.get("fib_answer", "").strip()
                if question_text and answer_text:
                    new_question = {"question": question_text, "answer": answer_text}
                    data[publication][subject][class_name][chapter][qtype].append(new_question)
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)
                    
            elif qtype == "True/False":
                question_text = request.form.get("true_false_question", "").strip()
                answer_text = request.form.get("true_false_answer", "").strip()
                if question_text and answer_text:
                    new_question = {"question": question_text, "answer": answer_text}
                    data[publication][subject][class_name][chapter][qtype].append(new_question)
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            elif qtype == "Choose the Best Answer":
                question = request.form.get("best_answer_question", "").strip()
                option1 = request.form.get("option1", "").strip()
                option2 = request.form.get("option2", "").strip()
                option3 = request.form.get("option3", "").strip()
                option4 = request.form.get("option4", "").strip()
                answer = request.form.get("answer", "").strip()

                if question and option1 and option2 and option3 and option4 and answer:
                    new_q = {
                        "question": question,
                        "options": [option1, option2, option3, option4],
                        "answer": answer
                    }
                    data[publication][subject][class_name][chapter][qtype].append(new_q)
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            elif qtype == "Full Form":
                full_form_abbr = request.form.get("full_form_abbr", "").strip()
                full_form_text = request.form.get("full_form_text", "").strip()
                if full_form_abbr and full_form_text:
                    data[publication][subject][class_name][chapter][qtype].append({full_form_abbr: full_form_text})
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            elif qtype == "One Word Answer":
                question_text = request.form.get("normal_question", "").strip()
                answer_text = request.form.get("one_word_answer", "").strip()
                
                if question_text and answer_text:
                    new_question = {"question": question_text, "answer": answer_text}
                    data[publication][subject][class_name][chapter][qtype].append(new_question)
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            else:
                question_text = request.form.get("normal_question", "").strip()
                if question_text:
                    lines = [line.strip() for line in question_text.split('\n') if line.strip()]
                    data[publication][subject][class_name][chapter][qtype].extend(lines)
                else:
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            db.save(data)
            
            return redirect(url_for('questions.add_question', 
                                  publication=publication,
                                  subject=subject, 
                                  class_name=class_name,
                                  chapter=chapter,
                                  qtype=qtype))
            
        except Exception as e:
            return render_template('add_question.html', 
                                publications=publications,
                                selected_pub=selected_pub,
                                selected_sub=selected_sub,
                                selected_cls=selected_cls,
                                selected_chapter=selected_chapter,
                                selected_qtype=selected_qtype,
                                data=data)
    
    else:
        selected_pub = request.args.get('publication', '')
        selected_sub = request.args.get('subject', '')
        selected_cls = request.args.get('class_name', '')
        selected_chapter = request.args.get('chapter', '')
        selected_qtype = request.args.get('qtype', '')

    return render_template('add_question.html', 
                         publications=publications,
                         selected_pub=selected_pub,
                         selected_sub=selected_sub,
                         selected_cls=selected_cls,
                         selected_chapter=selected_chapter,
                         selected_qtype=selected_qtype,
                         data=data)

@questions_bp.route('/get_questions/<publication>/<subject>/<class_name>/<chapter>')
def get_questions(publication, subject, class_name, chapter):
    data = db.load()
    chapter_data = data.get(publication, {}).get(subject, {}).get(class_name, {}).get(chapter, {})
    return chapter_data

@questions_bp.route("/view_questions", methods=["GET", "POST"])
def view_questions():
    data = db.load()
    publications = list(data.keys())
    questions_data = None
    selected_pub = selected_sub = selected_class = selected_chapter = None

    if request.method == "POST":
        selected_pub = request.form.get("publication")
        selected_sub = request.form.get("subject")
        selected_class = request.form.get("class_name")
        selected_chapter = request.form.get("chapter")

        if not (selected_pub and selected_sub and selected_class):
            return "❌ Please select Publication, Subject, and Class"

        if selected_chapter:
            questions_data = {selected_chapter: data[selected_pub][selected_sub][selected_class][selected_chapter]}
        else:
            questions_data = data[selected_pub][selected_sub][selected_class]

    return render_template(
        "view_questions.html",
        data=data,
        publications=publications,
        questions_data=questions_data,
        selected_pub=selected_pub,
        selected_sub=selected_sub,
        selected_class=selected_class,
        selected_chapter=selected_chapter,
    )

@questions_bp.route("/add_category", methods=["GET", "POST"])
def add_category():
    data = db.load()
    publications = list(data.keys())

    if request.method == "POST":
        pub = request.form["publication"]
        sub = request.form["subject"]
        cls = request.form["class_name"]
        chapter = request.form["chapter"]
        new_category = request.form["new_category"]

        if pub and sub and cls and chapter and new_category:
            if new_category not in data[pub][sub][cls][chapter]:
                data[pub][sub][cls][chapter][new_category] = []
                db.save(data)
                return "✅ Category Added Successfully!"
            else:
                return "⚠️ Category already exists!"

    return render_template("add_category.html", publications=publications, data=data)

@questions_bp.route('/rename_question', methods=['GET', 'POST'])
def rename_question():
    if request.method == 'POST':
        try:
            publication = request.form['publication']
            subject = request.form['subject']
            class_name = request.form['class_name']
            chapter = request.form['chapter']
            qtype = request.form['qtype']
            old_index = int(request.form['old_question_index'])

            data = db.load()
            qlist = data[publication][subject][class_name][chapter][qtype]

            if qtype in ["Fill in the Blanks", "True/False", "One Word Answer"]:
                qlist[old_index]['question'] = request.form['question_text']
                qlist[old_index]['answer'] = request.form['answer_text']
                
            elif qtype in ["Answer the Following", "Short Answer", "Long Answer"]:
                qlist[old_index] = request.form['simple_question']
                
            elif qtype == "Match the Following":
                left = request.form['match_left']
                right = request.form['match_right']
                qlist[old_index] = {left: right}
                
            elif qtype == "Choose the Best Answer":
                qlist[old_index]['question'] = request.form['question_mcq']
                qlist[old_index]['options'] = [
                    request.form.get('option1', ''),
                    request.form.get('option2', ''),
                    request.form.get('option3', ''),
                    request.form.get('option4', '')
                ]
                qlist[old_index]['answer'] = request.form['answer_mcq']
                
            elif qtype == "Full Form":
                abbr = request.form['abbr']
                full = request.form['full_form']
                qlist[old_index] = {abbr: full}

            db.save(data)
            return redirect(url_for('questions.rename_question'))

        except Exception as e:
            return redirect(url_for('questions.rename_question'))

    data = db.load()
    return render_template('rename_question.html', data=data)

@questions_bp.route('/delete_question', methods=['GET', 'POST'])
def delete_question():
    data = db.load()

    if request.method == 'POST':
        try:
            publication = request.form['publication']
            subject = request.form['subject']
            class_name = request.form['class_name']
            chapter = request.form['chapter']
            qtype = request.form['qtype']
            question_index = int(request.form['question_index'])

            qlist = data[publication][subject][class_name][chapter][qtype]

            if 0 <= question_index < len(qlist):
                qlist.pop(question_index)
                db.save(data)

            return redirect(url_for('questions.delete_question'))

        except Exception as e:
            return redirect(url_for('questions.delete_question'))

    publications = list(data.keys())
    return render_template("delete_question.html", data=data, publications=publications)

@questions_bp.route('/delete_question_type', methods=['GET', 'POST'])
def delete_question_type():
    data = db.load()
    message = None

    if request.method == 'POST':
        pub = request.form['publication']
        sub = request.form['subject']
        cls = request.form['class_name']
        chap = request.form['chapter']
        qtype = request.form['qtype']

        try:
            del data[pub][sub][cls][chap][qtype]
            if not data[pub][sub][cls][chap]:
                del data[pub][sub][cls][chap]
            db.save(data)
            message = f"Deleted all '{qtype}' questions from chapter '{chap}'."
        except KeyError:
            message = "Selected questions not found."

    return render_template('delete_question_type.html', data=data, message=message)