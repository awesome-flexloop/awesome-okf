---
okf_version: "0.2"
type: "index"
title: "conda-lock 实战示例"
sources:
  - "conda_lock/"
---

# 实战示例

本目录包含 4 个完整的实战示例，覆盖 conda-lock 从基础到高级的典型使用场景，提供可直接复制运行的命令和配置文件。

* [基础锁定工作流](basic-lock-workflow.md) — 创建 environment.yml → conda-lock lock 生成锁文件 → conda-lock install 安装环境 → conda-lock render 渲染格式的完整入门流程，含 Makefile 一键脚本和常见问题解答。对应概念：[5分钟快速上手](../concepts/01-getting-started.md)、[CLI 命令体系](../concepts/11-cli-commands.md)。
* [多平台锁定](multi-platform-lock.md) — 指定 `--platform linux-64 osx-arm64 win-64` 生成跨平台锁文件，使用平台选择器（`# [osx]`/`# [linux]`/`# [win]`）处理平台特定依赖，验证跨平台包版本一致性，渲染各平台 explicit 文件。对应概念：[跨平台锁定策略](../concepts/15-cross-platform-locking.md)、[源文件解析](../concepts/07-source-parsers.md)。
* [自定义虚拟包](custom-virtual-packages.md) — 创建 virtual-packages.yaml 锁定 CUDA 版本（__cuda=12.1）、glibc 版本（__glibc=2.28/2.35）、macOS 版本（__osx=13.0），使用 `--virtual-package-spec` 选项锁定 GPU/现代 Linux/macOS 环境，含虚拟包参考表和验证脚本。对应概念：[虚拟包系统](../concepts/10-virtual-packages.md)、[内容哈希机制](../concepts/12-content-hash.md)。
* [开发依赖与 category 过滤](dev-dependencies.md) — 使用 `category: dev/docs/test` 字段标记开发/文档/测试依赖，锁定时通过 `--dev-dependencies`/`--extras`、安装时通过 `--dev`/`--extras` 控制范围，理解 BFS 类别传播算法和 main 截断规则，支持 environment.yml 和 pyproject.toml 两种格式。对应概念：[依赖类别与传播](../concepts/14-categories-and-deps.md)、[锁文件 v1/v2 格式](../concepts/06-lockfile-formats.md)。

```{toctree}
:hidden:

basic-lock-workflow
custom-virtual-packages
dev-dependencies
multi-platform-lock
```
