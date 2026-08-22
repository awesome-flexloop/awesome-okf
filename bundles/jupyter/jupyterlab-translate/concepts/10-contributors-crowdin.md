---
type: Concept
title: Crowdin贡献者集成
description: jupyterlab-translate通过Crowdin API下载翻译贡献者报告并格式化为Markdown CONTRIBUTORS.md文件
tags: [crowdin, contributors, community, api, translation, report, markdown]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:15:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T13:15:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: contributors-source
    resource: /references/contributors-source.md
    title: Crowdin贡献者模块源码映射
---

# Crowdin贡献者集成

jupyterlab-translate 集成了Crowdin翻译平台API，可以自动下载每个语言的翻译贡献者报告，并将其格式化为Markdown格式的CONTRIBUTORS.md文件。这一功能用于在语言包中致谢翻译贡献者。

## 功能概述

贡献者更新功能由 `contributors.py` 模块实现，支持两种触发方式：

1. **CLI命令**：`jupyterlab-translate update-contributors <package_dir>`
2. **Hatch构建钩子**：非wheel构建时自动更新（需要CROWDIN_API_KEY环境变量）

## 前置条件

使用贡献者功能需要：

1. **Crowdin API密钥**：设置环境变量 `CROWDIN_API_KEY`
2. **网络访问**：能够访问Crowdin API（`https://api.crowdin.com`）
3. **Crowdin项目ID**：默认为JupyterLab官方项目ID `409874`

```bash
export CROWDIN_API_KEY="your-api-key-here"
```

## 核心API

### FirstCrowdinClient类

继承自 `crowdin_api.CrowdinClient`，配置如下：

| 属性 | 值 | 说明 |
|------|-----|------|
| `TOKEN` | `os.environ.get("CROWDIN_API_KEY")` | 从环境变量获取API密钥 |
| `PAGE_SIZE` | `100000` | 大分页大小，减少API请求次数 |

模块级创建了单例client：`client = FirstCrowdinClient()`

### get_contributors_report()

这是高层API函数，整合完整的报告获取流程：

```python
get_contributors_report(
    project_id: int = 409874,
    locale: Optional[str] = None,
    crowdin_key: Optional[str] = None
) -> str
```

**参数：**
- `project_id`：Crowdin项目ID，默认409874（JupyterLab官方）
- `locale`：语言代码（如 `ko`, `zh-CN`），None表示所有语言
- `crowdin_key`：可选的Crowdin API密钥（优先级高于环境变量）

**返回：** 格式化后的Markdown字符串

### 执行流程

```
get_contributors_report()
    │
    ├──→ get_project_data(project_id)
    │    获取项目信息（包含targetLanguages列表）
    │
    ├──→ get_languages(project_data)
    │    提取语言locale → {id, name}映射
    │
    ├──→ download_data(project_id, language_id)
    │    │
    │    ├──→ reports.generate_top_members_report()
    │    │    生成按词数统计的顶级成员报告（CSV格式）
    │    │
    │    ├──→ reports.check_report_generation_status()
    │    │    轮询报告生成状态，获取ETA
    │    │
    │    ├──→ time.sleep(wait_time)
    │    │    等待报告生成完成
    │    │
    │    └──→ reports.download_report() → requests.get(url)
    │         下载CSV报告内容
    │
    └──→ format_data(data, language)
         解析CSV，格式化为Markdown列表
```

## 报告参数

Crowdin报告使用以下参数：

| 参数 | 值 | 说明 |
|------|-----|------|
| 报告类型 | `top_members` | 顶级贡献者报告 |
| 统计维度 | `words` | 按翻译词数统计 |
| 格式 | `csv` | CSV格式输出 |
| 起始时间 | `2019-04-01T00:00:00Z` | JupyterLab翻译项目启动时间 |

## 等待策略

`download_data()` 实现了智能等待：

1. 调用 `check_report_generation_status()` 获取ETA
2. 如果ETA单位为"second"，等待 `amount * 2` 秒（双倍保险）
3. 如果ETA为null或其他单位，等待5秒
4. 然后下载报告

## CSV数据格式

Crowdin返回的CSV包含以下列：

| 列序 | 列名 | 说明 |
|------|------|------|
| 0 | Name | 用户名或"Name (username)"格式 |
| 1 | Languages | 参与的语言，分号分隔 |
| 2 | Translated (Words) | 翻译词数 |
| 3-7 | 其他统计列 | Target Words, Approved, Voted等 |

## 输出格式（Markdown）

`format_data()` 将CSV解析为以下Markdown格式：

```markdown
# Contributors

* 张三 ([@zhangsan](https://crowdin.com/profile/zhangsan))
* 李四 ([@lisi](https://crowdin.com/profile/lisi))
```

### 名称解析逻辑

`format_data()` 处理两种名称格式：

1. **带显示名**：`"张三 (zhangsan)"` → `* 张三 ([@zhangsan](https://crowdin.com/profile/zhangsan))`
2. **仅用户名**：`"zhangsan"` → `* zhangsan ([@zhangsan](https://crowdin.com/profile/zhangsan))`

名称可能是Python字面量字符串（通过 `ast.literal_eval()` 解析），也可能是纯文本。

### 过滤条件

只有满足以下条件的贡献者才会被列出：
- 翻译词数（Translated Words）> 0
- 如果指定了language参数，则该贡献者必须参与了该语言的翻译

## CLI使用

```bash
# 更新指定语言包的贡献者列表
jupyterlab-translate update-contributors ./language-packs/jupyterlab-language-pack-zh-CN
```

CLI命令的执行流程：
1. 检查 `CROWDIN_API_KEY` 环境变量，不存在则报错退出
2. 在包目录中查找 `jupyterlab_language_pack_??_??` 格式的目录
3. 从目录名提取locale代码（最后5个字符，如 `zh_CN`）
4. 调用 `get_contributors_report(locale=locale.replace("_", "-"))`
5. 将结果写入 `CONTRIBUTORS.md` 文件

## Hatch Hook集成

在 `JupyterLanguageBuildHook.initialize()` 中，非wheel构建时：

1. 检查 `CROWDIN_API_KEY` 环境变量
2. 如果存在，调用 `get_contributors_report(locale=...)`
3. 写入CONTRIBUTORS.md到包根目录
4. 构建wheel时不触发（wheel只编译翻译文件）

这意味着在构建sdist时，如果设置了API密钥，会自动更新贡献者列表。

## 注意事项

- API密钥可以通过参数 `crowdin_key` 传入，会临时覆盖client.TOKEN，调用后恢复
- 默认项目ID `409874` 是JupyterLab官方Crowdin项目，如果为自己的项目使用需要传入正确的project_id
- locale参数使用短横线格式（如 `zh-CN`, `ko-KR`），与Crowdin API一致
- 贡献者报告包含自2019年4月1日以来的所有翻译贡献

## 相关概念

- [Hatch构建钩子集成](/concepts/07-hatch-build-hook.md)
- [CLI命令参考](/concepts/03-cli-commands.md)
- [Crowdin贡献者模块源码映射](/references/contributors-source.md)
