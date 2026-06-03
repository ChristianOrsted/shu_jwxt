# GitHub 上传指南

本文档详细说明如何将项目上传到 GitHub。

## 📋 上传前准备

### 1. 确认文件完整性

确保以下文件已准备好：

```
✓ backend/ - 后端代码完整
✓ frontend/ - 前端代码完整
✓ docs/ - 文档文件（API.md, DB_DESIGN.md 等）
✓ README.md - 项目说明
✓ .gitignore - Git 忽略文件
✓ LICENSE - 许可证文件（可选）
```

### 2. 清理敏感信息

⚠️ **重要：上传前必须检查**

- [ ] 删除或确认 `.env` 文件已在 `.gitignore` 中
- [ ] 检查代码中是否有硬编码的密码或密钥
- [ ] 确认测试数据中的密码是通用测试密码（123456）
- [ ] 移除任何个人信息或敏感配置

### 3. 测试项目

上传前务必测试：

```bash
# 后端测试
cd backend
python init_db.py
python run.py
python test_api.py

# 前端测试
cd frontend
npm install
npm run dev
```

---

## 🚀 方法一：GitHub Desktop（推荐新手）

### 步骤 1: 下载并安装 GitHub Desktop

访问：https://desktop.github.com/

### 步骤 2: 登录 GitHub 账号

打开 GitHub Desktop → File → Options → Accounts → Sign in

### 步骤 3: 创建仓库

1. File → New Repository
2. 填写信息：
   - Name: `shu_jwxt`
   - Description: `学分制教务选课管理系统`
   - Local Path: 选择 `D:\shu_jwxt\shu_jwxt` 的父目录
   - Initialize with README: **取消勾选**（我们已有 README.md）
   - Git ignore: Python
   - License: MIT

### 步骤 4: 添加文件到仓库

GitHub Desktop 会自动检测到所有文件，点击左下角：
- Summary: `Initial commit: 完整的教务选课管理系统`
- Description: 可选，详细描述

点击 **Commit to main**

### 步骤 5: 发布到 GitHub

1. 点击顶部 **Publish repository**
2. 取消勾选 "Keep this code private"（如果想公开）
3. 点击 **Publish Repository**

完成！访问 `https://github.com/YOUR_USERNAME/shu_jwxt` 查看

---

## 💻 方法二：命令行（推荐熟悉 Git 的用户）

### 步骤 1: 初始化 Git 仓库

```bash
cd D:\shu_jwxt\shu_jwxt

# 初始化 Git
git init

# 配置用户信息（如果未配置）
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 步骤 2: 添加文件

```bash
# 查看文件状态
git status

# 添加所有文件
git add .

# 或分别添加
git add backend/
git add frontend/
git add docs/
git add README.md
git add .gitignore
```

### 步骤 3: 创建首次提交

```bash
git commit -m "Initial commit: 完整的教务选课管理系统

- 后端：Flask + MySQL，完整 API 实现
- 前端：Vue 3 + Element Plus
- 数据库：建表脚本、存储过程、触发器、测试数据
- 文档：API 文档、数据库设计、开发指南
- 测试：自动化测试脚本和部署脚本
"
```

### 步骤 4: 在 GitHub 创建远程仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - Repository name: `shu_jwxt`
   - Description: `学分制教务选课管理系统 - Flask + Vue 3 + MySQL`
   - Public/Private: 选择公开或私有
   - **不要勾选** Initialize with README
3. 点击 **Create repository**

### 步骤 5: 关联远程仓库并推送

```bash
# 添加远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/shu_jwxt.git

# 查看远程仓库
git remote -v

# 推送到 GitHub
git branch -M main
git push -u origin main
```

如果推送时要求登录：
- 输入 GitHub 用户名
- 密码使用 **Personal Access Token**（不是 GitHub 密码）

### 步骤 6: 创建 Personal Access Token（如需要）

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → Generate new token (classic)
3. 勾选 `repo` 权限
4. 生成并复制 Token
5. 在 git push 时输入 Token 作为密码

---

## 🏷️ 方法三：��用 GitHub CLI（最快捷）

### 步骤 1: 安装 GitHub CLI

访问：https://cli.github.com/

或使用包管理器：
```bash
# Windows (Scoop)
scoop install gh

# Mac
brew install gh
```

### 步骤 2: 登录

```bash
gh auth login
```

按提示选择：
- GitHub.com
- HTTPS
- Login with a web browser

### 步骤 3: 创建并推送

```bash
cd D:\shu_jwxt\shu_jwxt

# 初始化并提交
git init
git add .
git commit -m "Initial commit: 完整的教务选课管理系统"

# 创建远程仓库并推送（一条命令完成！）
gh repo create shu_jwxt --public --source=. --remote=origin --push
```

---

## 📝 推送后的工作

### 1. 添加项目描述和标签

在 GitHub 仓库页面：
1. 点击右上角齿轮图标（About 旁边）
2. 填写 Description: `学分制教务选课管理系统 - Flask + Vue 3 + MySQL`
3. 添加 Topics (标签):
   - `flask`
   - `vue3`
   - `mysql`
   - `education`
   - `course-selection`
   - `student-management`

### 2. 设置 README 显示

GitHub 会自动识别根目录的 `README.md` 并在仓库首页显示

### 3. 创建 Releases（可选）

创建第一个版本发布：
1. GitHub → Releases → Create a new release
2. Tag: `v1.0.0`
3. Title: `v1.0.0 - 初始版本`
4. Description: 描述功能特性
5. Publish release

### 4. 启用 GitHub Pages（可选）

如果想部署前端静态页面：
1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: main → /frontend
4. Save

---

## 🔄 日常更新流程

### 修改代码后推送

```bash
# 查看修改
git status

# 添加修改的文件
git add .

# 提交
git commit -m "feat: 添加新功能描述"

# 推送
git push
```

### Commit Message 规范

遵循约定式提交（Conventional Commits）：

```bash
git commit -m "feat: 添加学生成绩导出功能"
git commit -m "fix: 修复选课时间冲突判断错误"
git commit -m "docs: 更新 API 文档"
git commit -m "style: 格式化代码"
git commit -m "refactor: 重构数据库连接逻辑"
git commit -m "test: 添加选课接口测试用例"
git commit -m "chore: 更新依赖包版本"
```

---

## ⚠️ 常见问题

### Q1: git push 失败 - Authentication failed

**解决方法：**
使用 Personal Access Token 代替密码：
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/shu_jwxt.git
```

### Q2: 文件太大无法推送

**解决方法：**
检查是否误提交了大文件：
```bash
# 查看大文件
find . -type f -size +10M

# 从 Git 历史中移除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH_TO_LARGE_FILE" \
  --prune-empty --tag-name-filter cat -- --all
```

### Q3: .env 文件被误提交

**解决方法：**
```bash
# 从 Git 中移除但保留本地文件
git rm --cached backend/.env

# 添加到 .gitignore
echo "backend/.env" >> .gitignore

# 提交
git commit -m "chore: 移除 .env 文件"
git push
```

### Q4: 想修改最后一次提交

```bash
# 修改文件后
git add .
git commit --amend -m "新的提交信息"
git push --force  # 注意：强制推送会覆盖远程历史
```

---

## 📌 推送检查清单

上传前请确认：

- [ ] ✅ `.gitignore` 文件已创建
- [ ] ✅ `.env` 文件未被包含
- [ ] ✅ 没有硬编码的密码或密钥
- [ ] ✅ 所有代码可以正常运行
- [ ] ✅ README.md 已更新到最新
- [ ] ✅ 文档齐全（API.md, DB_DESIGN.md 等）
- [ ] ✅ 测试通过
- [ ] ✅ 依赖文件完整（requirements.txt, package.json）

---

## 🎉 推送成功后

### 1. 分享你的项目

```
项目地址：https://github.com/YOUR_USERNAME/shu_jwxt
```

### 2. 邀请协作者

Settings → Collaborators → Add people

### 3. 设置项目 Wiki

Settings → Features → Wikis → 勾选

### 4. 设置问题跟踪

Settings → Features → Issues → 勾选

---

## 🔗 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 官方指南](https://docs.github.com/)
- [GitHub Desktop 下载](https://desktop.github.com/)
- [GitHub CLI 文档](https://cli.github.com/)
- [Git 常用命令速查](https://training.github.com/downloads/zh_CN/github-git-cheat-sheet/)

---

**祝你上传成功！** 🚀

如有问题，欢迎查阅 GitHub 官方文档或在本项目创建 Issue。
