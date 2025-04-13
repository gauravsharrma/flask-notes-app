from flask import Flask, request, jsonify, render_template
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
 @@ -61,6 +66,24 @@ def delete_note(note_id):
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
