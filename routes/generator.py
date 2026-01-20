import random
import traceback
from flask import Blueprint, render_template, request, redirect, url_for
from database import db

generator_bp = Blueprint('generator', __name__)

@generator_bp.route('/generate', methods=['POST'])
def generate_question_paper():
    try:
        data = db.load()

        pub = request.form.get('publication', '').strip()
        sub = request.form.get('subject', '').strip()
        cls = request.form.get('class', '').strip()
        chapters = request.form.getlist('chapters')
        
        if not all([pub, sub, cls, chapters]):
            return redirect(request.referrer or url_for('main.index'))

        all_categories = set()
        valid_chapters = []
        
        for chapter in chapters:
            chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
            if chapter_data:
                valid_chapters.append(chapter)
                for qtype in chapter_data.keys():
                    all_categories.add(qtype)
            else:
                print(f"Warning: Chapter '{chapter}' not found in data for {pub}/{sub}/{cls}")

        if not valid_chapters:
            return redirect(request.referrer or url_for('main.index'))

        all_categories.add("Manual Questions")

        question_counts = {}
        marks = {}
        formatted_questions = {}

        # Process each question type
        for qtype in all_categories:
            key = qtype.lower().replace(" ", "_")
            count_field = f"{key}_count"
            mark_field = f"{key}_mark"
            
            count_value = request.form.get(count_field, "0")
            mark_value = request.form.get(mark_field, "")
            
            try:
                question_counts[qtype] = int(count_value)
            except ValueError:
                question_counts[qtype] = 0
            
            if mark_value and mark_value.strip():
                try:
                    marks[qtype] = float(mark_value)
                except ValueError:
                    marks[qtype] = 1.0
            else:
                marks[qtype] = 1.0
                
            formatted_questions[qtype] = []

        # MANUAL OVERRIDE for problematic types
        problematic_types = ["Choose the Best Answer", "Answer the Following"]
        for ptype in problematic_types:
            if ptype in all_categories:
                alt_keys = [
                    ptype.lower().replace(" ", "_"),
                    ptype.lower().replace("the ", "").replace(" ", "_"),
                    ptype.lower().replace(" ", "_").replace("the_", ""),
                    "choose_best_answer",
                    "answer_following"
                ]
                for alt_key in alt_keys:
                    alt_mark_field = f"{alt_key}_mark"
                    alt_value = request.form.get(alt_mark_field)
                    if alt_value:
                        try:
                            marks[ptype] = float(alt_value)
                            break
                        except ValueError:
                            continue

        # Manual questions handling
        manual_text = request.form.get('manual_questions', '').strip()
        manual_mark_value = request.form.get('manual_mark', "5.0")
        try:
            manual_mark = float(manual_mark_value)
        except ValueError:
            manual_mark = 5.0
            
        manual_format = request.form.get('manual_output_format', 'numbered')
        question_type = request.form.get('question_type', 'Write essays on the following').strip()

        if manual_text:
            if manual_format == 'numbered':
                manual_lines = [line.strip().replace('\r', '') for line in manual_text.split('\n') if line.strip()]
                formatted_questions["Manual Questions"] = manual_lines
                question_counts["Manual Questions"] = len(manual_lines)
                marks["Manual Questions"] = manual_mark
            else:
                formatted_questions["Manual Questions"] = [manual_text]
                question_counts["Manual Questions"] = 1
                marks["Manual Questions"] = manual_mark
        else:
            all_categories.discard("Manual Questions")
            question_counts.pop("Manual Questions", None)
            marks.pop("Manual Questions", None)
            formatted_questions.pop("Manual Questions", None)

        chapter_questions = {}
        for qtype in all_categories:
            if qtype in ["Match the Following", "Manual Questions", "Full Form"]:
                continue
                
            chapter_questions[qtype] = []
            
            for chapter in valid_chapters:
                chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
                questions = chapter_data.get(qtype, [])
                
                for question in questions:
                    if qtype == "Choose the Best Answer":
                        if isinstance(question, dict) and 'question' in question:
                            chapter_questions[qtype].append({
                                'question': question['question'],
                                'options': question.get('options', ['Option A', 'Option B', 'Option C', 'Option D'])
                            })
                        elif isinstance(question, str):
                            chapter_questions[qtype].append({
                                'question': question,
                                'options': ['Option A', 'Option B', 'Option C', 'Option D']
                            })
                    else:
                        if isinstance(question, dict) and 'question' in question:
                            chapter_questions[qtype].append(question['question'])
                        elif isinstance(question, str):
                            chapter_questions[qtype].append(question)

        # Full Form handling
        if "Full Form" in all_categories:
            full_form_items = []
            for chapter in valid_chapters:
                chapter_data = data.get(pub, {}).get(sub, {}).get(cls, {}).get(chapter, {})
                full_form_data = chapter_data.get("Full Form", [])
                for item in full_form_data:
                    if isinstance(item, dict):
                        for abbr, full_form in item.items():
                            full_form_items.append(abbr)
                    elif isinstance(item, str):
                        full_form_items.append(item)

            full_form_count = question_counts.get("Full Form", 0)
            if full_form_items and full_form_count > 0:
                formatted_questions["Full Form"] = random.sample(full_form_items, min(full_form_count, len(full_form_items)))
            else:
                formatted_questions["Full Form"] = []

        for qtype in all_categories:
            if qtype in ["Match the Following", "Manual Questions", "Full Form"]:
                continue
                
            all_available = chapter_questions.get(qtype, [])
            count_needed = question_counts.get(qtype, 0)
            
            if all_available and count_needed > 0:
                selected = random.sample(all_available, min(count_needed, len(all_available)))
                formatted_questions[qtype] = selected
            else:
                formatted_questions[qtype] = []

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
                options = list(dict.fromkeys([ans for ans in selected_answers if ans.strip()]))
                random.shuffle(options)
                formatted_questions["Fill in the Blanks"] = fill_questions
            else:
                formatted_questions["Fill in the Blanks"] = []
                options = []
        else:
            options = []

        total_marks = 0.0
        counts = {}
        for qtype in formatted_questions:
            count = len(formatted_questions[qtype])
            counts[qtype] = count
            total_marks += count * marks.get(qtype, 0)

        return render_template(
            'question_paper.html',
            subject=sub,
            class_name=cls,
            questions=formatted_questions,
            marks=marks,
            question_counts=question_counts,
            total_marks=total_marks,
            counts=counts,
            fill_options=options,
            publication=pub,
            question_type=question_type,
            output_format=manual_format,
            manual_marks=manual_mark
        )

    except Exception as e:
        print(f"Error generating question paper: {str(e)}")
        traceback.print_exc()
        return redirect(request.referrer or url_for('main.index'))