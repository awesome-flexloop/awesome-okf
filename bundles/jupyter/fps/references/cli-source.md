---
type: Reference
title: fps.cli._cli 源码信源
description: fps命令行接口源码登记，对应src/fps/cli/_cli.py
tags: [cli, click, command-line]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T14:50:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T14:50:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: fps-cli-py
    resource: /references/cli-source.md
    title: src/fps/cli/_cli.py
---

## 源码位置

`src/fps/cli/_cli.py` — fps CLI入口（click命令），约122行。

## CLI入口

入口点：`fps = "fps.cli._cli:main"`（pyproject.toml中注册）

## 命令选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `MODULE`（位置参数） | `str` | `""` | 模块路径（`file:Class`或entry-point名） |
| `--config` | `click.File()` | `None` | JSON配置文件路径 |
| `--show-config` | flag | `False` | 显示实际配置后退出 |
| `--help-all` | flag | `False` | 显示配置参数描述后退出 |
| `--set` | multiple（可重复） | `None` | 设置模块参数，格式`module.param=value` |
| `--backend` | `str` | `"asyncio"` | 事件循环后端（`asyncio`或`trio`） |
| `--timeout` | `float` | `None` | 启动超时（秒） |
| `--stop-timeout` | `float` | `1` | 停止超时（秒） |

## 执行流程

1. **配置构建**：
   - 无`--config`：通过`import_from_string(module)`导入类型，构造`{root_module_name: {"type": module_type}}`
   - 有`--config`：读取JSON文件，可通过MODULE参数选择子模块为根

2. **--set参数解析**：
   - 按`=`分割key和value
   - key按`.`分割为路径列表
   - 在config_dict中逐级创建`modules`子字典
   - 最终在叶子节点的`config`字典中设置参数值

3. **运行阶段**：
   - `get_root_module(config_dict)`构建根模块
   - 设置超时参数
   - `initialize(root_module)`递归初始化所有子模块
   - `--help-all`：输出`get_config_description()`后返回
   - `--show-config`：输出`dump_config(actual_config)`后继续运行
   - 最终调用`root_module.run(backend=backend)`

## 测试支持

- 全局变量`TEST = False`，设为True时只设置`CONFIG`全局变量不实际运行
- `get_config()`函数返回全局`CONFIG`，供测试获取配置字典
