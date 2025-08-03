import os
import json
import random
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for

import database

app = Flask(__name__)
DATA_FILE = 'data.json'

# Load data from JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save data to JSON
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Home Page
@app.route('/')
def index():
    data = load_data()
    publications = list(data.keys())
    return render_template('index.html', publications=publications)

# Get subjects
@app.route('/get_subjects/<publication>')
def get_subjects(publication):
    data = load_data()
    subjects = list(data.get(publication, {}).keys())
    return {"subjects": subjects}

# Get classes
@app.route('/get_classes/<publication>/<subject>')
def get_classes(publication, subject):
    data = load_data()
    classes = list(data.get(publication, {}).get(subject, {}).keys())
    return {"classes": classes}

@app.route('/get_chapters/<publication>/<subject>/<class_name>')
def get_chapters(publication, subject, class_name):
    data = load_data()
    class_data = data.get(publication, {}).get(subject, {}).get(class_name, {})

    # If class_data is a dict → normal chapters
    if isinstance(class_data, dict):
        chapters = list(class_data.keys())
    else:
        # If it’s a list (wrong structure), just return empty
        chapters = []

    return {"chapters": chapters}


# Show form to add a question
@app.route('/add')
def show_form():
    return render_template('add_question.html')

# Save a question
@app.route('/save_question', methods=['POST'])
def save_question():
    pub = request.form['publication']
    sub = request.form['subject']
    cls = request.form['class']
    ch = request.form['chapter']
    qtype = request.form['qtype']
    question = request.form.get('question', '').strip()
    match_key = request.form.get('match_key', '').strip()
    match_value = request.form.get('match_value', '').strip()

    data = load_data()
    data.setdefault(pub, {}).setdefault(sub, {}).setdefault(cls, {}).setdefault(ch, {}).setdefault(qtype, [])

    if qtype == "Match the Following" and match_key and match_value:
        data[pub][sub][cls][ch][qtype].append({match_key: match_value})
    elif question:
        data[pub][sub][cls][ch][qtype].append(question)

    save_data(data)
    return redirect(url_for('show_form'))




# Generate question paper
@app.route('/generate', methods=['POST'])
def generate_question_paper():
    data = load_data()

    pub = request.form.get('publication')
    sub = request.form.get('subject')
    cls = request.form.get('class')
    chapters = request.form.getlist('chapters')
   

    # Question type counts
    question_counts = {
        "Fill in the Blanks": int(request.form.get('fill_count', 0)),
        "True/False": int(request.form.get('tf_count', 0)),
        "Match the Following": int(request.form.get('match_count', 0)),
        "Choose the Best Answer": int(request.form.get('best_count', 0)),
        "Answer the Following": int(request.form.get('ans_count', 0)),
        "Full Form": int(request.form.get('fullform_count', 0)),
    }

    # Marks per question
    marks = {
        "Fill in the Blanks": int(request.form.get('fill_mark', 0)),
        "True/False": int(request.form.get('tf_mark', 0)),
        "Match the Following": int(request.form.get('match_mark', 0)),
        "Choose the Best Answer": int(request.form.get('best_mark', 0)),
        "Answer the Following": int(request.form.get('ans_mark', 0)),
        "Full Form": int(request.form.get('fullform_mark', 0)),
    }

    formatted_questions = {
        "Fill in the Blanks": [],
        "True/False": [],
        "Match the Following": [],
        "Choose the Best Answer": [],
        "Answer the Following": [],
        "Full Form": [],
        "Manual Questions": []
    }
    
    manual_questions = request.form.get('manual_questions', '').split('\n')
    manual_questions = [q.strip() for q in manual_questions if q.strip()]
    manual_mark = int(request.form.get('manual_mark', 0))
    
    formatted_questions["Manual Questions"] = manual_questions
    marks["Manual Questions"] = manual_mark
    question_counts["Manual Questions"] = len(manual_questions)

    # Collect questions
    for chapter in chapters:
        chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
        for qtype in formatted_questions:
            if qtype == "Match the Following":
                continue
            formatted_questions[qtype].extend(chapter_data.get(qtype, []))

    # Random sampling (non-match types)
    for qtype in formatted_questions:
        if qtype == "Match the Following":
            continue
        all_q = formatted_questions[qtype]
        formatted_questions[qtype] = random.sample(all_q, min(question_counts[qtype], len(all_q)))

    # Match the Following logic
    match_pairs = []
    for chapter in chapters:
        items = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {}).get("Match the Following", [])
        for pair in items:
            for k, v in pair.items():
                match_pairs.append((k.strip(), v.strip()))

    selected_match = random.sample(match_pairs, min(question_counts["Match the Following"], len(match_pairs)))

    # Shuffle only the right side (values)
    left = [k for k, v in selected_match]
    right = [v for k, v in selected_match]
    shuffled_right = right[:]
    random.shuffle(shuffled_right)

    formatted_questions["Match the Following"] = list(zip(left, shuffled_right))



    total_marks = sum(question_counts[qtype] * marks[qtype] for qtype in question_counts)

    return render_template(
        'question_paper.html',
        subject=sub,
        questions=formatted_questions,
        marks=marks,
        total_marks=total_marks,
        counts = {
            qtype: len(formatted_questions[qtype])
            for qtype in formatted_questions
        }

    )
    
@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    data = load_data()
    publications = list(data.keys())

    if request.method == 'POST':
        publication = request.form['publication']
        subject = request.form['subject']
        class_name = request.form['class']
        chapter = request.form['chapter']
        qtype = request.form['qtype']

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
            question_text = request.form.get("normal_question", "").strip()
            if question_text:
                lines = [line.strip() for line in question_text.split('\n') if line.strip()]
                data[publication][subject][class_name][chapter][qtype].extend(lines)

        save_data(data)
        return redirect(url_for('add_question'))

    # Pass publications to template to populate dropdown
    return render_template('add_question.html', publications=publications)


@app.route('/get_questions/<publication>/<subject>/<class_name>/<chapter>')
def get_questions(publication, subject, class_name, chapter):
    data = load_data()
    chapter_data = data.get(publication, {}).get(subject, {}).get(class_name, {}).get(chapter, {})
    return chapter_data  # returns JSON of all question types

@app.route('/add_info', methods=['GET', 'POST'])
def add_info():
    if request.method == 'POST':
        publication = request.form['publication']
        subject = request.form['subject']
        class_name = request.form['class_name']
        chapter = request.form['chapter']

        data = load_data()

        # Make sure each level is dict
        if publication not in data:
            data[publication] = {}
        if subject not in data[publication]:
            data[publication][subject] = {}
        if class_name not in data[publication][subject]:
            data[publication][subject][class_name] = {}
        if chapter not in data[publication][subject][class_name]:
            data[publication][subject][class_name][chapter] = {}

        save_data(data)
        return redirect(url_for('add_question'))

    return render_template('add_info.html')

def rename_key_in_json(filename, publication, subject=None, class_name=None, chapter=None,
                       new_publication=None, new_subject=None, new_class=None, new_chapter=None):
    with open(filename, "r") as f:
        data = json.load(f)

    if new_publication and publication in data:
        data[new_publication] = data.pop(publication)
        publication = new_publication  # update reference

    if subject and new_subject and subject in data[publication]:
        data[publication][new_subject] = data[publication].pop(subject)
        subject = new_subject

    if class_name and new_class and class_name in data[publication][subject]:
        data[publication][subject][new_class] = data[publication][subject].pop(class_name)
        class_name = new_class

    if chapter and new_chapter and chapter in data[publication][subject][class_name]:
        data[publication][subject][class_name][new_chapter] = \
            data[publication][subject][class_name].pop(chapter)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


@app.route('/rename', methods=['GET', 'POST'])
def rename_page():
    data = load_data()
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

        # ✅ Only rename fields where new value is provided
        rename_key_in_json(
            'data.json',
            publication=old_pub,
            subject=old_sub,
            class_name=old_class,
            chapter=old_chap,
            new_publication=new_pub if new_pub else None,
            new_subject=new_sub if new_sub else None,
            new_class=new_class if new_class else None,
            new_chapter=new_chap if new_chap else None
        )

        return redirect(url_for('rename_page'))

    return render_template('rename.html', publications=publications, data=data)

@app.route("/rename_question", methods=["GET", "POST"])
def rename_question():
    data = load_data()

    if request.method == "POST":
        pub = request.form["publication"]
        sub = request.form["subject"]
        cls = request.form["class_name"]
        chap = request.form["chapter"]
        qtype = request.form["qtype"]
        idx = int(request.form["old_question"])   # index from dropdown
        qlist = data[pub][sub][cls][chap][qtype]

        # Handle each type
        if qtype in ["Fill in the Blanks", "True/False", "Answer the Following", "Manual Questions"]:
            new_q = request.form["new_question"].strip()
            if new_q:
                qlist[idx] = new_q

        elif qtype == "Match the Following":
            new_left = request.form["new_left"].strip()
            new_right = request.form["new_right"].strip()
            if new_left and new_right:
                qlist[idx] = {new_left: new_right}

        elif qtype == "Choose the Best Answer":
            new_q = request.form["new_question_mcq"].strip()
            new_opts = [
                request.form["option1"].strip(),
                request.form["option2"].strip(),
                request.form["option3"].strip(),
                request.form["option4"].strip(),
            ]
            new_ans = request.form["answer"].strip()
            qlist[idx] = {
                "question": new_q,
                "options": new_opts,
                "answer": new_ans,
            }

        elif qtype == "Full Form":
            new_abbr = request.form["new_abbr"].strip()
            new_full = request.form["new_full"].strip()
            if new_abbr and new_full:
                qlist[idx] = {new_abbr: new_full}

        save_data(data)
        return "✅ Rename successful! <a href='/rename_question'>Rename more</a>"

    return render_template("rename_question.html", data=data)

# Run app
if __name__ == '__main__':
    app.run(debug=True)
