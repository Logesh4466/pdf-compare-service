from flask import Flask, request, jsonify
import io
import base64
from PyPDF2 import PdfReader
import difflib

app = Flask(__name__)

def extract_text_from_pdf(file_bytes):
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

@app.route("/compare_pdfs", methods=["POST"])
def compare_pdfs():
    try:
        data = request.get_json()
        if not data or "file1" not in data or "file2" not in data:
            return jsonify({"error": "Missing file1 or file2"}), 400

        file1_bytes = base64.b64decode(data["file1"])
        file2_bytes = base64.b64decode(data["file2"])

        text1 = extract_text_from_pdf(file1_bytes).splitlines()
        text2 = extract_text_from_pdf(file2_bytes).splitlines()

        diff = difflib.unified_diff(text1, text2, fromfile='version1', tofile='version2', lineterm='')

        added, removed = [], []
        for line in diff:
            if line.startswith('+ ') and not line.startswith('+++'):
                added.append(line[2:])
            elif line.startswith('- ') and not line.startswith('---'):
                removed.append(line[2:])

        return jsonify({
            "added": added,
            "removed": removed,
            "summary": f"{len(added)} lines added, {len(removed)} lines removed"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
