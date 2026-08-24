# 概念文档

本目录包含 rst-to-myst 的概念解释文档，按学习路径排序。

## 入门组

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [项目介绍与安装](00-introduction.md) | 安装、核心能力、CLI和API快速开始 |
| 01 | [命令行工具详细用法](01-cli-usage.md) | 所有子命令、全局选项和配置文件 |
| 02 | [Python API 使用指南](02-python-api.md) | 核心API函数、参数、返回值和代码示例 |

## 核心组

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | [三阶段转换流水线架构](03-conversion-pipeline.md) | RST→AST→Tokens→Markdown 转换流程 |
| 04 | [LosslessRSTParser 与自定义 Transform](04-lossless-parser.md) | 无损解析器设计和自定义AST变换 |
| 05 | [指令转换机制与 directives.yml 映射](05-directive-conversion.md) | RST指令到MyST指令的语法级映射 |
| 06 | [MarkdownItRenderer 与 AST→Token 遍历](06-token-rendering.md) | Visitor模式、token生成和inline管理 |
| 07 | [mdformat 渲染集成与自定义渲染器](07-mdformat-integration.md) | mdformat引擎使用和自定义渲染器 |

## 进机组

| 序号 | 文档 | 说明 |
|------|------|------|
| 08 | [ApplicationNamespace 与 Sphinx 扩展加载机制](08-namespace-mocking.md) | Mock Sphinx应用收集指令/角色 |
| 09 | [Front Matter 提取与 YAML 输出](09-front-matter.md) | RST field list 到 YAML front matter |
| 10 | [转换选项详解](10-configuration-options.md) | 所有转换选项的作用和使用场景 |

```{toctree}
:hidden:

00-introduction
01-cli-usage
02-python-api
03-conversion-pipeline
04-lossless-parser
05-directive-conversion
06-token-rendering
07-mdformat-integration
08-namespace-mocking
09-front-matter
10-configuration-options
```
