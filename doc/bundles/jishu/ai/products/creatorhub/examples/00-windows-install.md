---
okf_version: "0.2"
type: Example
title: "Windows 安装版：双击安装与首次启动"
description: "CreatorHub Windows 10/11 x64 安装包下载、安装、首次启动与浏览器组件准备、v0.2.0+ 更新机制、升级前备份与无签名安装包核验"
tags: [creatorhub, windows, installer, setup, webview2, update, quickstart]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-26T10:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-26T10:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: official-readme
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/README.md
  - id: official-changelog
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/CHANGELOG.md
---

# Windows 安装版：双击安装与首次启动

> 适用：Windows 10/11 x64。对应 v0.2.0+（2026-09-14 起）；v0.1.0 只有源码运行（F-024、F-054）。本页未实机复跑，步骤逐字来自官方 README/CHANGELOG。

## 前置条件

- Windows 10 或 11，x64（F-054）。
- 安装与首次启动**保持联网**：安装器可能联网安装 WebView2，首次启动会下载浏览器组件（F-054）。
- 不需要自行安装 Python、运行构建命令或下载源码（F-054）。
- 建议预留足够磁盘空间给 `data/media/` 与浏览器内核（官方未给具体容量，按实际内容量评估）。

## 步骤

### 1. 下载安装包

1. 打开 Releases 最新版页面：`https://github.com/3441293738/creatorhub/releases/latest`。
2. 在 Assets 中下载 `CreatorHub-Setup-版本-windows-x64.exe`。
3. 注意：`Source code (zip)` 是源码，不是安装包（F-054）。

> 只从本项目 GitHub Releases 下载。v0.2.0 的已知说明明确：安装包暂未配置发布者代码签名（F-054）。没有签名时，系统无法用信任链验证来源，下载后应核对页面来源与文件信息。

### 2. 安装

1. 双击安装包。
2. 按向导完成安装（v0.2.0 起安装与卸载向导默认简体中文）（F-071）。
3. 缺少 WebView2 时，安装器会自动联网安装（F-054）。
4. 安装完成后使用桌面快捷方式启动（F-054）。

### 3. 首次启动

1. 在启动中心点击“启动本地服务”（F-054）。
2. 首次会自动下载浏览器组件；就绪后打开工作台（F-054）。
3. 在面板中登录账号（步骤见 [02-accounts-monitoring-and-collection.md](02-accounts-monitoring-and-collection.md)）。

> 首次启动不要急着建大量任务：先登录一个号、跑一条监控，确认浏览器组件与网络正常（F-018 的小规模原则）。

### 4. 更新（v0.2.0+）

- 安装版默认**每天最多一次**后台检查新版本；只提醒，不自动下载（F-054）。
- 看到提醒后点“一键更新”，下载完成后确认“安装并重启”（F-054）。
- 下载支持**增量优先、完整包兜底、断点续传**；更新保留用户数据（F-054）。
- 可在「偏好设置 → 版本与更新」关闭自动检查或手动更新（F-054）。
- 尚无一键更新入口的旧版：先“停止并退出”，再手动运行新版安装包（F-054）。

### 5. 升级前备份

官方建议：备份项目时一并备份 `config.yaml` 和 `data/`（F-059）。升级前至少复制：

```text
config.yaml
data/creatorhub.db
data/profiles/
data/media/        # 体积大，可按需
```

> `data/profiles/` 等同账号登录权限，备份文件要放在加密盘或受控目录，不要上传网盘公共链接（F-032、F-067）。

## 验收清单

- [ ] 安装包来自官方 Releases，文件名形如 `CreatorHub-Setup-<版本>-windows-x64.exe`。
- [ ] 启动中心能“启动本地服务”，工作台能打开。
- [ ] 首次浏览器组件下载完成，账号页能发起扫码登录。
- [ ] 「偏好设置 → 版本与更新」可见检查/更新入口。
- [ ] 已备份 `config.yaml` 与 `data/`。

## 已知边界与排障

| 现象 | 处理 | 依据 |
|---|---|---|
| 安装/首次启动失败 | 确认 Windows 10/11 x64、保持联网、检查 WebView2 | F-054 |
| 浏览器组件未就绪 | 等待首次下载完成；源码模式可 `python -m patchright install chromium` | F-054、F-056 |
| 扫码登录没有弹窗 | 确认有桌面环境；抖音可用 Cookie 登录 | F-070 |
| 更新后页面仍是旧版 | 刷新工作台；确认启动中心版本 | F-071 |
| 无签名安全提示 | 确认下载来源为官方 Releases；不要在第三方站点下载 | F-054 |

## 下一步

- 不想用安装版：[源码运行](01-source-run.md)
- 装好后：[添加账号与监控](02-accounts-monitoring-and-collection.md)
