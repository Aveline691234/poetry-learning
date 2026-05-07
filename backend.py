"""
AI古诗小老师 - DeepSeek API代理服务
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import sys
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
API_URL = 'https://api.deepseek.com/chat/completions'

CHUGU_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chugu')

def log(msg):
    print(f"[DeepSeek Proxy] {msg}", file=sys.stderr)

@app.route('/api/chat', methods=['POST'])
def chat():
    log(f"Received chat request")
    if not API_KEY:
        log("ERROR: No API key configured")
        return jsonify({'error': '请设置DEEPSEEK_API_KEY'}), 500

    data = request.get_json()
    messages = data.get('messages', [])

    if not messages:
        log("ERROR: No messages provided")
        return jsonify({'error': 'No messages provided'}), 400

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    payload = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 500
    }

    log(f"Sending request to DeepSeek API...")
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        log(f"DeepSeek API response: {response.status_code}")

        result = response.json()
        log(f"Response data: {result}")

        if response.status_code != 200:
            log(f"ERROR: DeepSeek API returned status {response.status_code}")
            return jsonify({'error': f'API Error: {response.status_code}', 'details': result}), response.status_code

        return jsonify(result)
    except requests.exceptions.Timeout:
        log("ERROR: Request timed out")
        return jsonify({'error': '请求超时，请稍后重试'}), 504
    except requests.exceptions.ConnectionError as e:
        log(f"ERROR: Connection error - {e}")
        return jsonify({'error': f'连接失败: {str(e)}'}), 503
    except Exception as e:
        log(f"ERROR: Unexpected error - {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_progress', methods=['POST'])
def save_progress():
    try:
        data = request.get_json()
        student_key = data.get('studentKey', 'default')
        progress_data = data.get('progress', {})

        os.makedirs(CHUGU_DIR, exist_ok=True)

        filename = f"{student_key}.json"
        filepath = os.path.join(CHUGU_DIR, filename)

        existing_data = {}
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        existing_data.update(progress_data)
        existing_data['lastUpdated'] = datetime.now().isoformat()

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        log(f"Progress saved for {student_key}")
        return jsonify({'status': 'ok', 'file': filename})
    except Exception as e:
        log(f"ERROR saving progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_progress/<student_key>', methods=['GET'])
def load_progress(student_key):
    try:
        filename = f"{student_key}.json"
        filepath = os.path.join(CHUGU_DIR, filename)

        if not os.path.exists(filepath):
            return jsonify({'error': 'No progress found'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return jsonify(data)
    except Exception as e:
        log(f"ERROR loading progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/list_records', methods=['GET'])
def list_records():
    try:
        os.makedirs(CHUGU_DIR, exist_ok=True)
        files = [f for f in os.listdir(CHUGU_DIR) if f.endswith('.json')]
        return jsonify({'records': files})
    except Exception as e:
        log(f"ERROR listing records: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/all_progress', methods=['GET'])
def all_progress():
    try:
        os.makedirs(CHUGU_DIR, exist_ok=True)
        students = []
        for filename in os.listdir(CHUGU_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CHUGU_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    student_id = filename.replace('.json', '')
                    name = data.get('name', '')
                    students.append({
                        'studentId': student_id,
                        'name': name,
                        'progress': data
                    })
        students.sort(key=lambda x: x['studentId'])
        return jsonify({'students': students})
    except Exception as e:
        log(f"ERROR getting all progress: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'api_key_configured': bool(API_KEY),
        'api_key_preview': API_KEY[:8] + '...' if API_KEY else None
    })

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'name': 'AI古诗小老师 - DeepSeek API代理',
        'endpoints': {
            'chat': 'POST /api/chat',
            'health': 'GET /health',
            'save_progress': 'POST /api/save_progress',
            'load_progress': 'GET /api/load_progress/<student_key>'
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("AI古诗小老师 - DeepSeek API代理服务")
    print("=" * 50)
    print(f"后端地址: http://localhost:8000")
    print(f"API Key: {'已配置 ' + API_KEY[:8] + '...' if API_KEY else '未配置'}")
    print(f"学习记录目录: {CHUGU_DIR}")
    print("按Ctrl+C停止服务")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8000, debug=False)
