from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from utils.twitter import post_to_twitter

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        content = request.form.get("content")
        image = request.files.get("image")
        
        try:
            image_path = None
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

            post_to_twitter(content, image_path)
            
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            
            session["message"] = "Post published successfully on Twitter!"
        except Exception as e:
            session["message"] = f"Error: {str(e)}"
        
        return redirect(url_for("index"))

    if "message" in session:
        message = session.pop("message")
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)