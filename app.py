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
    try:
        data = load_data()

        # Step 1: Get form data with validation
        pub = request.form.get('publication', '').strip()
        sub = request.form.get('subject', '').strip()
        cls = request.form.get('class', '').strip()
        chapters = request.form.getlist('chapters')
        
        # Validate required fields
        if not all([pub, sub, cls, chapters]):
            # flash('Please fill all required fields: Publication, Subject, Class, and at least one Chapter', 'error')
            return redirect(request.referrer or url_for('index'))

        # Step 2: Collect all categories from selected chapters
        all_categories = set()
        valid_chapters = []
        
        for chapter in chapters:
            chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
            if chapter_data:  # Only include chapters that exist in data
                valid_chapters.append(chapter)
                for qtype in chapter_data.keys():
                    all_categories.add(qtype)
            else:
                print(f"Warning: Chapter '{chapter}' not found in data for {pub}/{sub}/{cls}")

        if not valid_chapters:
            # flash('No valid chapters found for the selected criteria', 'error')
            return redirect(request.referrer or url_for('index'))

        # Always include Manual Questions
        all_categories.add("Manual Questions")

        # Step 3: Build question_counts and marks dictionaries dynamically
        question_counts = {}
        marks = {}
        formatted_questions = {}

        for qtype in all_categories:
            # Convert category name to safe form key
            key = qtype.lower().replace(" ", "_")
            question_counts[qtype] = int(request.form.get(f"{key}_count", 0))
            marks[qtype] = int(request.form.get(f"{key}_mark", 0))
            formatted_questions[qtype] = []

        # Step 4: Handle manual questions
        manual_text = request.form.get('manual_questions', '').strip()
        manual_mark = int(request.form.get('manual_mark', 0))
        manual_format = request.form.get('manual_output_format', 'original')

        if manual_text:
            manual_lines = [line.strip().replace('\r', '') for line in manual_text.split('\n') if line.strip()]
            
            if manual_format == 'numbered':
                formatted_questions["Manual Questions"] = [f"{i+1}. {line}" for i, line in enumerate(manual_lines)]
                question_counts["Manual Questions"] = len(manual_lines)
            else:
                formatted_questions["Manual Questions"] = manual_lines
                question_counts["Manual Questions"] = 1
            
            marks["Manual Questions"] = manual_mark
        else:
            # Remove Manual Questions if no content
            all_categories.discard("Manual Questions")
            question_counts.pop("Manual Questions", None)
            marks.pop("Manual Questions", None)
            formatted_questions.pop("Manual Questions", None)

        # Step 5: Collect questions from valid chapters with proper formatting
        chapter_questions = {}
        for qtype in all_categories:
            if qtype in ["Match the Following", "Manual Questions"]:
                continue
                
            chapter_questions[qtype] = []
            
            for chapter in valid_chapters:
                chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
                questions = chapter_data.get(qtype, [])
                
                for question in questions:
                    if qtype == "Choose the Best Answer":
                        # Handle MCQ questions - ensure they have proper structure
                        if isinstance(question, dict) and 'question' in question:
                            # Valid MCQ format
                            chapter_questions[qtype].append({
                                'question': question['question'],
                                'options': question.get('options', ['Option A', 'Option B', 'Option C', 'Option D'])
                            })
                        elif isinstance(question, str):
                            # Convert string to valid MCQ format
                            chapter_questions[qtype].append({
                                'question': question,
                                'options': ['Option A', 'Option B', 'Option C', 'Option D']
                            })
                        else:
                            # Invalid format, skip
                            continue
                    else:
                        # Handle other question types
                        if isinstance(question, dict) and 'question' in question:
                            chapter_questions[qtype].append(question['question'])
                        elif isinstance(question, str):
                            chapter_questions[qtype].append(question)

        # Step 6: Random sample for normal categories
        for qtype in all_categories:
            if qtype in ["Match the Following", "Manual Questions"]:
                continue
                
            all_available = chapter_questions.get(qtype, [])
            count_needed = question_counts.get(qtype, 0)
            
            if all_available and count_needed > 0:
                selected = random.sample(all_available, min(count_needed, len(all_available)))
                formatted_questions[qtype] = selected
            else:
                formatted_questions[qtype] = []

        # Step 7: Special handling for Match the Following
        if "Match the Following" in all_categories:
            match_pairs = []
            
            for chapter in valid_chapters:
                items = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {}).get("Match the Following", [])
                for pair in items:
                    if isinstance(pair, dict):
                        for k, v in pair.items():
                            match_pairs.append((k.strip(), v.strip()))
                    elif isinstance(pair, (list, tuple)) and len(pair) == 2:
                        match_pairs.append((pair[0].strip(), pair[1].strip()))

            count_needed = question_counts.get("Match the Following", 0)
            if match_pairs and count_needed > 0:
                selected_match = random.sample(match_pairs, min(count_needed, len(match_pairs)))
                left = [k for k, v in selected_match]
                right = [v for k, v in selected_match]
                random.shuffle(right)
                formatted_questions["Match the Following"] = list(zip(left, right))
            else:
                formatted_questions["Match the Following"] = []

        # Step 8: Handle Fill in the Blanks with word bank
        if "Fill in the Blanks" in all_categories:
            fib_all_questions = []
            fib_all_answers = []

            for chapter in valid_chapters:
                chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
                fib_raw = chapter_data.get("Fill in the Blanks", [])

                for item in fib_raw:
                    if isinstance(item, dict) and 'question' in item:
                        fib_all_questions.append(item['question'])
                        fib_all_answers.append(item.get('answer', ''))
                    elif isinstance(item, str):
                        fib_all_questions.append(item)
                        fib_all_answers.append("")

            fib_count = question_counts.get("Fill in the Blanks", 0)
            
            if fib_all_questions and fib_count > 0:
                selected_indices = random.sample(range(len(fib_all_questions)), min(fib_count, len(fib_all_questions)))
                fill_questions = [fib_all_questions[i] for i in selected_indices]
                selected_answers = [fib_all_answers[i] for i in selected_indices]
                
                # Create word bank from unique non-empty answers
                options = list(dict.fromkeys([ans for ans in selected_answers if ans.strip()]))
                random.shuffle(options)
                
                formatted_questions["Fill in the Blanks"] = fill_questions
            else:
                formatted_questions["Fill in the Blanks"] = []
                options = []
        else:
            options = []

        # Step 9: Calculate total marks and prepare counts
        total_marks = 0
        counts = {}
        
        for qtype in formatted_questions:
            count = len(formatted_questions[qtype])
            counts[qtype] = count
            total_marks += count * marks.get(qtype, 0)

        # Step 10: Render template
        return render_template(
            'question_paper.html',
            subject=sub,
            class_name=cls,  # ✅ Added class_name here
            questions=formatted_questions,
            marks=marks,
            question_counts=question_counts,
            total_marks=total_marks,
            counts=counts,
            fill_options=options,
            publication=pub  # Optional: include publication info if needed
        )

    except Exception as e:
        print(f"Error generating question paper: {str(e)}")
        import traceback
        traceback.print_exc()  # This will show the full traceback
        # flash(f'Error generating question paper: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    data = load_data()
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
                # flash('All fields are required!', 'error')
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
            
            success_message = ""
            
            if qtype == "Match the Following":
                match_key = request.form.get("match_key", "").strip()
                match_value = request.form.get("match_value", "").strip()
                if match_key and match_value:
                    data[publication][subject][class_name][chapter][qtype].append({match_key: match_value})
                    success_message = f"Match pair added successfully: {match_key} → {match_value}"
                else:
                    # flash('Both key and value are required for Match the Following!', 'error')
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
                    success_message = f"Fill in the Blank question added: {question_text}"
                else:
                    # flash('Both question and answer are required for Fill in the Blanks!', 'error')
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
                    success_message = f"True/False question added: {question_text}"
                else:
                    # flash('Both question and answer are required for True/False!', 'error')
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
                    success_message = f"MCQ question added: {question}"
                else:
                    # flash('All fields (question, 4 options, and answer) are required for Choose the Best Answer!', 'error')
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
                    success_message = f"Full Form added: {full_form_abbr} = {full_form_text}"
                else:
                    # flash('Both abbreviation and full form are required!', 'error')
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            else:
                # Handle other question types (Answer the Following, etc.)
                question_text = request.form.get("normal_question", "").strip()
                if question_text:
                    lines = [line.strip() for line in question_text.split('\n') if line.strip()]
                    data[publication][subject][class_name][chapter][qtype].extend(lines)
                    success_message = f"{qtype} question(s) added successfully!"
                else:
                    # flash('Question text is required!', 'error')
                    return render_template('add_question.html', 
                                        publications=publications,
                                        selected_pub=selected_pub,
                                        selected_sub=selected_sub,
                                        selected_cls=selected_cls,
                                        selected_chapter=selected_chapter,
                                        selected_qtype=selected_qtype,
                                        data=data)

            # Save data and show success
            save_data(data)
            # flash(success_message, 'success')
            
            # Redirect with parameters to preserve selections
            return redirect(url_for('add_question', 
                                  publication=publication,
                                  subject=subject, 
                                  class_name=class_name,
                                  chapter=chapter,
                                  qtype=qtype))
            
        except Exception as e:
            # flash(f'Error adding question: {str(e)}', 'error')
            return render_template('add_question.html', 
                                publications=publications,
                                selected_pub=selected_pub,
                                selected_sub=selected_sub,
                                selected_cls=selected_cls,
                                selected_chapter=selected_chapter,
                                selected_qtype=selected_qtype,
                                data=data)
    
    else:
        # GET request - get parameters for persistence
        selected_pub = request.args.get('publication', '')
        selected_sub = request.args.get('subject', '')
        selected_cls = request.args.get('class_name', '')
        selected_chapter = request.args.get('chapter', '')
        selected_qtype = request.args.get('qtype', '')

    # Pass publications and selected values to template
    return render_template('add_question.html', 
                         publications=publications,
                         selected_pub=selected_pub,
                         selected_sub=selected_sub,
                         selected_cls=selected_cls,
                         selected_chapter=selected_chapter,
                         selected_qtype=selected_qtype,
                         data=data)
                           
                           
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

@app.route('/rename_question', methods=['GET', 'POST'])
def rename_question():
    if request.method == 'POST':
        publication = request.form['publication']
        subject = request.form['subject']
        class_name = request.form['class_name']
        chapter = request.form['chapter']
        qtype = request.form['qtype']
        old_index = int(request.form['old_question'])

        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        qlist = data[publication][subject][class_name][chapter][qtype]

        if qtype in ["Fill in the Blanks", "True/False", "Answer the Following", "Manual Questions"]:
            qlist[old_index]['question'] = request.form['question_fill_blank']
            qlist[old_index]['answer'] = request.form['answer_fill_blank']
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

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Just redirect without flash message
        return redirect(url_for('rename_question'))

    data = load_data()
    return render_template('rename_question.html', data=data)


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
