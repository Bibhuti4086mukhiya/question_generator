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
# @app.route('/generate', methods=['POST'])
# def generate_question_paper():
#     data = load_data()

#     pub = request.form.get('publication')
#     sub = request.form.get('subject')
#     cls = request.form.get('class')
#     chapters = request.form.getlist('chapters')
   

#     # Question type counts
#     question_counts = {
#         "Fill in the Blanks": int(request.form.get('fill_count', 0)),
#         "True/False": int(request.form.get('tf_count', 0)),
#         "Match the Following": int(request.form.get('match_count', 0)),
#         "Choose the Best Answer": int(request.form.get('best_count', 0)),
#         "Answer the Following": int(request.form.get('ans_count', 0)),
#         "Full Form": int(request.form.get('fullform_count', 0)),
#         "One Word Answer": int(request.form.get('oneword_count', 0)),
#         "Short Question Answer": int(request.form.get('short_count', 0)),
#         "Long Question Answer": int(request.form.get('long_count', 0)),
#     }


#     # Marks per question
#     marks = {
#         "Fill in the Blanks": int(request.form.get('fill_mark', 0)),
#         "True/False": int(request.form.get('tf_mark', 0)),
#         "Match the Following": int(request.form.get('match_mark', 0)),
#         "Choose the Best Answer": int(request.form.get('best_mark', 0)),
#         "Answer the Following": int(request.form.get('ans_mark', 0)),
#         "Full Form": int(request.form.get('fullform_mark', 0)),
#         "One Word Answer": int(request.form.get('oneword_mark', 0)),
#         "Short Question Answer": int(request.form.get('short_mark', 0)),
#         "Long Question Answer": int(request.form.get('long_mark', 0)),
#     }

#     formatted_questions = {
#         "Fill in the Blanks": [],
#         "True/False": [],
#         "Match the Following": [],
#         "Choose the Best Answer": [],
#         "Full Form": [],
#         "One Word Answer": [],
#         "Answer the Following": [],
#         "Short Question Answer": [],
#         "Long Question Answer": [],
#         "Manual Questions": []
#     }
    
#     manual_questions = request.form.get('manual_questions', '').split('\n')
#     manual_questions = [q.strip() for q in manual_questions if q.strip()]
#     manual_mark = int(request.form.get('manual_mark', 0))
    
#     formatted_questions["Manual Questions"] = manual_questions
#     marks["Manual Questions"] = manual_mark
#     question_counts["Manual Questions"] = len(manual_questions)

#     # Collect questions
#     for chapter in chapters:
#         chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
#         for qtype in formatted_questions:
#             if qtype == "Match the Following":
#                 continue
#             formatted_questions[qtype].extend(chapter_data.get(qtype, []))

#     # Random sampling (non-match types)
#     for qtype in formatted_questions:
#         if qtype == "Match the Following":
#             continue
#         all_q = formatted_questions[qtype]
#         formatted_questions[qtype] = random.sample(all_q, min(question_counts[qtype], len(all_q)))

#     # Match the Following logic
#     match_pairs = []
#     for chapter in chapters:
#         items = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {}).get("Match the Following", [])
#         for pair in items:
#             for k, v in pair.items():
#                 match_pairs.append((k.strip(), v.strip()))

#     selected_match = random.sample(match_pairs, min(question_counts["Match the Following"], len(match_pairs)))

#     # Shuffle only the right side (values)
#     left = [k for k, v in selected_match]
#     right = [v for k, v in selected_match]
#     shuffled_right = right[:]
#     random.shuffle(shuffled_right)

#     formatted_questions["Match the Following"] = list(zip(left, shuffled_right))



#     total_marks = sum(question_counts[qtype] * marks[qtype] for qtype in question_counts)

#     return render_template(
#         'question_paper.html',
#         subject=sub,
#         questions=formatted_questions,
#         marks=marks,
#         total_marks=total_marks,
#         counts = {
#             qtype: len(formatted_questions[qtype])
#             for qtype in formatted_questions
#         }

#     )

# Generate question paper dynamically
@app.route('/generate', methods=['POST'])
def generate_question_paper():
    data = load_data()

    pub = request.form.get('publication')
    sub = request.form.get('subject')
    cls = request.form.get('class')
    chapters = request.form.getlist('chapters')

    # Step 1: Collect all categories from selected chapters
    all_categories = set()
    for chapter in chapters:
        chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
        for qtype in chapter_data.keys():
            all_categories.add(qtype)

    # Always include Manual Questions
    all_categories.add("Manual Questions")

    # Step 2: Build question_counts and marks dictionaries dynamically
    question_counts = {}
    marks = {}
    formatted_questions = {}

    for qtype in all_categories:
        # convert category name to safe form key
        key = qtype.lower().replace(" ", "_")
        question_counts[qtype] = int(request.form.get(f"{key}_count", 0))
        marks[qtype] = int(request.form.get(f"{key}_mark", 0))
        formatted_questions[qtype] = []

    # Step 3: Handle manual questions separately
    # Manual Questions
    manual_questions = request.form.get('manual_questions', '').split('\n')
    manual_questions = [q.strip() for q in manual_questions if q.strip()]

    manual_mark = int(request.form.get('manual_mark', 0))

    formatted_questions["Manual Questions"] = manual_questions
    marks["Manual Questions"] = manual_mark
    question_counts["Manual Questions"] = len(manual_questions)   # ✅ number of lines in textarea

    # Step 4: Collect questions from chapters
    for chapter in chapters:
        chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
        for qtype in all_categories:
            if qtype in ["Match the Following"]:
                continue
            formatted_questions[qtype].extend(chapter_data.get(qtype, []))

    # Step 5: Random sample for normal categories
    for qtype in formatted_questions:
        if qtype in ["Match the Following"]:
            continue
        all_q = formatted_questions[qtype]
        count = question_counts.get(qtype, 0)
        formatted_questions[qtype] = random.sample(all_q, min(count, len(all_q))) if all_q else []

    # Step 6: Special handling for Match the Following
    if "Match the Following" in all_categories:
        match_pairs = []
        for chapter in chapters:
            items = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {}).get("Match the Following", [])
            for pair in items:
                for k, v in pair.items():
                    match_pairs.append((k.strip(), v.strip()))

        selected_match = random.sample(match_pairs, min(question_counts["Match the Following"], len(match_pairs))) if match_pairs else []
        left = [k for k, v in selected_match]
        right = [v for k, v in selected_match]
        random.shuffle(right)
        formatted_questions["Match the Following"] = list(zip(left, right))

    # Step 7: Total marks
    total_marks = sum(question_counts[qtype] * marks.get(qtype, 0) for qtype in question_counts)

    return render_template(
        'question_paper.html',
        subject=sub,
        questions=formatted_questions,
        marks=marks,
        total_marks=total_marks,
        counts={qtype: len(formatted_questions[qtype]) for qtype in formatted_questions}
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
        return redirect(url_for('rename_question'))

    return render_template("rename_question.html", data=data)


@app.route('/delete_question', methods=['GET', 'POST'])
def delete_question():
    data = load_data()  # Load JSON

    if request.method == 'POST':
        publication = request.form['publication']
        subject = request.form['subject']
        class_name = request.form['class_name']
        chapter = request.form['chapter']
        qtype = request.form['qtype']
        old_question = request.form['old_question']

        try:
            if qtype in ["Fill in the Blanks", "True/False", "Answer the Following", "Manual Questions", "Full Form"]:
                if old_question in data[publication][subject][class_name][chapter][qtype]:
                    data[publication][subject][class_name][chapter][qtype].remove(old_question)

            elif qtype == "Match the Following":
                match_list = data[publication][subject][class_name][chapter][qtype]
                for pair in match_list:
                    if old_question in pair.keys():
                        match_list.remove(pair)
                        break

            elif qtype == "Choose the Best Answer":
                mcq_list = data[publication][subject][class_name][chapter][qtype]
                for mcq in mcq_list:
                    if mcq["question"] == old_question:
                        mcq_list.remove(mcq)
                        break

            save_data(data)
            return redirect(url_for('delete_question'))

        except Exception as e:
            return f"❌ Error: {e}"

    # ⬇️ This part runs only when method == GET
    publications = list(data.keys())
    return render_template("delete_question.html",data=data,publications=publications)

@app.route('/delete', methods=['GET', 'POST'])
def delete_page():
    data = load_data()

    if request.method == 'POST':
        publication = request.form.get('publication')
        subject = request.form.get('subject')
        class_name = request.form.get('class_name')
        chapter = request.form.get('chapter')

        try:
            if publication and not subject:  
                # Delete entire publication
                if publication in data:
                    del data[publication]

            elif publication and subject and not class_name:  
                # Delete subject
                if subject in data[publication]:
                    del data[publication][subject]

            elif publication and subject and class_name and not chapter:  
                # Delete class
                if class_name in data[publication][subject]:
                    del data[publication][subject][class_name]

            elif publication and subject and class_name and chapter:  
                # Delete chapter
                if chapter in data[publication][subject][class_name]:
                    del data[publication][subject][class_name][chapter]

            save_data(data)
            return redirect(url_for('delete_page'))

        except Exception as e:
            return f"❌ Error: {e}"

    publications = list(data.keys())
    return render_template("delete.html", data=data, publications=publications)

@app.route("/view_questions", methods=["GET", "POST"])
def view_questions():
    data = load_data()
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

        if selected_chapter:  # one chapter only
            questions_data = {selected_chapter: data[selected_pub][selected_sub][selected_class][selected_chapter]}
        else:  # all chapters of the class
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
    
@app.route('/get_question_types', methods=['POST'])
def get_question_types():
    data = load_data()
    req = request.get_json()

    pub = req.get("publication")
    sub = req.get("subject")
    cls = req.get("class")
    chapters = req.get("chapters", [])

    # Collect all unique question types from selected chapters
    question_types = set()
    for chapter in chapters:
        chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
        for qtype in chapter_data.keys():
            question_types.add(qtype)

    # Always add Manual Questions
    question_types.add("Manual Questions")

    return jsonify({"types": list(question_types)})



@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    data = load_data()
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
                save_data(data)
                return "✅ Category Added Successfully!"
            else:
                return "⚠️ Category already exists!"

    return render_template("add_category.html", publications=publications, data=data)

@app.route("/get_categories/<pub>/<sub>/<cls>", methods=["GET"])
def get_categories(pub, sub, cls):
    chapters_param = request.args.get("chapters", "")
    selected_chapters = chapters_param.split(",") if chapters_param else []

    data = load_data()
    categories = set()

    try:
        for chapter in selected_chapters:
            chapter = chapter.strip()
            if chapter and chapter in data.get(pub, {}).get(sub, {}).get(cls, {}):
                cats = list(data[pub][sub][cls][chapter].keys())
                categories.update(cats)
    except Exception as e:
        print("❌ Error fetching categories:", e)

    return {"categories": sorted(list(categories))}

@app.route('/delete_question_type', methods=['GET', 'POST'])
def delete_question_type():
    data = load_data()
    message = None

    if request.method == 'POST':
        pub = request.form['publication']
        sub = request.form['subject']
        cls = request.form['class_name']
        chap = request.form['chapter']
        qtype = request.form['qtype']

        try:
            # Delete the question type from that chapter
            del data[pub][sub][cls][chap][qtype]
            
            # If chapter is empty after deletion, you can optionally delete chapter
            if not data[pub][sub][cls][chap]:
                del data[pub][sub][cls][chap]

            save_data(data)
            message = f"Deleted all '{qtype}' questions from chapter '{chap}'."

        except KeyError:
            message = "Selected questions not found."

    return render_template('delete_question_type.html', data=data, message=message)


# Run app
if __name__ == '__main__':
    app.run(debug=True)
