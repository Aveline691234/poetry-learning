"""
AI古诗小老师 - DeepSeek API代理服务

支持三种运行模式：
1. 本地模式：无需API Key，使用内置的本地AI响应
2. 代理模式：通过后端转发请求到DeepSeek（需要配置DEEPSEEK_API_KEY）
3. 直连模式：前端直接调用DeepSeek API（用户自行配置API Key）

环境变量配置：
- DEEPSEEK_API_KEY: DeepSeek API密钥（可选）
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

# 本地AI响应库
LOCAL_RESPONSES = {
    "default": [
        "你想了解哪一句诗呢？",
        "请告诉我你想学习什么？",
        "我可以教你背诵这首诗哦！"
    ],
    "hello": [
        "你好呀！我是泊船瓜洲小助手，今天来学《泊船瓜洲》吧！",
        "嗨！欢迎来到古诗学习！"
    ],
    "meaning": [
        "这首诗写王安石路过瓜洲，望见家乡钟山就在不远处，春风吹绿了江南岸，他望着月亮想念家乡。",
        "诗人泊船瓜洲，望着对岸的家乡钟山，春风又吹绿了江南两岸，明月啊，你什么时候能照着我回家呢？"
    ],
    "author": [
        "王安石（1021-1086），字介甫，号半山，北宋临川人。唐宋八大家之一，还当过宰相，主导了著名的\"王安石变法\"！",
        "王安石是北宋著名的政治家、文学家和改革家，是唐宋八大家之一。"
    ],
    "green": [
        "当然是\"绿\"字！王安石为了这个字改了十几次，原来用过\"到\"\"过\"\"满\"，最后选了\"绿\"字——春风把江南都吹绿了，多生动啊！",
        "\"绿\"字是诗眼，把春风拟人化，让读者看到春天染绿江南的动态画面。"
    ],
    "first_line": [
        "「京口瓜洲一水间」——京口在长江南岸（今镇江），瓜洲在北岸，只隔一条长江。\"一水间\"写出距离之近，暗示诗人与家乡近在咫尺。",
        "第一句描写诗人站在江边，看到京口和瓜洲隔江相望的景象。"
    ],
    "second_line": [
        "「钟山只隔数重山」——钟山是王安石家乡（南京紫金山），\"只隔\"强调不远，\"数重山\"又暗示阻隔，近而不可及，更添惆怅。",
        "第二句表达诗人对家乡的思念，钟山就在不远处。"
    ],
    "third_line": [
        "「春风又绿江南岸」——千古名句！\"绿\"字是诗眼，改了十几次才定。\"绿\"字把春风拟人化，让读者看到春天染绿江南的动态画面。",
        "第三句是千古名句，描写春天来了，江南都变绿了。"
    ],
    "fourth_line": [
        "「明月何时照我还」——诗人望着明月思念家乡，\"何时\"二字饱含期盼与无奈。明月本无情，诗人却希望它照着自己回家。",
        "最后一句表达诗人的思乡之情，问明月什么时候能照着他回家。"
    ],
    "recite": [
        "好的！让我们开始背诵挑战！准备好了吗？",
        "太棒了！我们来背诵这首诗吧！"
    ]
}

def log(msg):
    print(f"[DeepSeek Proxy] {msg}", file=sys.stderr)

def get_local_response(user_message):
    """根据用户消息返回本地响应"""
    msg = user_message.lower()
    
    if any(word in msg for word in ['你好', '嗨', '哈喽', '您好']):
        return LOCAL_RESPONSES["hello"][0]
    if any(word in msg for word in ['什么意思', '解释', '翻译', '诗意']):
        return LOCAL_RESPONSES["meaning"][0]
    if any(word in msg for word in ['作者', '王安石', '谁写']):
        return LOCAL_RESPONSES["author"][0]
    if any(word in msg for word in ['哪个字', '最好', '名句', '赏析', '诗眼', '绿']):
        return LOCAL_RESPONSES["green"][0]
    if any(word in msg for word in ['第一句', '京口']):
        return LOCAL_RESPONSES["first_line"][0]
    if any(word in msg for word in ['第二句', '钟山']):
        return LOCAL_RESPONSES["second_line"][0]
    if any(word in msg for word in ['第三句', '春风']):
        return LOCAL_RESPONSES["third_line"][0]
    if any(word in msg for word in ['第四句', '明月']):
        return LOCAL_RESPONSES["fourth_line"][0]
    if any(word in msg for word in ['开始背诵', '背诗', '背诵']):
        return LOCAL_RESPONSES["recite"][0]
    
    return LOCAL_RESPONSES["default"][0]


@app.route('/api/chat', methods=['POST'])
def chat():
    log(f"Received chat request")
    
    data = request.get_json()
    messages = data.get('messages', [])

    if not messages:
        log("ERROR: No messages provided")
        return jsonify({'error': 'No messages provided'}), 400

    # 获取用户最后一条消息
    user_message = ""
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_message = msg.get('content', '')
            break

    # 如果没有配置API Key，返回本地响应
    if not API_KEY:
        log("INFO: No API key configured, returning local response")
        local_response = get_local_response(user_message)
        return jsonify({
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': local_response
                }
            }]
        })

    # 有API Key，调用DeepSeek API
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
            # API失败时返回本地响应作为降级
            local_response = get_local_response(user_message)
            log(f"Falling back to local response")
            return jsonify({
                'choices': [{
                    'message': {
                        'role': 'assistant',
                        'content': f"⚠️ AI服务暂时不可用，使用本地模式：\n{local_response}"
                    }
                }]
            })

        return jsonify(result)
    except requests.exceptions.Timeout:
        log("ERROR: Request timed out")
        local_response = get_local_response(user_message)
        return jsonify({
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': f"⚠️ 请求超时，使用本地模式：\n{local_response}"
                }
            }]
        })
    except requests.exceptions.ConnectionError as e:
        log(f"ERROR: Connection error - {e}")
        local_response = get_local_response(user_message)
        return jsonify({
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': f"⚠️ 连接失败，使用本地模式：\n{local_response}"
                }
            }]
        })
    except Exception as e:
        log(f"ERROR: Unexpected error - {e}")
        local_response = get_local_response(user_message)
        return jsonify({
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': f"⚠️ 服务暂时不可用，使用本地模式：\n{local_response}"
                }
            }]
        })

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
