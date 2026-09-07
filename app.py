import os
import uuid
import shutil
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, request, send_file, jsonify, render_template
from PyPDF2 import PdfMerger

app = Flask(__name__)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

CLEANUP_INTERVAL = int(os.environ.get("CLEANUP_INTERVAL", 3600))
SESSION_MAX_AGE = int(os.environ.get("SESSION_MAX_AGE", 3600))

sessions = {}


def cleanup_old_sessions():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        now = datetime.now()
        for session_id in os.listdir(UPLOAD_DIR):
            session_dir = os.path.join(UPLOAD_DIR, session_id)
            if not os.path.isdir(session_dir):
                continue
            dir_age = now - datetime.fromtimestamp(os.path.getmtime(session_dir))
            if dir_age > timedelta(seconds=SESSION_MAX_AGE):
                shutil.rmtree(session_dir, ignore_errors=True)
                sessions.pop(session_id, None)


cleanup_thread = threading.Thread(target=cleanup_old_sessions, daemon=True)
cleanup_thread.start()


def purge_sessions(max_age_seconds=None):
    max_age = max_age_seconds or SESSION_MAX_AGE
    now = datetime.now()
    purged = []
    for session_id in os.listdir(UPLOAD_DIR):
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        if not os.path.isdir(session_dir):
            continue
        dir_age = now - datetime.fromtimestamp(os.path.getmtime(session_dir))
        if dir_age > timedelta(seconds=max_age):
            shutil.rmtree(session_dir, ignore_errors=True)
            sessions.pop(session_id, None)
            purged.append(session_id)
    return purged


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    uploaded = []
    for f in files:
        if f.filename and f.filename.lower().endswith(".pdf"):
            filepath = os.path.join(session_dir, f.filename)
            f.save(filepath)
            uploaded.append({"name": f.filename, "path": filepath})

    sessions[session_id] = uploaded
    return jsonify({"session_id": session_id, "files": [u["name"] for u in uploaded]})


@app.route("/reorder", methods=["POST"])
def reorder():
    data = request.json
    session_id = data.get("session_id")
    order = data.get("order")

    if session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    files = sessions[session_id]
    file_map = {os.path.basename(f["path"]): f["path"] for f in files}
    reordered = []
    for name in order:
        if name in file_map:
            reordered.append({"name": name, "path": file_map[name]})
    sessions[session_id] = reordered
    return jsonify({"status": "ok"})


@app.route("/merge", methods=["POST"])
def merge():
    data = request.json
    session_id = data.get("session_id")

    if session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    files = sessions[session_id]
    if not files:
        return jsonify({"error": "No files to merge"}), 400

    merger = PdfMerger()
    for f in files:
        merger.append(f["path"])

    output_path = os.path.join(UPLOAD_DIR, session_id, "merged.pdf")
    merger.write(output_path)
    merger.close()

    return jsonify({"download_url": f"/download/{session_id}"})


@app.route("/download/<session_id>")
def download(session_id):
    output_path = os.path.join(UPLOAD_DIR, session_id, "merged.pdf")
    if not os.path.exists(output_path):
        return jsonify({"error": "Merged file not found"}), 404
    return send_file(output_path, as_attachment=True, download_name="merged.pdf")


@app.route("/admin/cleanup", methods=["POST"])
def admin_cleanup():
    data = request.json or {}
    max_age = data.get("max_age_seconds")
    purged = purge_sessions(max_age)
    return jsonify({"purged": purged, "count": len(purged)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
