# AI Sports Daily 🏃‍♂️🤖

一个零成本、自动化的AI运动日报生成系统，部署在GitHub Pages上。

## 项目简介

本项目旨在每天自动从RSS和Reddit采集AI前沿、运动科学、装备评测等领域的最新资讯，利用本地LLM（Ollama）生成中文摘要，并发布为静态网页，方便在微信等移动端阅读。

## 🚀 快速开始

### 1. Fork 本仓库
点击右上角的 **Fork** 按钮，将项目复制到您自己的GitHub账号下。

### 2. 配置 Reddit API (必选)
为了获取Reddit数据，您需要注册一个Reddit应用：

1.  登录 [Reddit](https://www.reddit.com)。
2.  访问 [Reddit App Preferences](https://www.reddit.com/prefs/apps)。
3.  点击 **"create another app..."** (或 "create app")。
4.  填写信息：
    - **name**: `AI Sports Daily` (或任意名称)
    - **type**: 选择 **script** (重要!)
    - **description**: (留空)
    - **about url**: (留空)
    - **redirect uri**: `http://localhost:8080` (必填，虽然不需要实际使用)
5.  点击 **create app**。
6.  获取以下两个值：
    - **Client ID**: 应用名称下方的字符串（例如 `AbCdEfGhIjKlMn`）。
    - **Client Secret**: `secret` 字段对应的值。

### 3. 配置 GitHub Secrets (必选)
为了让GitHub Actions自动运行，需要配置密钥：

1.  在您的GitHub仓库页面，点击 **Settings** -> **Secrets and variables** -> **Actions**。
2.  点击 **New repository secret**，添加以下变量：

| Name | Value | 说明 |
| :--- | :--- | :--- |
| `REDDIT_CLIENT_ID` | (填入您的Client ID) | Reddit API ID |
| `REDDIT_CLIENT_SECRET` | (填入您的Client Secret) | Reddit API Secret |
| `REDDIT_USER_AGENT` | `python:ai-sports-daily:v1.0 (by /u/YOUR_USERNAME)` | 格式随意，建议填真实用户名 |

### 4. 开启 GitHub Pages
1.  在您的GitHub仓库页面，点击 **Settings** -> **Pages**。
2.  在 **Build and deployment** -> **Source** 中，选择 **Deploy from a branch**。
3.  在 **Branch** 中，选择 **gh-pages** 分支（如果还没有该分支，请等待第一次Actions运行成功后会自动创建，然后再来选择）。
4.  点击 **Save**。

## 🛠️ 本地开发与预览

如果您想在本地运行或测试生成的网页：

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **运行生成器** (模拟数据):
    ```bash
    python src/generator/html_builder.py
    ```

3.  **本地预览**:
    进入 `output` 目录并启动简单服务器：
    ```bash
    cd output
    python -m http.server 8000
    ```
    然后在浏览器访问 `http://localhost:8000`。

## 📂 项目结构

- `.github/workflows`: 自动化部署脚本
- `src`: Python源码
    - `generator`: 静态网页生成逻辑
- `template`: HTML模板
- `static`: CSS样式与JS脚本
- `output`: 生成的静态网站（由脚本自动生成，通过gh-pages分支发布）

## ⚠️ 注意事项

- **Ollama**: 在GitHub Actions中，我们自动安装Ollama并拉取Mistral模型。这需要一些时间，且受限于GitHub Actions的资源（无GPU），速度较慢。
- **.nojekyll**: 输出目录包含 `.nojekyll` 文件，确保GitHub Pages不会忽略下划线开头的文件。
- **文章归档**: 单日超过50篇文章时，仅保留最重要的30篇显示在HTML中，其余存入 `archive.json`。

## 📄 License
MIT
