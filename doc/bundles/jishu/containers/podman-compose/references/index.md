# 信源索引

本目录包含 podman-compose OKF Wiki 所有文档引用的信源登记文件。

## 信源列表

| 信源ID | 文件 | 描述 |
|--------|------|------|
| readme | [readme-source.md](readme-source.md) | podman-compose 官方 README 文档，包含项目概述、安装方法、依赖说明 |
| source-code | [source-code-map.md](source-code-map.md) | podman_compose.py 源码信源登记：版本固定（v1.6.0 / commit e3df104）、结构地图与核心符号索引 |
| docs | [docs-source.md](docs-source.md) | 官方 docs/ 文档信源：7 份版本 Changelog、Extensions 扩展说明、Mappings 历史映射与 bash 补全脚本 |
| examples | [examples-source.md](examples-source.md) | 官方 examples/ 目录信源：12 个示例应用的清单、文件构成与演示特性索引 |

## 信源说明

所有概念文档和示例文档的 `sources` 字段均指向本目录下的信源文件，确保知识可溯源、可验证。

```{toctree}
:hidden:
:maxdepth: 2

readme-source
source-code-map
docs-source
examples-source
```
