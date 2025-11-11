from flask import Flask, render_template, request, send_file, jsonify
import os
import threading
import time
from werkzeug.utils import secure_filename

# Import your existing scripts
from large_audio_transcribe import get_large_audio_transcription_on_silence
from ollama_summarize import summarize_transcript

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# Global variable to track processing status
processing_status = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3', 'm4a', 'mp4', 'avi'}

def process_audio_file(audio_path, task_id):
    """Complete processing pipeline using your existing functions"""
    try:
        processing_status[task_id] = {'status': 'transcribing', 'progress': 20}
        
        # Step 1: Transcription using your large_audio_transcribe function
        transcript_text = get_large_audio_transcription_on_silence(audio_path)
        
        # Save transcript
        transcript_path = f"outputs/transcript_{task_id}.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)
        
        processing_status[task_id] = {'status': 'summarizing', 'progress': 60, 'transcript_path': transcript_path}
        
        # Step 2: Summarization using your ollama_summarize function
        summary_path = f"outputs/summary_{task_id}.txt"
        summary_text = summarize_transcript(transcript_path, summary_path)
        
        processing_status[task_id] = {
            'status': 'complete', 
            'progress': 100, 
            'transcript_path': transcript_path,
            'summary_path': summary_path
        }
        
    except Exception as e:
        processing_status[task_id] = {'status': 'error', 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        task_id = f"{timestamp}_{filename}"
        
        # Save uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        file.save(file_path)
        
        # Initialize processing status
        processing_status[task_id] = {'status': 'uploaded', 'progress': 10}
        
        # Start processing in background
        thread = threading.Thread(target=process_audio_file, args=(file_path, task_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({'task_id': task_id, 'message': 'File uploaded and processing started'})
    
    return jsonify({'error': 'Invalid file type. Please upload WAV, MP3, M4A, MP4, or AVI files'}), 400

@app.route('/status/<task_id>')
def get_status(task_id):
    return jsonify(processing_status.get(task_id, {'status': 'not_found'}))

@app.route('/download/<task_id>/<file_type>')
def download_file(task_id, file_type):
    status = processing_status.get(task_id, {})
    
    if file_type == 'transcript' and 'transcript_path' in status:
        return send_file(status['transcript_path'], as_attachment=True, download_name=f'transcript_{task_id}.txt')
    elif file_type == 'summary' and 'summary_path' in status:
        return send_file(status['summary_path'], as_attachment=True, download_name=f'meeting_summary_{task_id}.txt')
    
    return jsonify({'error': 'File not found or not ready'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)