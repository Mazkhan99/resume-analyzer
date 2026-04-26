import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from parser import extract_text_from_pdf, preprocess_for_tfidf
from matcher import analyze_gap
from scorer import calculate_multi_dimensional_scores
from recommender import generate_suggestions, analyze_resume_quality

# ------------------ LOGGING ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ PATH FIX (IMPORTANT) ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "../frontend"),
    static_url_path=""
)

CORS(app)

# ------------------ CONFIG ------------------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------ ROUTES ------------------

# 👉 Frontend serve karega (VERY IMPORTANT)
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


# 👉 Resume analyze API
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    try:
        logger.info("Received analyze request")

        # -------- JOB DESCRIPTION --------
        if "job_description" not in request.form:
            return jsonify({"error": "Missing job_description"}), 400

        job_description = request.form["job_description"]

        if not job_description.strip():
            return jsonify({"error": "Job description empty"}), 400

        resume_text = ""

        # -------- RESUME INPUT --------
        if "resume_text" in request.form and request.form["resume_text"].strip():
            resume_text = request.form["resume_text"]

        elif "resume_file" in request.files:
            file = request.files["resume_file"]

            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)

                # Extract text
                if filename.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(filepath)
                else:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        resume_text = f.read()

                os.remove(filepath)

            else:
                return jsonify({"error": "Invalid file type"}), 400

        else:
            return jsonify({"error": "Provide resume_text or file"}), 400

        if not resume_text.strip():
            return jsonify({"error": "Empty resume"}), 400

        # -------- PROCESS --------
        processed_resume = preprocess_for_tfidf(resume_text)
        processed_jd = preprocess_for_tfidf(job_description)

        gap_analysis = analyze_gap(resume_text, job_description)

        scores = calculate_multi_dimensional_scores(
            processed_resume,
            processed_jd,
            gap_analysis["skills_found"],
            gap_analysis["jd_skills"],
        )

        suggestions = generate_suggestions(
            gap_analysis["missing_skills"],
            gap_analysis["critical_missing_skills"],
        )

        feedback = analyze_resume_quality(resume_text)

        # -------- RESPONSE --------
        return jsonify({
            "match_score": scores["final_score"],
            "skill_score": scores["skill_score"],
            "similarity_score": scores["similarity_score"],
            "skills_found": gap_analysis["skills_found"],
            "missing_skills": gap_analysis["missing_skills"],
            "critical_missing_skills": gap_analysis["critical_missing_skills"],
            "suggestions": suggestions,
            "resume_feedback": feedback
        })

    except Exception as e:
        logger.error(f"ERROR: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)