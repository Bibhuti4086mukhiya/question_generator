from flask import Blueprint, render_template, jsonify, request
from database import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    data = db.load()
    publications = list(data.keys())
    return render_template('index.html', publications=publications)

@main_bp.route('/get_subjects/<publication>')
def get_subjects(publication):
    data = db.load()
    subjects = list(data.get(publication, {}).keys())
    return {"subjects": subjects}

@main_bp.route('/get_classes/<publication>/<subject>')
def get_classes(publication, subject):
    data = db.load()
    classes = list(data.get(publication, {}).get(subject, {}).keys())
    return {"classes": classes}

@main_bp.route('/get_chapters/<publication>/<subject>/<class_name>')
def get_chapters(publication, subject, class_name):
    data = db.load()
    class_data = data.get(publication, {}).get(subject, {}).get(class_name, {})

    # If class_data is a dict → normal chapters
    if isinstance(class_data, dict):
        chapters = list(class_data.keys())
    else:
        # If it’s a list (wrong structure), just return empty
        chapters = []

    return {"chapters": chapters}

@main_bp.route('/get_question_types', methods=['POST'])
def get_question_types():
    data = db.load()
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

@main_bp.route("/get_categories/<pub>/<sub>/<cls>", methods=["GET"])
def get_categories(pub, sub, cls):
    chapters_param = request.args.get("chapters", "")
    selected_chapters = chapters_param.split(",") if chapters_param else []

    data = db.load()
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