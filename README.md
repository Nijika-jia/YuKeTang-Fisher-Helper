# 雨课堂助手 Web 版

- 基于 [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) 和 [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

## 功能

- **自动签到** — 自动完成签到（模拟通过 APP 扫二维码进入课堂）
- **自动答题** — 支持单选、多选、投票和简答题，可配置答题策略（随机、空白或 AI）
- **自动弹幕** — 当一段时间内出现超过 3 条相同弹幕时自动跟发（默认阈值可调）
- **点名提醒** — 点名时发送通知提醒
- **语音通知** — 支持语音播报课程事件
- **分课程设置** — 对每门课程进行精细化的自动化控制
- **多服务器支持** — 支持多个雨课堂服务器
- **双语界面** — 支持中英文切换
- **实时面板** — 实时展示所有课程事件动态

## 快速开始

### 方式一：下载可执行文件（本地机器推荐）

1. 前往 [Releases 页面](https://github.com/dvdsanyi/Yuketang-Helper-Web/releases)，下载对应平台的可执行文件
2. 运行可执行文件，浏览器会自动打开 <http://localhost:8500>

> macOS/linux 用户需先运行 `chmod +x YuketangHelper-<OS>-<VERSION>`（自行补全文件名）; macOS 用户如遇安全提示请前往 **系统设置 → 隐私与安全性** 点击"仍要打开"

### 方式二：源代码 Python 启动（开发者推荐）

1. [下载源代码 ZIP](https://codeload.github.com/dvdsanyi/Yuketang-Helper-Web/zip/refs/heads/main) 并解压，或使用 Git Clone
1. 安装 [Python 3](https://www.python.org/) 和 [Node.js](https://nodejs.org/)
1. 在项目根目录下运行：

   ```zsh
   python start.py
   ```

1. 在浏览器中打开 <http://localhost:8500> 即可使用

### 方式三：Docker 部署（服务器推荐）

1. 下载并安装 Docker
1. 打开 Docker
1. 运行：

   ```zsh
   docker pull dvdyyz/yuketang-helper:latest && 
   docker run -d --name yuketang-helper --restart unless-stopped -p 8500:8500 dvdyyz/yuketang-helper:latest
   ```

1. 在浏览器中打开 <http://localhost:8500> 即可使用

## 启动

- **可执行文件**：直接运行可执行文件即可
- **Python**：在项目根目录下运行 `python start.py`，然后在浏览器中打开 <http://localhost:8500>
- **Docker**：打开 Docker，运行 `docker run -d --name yuketang-helper --restart unless-stopped -p 8500:8500 dvdyyz/yuketang-helper:latest`，然后在浏览器中打开 <http://localhost:8500>

## 停止

- **可执行文件**：关闭终端窗口
- **Python**：运行 `python stop.py`
- **Docker**：运行 `docker stop yuketang-helper`

## 获取 AI API密钥（免费）

- **ModelScope**: 登录 [ModelScope](https://modelscope.cn/)，**先在[账号设置](https://modelscope.cn/my/settings/account)中绑定阿里云账号**，然后前往[访问控制](https://modelscope.cn/my/access/token)，点击 **新建访问令牌**

- **Google**: 登录 [Google AI Studio](https://aistudio.google.com/)，进入 [Get API Key page](https://aistudio.google.com/api-keys)，点击 **Create API Key**

## 待办

- [ ] 支持多种 LLM API
- [ ] 支持填空题答题
- [ ] 自动预习
- [ ] 自动抢红包

---

# Yuketang Helper Web

- Based on [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) and [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

## Features

- **Auto Sign-in** — Automatically checks in (simulates scanning the QR code via the app to enter the classroom)
- **Auto Quiz Answering** — Handles single/multiple choice, voting, and short-answer questions with configurable strategies (random, blank, or AI)
- **Auto Danmu** — Automatically sends a bullet chat when more than 3 identical messages appear within a short period (default threshold is adjustable)
- **Roll Call Notifications** — Alerts you when roll call happens
- **Voice Notifications** — Text-to-speech announcements for lesson events
- **Per-Course Settings** — Fine-grained control over automation for each course
- **Multi-Server Support** — Supports multiple Yuketang servers
- **Bilingual UI** — English and Chinese interface
- **Real-time Dashboard** — Live activity feed of all lesson events

## Quick Start

### Option 1: Download Executable (Recommended for Local)

1. Go to the [Releases page](https://github.com/dvdsanyi/Yuketang-Helper-Web/releases) and download the executable for your platform
2. Run the executable — your browser will automatically open <http://localhost:8500>

> macOS/Linux users: run `chmod +x YuketangHelper-<OS>-<VERSION>` first (replace with actual filename); macOS users: if you see a security warning, go to **System Settings → Privacy & Security** and click "Open Anyway"

### Option 2: Python from Source (Recommended for Developers)

1. [Download source code ZIP](https://codeload.github.com/dvdsanyi/Yuketang-Helper-Web/zip/refs/heads/main) and extract, or use Git Clone
1. Install [Python 3](https://www.python.org/) and [Node.js](https://nodejs.org/)
1. Run the following command in the project root directory:

   ```zsh
   python start.py
   ```

1. Open <http://localhost:8500> in your browser to use the app

### Option 3: Docker Deployment (Recommended for Servers)

1. Download and install Docker
1. Open Docker
1. Run:

   ```zsh
   docker pull dvdyyz/yuketang-helper:latest && 
   docker run -d --name yuketang-helper --restart unless-stopped -p 8500:8500 dvdyyz/yuketang-helper:latest
   ```

1. Open <http://localhost:8500> in your browser to use the app

## Run

- **Executable**: Simply run the executable file
- **Python**: Run `python start.py` in the project root directory, then open <http://localhost:8500> in your browser
- **Docker**: Open Docker, run `docker run -d --name yuketang-helper --restart unless-stopped -p 8500:8500 dvdyyz/yuketang-helper:latest`, then open <http://localhost:8500> in your browser

## Stop

- **Executable**: Close the terminal window
- **Python**: Run `python stop.py`
- **Docker**: Run `docker stop yuketang-helper`

## Get AI API Key (Free)

- **ModelScope**: Log in at [ModelScope](https://modelscope.cn/), **first bind your Alibaba Cloud account in [Account Settings](https://modelscope.cn/my/settings/account)**, then go to [Access Control](https://modelscope.cn/my/access/token) and click **Create Your Token**

- **Google**: Log in at [Google AI Studio](https://aistudio.google.com/), go to the [Get API Key page](https://aistudio.google.com/api-keys), and click **Create API Key**

## TODO

- [ ] Support multiple LLM APIs
- [ ] Support Fill-in-the-blank answering
- [ ] Auto preview
- [ ] Auto red packet grabbing
