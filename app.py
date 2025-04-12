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

@app.route('/export/excel')
def export_excel():
    notes = Note.query.all()
    data = [{"ID": n.id, "Note": n.text} for n in notes]

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=port)
