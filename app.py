from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

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
        "notes": [{"id": n.id, "text": n.text} for n in notes],
        "total": total
    })

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    note = Note(text=data['text'])
    db.session.add(note)
    db.session.commit()
    return jsonify({"id": note.id, "text": note.text}), 201

@app.route('/notes/<int:note_id>', methods=['PUT'])
def edit_note(note_id):
    data = request.get_json()
    note = Note.query.get_or_404(note_id)
    note.text = data['text']
    db.session.commit()
    return jsonify({"id": note.id, "text": note.text})

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=port)
