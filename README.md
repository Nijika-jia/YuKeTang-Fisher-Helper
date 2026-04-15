# 雨课堂助手 Web 版

- 基于 [RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant) 和 [THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper)

## 语言
- 中文 | [English](README_EN.md)

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

### 自动初始化（推荐）
1. 下载源代码 ZIP并解压，或使用 Git Clone
```zsh
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
```
2. 双击运行项目根目录下的：
   init.bat
3. 等待初始化完成后，双击运行：
   run.bat
4. 在浏览器中打开 <http://localhost:8500> 即可使用

### 手动初始化
1. 下载源代码 ZIP并解压，或使用 Git Clone
```zsh
git clone https://github.com/Nijika-jia/YuKeTang-Fisher-Helper.git
```
2. 安装 [Python 3](https://www.python.org/) 和 [Node.js](https://nodejs.org/)
3. 初始化前端依赖：
   ```zsh
   cd frontend
   npm install
   ```
4. 初始化后端依赖：
   ```zsh
   cd backend
   pip install -r requirements.txt
   ```
5. 在项目根目录下双击运行：
   run.bat

6. 在浏览器中打开 <http://localhost:8500> 即可使用

## 启动

- **Python**：在项目根目录下运行 `python start.py`，或双击运行 `run.bat`，然后在浏览器中打开 <http://localhost:8500>

## 停止

- **Python**：运行 `python stop.py` 或关闭终端窗口

## 获取 AI API密钥（免费）

- **ModelScope**: 登录 [ModelScope](https://modelscope.cn/)，**先在[账号设置](https://modelscope.cn/my/settings/account)中绑定阿里云账号**，然后前往[访问控制](https://modelscope.cn/my/access/token)，点击 **新建访问令牌**

- **Google**: 登录 [Google AI Studio](https://aistudio.google.com/)，进入 [Get API Key page](https://aistudio.google.com/api-keys)，点击 **Create API Key**

## 待办

- [ ] 支持多种 LLM API
- [ ] 支持填空题答题
- [ ] 自动预习
