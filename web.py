# with user log support

from flask import Flask, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from database import get_user_content_by_user_id  # Using database.py as is

app = Flask(__name__, template_folder='templates')

# Configure SQLite database for logs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize logs database
db = SQLAlchemy(app)

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # 'Login', 'View Content'
    content_name = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

BASE_DIR = 'generated_content'

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    if not user_id:
        return "Error: Please provide a user_id in the query parameters.", 400

    # Log the login attempt to user_logs.db
    log = UserLog(user_id=user_id, action='Login')
    db.session.add(log)
    db.session.commit()

    # Get user content info from database.py
    content = get_user_content_by_user_id(user_id)
    if not content:
        return "No content found for this user.", 404

    user_dir = os.path.join(BASE_DIR, user_id)
    if not os.path.exists(user_dir):
        return f"Error: Directory for user '{user_id}' does not exist.", 404

    # Check the status of the content
    if content.status == "Processing":
        # If content is still processing, show processing page
        return render_template('processing.html')
    else:
        # Content is completed.
        # Safely parse the paths from the JSON-stored format
        images = []
        videos = []
        if content.image_paths:
            # Using eval for simplicity. Prefer json.loads in real usage.
            images = [os.path.basename(p) for p in eval(content.image_paths)]
        if content.video_paths:
            videos = [os.path.basename(p) for p in eval(content.video_paths)]

        return render_template('gallery.html', user_id=user_id, images=images, videos=videos)

@app.route('/content/<user_id>/<filename>')
def serve_content(user_id, filename):
    user_dir = os.path.join(BASE_DIR, user_id)

    # Log the content view
    log = UserLog(user_id=user_id, action='View Content', content_name=filename)
    db.session.add(log)
    db.session.commit()

    return send_from_directory(user_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
