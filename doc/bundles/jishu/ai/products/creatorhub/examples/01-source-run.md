---
okf_version: "0.2"
type: Example
title: "源码运行：环境、启动与自检"
description: "CreatorHub 源码模式：Python 3.10+ 环境、start.cmd/start.sh、手动安装、selftest 与 uvicorn、端口/开发模式、常见安装错误与安全绑定"
tags: [creatorhub, source-run, python, fastapi, uvicorn, patchright, selftest, troubleshooting]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T10:38:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-26T10:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: official-readme
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/README.md
---

# 源码运行：环境、启动与自检

> 适用：开发者、macOS/Linux、或需要改代码的用户。Windows 安装版用户可跳过本页（F-055）。步骤逐字来自官方 README；未实机复跑。

## 环境要求

| 依赖 | 要求 | 说明 |
|---|---|---|
| Python | 3.10+ | 主运行时（F-055） |
| 桌面环境 | 需要 | 扫码登录需要弹出浏览器（F-055） |
| Google Chrome | 可选，建议 | 小红书扫码登录建议安装稳定版 Chrome（F-055） |
| Node.js | 18+ | **仅**启用小红书 `api` 发布兼容模式时需要（F-055） |
| ffmpeg | 可选 | 未安装时使用 Python 依赖附带的 ffmpeg（F-055） |

## 一键启动

### 1. 克隆

```bash
git clone https://github.com/3441293738/creatorhub.git
cd creatorhub
```

### 2. 启动

Windows：

```bat
.\start.cmd
```

macOS / Linux：

```bash
chmod +x start.sh
./start.sh
```

首次运行会自动：创建虚拟环境 → 安装依赖和 Chromium → 生成 `config.yaml` → 打开 `http://127.0.0.1:8000`（F-035）。

### 3. 常用命令

```bash
.\start.cmd install        # 重新安装或更新依赖
.\start.cmd check          # 环境自检
.\start.cmd --no-open      # 启动后不自动打开页面
.\start.cmd --port 8080    # 使用其他端口
.\start.cmd --reload       # 开发模式
```

macOS / Linux 将 `.\start.cmd` 换成 `./start.sh`（F-055）。

## 手动安装（可选）

需要自行控制虚拟环境或排障时：

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
python -m patchright install chromium

# 复制 config.example.yaml 为 config.yaml 后启动
python selftest.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

仅当显式启用小红书 API 发布兼容模式时，才需安装 Node.js 依赖：

```bash
npm install
```

依据：F-056。`selftest.py` 与 `tests/` 的存在见 F-034。

## 验收清单

- [ ] `python --version` ≥ 3.10。
- [ ] `.\start.cmd check` 或 `python selftest.py` 通过。
- [ ] 浏览器 Chromium 已安装（`python -m patchright install chromium` 无报错）。
- [ ] `http://127.0.0.1:8000` 可打开工作台。
- [ ] `config.yaml` 已生成，且未被提交到 Git。

## 安全绑定

官方命令示例绑定 `127.0.0.1`（F-035、F-056）。**不要把服务监听到 `0.0.0.0` 或暴露公网**：面板持有全部账号登录态，等同于账号控制台（F-032、F-067）。

如果必须远程访问，建议通过 SSH 隧道或受控 VPN，并额外加认证层；不要直接端口映射。

## 常见安装错误

| 现象 | 处理 | 依据 |
|---|---|---|
| macOS 报 `command /usr/bin/clang++ failed with code 1` | 更新代码后删除旧 `.venv`，再运行 `./start.sh install`；安装器会先升级 pip/setuptools/wheel | F-070 |
| Patchright 启动失败或找不到浏览器 | `python -m patchright install chromium` | F-070 |
| 扫码登录没有弹窗 | 确认当前机器有桌面环境；抖音也可用 Cookie 登录 | F-055 |
| Windows 下 Patchright 子进程错误 | 使用单 worker 启动，不要添加 `--workers` | F-070 |
| 仅音频仍得到 MP4，或视频没声音/画质受限 | 更新依赖；安装系统 ffmpeg 并加入 `PATH` | F-070 |

## 与 Windows 安装版的选择

| 维度 | Windows 安装版 | 源码运行 |
|---|---|---|
| 适用系统 | Windows 10/11 x64 | Windows / macOS / Linux |
| 安装成本 | 双击，自动处理 WebView2 与浏览器组件 | 需 Python 环境，首次自动装依赖 |
| 更新 | 启动中心提醒，一键更新（v0.2.0+） | `git pull` + `start.cmd install` |
| 改代码 | 不适合 | 适合，支持 `--reload` |
| 许可 | 同样受无 LICENSE 约束（F-065） | 同样受无 LICENSE 约束 |

## 下一步

- 启动成功：[添加账号与监控](02-accounts-monitoring-and-collection.md)
- 配置与风控：[任务队列与风控](../concepts/03-task-queue-and-risk-control.md)
