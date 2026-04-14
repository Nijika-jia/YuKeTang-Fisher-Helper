# Yuketang Helper Web

- Based on [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) and [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

## Language
- [中文](README.md) | English

## Features

- **Auto Sign-in** — Automatically checks in (simulates scanning the QR code via the app to enter the classroom)
- **Auto Quiz Answering** — Handles single/multiple choice, voting, and short-answer questions with configurable strategies (random, blank, AI, or answer queue)
- **Answer Queue** — Supports preset answers, prompts users to fill in corresponding answers by PPT page number, and automatically submits preset answers
- **Auto Danmu** — Automatically sends a bullet chat when more than 3 identical messages appear within a short period (default threshold is adjustable)
- **Auto Red Packet** — Automatically grabs red packets when received
- **Roll Call Notifications** — Alerts you when roll call happens
- **Voice Notifications** — Text-to-speech announcements for lesson events
- **Per-Course Settings** — Fine-grained control over automation for each course
- **Multi-Server Support** — Supports multiple Yuketang servers
- **Bilingual UI** — English and Chinese interface
- **Real-time Dashboard** — Live activity feed of all lesson events

## Quick Start

### Option 1: Python from Source (Recommended)

#### Auto Initialization (Recommended)
1. Download source code ZIP and extract, or use Git Clone
```zsh
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
```
2. Double-click to run in the project root directory:
   init.bat
3. After initialization is complete, double-click to run:
   run.bat
4. Open <http://localhost:8500> in your browser to use the app

#### Manual Initialization
1. Download source code ZIP and extract, or use Git Clone
```zsh
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
```
2. Install [Python 3](https://www.python.org/) and [Node.js](https://nodejs.org/)
3. Initialize frontend dependencies:
   ```zsh
   cd frontend
   npm install
   ```
4. Initialize backend dependencies:
   ```zsh
   cd backend
   pip install -r requirements.txt
   ```
5. Double-click to run in the project root directory:
   run.bat

6. Open <http://localhost:8500> in your browser to use the app

## Run

- **Python**: Run `python start.py` in the project root directory, or double-click `run.bat`, then open <http://localhost:8500> in your browser

## Stop

- **Python**: Run `python stop.py` or close the terminal window

## Get AI API Key (Free)

- **ModelScope**: Log in at [ModelScope](https://modelscope.cn/), **first bind your Alibaba Cloud account in [Account Settings](https://modelscope.cn/my/settings/account)**, then go to [Access Control](https://modelscope.cn/my/access/token) and click **Create Your Token**

- **Google**: Log in at [Google AI Studio](https://aistudio.google.com/), go to the [Get API Key page](https://aistudio.google.com/api-keys), and click **Create API Key**

## TODO

- [ ] Support multiple LLM APIs
- [ ] Support Fill-in-the-blank answering
- [ ] Auto preview