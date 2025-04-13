from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Note')
    tags = db.Column(db.String(255), nullable=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notes', methods=['GET'])
def get_notes():
    search = request.args.get('search', '').lower()
    page = int(request.args.get('page', 0))
    per_page = int(request.args.get('per_page', 2))

    query = Note.query
    if search:
        query = query.filter(Note.text.ilike(f"%{search}%"))

    total = query.count()
    notes = query.offset(page * per_page).limit(per_page).all()

    return jsonify({
        "notes": [
            {"id": n.id, "text": n.text, "category": n.category, "tags": n.tags} for n in notes
        ],
        "total": total
    })

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    note = Note(
        text=data['text'],
        category=data.get('category', 'Note'),
        tags=data.get('tags', '')
    )
    db.session.add(note)
    db.session.commit()
    return jsonify({
        "id": note.id,
        "text": note.text,
        "category": note.category,
        "tags": note.tags
    }), 201

@app.route('/notes/<int:note_id>', methods=['PUT'])
def edit_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)
    note.text = data['text']
    note.category = data.get('category', note.category)
    note.tags = data.get('tags', note.tags)
    db.session.commit()
    return jsonify({
        "id": note.id,
        "text": note.text,
        "category": note.category,
        "tags": note.tags
    })

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return '', 204

@app.route('/export/excel')
def export_excel():
    notes = Note.query.all()
    data = [
        {"ID": n.id, "Note": n.text, "Category": n.category, "Tags": n.tags} for n in notes
    ]

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Notes')

    output.seek(0)
    return send_file(
        output,
        download_name='notes.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/tags', methods=['GET'])
def get_tags():
    all_tags = []
    for note in Note.query.with_entities(Note.tags).all():
        if note.tags:
            all_tags.extend(tag.strip() for tag in note.tags.split(',') if tag.strip())
    unique_tags = sorted(set(all_tags))
    return jsonify(unique_tags)

@app.before_request
def run_manual_db_patch():
    if not hasattr(app, 'db_patch_done'):
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE note ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'Note';"))
            conn.execute(db.text("ALTER TABLE note ADD COLUMN IF NOT EXISTS tags VARCHAR(255);"))
        app.db_patch_done = True


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=port)
