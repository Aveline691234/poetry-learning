# AI古诗小老师 - 产品开发文档

## 版本信息

| 项目 | 内容 |
|------|------|
| 文档版本 | V2.0 |
| 创建日期 | 2026-05-02 |
| 作者 | AI Assistant |

---

## 一、项目结构

### 1.1 文件目录

```
poetry-learning/
├── 前端文件
│   ├── index_optimized.html  # 诗词学习主页（核心）
│   ├── recite.html           # 背诵挑战
│   ├── game.html             # 趣味游戏
│   ├── camera.html           # 摄像头互动
│   ├── chat.html             # AI聊天
│   ├── progress.html         # 学习进度
│   ├── teacher.html          # 教师界面
│   ├── login.html            # 登录页
│   └── index.html            # 旧版入口
│
├── 后端文件
│   ├── backend.py            # Flask后端服务
│   └── api/
│       └── chat.py          # Vercel Serverless函数
│
├── 配置文件
│   ├── vercel.json           # Vercel配置
│   └── requirements.txt      # Python依赖
│
├── 数据文件
│   ├── corpus/
│   │   └── poem_data.json   # 诗词语料库
│   └── chugu/
│       └── *.json           # 学习进度存储
│
└── 文档
    ├── AI古诗小老师 PRD_V2.0.md
    ├── AI古诗小老师 TEST_V2.0.md
    ├── AI古诗小老师 DEV_V2.0.md
    └── VERCEL_DEPLOY.md
```

### 1.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | 原生HTML/CSS/JS | 无框架依赖 |
| UI框架 | Tailwind CSS (CDN) | 样式框架 |
| 语音合成 | Web Speech API | 浏览器原生TTS |
| 语音识别 | Web Speech API | 浏览器原生STT |
| 后端框架 | Flask (Python) | 本地开发 |
| AI服务 | DeepSeek API | AI对话 |
| 部署平台 | Vercel | 前端+Serverless |

---

## 二、快速开始

### 2.1 本地开发环境

**前置要求**：
- Python 3.7+
- Node.js 14+ (可选，用于Live Server)
- Chrome/Edge浏览器

**步骤**：

```bash
# 1. 克隆项目
cd poetry-learning

# 2. 安装Python依赖
pip install flask flask-cors requests

# 3. 启动后端服务
python backend.py

# 4. 打开浏览器
# 方式A: 直接打开HTML文件
# file:///path/to/poetry-learning/index_optimized.html

# 方式B: 使用Live Server (VS Code)
# 右键 index_optimized.html → Open with Live Server
```

**后端服务地址**：`http://localhost:8000`

### 2.2 Vercel部署

**步骤**：

1. **上传代码到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/poetry-learning.git
   git push -u origin main
   ```

2. **导入Vercel**
   - 访问 https://vercel.com
   - 点击 "New Project"
   - 导入GitHub仓库

3. **配置环境变量**
   - 在Vercel项目设置中添加：
     - Name: `DEEPSEEK_API_KEY`
     - Value: `sk-你的密钥`

4. **部署**
   - 点击 "Deploy"
   - 等待1-2分钟
   - 获得公开网址

---

## 三、核心模块开发

### 3.1 语音系统

#### 3.1.1 语音合成 (TTS)

**使用示例**：

```javascript
function speakText(text, onFinish = null) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 0.85;

    // 语音选择
    const voices = window.speechSynthesis.getVoices();
    const xiaoxiaoVoice = voices.find(v =>
        v.lang === 'zh-CN' && v.name.includes('Xiaoxiao')
    );
    if (xiaoxiaoVoice) utterance.voice = xiaoxiaoVoice;

    utterance.onend = () => {
        if (onFinish) onFinish();
    };

    window.speechSynthesis.speak(utterance);
}
```

**关键点**：
- 优先选择 Xiaoxiao/Yaoyao/Luna 等中文女声
- 语速设置为 0.85（比默认慢，更自然）
- 必须在 `window.speechSynthesis.onvoiceschanged` 加载完成后才能获取语音列表

#### 3.1.2 语音识别 (STT)

**使用示例**：

```javascript
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SR();

recognition.lang = 'zh-CN';
recognition.continuous = false;
recognition.interimResults = true;

recognition.onresult = (event) => {
    for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
            const text = event.results[i][0].transcript;
            // 处理识别结果
        }
    }
};

recognition.start();
```

**关键点**：
- 需要用户授权麦克风权限
- `continuous: false` 表示单次识别
- `interimResults: true` 可以显示实时中间结果

#### 3.1.3 语音状态管理

```javascript
let isListening = false;
let isAISpeaking = false;

// 开始聆听前检查
function startListening() {
    if (isAISpeaking) return; // AI说话时不录音
    // ...
}

// 说话前停止聆听
function speakText(text, onFinish) {
    stopListening(); // 先停止聆听
    // ... 播放语音
}
```

### 3.2 背诵挑战模块 (recite.html)

#### 3.2.1 状态管理

```javascript
const state = {
    currentReciteIndex: 0,    // 当前背诵到第几句
    proficiency: 70,           // 熟练程度 30/70/100
    isListening: false,      // 是否在聆听
    isAISpeaking: false,      // AI是否在说话
    isReciting: false,        // 是否在背诵模式
    deepseekAvailable: false, // DeepSeek是否可用
    stats: { correct: 0, wrong: 0, hint: 0 }, // 正确/错误/提示次数
    hintLevel: 0,             // 当前提示级别
    consecutiveWrong: 0,     // 连续错误次数
    conversationContext: [],  // 对话历史
    voiceConfig: { index: undefined, name: 'auto' } // 语音配置
};
```

#### 3.2.2 背诵流程

```
选择熟练度 → 显示背诵页 → AI引导语 → 自动聆听 →
用户说话 → 判断对错 → 正确/错误 → 继续/提示 → 下一句
```

#### 3.2.3 判断逻辑

```javascript
function checkRecitation(text) {
    const cleanText = text.replace(/[，。！？、]/g, '');
    const target = CORPUS.lines[state.currentReciteIndex].text.replace(/[，。！？、]/g, '');

    if (cleanText === target) return 'correct';
    if (cleanText.includes(target) || target.includes(cleanText)) return 'correct';

    // 字符匹配率
    let matchCount = 0;
    for (const char of target.split('')) {
        if (cleanText.includes(char)) matchCount++;
    }

    const rate = matchCount / target.length;
    if (rate >= 0.6) return 'correct';
    if (rate < 0.3 && cleanText.length > 3) return 'wrong';
    return 'unclear';
}
```

### 3.3 DeepSeek API集成

#### 3.3.1 调用格式

```javascript
async function callDeepSeek(prompt) {
    const apiUrl = `${window.location.origin}/api/chat`;

    const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            messages: [
                { role: 'system', content: SYSTEM_PROMPT },
                ...history,
                { role: 'user', content: prompt }
            ]
        })
    });

    const data = await response.json();
    return data.choices[0].message.content;
}
```

#### 3.3.2 SYSTEM_PROMPT 示例

```javascript
const SYSTEM_PROMPT = `你是《泊船瓜洲》背诵小助手，专门帮助小朋友背诵古诗。

【绝对禁止】
- 永远不要直接说出完整诗句！
- 永远不要说超过两个字的开头提示！
- 不要把诗句用引号框起来！

【回答要求】
- 说话简短，像聊天一样
- 每句话不超过30个字
- 自然流畅，不要生硬`;
```

### 3.4 后端 API

#### 3.4.1 本地 Flask 后端 (backend.py)

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])

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

    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    return jsonify(response.json())
```

#### 3.4.2 Vercel Serverless 函数 (api/chat.py)

```python
import vercel
import requests
import os

API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

@vercel.serverless_function()
def handler(request):
    if request.method == 'OPTIONS':
        return vercel.Response(
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    data = request.json()
    messages = data.get('messages', [])

    response = requests.post(
        'https://api.deepseek.com/chat/completions',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_KEY}'
        },
        json={
            'model': 'deepseek-chat',
            'messages': messages
        },
        timeout=30
    )

    return vercel.Response(
        status=200,
        headers={'Access-Control-Allow-Origin': '*'},
        body=json.dumps(response.json())
    )
```

---

## 四、关键代码片段

### 4.1 语音选择器初始化

```javascript
function loadVoices() {
    const voiceSelect = document.getElementById('voiceSelect');
    const voices = window.speechSynthesis.getVoices();

    voiceSelect.innerHTML = '<option value="auto">自动选择最佳语音</option>';

    // 中文语音优先
    const zhVoices = voices.filter(v => v.lang.includes('zh'));
    zhVoices.forEach((voice) => {
        const option = document.createElement('option');
        option.value = voices.indexOf(voice);
        option.textContent = `${voice.name} (${voice.lang})`;
        voiceSelect.appendChild(option);
    });

    // 监听选择变化
    voiceSelect.addEventListener('change', (e) => {
        const index = e.target.value;
        state.voiceConfig.index = index === 'auto' ? undefined : parseInt(index);
    });
}

// 必须在 voiceschanged 事件后调用
window.speechSynthesis.onvoiceschanged = loadVoices;
loadVoices(); // 可能已经加载
```

### 4.2 自动背诵流程

```javascript
async function askForRecitation() {
    const lineNum = state.currentReciteIndex + 1;

    if (state.deepseekAvailable) {
        const response = await callDeepSeek(`请引导用户背诵第${lineNum}句`);
        if (response) {
            speakText(response, () => startListening());
            return;
        }
    }

    // 本地模式回退
    const greetings = getNaturalGreeting(lineNum);
    speakText(greetings, () => startListening());
}

function handleCorrectAnswer() {
    state.currentReciteIndex++;
    state.consecutiveWrong = 0;
    state.hintLevel = 0;

    if (state.currentReciteIndex >= CORPUS.lines.length) {
        showResult(); // 完成
    } else {
        askForRecitation(); // 下一句
    }
}

function handleWrongAnswer() {
    state.consecutiveWrong++;
    state.stats.wrong++;

    if (state.consecutiveWrong === 1) {
        speakText('没关系，再想想！', () => startListening());
    } else if (state.consecutiveWrong === 2) {
        // 给出第一个提示
        const hint = CORPUS.lines[state.currentReciteIndex].hints[0];
        speakText(`提示一下，${hint}`, () => startListening());
    }
    // ...
}
```

### 4.3 语音与聆听互斥

```javascript
function speakText(text, onFinish) {
    // 说话前先停止聆听
    if (recognition) {
        recognition.stop();
    }
    isAISpeaking = true;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => {
        isAISpeaking = false;
        if (onFinish) onFinish();
    };

    window.speechSynthesis.speak(utterance);
}

function startListening() {
    // AI说话时不录音
    if (isAISpeaking) return;

    recognition.start();
    isListening = true;
}

recognition.onstart = () => {
    // 监听开始时，如果AI在说话就停止
    if (isAISpeaking) {
        recognition.stop();
        window.speechSynthesis.cancel();
    }
};
```

---

## 五、配置文件说明

### 5.1 vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python",
      "config": {"runtime": "python3.9"}
    },
    {
      "src": "**/*.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/chat",
      "dest": "/api/chat.py"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "DEEPSEEK_API_KEY": "@deepseek_api_key"
  }
}
```

### 5.2 requirements.txt

```
vercel==0.0.1
requests==2.31.0
```

### 5.3 环境变量

| 变量名 | 说明 | 必填 | 示例 |
|--------|------|------|------|
| DEEPSEEK_API_KEY | DeepSeek API密钥 | 是 | sk-xxxxxxxxxx |

---

## 六、常见问题

### Q1: 语音列表为空？

**原因**：语音列表异步加载，需要等待 `onvoiceschanged` 事件。

**解决**：
```javascript
window.speechSynthesis.onvoiceschanged = () => {
    const voices = window.speechSynthesis.getVoices();
    // 现在可以获取语音列表了
};
```

### Q2: 语音识别没有反应？

**可能原因**：
1. 浏览器不支持 Web Speech API（需Chrome/Edge）
2. 麦克风权限被拒绝
3. 网络问题（某些浏览器需要网络验证）

**解决**：
```javascript
recognition.onerror = (event) => {
    if (event.error === 'not-allowed') {
        alert('请允许使用麦克风权限');
    }
};
```

### Q3: DeepSeek API 调用失败？

**可能原因**：
1. API Key 未设置或错误
2. 网络问题
3. API 额度用尽

**解决**：
- 检查环境变量 `DEEPSEEK_API_KEY`
- 查看 Vercel 后台日志
- 本地测试：`curl` 调用后端接口

### Q4: CORS 错误？

**原因**：前端直接调用第三方API被浏览器阻止。

**解决**：通过后端代理转发API请求（已在 backend.py 和 api/chat.py 中实现）。

---

## 七、代码规范

### 7.1 HTML 规范

- 使用语义化标签
- 使用 Tailwind CSS 类名
- ID 命名：`小驼峰`（如 `userInput`）
- 注释：功能块之间添加注释

### 7.2 CSS 规范

- 使用 CSS 变量定义主题色
- 使用 Tailwind CSS 优先
- 动画使用 `@keyframes`

### 7.3 JavaScript 规范

- 使用 `const`/`let`，避免 `var`
- 使用箭头函数
- 状态变量集中管理
- 异步函数使用 `async/await`
- 控制台日志区分级别：`console.log` / `console.error`

### 7.4 Python 规范

- 使用 `snake_case` 命名
- 添加类型注解（可选）
- 异常处理添加日志

---

## 八、更新日志

### V2.0 (2026-05-02)

**新增功能**：
- recite.html 完整背诵挑战模块
- 三种熟练度选择（30%/70%/100%）
- 自动背诵流程
- DeepSeek AI 集成
- 语音选择器
- 延时播放功能

**优化**：
- 语音系统统一使用 Xiaoxiao 优先
- 语音与聆听状态互斥
- 错误处理优化

**文档**：
- 新增 PRD/TEST/DEV 三份文档

### V1.0 (早期版本)

- index_optimized.html 诗词学习
- game.html 趣味游戏
- camera.html 摄像头互动
- chat.html AI聊天

---

**文档结束**
