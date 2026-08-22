---
type: Reference
title: "构建后处理脚本源码"
description: "scripts/add_plausible.py 和 scripts/filter_xeus_kernels.py 两个构建后处理脚本的完整API与逻辑解析"
tags: [build-scripts, post-build, beautifulsoup, plausible, xeus-kernels, kernel-filtering]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: add-plausible-py
    resource: "../../../../../external/libs/jupyter/try-jupyter/scripts/add_plausible.py"
    title: "try-jupyter/scripts/add_plausible.py"
  - id: filter-kernels-py
    resource: "../../../../../external/libs/jupyter/try-jupyter/scripts/filter_xeus_kernels.py"
    title: "try-jupyter/scripts/filter_xeus_kernels.py"
---

# 构建后处理脚本源码

本信源登记 `scripts/` 目录下两个Python后处理脚本的完整API与逻辑。

## 1. scripts/add_plausible.py — Plausible分析注入脚本

### 模块常量

| 常量 | 值 | 说明 |
|------|---|------|
| `PLAUSIBLE_SRC` | `"https://plausible.io/js/pa-B75UO5--FNXYQSG7GBWkf.js"` | Plausible分析脚本URL |
| `PLAUSIBLE_INIT` | 初始化代码字符串 | Plausible客户端初始化与hash路由支持 |

`PLAUSIBLE_INIT` 完整内容：
```javascript
window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},
plausible.init=plausible.init||function(i){plausible.o=i||{}};
plausible.init()
```

### 函数：`inject_plausible(dist_dir: Path) -> None`

遍历 `dist_dir` 下所有 `.html` 文件，向每个HTML的 `<head>` 中注入两个 `<script>` 标签：

1. **外部脚本**：`<script async src="PLAUSIBLE_SRC">`
2. **内联初始化脚本**：`<script>PLAUSIBLE_INIT</script>`

处理逻辑：
- 使用 `Path.rglob("*.html")` 递归查找所有HTML文件
- 使用 `BeautifulSoup(html_file.read_text(), "html.parser")` 解析HTML
- 查找 `<head>` 标签；无 `<head>` 时打印警告并跳过
- 通过 `soup.new_tag("script")` 创建新标签，设置属性后 `head.append()`
- 最后使用 `html_file.write_text(str(soup))` 写回文件

### 函数：`main() -> None`

CLI入口：
1. 使用 `argparse` 解析命令行参数，接受 `dist_dir` 位置参数（Path类型）
2. 检查 `dist_dir` 是否存在；不存在时打印错误提示 "Please run 'pixi run build' first." 并返回
3. 调用 `inject_plausible(dist_dir)`
4. 打印 "Done!"

## 2. scripts/filter_xeus_kernels.py — Xeus内核过滤脚本

### 模块常量

| 常量 | 值 | 说明 |
|------|---|------|
| `KERNELS_TO_KEEP` | `{"xcpp23", "xc23", "xr", "xpython", "xsqlite"}` | 保留的内核ID集合 |

保留的5个内核：

| 内核ID | 对应语言 | 环境文件 |
|--------|---------|---------|
| `xpython` | Python (xeus-python) | environment-python.yml |
| `xcpp23` / `xc23` | C++23 (xeus-cpp) | environment-cpp.yml |
| `xr` | R (xeus-r) | environment-r.yml |
| `xsqlite` | SQLite (xeus-sqlite) | environment-sqlite.yml |

> 注意：C++内核有两个ID（`xcpp23` 和 `xc23`），均保留以兼容不同版本标识。

### 函数：`filter_kernels(dist_dir: Path) -> None`

过滤xeus内核列表：
1. 构建路径 `dist_dir / "xeus" / "kernels.json"`
2. 检查文件是否存在；不存在时打印警告并返回
3. 使用 `json.load()` 读取kernels列表
4. 打印原始内核数量和ID列表
5. 列表推导过滤：`[k for k in kernels if k["kernel"] in KERNELS_TO_KEEP]`
6. 使用 `json.dump(filtered_kernels, f)` 写回文件
7. 打印保留的内核数量和ID列表

### 函数：`main() -> None`

CLI入口，与add_plausible.py结构相同：
1. argparse接受 `dist_dir` 参数
2. 目录存在性检查
3. 调用 `filter_kernels(dist_dir)`
4. 打印 "Done!"

## 构建管线调用顺序

在CI和RTD构建中，两个脚本按以下顺序执行：

```
pixi run build          → jupyter lite build (生成dist/)
pixi run filter-kernels → python scripts/filter_xeus_kernels.py dist
pixi run add-plausible  → python scripts/add_plausible.py dist
```

1. 先过滤内核（减少不必要的内核包）
2. 再注入分析代码（所有HTML页面统一添加）

## 相关信源

- [pyproject.toml 信源](pyproject-source.md)（pixi任务定义）
- [CI/CD工作流信源](ci-source.md)（build job步骤）
