---
okf_version: "0.2"
type: concept
title: "主题、扩展列表与许可证"
description: "理解主题CSS服务与URL重写机制、扩展黑白名单远程获取与定时刷新、第三方许可证收集与多格式报告生成。"
tags: [themes, css, url-rewrite, listings, blacklist, whitelist, licenses, report]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:30:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T12:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: themes-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/themes_handler.py"
    title: "jupyterlab_server/themes_handler.py"
  - id: listings-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/listings_handler.py"
    title: "jupyterlab_server/listings_handler.py"
  - id: licenses-handler-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_server/jupyterlab_server/licenses_handler.py"
    title: "jupyterlab_server/licenses_handler.py"
---

# 主题、扩展列表与许可证

本章介绍 jupyterlab_server 的三个辅助子系统：主题文件服务、扩展黑白名单管理和第三方许可证报告。

## 主题系统（ThemesHandler）

```python
class ThemesHandler(FileFindHandler):
```

主题处理器继承自 `jupyter_server.base.handlers.FileFindHandler`，增加了CSS URL重写功能。

### 为什么需要URL重写？

JupyterLab主题以CSS文件形式分发，主题CSS中可能引用了字体、图标等静态资源：

```css
/* 主题CSS中的URL */
@font-face {
  font-family: 'Theme Font';
  src: url('./fonts/theme-font.woff2') format('woff2');
}
```

当通过 `themes_url` 路径（如 `/lab/api/themes/`）服务这些CSS文件时，浏览器会基于CSS文件的URL解析相对路径。由于主题文件实际位于扩展的 themes 目录而非themes_url路径，需要服务端重写URL为正确的绝对路径。

### URL重写算法

ThemesHandler._get_css() 的重写逻辑：

1. 读取CSS文件内容（bytes）
2. 如果 `themes_url` 未设置，返回空
3. 使用正则 `re.compile(r"url\((?P<url>.*?)\)")` 匹配所有 `url(...)` 模式
4. 对每个匹配的URL：
   - 去除引号（单/双引号）
   - 绝对路径（`/`开头）或有scheme（如http://）的URL保持不变
   - 相对路径替换为 `{themes_url}/{basedir}/{relative_path}`，其中basedir是CSS文件所在主题目录名
5. 返回重写后的CSS内容

### 主题目录发现

初始化时，ThemesHandler从 labextensions_path 递归发现主题目录：

1. 遍历每个 labextensions_path 目录
2. 递归查找所有 `**/themes` 目录
3. 将核心 themes_dir 放在最后（扩展主题优先，可覆盖核心主题）
4. 将所有主题目录传递给父类 FileFindHandler 作为搜索路径

## 扩展列表系统（ListingsHandler）

```python
class ListingsHandler(APIHandler):
```

ListingsHandler 提供扩展黑白名单功能，允许管理员从远程URL获取扩展屏蔽/允许列表。

### 黑白名单模式

| 模式 | 配置项 | 行为 |
|------|--------|------|
| 黑名单模式 | `blocked_extensions_uris` | 屏蔽列表中的扩展不可安装 |
| 白名单模式 | `allowed_extensions_uris` | 仅允许列表中的扩展安装 |
| 禁用模式 | 两者都不设置 | 所有扩展均可安装 |

> ⚠️ 黑名单和白名单不能同时使用，否则add_handlers()会记录警告并退出。

### 远程获取机制

`fetch_listings(logger)` 函数执行实际的列表获取：

1. 遍历 `ListingsHandler.blocked_extensions_uris` 集合
2. 对每个URI发送HTTP GET请求（使用 `requests` 库）
3. 解析响应JSON中的 `blocked_extensions` 列表
4. 对 `allowed_extensions_uris` 执行相同操作
5. 将合并结果序列化为JSON存入 `ListingsHandler.listings` 类属性

### 定时刷新

配置了列表URI时，add_handlers() 启动 `tornado.ioloop.PeriodicCallback`：
- 刷新间隔：`ListingsHandler.listings_refresh_seconds`（默认3600秒=1小时）
- 带0-2秒随机jitter，避免多实例同时刷新造成服务端雪崩
- 刷新回调调用 `fetch_listings(None)`

### 请求路径

仅响应特定路径 `@jupyterlab/extensionmanager-extension/listings.json`：
```python
path = self.request.path.strip("/")
if path.endswith(ListingsHandler.LISTINGS_URL_SUFFIX):
    # 返回listings JSON
else:
    raise web.HTTPError(404)
```

## 许可证报告系统（LicensesHandler/LicensesApp）

许可证系统收集JupyterLab及其联邦扩展中的第三方许可证信息，支持JSON/CSV/Markdown三种输出格式。

### LicensesManager

```python
class LicensesManager(LoggingConfigurable):
```

许可证管理器负责发现、读取和格式化许可证信息。

#### 许可证发现

1. 查找应用static目录中的 `package.json`（应用本身的依赖信息）
2. 在static目录中查找第三方许可证文件（默认 `third-party-licenses.json` 和 `static/third-party-licenses.json`）
3. 遍历联邦扩展目录，同样查找第三方许可证文件
4. 对每个许可证bundle（应用+每个联邦扩展），读取package.json中的依赖列表

#### 报告格式

**JSON格式**（report_json）：
```json
{
  "bundles": [
    {
      "name": "@jupyterlab/application-extension",
      "versionInfo": "3.0.0",
      "packages": [
        {
          "name": "react",
          "versionInfo": "17.0.2",
          "licenseId": "MIT",
          "extractedText": "MIT License\n..."
        }
      ]
    }
  ]
}
```

**CSV格式**（report_csv）：列包含 bundle、name、versionInfo、licenseId、extractedText，用csv.writer输出。

**Markdown格式**（report_markdown）：每个bundle一个二级标题，每个包一个表格或列表，full_text=True时包含完整许可证文本。

#### bundles_pattern过滤

`bundles_pattern` 参数支持正则表达式过滤bundle名称：
- `.*`（默认）：所有bundle
- `@jupyterlab/.*`：仅JupyterLab核心bundle
- `^(?!@jupyterlab)`：排除JupyterLab核心，仅显示第三方

### LicensesHandler REST API

`GET /lab/api/licenses/` 支持以下查询参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `full_text` | "true" | 是否包含完整许可证文本 |
| `format` | "json" | 输出格式：json/csv/markdown |
| `bundles` | ".*" | bundle名称正则过滤 |
| `download` | "0" | 是否作为附件下载（Content-Disposition） |

Handler重写了 `finish()` 方法，根据format设置正确的Content-Type（而非默认的application/json）。

### LicensesApp CLI

```bash
# Markdown报告到stdout
python -m jupyterlab_server.licenses

# JSON格式
python -m jupyterlab_server.licenses --json

# CSV格式
python -m jupyterlab_server.licenses --csv

# 不包含完整许可证文本
python -m jupyterlab_server.licenses --no-full-text

# 指定输出文件
python -m jupyterlab_server.licenses > licenses.md
```

CLI类通过JupyterApp的aliases/flags系统支持命令行参数。

---

**下一步阅读：**
- [国际化](08-internationalization.md) — gettext翻译系统
- [进程管理与测试](09-process-and-cli.md)
