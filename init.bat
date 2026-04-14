@echo off

rem 雨课堂助手初始化脚本
echo 开始初始化雨课堂助手...
echo.

rem 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python。请先安装Python 3.10+并添加到PATH。
    echo 下载地址：https://www.python.org/
    pause
    exit /b 1
)

echo ✓ Python已安装

rem 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Node.js。请先安装Node.js并添加到PATH。
    echo 下载地址：https://nodejs.org/
    pause
    exit /b 1
)

echo ✓ Node.js已安装

rem 初始化前端依赖
echo.
echo 正在安装前端依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo 错误：前端依赖安装失败。
    pause
    exit /b 1
)
echo ✓ 前端依赖安装成功

rem 初始化后端依赖
echo.
echo 正在安装后端依赖...
cd ..
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误：后端依赖安装失败。
    pause
    exit /b 1
)
echo ✓ 后端依赖安装成功

rem 完成提示
echo.
echo ======================================
echo 初始化完成！
echo 你现在可以运行 run.bat 启动雨课堂助手。
echo 启动后在浏览器中打开 http://localhost:8500 即可使用。
echo ======================================
echo.
pause