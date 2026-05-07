"""
AI古诗小老师 - 进度存储 API（Supabase 版）
路由:
  POST   /api/progress          -> save_progress
  GET    /api/progress?key=xxx  -> load_progress
  GET    /api/progress?all=1    -> all_progress
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import json
import sys
from datetime import datetime

# Supabase 配置（需在 Vercel 环境变量中设置）
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
TABLE = 'poetry_progress'

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
}


def log(msg):
    print(f"[Progress API] {msg}", file=sys.stderr)


def supabase_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }


def _check_supabase():
    return bool(SUPABASE_URL and SUPABASE_KEY)


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if not _check_supabase():
            self._respond(503, {'error': '未配置 Supabase 环境变量'})
            return

        try:
            import requests as req
            qs = parse_qs(urlparse(self.path).query)

            if qs.get('all', [''])[0] == '1':
                # 获取全部学生
                url = f"{SUPABASE_URL}/rest/v1/{TABLE}?select=*&order=student_key.asc"
                r = req.get(url, headers=supabase_headers(), timeout=10)
                rows = r.json()
                students = []
                for row in rows:
                    data = row.get('progress_data', {})
                    students.append({
                        'studentId': row['student_key'],
                        'name': data.get('name', ''),
                        'progress': data,
                    })
                self._respond(200, {'students': students})
                return

            key = qs.get('key', [''])[0]
            if not key:
                self._respond(400, {'error': '缺少 key 参数'})
                return

            url = f"{SUPABASE_URL}/rest/v1/{TABLE}?student_key=eq.{key}&select=*"
            r = req.get(url, headers=supabase_headers(), timeout=10)
            rows = r.json()
            if not rows:
                self._respond(404, {'error': 'No progress found'})
                return
            self._respond(200, rows[0]['progress_data'])

        except Exception as e:
            log(f"GET ERROR: {e}")
            self._respond(500, {'error': str(e)})

    def do_POST(self):
        if not _check_supabase():
            self._respond(503, {'error': '未配置 Supabase 环境变量'})
            return

        try:
            import requests as req
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            student_key = data.get('studentKey', 'default')
            progress_data = data.get('progress', {})
            progress_data['lastUpdated'] = datetime.now().isoformat()

            # Upsert（插入或更新）
            url = f"{SUPABASE_URL}/rest/v1/{TABLE}"
            headers = supabase_headers()
            headers['Prefer'] = 'resolution=merge-duplicates,return=representation'
            payload = {
                'student_key': student_key,
                'progress_data': progress_data,
                'updated_at': datetime.now().isoformat(),
            }
            r = req.post(url, headers=headers, json=payload, timeout=10)
            if r.status_code not in (200, 201):
                log(f"Supabase error: {r.status_code} {r.text}")
                self._respond(500, {'error': f'Supabase error: {r.text}'})
                return

            self._respond(200, {'status': 'ok', 'studentKey': student_key})

        except Exception as e:
            log(f"POST ERROR: {e}")
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
        pass
