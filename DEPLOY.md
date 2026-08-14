# 个股排雷扫描仪 — Render 部署指南

> 本指南将带你把「个股排雷扫描仪」部署到 Render（国外 PaaS 平台），生成一个公网可访问的 HTTPS 链接。

---

## 前置条件

1. 一个 **GitHub 账号**（免费注册：https://github.com/signup）
2. 一个 **Render 账号**（免费注册：https://dashboard.render.com/register，可直接用 GitHub 账号登录）

---

## 第一步：把代码上传到 GitHub

### 1.1 创建 GitHub 仓库

1. 打开 https://github.com/new
2. Repository name 填写：`stock-analyzer`（或任意名字）
3. 选择 **Public**（公开，免费）
4. 点击 **Create repository**

### 1.2 本地代码推送到 GitHub

打开终端，执行以下命令（把 `你的用户名` 替换成你的 GitHub 用户名）：

```bash
# 进入项目目录
cd "/Users/ouyanghengxin/WorkBuddy AI/2026-08-12-15-25-31/stock_analyzer"

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 关联远程仓库（替换 你的用户名）
git remote add origin https://github.com/你的用户名/stock-analyzer.git

# 推送代码
git branch -M main
git push -u origin main
```

推送成功后，刷新 GitHub 页面应该能看到所有文件。

---

## 第二步：在 Render 上部署

### 2.1 创建 Web Service

1. 登录 https://dashboard.render.com
2. 点击 **New +** → **Web Service**
3. 选择你刚才创建的 GitHub 仓库 `stock-analyzer`
4. 点击 **Connect**

### 2.2 配置服务

在配置页面填写以下信息：

| 配置项 | 填写内容 |
|--------|----------|
| **Name** | `stock-analyzer`（或任意名字） |
| **Region** | `Oregon (US West)`（默认即可） |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Plan** | `Free`（免费） |

> 💡 如果你上传了 `render.yaml`，Render 会自动识别这些配置。

5. 点击页面底部的 **Create Web Service**

### 2.3 等待部署完成

- Render 会自动拉取代码、安装依赖、启动服务
- 第一次部署大概需要 **3-5 分钟**（akshare + pandas + numpy 包比较大）
- 部署成功后，页面会显示一个绿色的 **Live** 状态
- 点击页面顶部的链接（类似 `https://stock-analyzer-xxxx.onrender.com`）即可访问

---

## 第三步：访问你的网站

部署完成后，你会得到一个类似这样的链接：

```
https://stock-analyzer-abc123.onrender.com
```

把这个链接发给任何人，他们都能直接打开使用。

> ⚠️ **免费版的限制**：如果 15 分钟内没有人访问，服务会进入休眠状态。下一次访问时需要 **10-30 秒** 的冷启动时间。这是免费版的正常行为，不影响正常使用。

---

## 文件说明（已自动生成）

| 文件 | 作用 |
|------|------|
| `Procfile` | 告诉 Render 如何启动应用 |
| `render.yaml` | Render Blueprint 配置，支持一键部署 |
| `requirements.txt` | Python 依赖列表（含 gunicorn） |
| `app.py` | Flask 主程序（已适配生产环境） |

---

## 后续更新代码

如果你修改了代码，只需重新推送到 GitHub，Render 会自动重新部署：

```bash
cd "/Users/ouyanghengxin/WorkBuddy AI/2026-08-12-15-25-31/stock_analyzer"
git add .
git commit -m "更新说明"
git push origin main
```

---

## 常见问题

**Q: 部署失败，Build 阶段报错？**
A: 检查 `requirements.txt` 是否正确上传，或者尝试在 Build Command 里加上 `pip install --upgrade pip`。

**Q: 访问网站显示 "Service Unavailable"？**
A: 免费版冷启动需要等待 10-30 秒，刷新一下即可。

**Q: 国内访问慢？**
A: Render 服务器在美国，国内访问有一定延迟。如果需要国内速度，建议升级到方案 B（国内云服务器）。

**Q: 可以绑定自定义域名吗？**
A: 可以。在 Render 后台的 **Settings → Custom Domains** 里添加你的域名，按提示配置 DNS 即可。
