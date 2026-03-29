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

### Prerequisites

- [Docker](https://www.docker.com/)

### Run

```bash
docker compose up -d --build
```

Open <http://localhost:8500> in your browser to use the app.

### Stop

To stop the app, stop the container via Docker.

### Get AI API Key

**Google** — Log in at [Google AI Studio](https://aistudio.google.com/), go to the [Get API Key page](https://aistudio.google.com/api-keys), and click **Create API Key**.

**ModelScope** — Log in at [ModelScope](https://modelscope.cn/), then go to [Account Settings → Access Control](https://modelscope.cn/my/access/token), and click **Create Your Token**.

## TODO

- [ ] Support multiple LLM APIs
- [ ] Support Fill-in-the-blank answering

---

# 雨课堂助手 Web 版

基于 Web 的雨课堂自动化工具。实时监控进行中的课程，自动处理签到、答题、弹幕和点名通知。
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

### 环境要求

- [Docker](https://www.docker.com/)

### 启动

```bash
docker compose up -d --build
```

在浏览器中打开 <http://localhost:8500> 即可使用。

### 停止

通过 Docker 停止容器。

### 获取 AI API Key

**Google** — 登录 [Google AI Studio](https://aistudio.google.com/)，进入[Get API Key page](https://aistudio.google.com/api-keys)，点击 **Create API Key** 即可生成。

**ModelScope** — 登录 [ModelScope](https://modelscope.cn/)，前往[账号设置 → 访问控制](https://modelscope.cn/my/access/token)，点击 **新建访问令牌** 获取 API Key。

## 待办

- [ ] 支持多种 LLM API
- [ ] 支持填空题答题
