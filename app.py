from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Response
import csv
import io

app = Flask(__name__)

# Get database URL from environment variable (set by Render)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Note model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/notes', methods=['GET', 'POST'])
def handle_notes():
    if request.method == 'POST':
        data = request.get_json()
        note = Note(text=data.get('text', ''))
        db.session.add(note)
        db.session.commit()
        return jsonify({"status": "added"}), 201

    all_notes = Note.query.all()
    return jsonify([{"text": n.text} for n in all_notes])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=port)

@app.route('/debug/show-notes')
def show_notes():
    all_notes = Note.query.all()
    return '<br>'.join(f"- {note.text}" for note in all_notes)

@app.route('/export/json')
def export_json():
    all_notes = Note.query.all()
    notes_list = [{"text": n.text} for n in all_notes]
    return jsonify(notes_list)

@app.route('/export/csv')
def export_csv():
    all_notes = Note.query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['text'])

    for note in all_notes:
        writer.writerow([note.text])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=notes.csv"}
    )

