from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)
NOTES_FILE = 'notes.json'

# Load notes from file if it exists
if os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, 'r') as f:
        notes = json.load(f)
else:
    notes = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/notes', methods=['GET', 'POST'])
def handle_notes():
    global notes
    if request.method == 'POST':
        data = request.get_json()
        notes.append(data)

        # Save to file
        with open(NOTES_FILE, 'w') as f:
            json.dump(notes, f)

        return jsonify({"status": "added"}), 201

    return jsonify(notes)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
