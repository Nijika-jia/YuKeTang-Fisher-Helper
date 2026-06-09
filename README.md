<div align="center">

# Yuketang Helper Web

**雨课堂助手 Web 版**

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

> 基于 [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) 和 [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)
<div align="center">

# Yuketang Helper Web

**雨课堂助手 Web 版**

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

> 基于 [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) 和 [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

中文 | [English](README_EN.md)

## 功能

- **自动签到** — 自动完成签到（模拟通过 APP 扫二维码进入课堂）
- **自动答题** — 支持单选、多选、投票和简答题，可配置答题策略（随机、空白、AI 或答案队列）
- **答案队列** — 支持预设答案，按PPT页数提示用户填写对应答案，自动提交预设答案(配合 [yuketang-helper-auto](https://github.com/ZaytsevZY/yuketang-helper-auto) 使用, 此项目可以看到后面未出现的PPT页, 为答案队列的答案填入提供支持)
- **自动弹幕** — 当一段时间内出现超过 3 条相同弹幕时自动跟发（默认阈值可调）
- **自动抢红包** — 收到红包时自动抢
- **点名提醒** — 点名时发送通知提醒
- **语音通知** — 支持语音播报课程事件,支持自定义语音通知音频
- **分课程设置** — 对每门课程进行精细化的自动化控制
- **多服务器支持** — 支持多个雨课堂服务器
- **双语界面** — 支持中英文切换
- **实时面板** — 实时展示所有课程事件动态

## 快速开始

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

##  技术栈

| 层级 | 技术 |
|------|------|
| **前端** | React 18 + TypeScript + Vite + react-i18next |
| **后端** | FastAPI + Uvicorn + WebSocket |
| **AI** | Google Gemini / OpenAI / ModelScope |
| **部署** | Docker + Docker Compose / PyInstaller |

##  获取 AI API 密钥（免费）

| 提供商 | 获取方式 |
|--------|---------|
| **ModelScope** | 登录 [ModelScope](https://modelscope.cn/)，先在[账号设置](https://modelscope.cn/my/settings/account)绑定阿里云账号，然后前往[访问控制](https://modelscope.cn/my/access/token)新建令牌 |
| **Google** | 登录 [Google AI Studio](https://aistudio.google.com/)，进入 [Get API Key](https://aistudio.google.com/api-keys) 创建密钥 |

##  使用说明

- **启动**：`python start.py` 或双击 `run.bat`
- **停止**：`python stop.py` 或关闭终端窗口
- **访问**：http://localhost:8500

##  待办

- [ ] 支持更多 LLM API
- [ ] 支持填空题答题
- [ ] 自动预习

##  免责声明

本项目仅供学习交流使用，使用者需自行承担使用风险。请遵守相关法律法规和学校规定，作者不对因使用本项目造成的任何后果负责。

##  开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star ⭐**

</div>
