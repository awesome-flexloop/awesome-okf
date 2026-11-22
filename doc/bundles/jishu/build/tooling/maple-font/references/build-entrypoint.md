---
type: Reference
title: "构建入口参考"
description: "build.py / task.py 的入口函数、参数解析、解析器、BuildPlan 与 MapleBuildPipeline 的公开接口"
tags: ["api", "entrypoint", "cli", "task", "pipeline"]
sources:
  - id: build-py
    resource: https://github.com/subframe7536/maple-font/blob/variable/build.py
    title: build.py
  - id: orchestrator
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/pipeline/orchestrator.py
    title: scripts/pipeline/orchestrator.py
  - id: task-init
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/task/__init__.py
    title: scripts/task/__init__.py
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 构建入口参考

## 1. build.py

```python
#!/usr/bin/env python3
from scripts.pipeline import main

if __name__ == "__main__":
    main()
```

`build.py` 本身不含逻辑，便于以脚本方式运行，也便于测试直接导入 `main`。

## 2. `main()`

```python
# scripts/pipeline/orchestrator.py
def main(args: list[str] | None = None, version: str | None = None) -> None: ...
```

执行顺序：

1. `version = version or version_tag()`；
2. `parsed_args = parse_args(args, version=resolved_version)`；
3. `--debug` 且未显式设置日志环境变量时，把日志级别设为 `DEBUG`；
4. `BuildConfigResolver(version_tag=...).resolve(parsed_args)` → `ResolvedConfig`；
5. `BuildRuntimeContext.from_config(font_config)`；
6. 若 `--dry`：打印后返回（本地两段 JSON，CI 仅配置 JSON）；
7. `MapleBuildPipeline(font_config, runtime_context).build()`；
8. `BuildDependencyError` → `logger.error` + `SystemExit(1)`；
9. `finally` 中恢复临时设置的日志环境变量。

## 3. `parse_args()`

```python
# scripts/config/cli.py
def build_parser(version: str | None = None) -> argparse.ArgumentParser: ...
def parse_args(args: list[str] | None = None, version: str | None = None) -> argparse.Namespace: ...
```

参数按五组注册：

| 组 | 参数 |
|----|------|
| 通用 | `-v/--version`、`-d/--dry`、`--debug` |
| 特征 | `-n/--normal`、`--standard-zero`、`--legacy-thin-weight-class`、`--feat`、`--apply-fea-file`、`--hinted/--no-hinted`、`--liga/--no-liga`、`--infinite-arrow/--no-infinite-arrow`、`--remove-tag-liga`、`--line-height`、`--width` |
| 构建 | `--format`、`--least-styles`、`--cache`、`--archive` |
| Nerd Font | `--nf/--no-nf`、`--nf-mono`、`--nf-propo`、`--nf-variable`、`--font-patcher` |
| CJK | `--cjk`、`--cjk-variable`、`--cjk-narrow`、`--cjk-scale-factor`、`--cjk-both`、`--cjk-hinted/--no-cjk-hinted` |

弃用组：`--cn`、`--no-cn`、`--cn-narrow`、`--cn-scale-factor`、`--cn-both`。

`--format` 接受逗号分隔的 `ttf,otf,woff2`；Variable 不受该参数影响，始终构建。

## 4. `BuildConfigResolver`

```python
# scripts/config/resolver.py
class BuildConfigResolver:
    def __init__(self, project_root: str | Path = ".", version_tag: str = "v7.9"): ...
    def load_defaults(self) -> ResolvedConfig: ...
    def resolve(self, args) -> ResolvedConfig: ...
    def resolve_project_config(self) -> ResolvedConfig: ...
```

- `resolve(args)`：默认值 → JSON → 弃用 CLI → CLI → identity 派生；
- `resolve_project_config()`：只解析项目配置，不读 CLI；
- `load_defaults()`：返回代码默认模型，便于测试或比较。

## 5. `BuildRuntimeContext`

```python
# scripts/config/runtime.py
@dataclass(slots=True)
class BuildRuntimeContext:
    src_dir: str
    output_root: str
    output_otf: str
    output_ttf: str
    output_ttf_hinted: str
    output_variable: str
    output_woff2: str
    output_nf: str
    ttf_base_dir: str
    is_nf_built: bool
    is_cjk_built: bool
    effective_github_mirror: str
    font_forge_bin: str | None
    resolved_vertical_metric: tuple[int, int]

    @classmethod
    def from_config(cls, config: ResolvedConfig) -> BuildRuntimeContext: ...
    @property
    def output_nf_variable(self) -> str: ...
    def feature_file_path(self, is_italic: bool, is_cjk: bool = False) -> str: ...
    def to_dict(self, config: ResolvedConfig | None = None) -> dict[str, Any]: ...
```

`is_nf_built` 与 `is_cjk_built` 是可变标志，由流水线在对应阶段完成后设置，供后续阶段判断依赖是否满足。

## 6. `BuildPlan`

```python
# scripts/pipeline/orchestrator.py
@dataclass
class BuildPlan:
    target_styles: list[str] | None
    required_base_formats: tuple[Literal["variable", "ttf", "otf"], ...]
    build_woff2: bool
    build_nerd_font: bool
    build_nerd_font_variable: bool
    cjk_mode: Literal["variable", "static"] | None
    cleanup_base_static: bool
    archive: bool

    @classmethod
    def from_config(cls, config: ResolvedConfig) -> BuildPlan: ...
```

`from_config` 的派生规则见 [构建流水线](../concepts/01-build-pipeline.md)。

## 7. `MapleBuildPipeline`

```python
class MapleBuildPipeline:
    def __init__(self, font_config: ResolvedConfig, runtime_context: BuildRuntimeContext): ...
    def build(self) -> None: ...
```

主要内部方法（不保证跨版本稳定）：

| 方法 | 作用 |
|------|------|
| `prepare_output_root()` | 无缓存时清理输出根目录 |
| `_build_base_outputs()` | 源准备、Fontmake 编译、基础后处理 |
| `_build_derived_outputs()` | AutoHint 与 WOFF2 |
| `_build_cjk_outputs(executor)` | CJK 阶段 |
| `write_build_config()` | 开始前写 `fonts/build-config.json` |
| `write_build_record()` | 成功后写缓存 |
| `archive_outputs()` | `--archive` 归档 |
| `finish_build()` | 收尾：重写配置、写缓存 |

## 8. task.py

```python
# task.py
from scripts.task import main

if __name__ == "__main__":
    main()
```

```python
# scripts/task/__init__.py
def build_parser() -> argparse.ArgumentParser: ...
def main() -> None: ...
```

注册模块与子命令：

| 子命令 | 入口模块 | 用途 |
|--------|----------|------|
| `nf` | `task/nf.py` | 更新 Nerd Font 版本、下载修补器、重建三份基座 |
| `fea` | `task/fea.py` | 重新生成 `.fea`、特性文档、schema 与浏览器规则 |
| `designspace` | `task/designspace.py` | 由 `.glyphs` 导出 Designspace/UFO |
| `release` | `task/release.py` | 版本号、构建、标签与推送 |
| `cjk` | `task/cjk.py` | 重建 CJK 变量/静态基座 |
| `googlefonts` | `task/googlefonts.py` | Google Fonts 相关流程 |
| `publish` | `task/publish.py` | 发布归档、manifest 与上架 |

`main()` 在没有子命令时打印帮助；有子命令时配置日志、记录任务名并调用对应 `run(args)`。

## 9. 退出码与异常

| 情况 | 行为 |
|------|------|
| 正常完成 | 退出码 0 |
| `BuildDependencyError` | 记录错误，退出码 1 |
| 其他异常 | 向上传播（便于测试捕获） |
| `--dry` | 打印后正常返回 |

## 10. 相关文档

- 配置模型字段：[ResolvedConfig 参考](resolved-config.md)
- 阶段与缓存语义：[并行构建与缓存](../concepts/08-parallel-build.md)
