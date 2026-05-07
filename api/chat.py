"""
AI古诗小老师 - /api/chat Vercel Serverless 函数
标准 Python http.server Handler 格式
"""
from http.server import BaseHTTPRequestHandler
import requests
import os
import json
import sys

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
API_URL = 'https://api.deepseek.com/chat/completions'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
}


def log(msg):
    print(f"[DeepSeek Proxy] {msg}", file=sys.stderr)


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        if not API_KEY:
            log("ERROR: No API key configured")
            self._respond(500, {'error': '请配置 DEEPSEEK_API_KEY 环境变量'})
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            messages = data.get('messages', [])

            if not messages:
                self._respond(400, {'error': 'No messages provided'})
                return

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
            }

            payload = {
                'model': 'deepseek-chat',
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 500,
            }

            log("Sending request to DeepSeek API...")
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            log(f"DeepSeek API response: {resp.status_code}")
            result = resp.json()

            if resp.status_code != 200:
                self._respond(resp.status_code, {
                    'error': f'API Error: {resp.status_code}',
                    'details': result,
                })
                return

            self._respond(200, result)

        except requests.exceptions.Timeout:
            log("ERROR: Request timed out")
            self._respond(504, {'error': '请求超时，请稍后重试'})
        except Exception as e:
            log(f"ERROR: {e}")
            self._respond(500, {'error': str(e)})

    def _respond(self, status: int, body: dict):
        payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        # 抑制 BaseHTTPRequestHandler 默认日志，避免 Vercel 日志杂乱
        pass
