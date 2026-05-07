# AI Poetry Tutor - Bo Chuan Guo Zhou

一个基于AI的儿童古诗学习助手，帮助孩子学习王安石的《泊船瓜洲》。

## 功能特点

- 🎥 **摄像头互动**：检测孩子的脸，增加学习趣味性
- 🎤 **语音交互**：像豆包/小爱同学一样对话
- 📖 **古诗学习**：逐句讲解《泊船瓜洲》
- ⭐ **学习进度**：记录学习进度和连续学习天数
- 🎮 **互动练习**：背诵练习和问答测试

## 文件结构

```
poetry-learning/
├── index.html          # 前端网页应用
├── backend.py          # Python后端服务
├── requirements.md     # 需求文档
└── README.md           # 使用说明
```

## 快速开始

### 方法一：直接打开网页（推荐）

1. 用浏览器打开 `index.html` 文件
2. 点击「开启摄像头」按钮
3. 点击麦克风按钮开始语音交互

### 方法二：启动后端服务（需要API密钥）

1. 安装依赖：
```bash
pip install fastapi uvicorn requests websocket-client
```

2. 在 `backend.py` 中填写您的讯飞API密钥：
```python
CONFIG = {
    "APPID": "您的APPID",
    "APIKEY": "您的APIKey",
    "APISecret": "您的APISecret"
}
```

3. 启动服务：
```bash
python backend.py
```

4. 访问 http://localhost:8000

## API配置

### 科大讯飞API注册

1. 访问 https://www.xfyun.cn 注册账号
2. 创建应用并开通以下服务：
   - 语音识别（ASR）
   - 语音合成（TTS）
   - 星火认知大模型

3. 获取密钥：
   - APPID
   - APIKey
   - APISecret

### 配置位置

- **前端**：`index.html` 中的 `API_CONFIG` 对象
- **后端**：`backend.py` 中的 `CONFIG` 对象

## 功能说明

### 学习模式
- **学习**：逐句学习古诗，听AI老师讲解意思
- **练习**：根据提示背诵诗句
- **测试**：回答关于古诗的问题

### 交互方式
- 点击诗句查看解释
- 点击麦克风说话
- AI老师会自动引导学习

## 技术栈

- **前端**：HTML5 + CSS3 + JavaScript
- **后端**：Python FastAPI
- **语音**：Web Speech API / 讯飞API
- **存储**：LocalStorage

## 浏览器兼容性

- Chrome（推荐）
- Edge
- Safari
- Firefox

## 注意事项

1. 使用摄像头和麦克风需要用户授权
2. 语音识别需要联网
3. 建议使用耳机获得更好的体验

## 开发说明

### 修改古诗内容

在 `index.html` 中修改 `POEM_DATA` 对象：

```javascript
const POEM_DATA = {
    title: "诗名",
    author: "作者",
    content: ["第一句", "第二句", "第三句", "第四句"],
    pinyin: ["拼音1", "拼音2", "拼音3", "拼音4"],
    translations: ["解释1", "解释2", "解释3", "解释4"],
    background: "背景故事"
};
```

### 添加新功能

在 `index.html` 的 `generateAIResponse` 函数中添加新的对话规则。

## 许可证

MIT License