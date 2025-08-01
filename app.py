import os
import json
import random
from flask import Flask, jsonify, render_template, request, redirect, url_for

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




# Run app
if __name__ == '__main__':
    app.run(debug=True)
