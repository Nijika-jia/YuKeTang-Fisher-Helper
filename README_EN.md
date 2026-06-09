<div align="center">

# Yuketang Helper Web

**Yuketang (Rain Classroom) Helper — Web Edition**

[![GitHub Release](https://img.shields.io/github/v/release/Nijika-jia/YuKeTang-Fisher-Helper?style=flat-square&logo=github&label=Release)](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/releases)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/github/license/Nijika-jia/YuKeTang-Fisher-Helper?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/releases)

</div>

---

> Based on [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) and [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

[中文](README.md) | English

##  Features

| Feature | Description |
|---------|-------------|
| **Auto Sign-in** | Simulates app QR code scanning to automatically check in |
| **Auto Quiz Answering** | Handles single/multiple choice, voting, and short-answer questions with configurable strategies (random / blank / AI / answer queue) |
| **Answer Fallback Strategy** | Answer queue → AI → Random, three-level fallback to ensure no question is missed |
| **Answer Queue** | Preset answers matched by PPT page number, with batch import and editing support |
| **AI Answering** | Supports Google Gemini, OpenAI, ModelScope and more LLM providers |
| **Auto Danmu** | Automatically sends bullet chat when 3+ identical messages appear (threshold adjustable) |
| **Auto Red Packet** | Automatically grabs red packets when received |
| **Roll Call Alert** | Sends notification when roll call is detected |
| **Voice Notification** | Text-to-speech announcements for lesson events, with custom audio support |
| **Per-Course Settings** | Fine-grained automation control for each course |
| **Multi-Server Support** | Supports multiple Yuketang servers |
| **Bilingual UI** | English and Chinese interface |
| **Real-time Dashboard** | Live activity feed of all lesson events |

##  Quick Start

### Option 1: Auto Initialization (Recommended)

```bash
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
cd YuKeTang-Fisher-Helper
```

1. Double-click `init.bat` and wait for initialization
2. Double-click `run.bat`
3. Open http://localhost:8500 in your browser

### Option 2: Manual Initialization

```bash
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
cd YuKeTang-Fisher-Helper

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend && pip install -r requirements.txt && cd ..

# Start
python start.py
```

Open http://localhost:8500 in your browser.

### Option 3: Docker

```bash
docker compose up -d
```

### Option 4: Download Executable

Go to [Releases](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/releases) to download the executable for your platform.

##  Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18 + TypeScript + Vite + react-i18next |
| **Backend** | FastAPI + Uvicorn + WebSocket |
| **AI** | Google Gemini / OpenAI / ModelScope |
| **Deployment** | Docker + Docker Compose / PyInstaller |

##  Get AI API Key (Free)   

| Provider | How to Get |
|----------|------------|
| **ModelScope** | Log in at [ModelScope](https://modelscope.cn/), bind your Alibaba Cloud account in [Account Settings](https://modelscope.cn/my/settings/account), then go to [Access Control](https://modelscope.cn/my/access/token) to create a token |
| **Google** | Log in at [Google AI Studio](https://aistudio.google.com/), go to [Get API Key](https://aistudio.google.com/api-keys) and create a key |

##  Usage

- **Start**: `python start.py` or double-click `run.bat`
- **Stop**: `python stop.py` or close the terminal
- **Access**: http://localhost:8500

##  TODO

- [ ] Support more LLM APIs
- [ ] Support fill-in-the-blank answering
- [ ] Auto preview

##  Disclaimer

This project is for educational purposes only. Users assume all risks. Please comply with applicable laws and school regulations. The author is not responsible for any consequences arising from the use of this project.

##  License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**If this project helps you, please consider giving it a Star ⭐**

</div>
