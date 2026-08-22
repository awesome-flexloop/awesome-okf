---
type: "reference"
title: Sphinx 构建器基类 API 参考
description: Builder基类的属性和方法参考。
tags: [sphinx, api, builder, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-22T15:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: builder-py
    resource: /references/builder-api.md
    title: sphinx/builders/__init__.py 源码
---
# Sphinx 构建器基类 API 参考

所有构建器继承自`Builder`基类，定义在`sphinx/builders/__init__.py`。

## 类属性（ClassVar）

| 属性 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| `name` | `str` | `''` | 构建器名称，CLI选择用（如'html'） |
| `format` | `str` | `''` | 输出格式/文件扩展名 |
| `epilog` | `str` | `''` | 构建完成消息模板（支持{outdir},{project}） |
| `default_translator_class` | `type[NodeVisitor]` | - | 默认Translator类 |
| `versioning_method` | `str` | `'none'` | 版本控制方法 |
| `versioning_compare` | `bool` | `False` | 是否比较版本 |
| `allow_parallel` | `bool` | `False` | 是否支持并行write_doc |
| `use_message_catalog` | `bool` | `True` | 是否使用消息目录（i18n） |
| `supported_image_types` | `list[str]` | `[]` | 支持的图片MIME类型 |
| `supported_remote_images` | `bool` | `False` | 是否支持远程图片 |
| `supported_data_uri_images` | `bool` | `False` | 是否支持data-URI嵌入图片 |

## 实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `srcdir` | `_StrPath` | 源目录 |
| `confdir` | `_StrPath` | 配置目录 |
| `outdir` | `_StrPath` | 输出目录 |
| `doctreedir` | `_StrPath` | doctree缓存目录 |
| `env` | `BuildEnvironment` | 构建环境 |
| `events` | `EventManager` | 事件管理器 |
| `config` | `Config` | 配置对象 |
| `tags` | `Tags` | 标签集合 |
| `phase` | `BuildPhase` | 当前构建阶段 |
| `images` | `dict[str, str]` | 需要复制的图片（源→目标） |
| `imagedir` | `str` | 图片目录名 |
| `imgpath` | `str` | 当前文档到图片目录的相对路径 |

## 核心方法（子类需重写）

| 方法 | 说明 |
|------|------|
| `init()` | 构建器初始化，加载模板/配置 |
| `get_outdated_docs() -> list[str]` | 返回需要重新构建的文档名列表 |
| `prepare_writing(docnames)` | 写入前准备 |
| `write_doc(docname, doctree)` | 写入单个文档（核心方法） |
| `write_doc_serialized(docname, doctree)` | 并行模式下的序列化写入 |
| `finish()` | 构建完成后的收尾工作（生成索引等） |
| `cleanup()` | 清理临时资源 |
| `get_target_uri(docname, typ=None) -> str` | 获取文档的URI |
| `get_relative_uri(from_, to, typ=None) -> str` | 获取相对URI |
