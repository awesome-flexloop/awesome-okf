---
okf_version: "0.2"
type: "reference-index"
bundle: jupyterlab-probot
title: 参考文档索引
description: jupyterlab-probot 源码参考文档导航
---

# 参考文档索引

本目录包含 jupyterlab-probot 的源码参考文档，基于实际源码逐行分析：

| 文档 | 对应源文件 | 内容 |
|------|-----------|------|
| [index.ts 源码详解](index-ts-source.md) | src/index.ts | 核心逻辑完整注释（248行），包含6大事件处理器、配置加载、工具函数 |
| [schema.json 配置规范](config-schema-source.md) | schema.json | 配置项完整定义，含字段说明、默认值、约束条件 |

## 其他源文件

| 文件 | 用途 |
|------|------|
| package.json | 依赖声明、npm 脚本（`npm run build`/`npm start`/`npm test`） |
| app.yml | GitHub App 注册清单，声明所需权限和事件订阅 |
| tsconfig.json | TypeScript 编译配置 |
| test/index.test.ts | 基于 nock 的事件驱动测试用例 |
| CODE_OF_CONDUCT.md | 项目行为准则 |
| LICENSE | BSD-3-Clause 许可证 |


```{toctree}
:hidden:
:maxdepth: 7

config-schema-source
index-ts-source
```
