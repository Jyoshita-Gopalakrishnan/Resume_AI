from flask import Flask, request, jsonify
import fitz  # PyMuPDF for PDF parsing
import os

app = Flask(__name__)

# Load technical skills from a file
def load_skills(file_path="skills.txt"):
    try:
        with open(file_path, "r") as f:
            return [skill.strip().lower() for skill in f.readlines()]
    except FileNotFoundError:
        print("Error: skills.txt not found.")
        return []

# Extract text from uploaded PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in pdf_document:
            text += page.get_text("text")  # Ensure extraction in text mode
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# Compare resume text with technical skills (whole-word matching)
def find_matching_skills(resume_text, skill_list):
    resume_text = resume_text.lower()
    matched_skills = [skill for skill in skill_list if skill in resume_text]
    return list(set(matched_skills))  # Remove duplicates

# Load skills once when app starts
skill_list = load_skills()

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    
    # Ensure it's a PDF
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
    
    # Extract resume text
    resume_text = extract_text_from_pdf(file)

    # Validate extraction
    if not resume_text.strip():
        return jsonify({"error": "Failed to extract text from PDF"}), 500

    # Find matching skills
    matched_skills = find_matching_skills(resume_text, skill_list)

    return jsonify({
        "message": "Resume processed successfully",
        "matched_skills": matched_skills
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
