import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from parser import extract_text_from_pdf, preprocess_for_tfidf
from matcher import analyze_gap
from scorer import calculate_multi_dimensional_scores
from recommender import generate_suggestions, analyze_resume_quality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------- FIXED PATHS -----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ----------- ROUTES -----------

@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

# fallback (important for Render)
@app.route("/<path:path>")
def serve_static(path):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ----------- ANALYZE API -----------

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    try:
        job_description = request.form.get("job_description", "")
        resume_text = request.form.get("resume_text", "")

        if not job_description:
            return jsonify({"error": "Job description required"}), 400

        # FILE UPLOAD SUPPORT
        if "resume_file" in request.files:
            file = request.files["resume_file"]
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            if file.filename.endswith(".pdf"):
                resume_text = extract_text_from_pdf(filepath)
            else:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    resume_text = f.read()

            os.remove(filepath)

        if not resume_text:
            return jsonify({"error": "Resume text missing"}), 400

        processed_resume = preprocess_for_tfidf(resume_text)
        processed_jd = preprocess_for_tfidf(job_description)

        gap = analyze_gap(resume_text, job_description)

        scores = calculate_multi_dimensional_scores(
            processed_resume,
            processed_jd,
            gap["skills_found"],
            gap["jd_skills"]
        )

        suggestions = generate_suggestions(
            gap["missing_skills"],
            gap["critical_missing_skills"]
        )

        feedback = analyze_resume_quality(resume_text)

        return jsonify({
            "match_score": scores["final_score"],
            "skills_found": gap["skills_found"],
            "missing_skills": gap["missing_skills"],
            "suggestions": suggestions,
            "resume_feedback": feedback
        })

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


# ----------- RUN -----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)