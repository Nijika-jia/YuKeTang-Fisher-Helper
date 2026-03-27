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

Open <http://localhost:8000> in your browser to use the app.

### Get Gemini API Key

To use AI-powered quiz answering, you need a Gemini API key. Visit [Google AI Studio](https://aistudio.google.com/), go to the [Get API Key page](https://aistudio.google.com/api-keys), and click **Create API Key** to generate one.

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

在浏览器中打开 <http://localhost:8000> 即可使用。

### 获取 Gemini API Key

如需使用 AI 自动答题功能，需要 Gemini API Key。前往 [Google AI Studio](https://aistudio.google.com/)，前往 [Get API Key 页面](https://aistudio.google.com/api-keys)，点击 **Create API Key** 即可生成。

## 待办

- [ ] 支持多种 LLM API
- [ ] 支持填空题答题
