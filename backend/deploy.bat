@echo off
REM Windows 批处理部署脚本
chcp 65001 >nul

echo ============================================================
echo 学分制教务选课管理系统 - 一键部署脚本 (Windows)
echo ============================================================

REM 检查 Python
echo.
echo [1/6] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo × Python 未安装，请先安装 Python 3.8+
    pause
    exit /b 1
)
python --version
echo √ Python 可用

REM 检查 pip
echo.
echo [2/6] 检查 pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo × pip 未安装
    pause
    exit /b 1
)
echo √ pip 可用

REM 安装依赖
echo.
echo [3/6] 安装 Python 依赖...
python -m pip install -r requirements.txt -q
if %errorlevel% equ 0 (
    echo √ 依赖安装成功
) else (
    echo × 依赖安装失败
    pause
    exit /b 1
)

REM 配置环境变量
echo.
echo [4/6] 配置环境变量...
if not exist .env (
    copy .env.example .env >nul
    echo √ 已创建 .env 文件
    echo   请编辑 .env 文件配置数据库连接信息
) else (
    echo √ .env 文件已存在
)

REM 初始化数据库
echo.
echo [5/6] 初始化数据库...
python init_db.py
if %errorlevel% equ 0 (
    echo √ 数据库初始化成功
) else (
    echo × 数据库初始化失败
    echo   请检查 MySQL 服务是否启动，配置是否正确
    pause
    exit /b 1
)

REM 完成
echo.
echo ============================================================
echo √ 部署完成！
echo ============================================================
echo.
echo 后续操作：
echo 1. 启动后端服务：python run.py
echo 2. 测试接口：python test_api.py
echo 3. 查看文档：type README.md
echo.
echo 演示账号：
echo   学生: S2023001 / 123456
echo   教师: T1001 / 123456
echo   管理员: admin / 123456
echo.
pause
