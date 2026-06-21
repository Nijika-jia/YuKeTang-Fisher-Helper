<div align="center">

# Yuketang Helper Web

**雨课堂助手 Web 版**

[![Release](https://img.shields.io/github/v/release/Nijika-jia/YuKeTang-Fisher-Helper?style=for-the-badge&logo=github&label=RELEASE)](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/releases)
[![License](https://img.shields.io/github/license/Nijika-jia/YuKeTang-Fisher-Helper?style=for-the-badge)](LICENSE)

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Platform](https://img.shields.io/badge/Platform-Win%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/releases)
[![Bilingual](https://img.shields.io/badge/i18n-中%20%7C%20EN-blueviolet?style=for-the-badge)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-ff69b4?style=for-the-badge)](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/pulls)

</div>

> 基于 [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) 和 [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

中文 | [English](README_EN.md)

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| **自动签到** | 模拟 APP 扫码进入课堂，自动完成签到 |
| **自动答题** | 支持单选、多选、投票和简答题，可配置答题策略（随机 / 空白 / AI / 答案队列） |
| **答题降级策略** | 答案队列 → AI 答题 → 随机答题，三级降级确保不漏答 |
| **答案队列** | 预设答案，按 PPT 页数匹配自动提交，支持批量导入与编辑 |
| **AI 答题** | 支持 Google Gemini、OpenAI、ModelScope 等多种 LLM |
| **自动弹幕** | 检测到 3 条以上相同弹幕时自动跟发（阈值可调） |
| **自动抢红包** | 收到红包时自动抢 |
| **点名提醒** | 点名时发送通知提醒 |
| **语音通知** | 支持语音播报课程事件，支持自定义音频 |
| **分课程设置** | 对每门课程进行精细化自动化控制 |
| **多服务器支持** | 支持多个雨课堂服务器 |
| **双语界面** | 支持中英文切换 |
| **实时面板** | 实时展示所有课程事件动态 |

## 🚀 快速开始

### 方式一：自动初始化（推荐）

```bash
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
cd YuKeTang-Fisher-Helper
```

1. 双击运行 `init.bat` 等待初始化完成
2. 双击运行 `run.bat`
3. 浏览器打开 http://localhost:8500

### 方式二：手动初始化

```bash
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
cd YuKeTang-Fisher-Helper

# 安装前端依赖
cd frontend && npm install && cd ..

# 安装后端依赖
cd backend && pip install -r requirements.txt && cd ..

# 启动
python start.py
```

浏览器打开 http://localhost:8500

### 方式三：Docker

```bash
docker compose up -d
```

### 方式四：下载可执行文件

前往 [Releases](https://github.com/Nijika-jia/YuKeTang-Fisher-Helper/releases) 下载对应平台的可执行文件，双击运行即可。

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React 18 + TypeScript + Vite + react-i18next |
| **后端** | FastAPI + Uvicorn + WebSocket |
| **AI** | Google Gemini / OpenAI / ModelScope |
| **部署** | Docker + Docker Compose / PyInstaller |

## 🔑 获取 AI API 密钥（免费）

| 提供商 | 获取方式 |
|--------|---------|
| **ModelScope** | 登录 [ModelScope](https://modelscope.cn/)，先在[账号设置](https://modelscope.cn/my/settings/account)绑定阿里云账号，然后前往[访问控制](https://modelscope.cn/my/access/token)新建令牌 |
| **Google** | 登录 [Google AI Studio](https://aistudio.google.com/)，进入 [Get API Key](https://aistudio.google.com/api-keys) 创建密钥 |

## 📖 使用说明

- **启动**：`python start.py` 或双击 `run.bat`
- **停止**：`python stop.py` 或关闭终端窗口
- **访问**：http://localhost:8500

## 📋 待办

- [ ] 支持更多 LLM API
- [ ] 支持填空题答题
- [ ] 自动预习

## ⚠️ 免责声明

本项目仅供学习交流使用，使用者需自行承担使用风险。请遵守相关法律法规和学校规定，作者不对因使用本项目造成的任何后果负责。

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star ⭐**

</div>
