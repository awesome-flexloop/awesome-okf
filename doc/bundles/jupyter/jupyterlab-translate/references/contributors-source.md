---
type: Reference
title: Crowdin贡献者模块源码映射
description: jupyterlab-translate contributors模块（contributors.py）的Crowdin API集成
tags: [crowdin, contributors, api, i18n, community]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contributors-source
    resource: /references/contributors-source.md
    title: contributors.py 源码
---

# Crowdin贡献者模块源码映射

本文档记录 `jupyterlab_translate/contributors.py` 模块的Crowdin API集成逻辑。

## 模块信息

- **源文件**：`jupyterlab_translate/contributors.py`
- **角色**：从Crowdin项目下载翻译贡献者报告，格式化为Markdown
- **外部依赖**：crowdin-api-client, requests

## 常量

| 常量 | 值 | 源码行 | 说明 |
|------|-----|--------|------|
| `CONTRIBUTORS` | `"CONTRIBUTORS.md"` | 第17行 | 贡献者文件名 |

## 类：FirstCrowdinClient

继承自 `crowdin_api.CrowdinClient`：

| 属性 | 值 | 源码行 | 说明 |
|------|-----|--------|------|
| `TOKEN` | `os.environ.get("CROWDIN_API_KEY")` | 第21行 | 从环境变量获取API密钥 |
| `PAGE_SIZE` | `100000` | 第22行 | 默认分页大小 |

模块级单例：`client = FirstCrowdinClient()`（第25行）

## 函数清单

| 函数 | 签名 | 源码行 | 功能 |
|------|------|--------|------|
| `get_project_data` | `(project_id: int = 409874) -> dict` | 第28-43行 | 获取Crowdin项目数据 |
| `get_languages` | `(project_data: dict) -> dict` | 第46-64行 | 提取目标语言locale→{id,name}映射 |
| `download_data` | `(project_id=409874, language_id=None) -> str` | 第67-107行 | 生成并下载top members CSV报告 |
| `format_data` | `(data: dict, language: str = None) -> str` | 第110-167行 | 解析CSV，格式化为Markdown贡献者列表 |
| `get_contributors_report` | `(project_id=409874, locale=None, crowdin_key=None) -> str` | 第170-210行 | 高层API：获取项目→语言ID→下载→格式化 |

## 默认配置

- **默认Crowdin项目ID**：`409874`（JupyterLab官方翻译项目）
- **报告起始时间**：`2019-04-01T00:00:00Z`
- **报告类型**：top_members_report，按words统计
- **等待策略**：ETA为"second"时等待 `amount*2` 秒，否则等待5秒

## 输出格式

`format_data()` 输出Markdown格式：

```markdown
# Contributors

* 张三 ([@zhangsan](https://crowdin.com/profile/zhangsan))
* 李四 ([@lisi](https://crowdin.com/profile/lisi))
```

只包含翻译词数>0的贡献者。

## CLI调用

`update-contributors` 子命令调用流程：
1. 检查 `CROWDIN_API_KEY` 环境变量
2. 发现 `jupyterlab_language_pack_??_??` 格式的Python包目录
3. 从包名提取locale（取最后5个字符，如`ko_KR`）
4. 调用 `get_contributors_report(locale=...)`
5. 写入CONTRIBUTORS.md文件

## Hatch Hook集成

在 `JupyterLanguageBuildHook.initialize()` 中，非wheel构建时：
1. 检查 `CROWDIN_API_KEY` 环境变量
2. 如果存在，调用 `get_contributors_report()` 更新CONTRIBUTORS.md

## 相关概念

- [Crowdin贡献者集成](/concepts/10-contributors-crowdin.md)
- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
- [CLI命令参考](/concepts/03-cli-commands.md)
