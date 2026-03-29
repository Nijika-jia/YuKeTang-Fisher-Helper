# 雨课堂助手 Web 版

- 基于 Web 的雨课堂自动化工具。实时监控进行中的课程，自动处理签到、答题、弹幕和点名通知。
基于 [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) 和 [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

## 功能

- **自动签到** — 课程开始时自动签到
- **自动答题** — 支持单选、多选、投票和简答题，可配置答题策略（随机或 AI）
- **自动弹幕** — 自动发送弹幕消息
- **点名提醒** — 点名时发送通知提醒
- **分课程设置** — 对每门课程进行精细化的自动化控制
- **双语界面** — 支持中英文切换
- **实时面板** — 实时展示所有课程事件动态

## 快速开始

### 方式一：下载可执行文件（推荐）

1. 前往 [Releases 页面](https://github.com/dvdsanyi/Yuketang-Helper-Web/releases)，下载对应平台的可执行文件。
2. 运行可执行文件，浏览器会自动打开 <http://localhost:8500>。

> macOS 用户需先运行 `chmod +x YuketangHelper-macOS`，如遇安全提示请前往 **系统设置 → 隐私与安全性** 点击"仍要打开"。

### 方式二：Docker 部署

1. [下载源代码 ZIP](https://codeload.github.com/dvdsanyi/Yuketang-Helper-Web/zip/refs/heads/main) 并解压，或使用 Git Clone。
1. 下载并安装 [Docker Desktop](https://www.docker.com/)。
1. 打开 Docker Desktop。
1. 在项目根目录下运行以下命令：

   ```zsh
   docker compose up -d --build
   ```

1. 在浏览器中打开 <http://localhost:8500> 即可使用。

## 启动

- **可执行文件**：直接运行可执行文件即可。
- **Docker**：在 Docker Desktop 的 Containers 界面启动 container，然后在浏览器中打开 <http://localhost:8500>。

## 停止

- **可执行文件**：关闭终端窗口，或按 `Ctrl+C`。
- **Docker**：在 Docker Desktop 的 Containers 界面停止 container。

## 获取 AI API密钥

- **Google**: 登录 [Google AI Studio](https://aistudio.google.com/)，进入 [Get API Key page](https://aistudio.google.com/api-keys)，点击 **Create API Key**。

- **ModelScope**: 登录 [ModelScope](https://modelscope.cn/)，**先在[账号设置](https://modelscope.cn/my/settings/account)中绑定阿里云账号**，然后前往[访问控制](https://modelscope.cn/my/access/token)，点击 **新建访问令牌**。

## 待办

- [ ] 支持多种 LLM API
- [ ] 支持填空题答题

---

# Yuketang Helper Web

A web-based automation tool for Yuketang online learning platform. It monitors active lessons in real time and automatically handles sign-ins, quizzes, bullet chats, and roll call notifications.
Based on [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) and [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

## Features

- **Auto Sign-in** — Automatically checks in when a lesson starts
- **Auto Quiz Answering** — Handles single/multiple choice, voting, and short-answer questions with configurable strategies (random or AI)
- **Auto Danmu** — Sends bullet chat messages automatically
- **Roll Call Notifications** — Alerts you when roll call happens
- **Per-Course Settings** — Fine-grained control over automation for each course
- **Bilingual UI** — English and Chinese interface
- **Real-time Dashboard** — Live activity feed of all lesson events

## Quick Start

### Option 1: Download Executable (Recommended)

1. Go to the [Releases page](https://github.com/dvdsanyi/Yuketang-Helper-Web/releases) and download the executable for your platform.
2. Run the executable — your browser will automatically open <http://localhost:8500>.

> macOS users: run `chmod +x YuketangHelper-macOS` first. If you see a security warning, go to **System Settings → Privacy & Security** and click "Open Anyway".

### Option 2: Docker Deployment

1. [Download source code ZIP](https://codeload.github.com/dvdsanyi/Yuketang-Helper-Web/zip/refs/heads/main) and extract, or use Git Clone.
1. Download and install [Docker Desktop](https://www.docker.com/).
1. Open Docker Desktop.
1. Run the following command in the project root directory:

   ```zsh
   docker compose up -d --build
   ```

1. Open <http://localhost:8500> in your browser to use the app.

## Run

- **Executable**: Simply run the executable file.
- **Docker**: Start the container in the Containers tab of Docker Desktop, then open <http://localhost:8500> in your browser.

## Stop

- **Executable**: Close the terminal window, or press `Ctrl+C`.
- **Docker**: Stop the container in the Containers tab of Docker Desktop.

## Get AI API Key

- **Google**: Log in at [Google AI Studio](https://aistudio.google.com/), go to the [Get API Key page](https://aistudio.google.com/api-keys), and click **Create API Key**.

- **ModelScope**: Log in at [ModelScope](https://modelscope.cn/), **first bind your Alibaba Cloud account in [Account Settings](https://modelscope.cn/my/settings/account)**, then go to [Access Control](https://modelscope.cn/my/access/token) and click **Create Your Token**.

## TODO

- [ ] Support multiple LLM APIs
- [ ] Support Fill-in-the-blank answering
