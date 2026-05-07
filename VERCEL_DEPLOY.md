# Vercel 部署指南

## 部署步骤

### 1. 上传代码到 GitHub

1. 在 GitHub 创建新仓库，例如 `poetry-learning`
2. 将以下文件上传到仓库：
   - `api/chat.py`
   - `vercel.json`
   - `requirements.txt`
   - `recite.html`
   - 其他需要的 HTML 文件

### 2. 注册 Vercel

1. 访问 https://vercel.com
2. 使用 GitHub 账号登录
3. 点击 "New Project"

### 3. 导入项目

1. 选择你刚创建的 GitHub 仓库
2. 点击 "Import"

### 4. 配置环境变量

1. 在 Vercel 项目设置中找到 "Environment Variables"
2. 添加新变量：
   - **Name**: `DEEPSEEK_API_KEY`
   - **Value**: 你的 DeepSeek API Key（格式：`sk-xxxxxxxx`）

### 5. 部署

1. 点击 "Deploy"
2. 等待 1-2 分钟部署完成
3. 获得一个公开网址，例如：`https://poetry-learning.vercel.app`

## 文件结构

```
poetry-learning/
├── api/
│   └── chat.py          # Vercel Serverless 函数
├── vercel.json          # Vercel 配置
├── requirements.txt     # Python 依赖
├── recite.html          # 背诵挑战页面
└── 其他 HTML 文件
```

## 部署后访问

- 背诵挑战：`https://你的项目名.vercel.app/recite.html`

## 注意事项

1. **DeepSeek API Key** 必须设置为 Vercel 环境变量，否则 API 无法调用
2. Vercel 免费版有调用限制（约 100 次/天），如果需要更多可以升级
3. 第一次部署可能需要几分钟时间

## 本地测试

如果想在本地测试，需要：

1. 安装 Vercel CLI：
   ```bash
   npm i -g vercel
   ```

2. 本地运行：
   ```bash
   cd poetry-learning
   vercel dev
   ```

3. 设置环境变量：
   ```bash
   DEEPSEEK_API_KEY=sk-xxxxxx vercel dev
   ```
