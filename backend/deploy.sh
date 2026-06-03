#!/bin/bash
# Windows 用户请使用 Git Bash 或 WSL 运行此脚本

echo "============================================================"
echo "学分制教务选课管理系统 - 一键部署脚本"
echo "============================================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo -e "\n${YELLOW}[1/6] 检查 Python 环境...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}✗ Python 未安装，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ 找到 Python: $PYTHON_VERSION${NC}"

# 检查 pip
echo -e "\n${YELLOW}[2/6] 检查 pip...${NC}"
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}✗ pip 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip 可用${NC}"

# 安装依赖
echo -e "\n${YELLOW}[3/6] 安装 Python 依赖...${NC}"
$PYTHON_CMD -m pip install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
else
    echo -e "${RED}✗ 依赖安装失败${NC}"
    exit 1
fi

# 配置环境变量
echo -e "\n${YELLOW}[4/6] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ 已创建 .env 文件${NC}"
    echo -e "${YELLOW}  请编辑 .env 文件配置数据库连接信息${NC}"
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

# 检查 MySQL
echo -e "\n${YELLOW}[5/6] 检查 MySQL 连接...${NC}"
if command -v mysql &> /dev/null; then
    # 从 .env 读取配置
    source .env
    mysql -u$DB_USER -p$DB_PASSWORD -e "SELECT 1" &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ MySQL 连接成功${NC}"

        # 初始化数据库
        echo -e "\n${YELLOW}[6/6] 初始化数据库...${NC}"
        $PYTHON_CMD init_db.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 数据库初始化成功${NC}"
        else
            echo -e "${RED}✗ 数据库初始化失败${NC}"
            exit 1
        fi
    else
        echo -e "${RED}✗ MySQL 连接失败，请检查配置${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ mysql 命令不可用，跳过自动初始化${NC}"
    echo -e "${YELLOW}  请手动执行: python init_db.py${NC}"
fi

# 完成
echo -e "\n============================================================"
echo -e "${GREEN}✓ 部署完成！${NC}"
echo -e "============================================================"
echo -e "\n后续操作："
echo -e "1. ${YELLOW}启动后端服务：${NC}python run.py"
echo -e "2. ${YELLOW}测试接口：${NC}python test_api.py"
echo -e "3. ${YELLOW}查看文档：${NC}cat README.md"
echo -e "\n演示账号："
echo -e "  学生: ${GREEN}S2023001 / 123456${NC}"
echo -e "  教师: ${GREEN}T1001 / 123456${NC}"
echo -e "  管理员: ${GREEN}admin / 123456${NC}"
echo ""
