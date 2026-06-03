#!/bin/bash
# 一键上传到 GitHub 脚本

echo "============================================================"
echo "GitHub 上传脚本"
echo "============================================================"

# 检查是否在项目目录
if [ ! -f "README.md" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 1. 初始化 Git（如果未初始化）
if [ ! -d ".git" ]; then
    echo "[1/5] 初始化 Git 仓库..."
    git init
    git branch -M main
else
    echo "[1/5] Git 已初始化"
fi

# 2. 添加所有文件
echo "[2/5] 添加文件到 Git..."
git add .

# 3. 查看状态
echo "[3/5] 文件状态："
git status --short

# 4. 创建提交
echo "[4/5] 创建提交..."
git commit -m "Initial commit: 完整的学分制教务选课管理系统

- 后端: Flask + MySQL，30+ API 接口实现
- 前端: Vue 3 + Element Plus 完整界面
- 数据库: 建表脚本、存储过程、触发器、测试数据
- 文档: API 文档、数据库设计、开发指南、测试指南
- 测试: 自动化测试脚本和一键部署脚本

功能特性:
- JWT 认证和三角色权限控制
- 完整的选课、退课、成绩管理流程
- 实时统计和消息通知
- 业务逻辑封装在存储过程中
- 触发器自动同步选课人数

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
" || echo "提交失败（可能没有修改）"

# 5. 提示用户添加远程仓库
echo ""
echo "============================================================"
echo "[5/5] 准备推送到 GitHub"
echo "============================================================"
echo ""
echo "请按以下步骤操作："
echo ""
echo "1. 访问 https://github.com/new 创建新仓库"
echo "   仓库名: shu_jwxt"
echo "   描述: 学分制教务选课管理系统 - Flask + Vue 3 + MySQL"
echo "   不要勾选 'Initialize with README'"
echo ""
echo "2. 创建后，运行以下命令（替换 YOUR_USERNAME）："
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/shu_jwxt.git"
echo "   git push -u origin main"
echo ""
echo "或者使用 GitHub CLI（推荐）："
echo ""
echo "   gh repo create shu_jwxt --public --source=. --remote=origin --push"
echo ""
echo "============================================================"
