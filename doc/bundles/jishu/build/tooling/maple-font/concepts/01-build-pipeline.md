---
type: Concept
title: "构建流水线"
description: "main() 如何解析配置、派生 BuildPlan，并按阶段执行基础编译、派生输出、Nerd Font 与 CJK 集成"
tags: ["pipeline", "build-plan", "fontmake", "orchestrator"]
sources:
  - id: pipeline-readme
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/pipeline/README.md
    title: Maple Build Pipeline
  - id: scripts-readme
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/README.md
    title: Maple Mono Build System
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 构建流水线

## 1. 三个状态对象

v8 把“用户想要什么”“本次要做什么”“在哪里做”拆成三个对象，避免阶段函数各自解释配置。

| 对象 | 归属 | 职责 |
|------|------|------|
| `ResolvedConfig` | `config/` | 归一化后的用户意图：格式、样式、特征、Nerd Font、CJK 选择、缓存、输出设置 |
| `BuildRuntimeContext` | `config/runtime.py` | 文件系统路径、垂直度量、GitHub 镜像、FontForge 路径与可变的“上游已产出”标志 |
| `BuildPlan` | `pipeline/orchestrator.py` | 一次性派生：目标样式、必需基础格式、WOFF2、Nerd Font、CJK 模式、清理与归档策略 |

`BuildPlan` 只在正常构建时创建一次；`--dry` 在它之前就返回。

## 2. 入口与 dry-run

```python
def main(args: list[str] | None = None, version: str | None = None) -> None:
    parsed_args = parse_args(args, version=resolved_version)
    resolver = BuildConfigResolver(version_tag=resolved_version)
    font_config = resolver.resolve(parsed_args)
    runtime_context = BuildRuntimeContext.from_config(font_config)
    if parsed_args.dry:
        # 本地输出带标签的 resolved_config / runtime_context 两段 JSON
        # CI 只输出 resolved_config JSON，便于直接解析
        return
    MapleBuildPipeline(font_config, runtime_context).build()
```

- **本地 dry-run**：stdout 输出 `resolved_config` 与 `runtime_context` 两个带标签的 JSON 对象，警告写入 stderr。
- **CI dry-run**：stdout 只输出 `resolved_config` JSON，不含标签。
- `--dry` 不创建 `BuildPlan`，也不创建任何输出目录。

## 3. 正常调用顺序

```
build.py
  └─ scripts.pipeline.main()
       ├─ parse_args / BuildConfigResolver.resolve
       ├─ BuildRuntimeContext.from_config
       ├─ BuildPlan.from_config
       ├─ MapleBuildPipeline.build()
       │    ├─ prepare_output_root()          # 无 --cache 时清理输出根目录
       │    ├─ write_build_config()           # 开始前写 fonts/build-config.json
       │    ├─ _build_base_outputs()
       │    │    ├─ prepare_fontmake_sources # Designspace/UFO + 度量 + 特征 + 冻结
       │    │    ├─ compile_fontmake_formats # Variable / TTF / OTF 分支
       │    │    └─ 基础后处理：命名、别名、宽度校验
       │    ├─ _build_derived_outputs()
       │    │    ├─ AutoHint → fonts/TTF-AutoHint/
       │    │    └─ WOFF2    → fonts/Woff2/
       │    ├─ Nerd Font 阶段 → fonts/NF/ 或 NFMono / NFPropo
       │    ├─ CJK 阶段 → fonts/<LOCALE>/ 与 NF / Variable 变体
       │    ├─ 清理未请求的 TTF / TTF-AutoHint
       │    ├─ finish_build()：重写 build-config.json、写 build-cache.json
       │    └─ archive_outputs()：仅在 --archive 时执行
       └─ 异常：BuildDependencyError → 记录日志并以退出码 1 结束
```

整个正常流水线共享一个执行器，用于源准备、编译、后处理与派生阶段。`fonts/temp/` 下的 Fontmake 临时工作在基础阶段结束后清理，失败路径同样通过 `finally` 清理。

## 4. BuildPlan 的决策规则

| 决策 | 规则 |
|------|------|
| 目标样式 | `--least-styles` → Regular/Bold/Italic/BoldItalic；`--debug` → Regular/Italic；否则全部 |
| 基础格式 | Variable 恒需；请求 TTF/WOFF2 或需要 hinted/NF 静态基座时加 TTF；请求 OTF 且非 debug 时加 OTF |
| WOFF2 | 仅在请求且非 debug 时构建，输入为 `fonts/TTF/` 静态 TTF |
| Nerd Font | `nerd_font.enable` 为真时构建；debug 解析会关闭 |
| CJK 模式 | 未选择任何 locale 时为 `None`，否则取 `static` 或 `variable` |
| CJK 配置档 | NF 可用且 `with_nerd_font` 为真时选 NF；NF 不可用或 `cjk-both` 时增加普通档 |
| 清理 | 未请求 TTF 时，等所有消费者完成后删除 `fonts/TTF/` 与 `fonts/TTF-AutoHint/` |
| 归档 | 仅由解析后的 archive 标志控制，处理归档时刻已存在的所有非 JSON 输出目录 |

## 5. 基础阶段（`pipeline/fontmake.py`）

1. **源准备**：加载已提交的 regular/italic Designspace 与 UFO，应用构建度量与特征配置，把启用的单一替换冻结到每个 master，最后物化到一次性工作区。
2. **分支编译**：从同一份已准备源并行提交 Variable、TTF、OTF 三个 Fontmake 分支。
3. **基础后处理**：处理元数据、命名、Unicode 别名与宽度校验，然后发布到 `fonts/Variable/`、`fonts/TTF/`、`fonts/OTF/`。

工作函数与任务数据类都保持模块级定义，以便进程执行器可以 pickle。

## 6. 派生阶段（`pipeline/base_fonts.py`）

| 阶段 | 输入 | 输出 | 缓存特性 |
|------|------|------|----------|
| AutoHint | `fonts/TTF/` | `fonts/TTF-AutoHint/` | 独立阶段身份，可单独复用 |
| WOFF2 | `fonts/TTF/` | `fonts/Woff2/` | 独立阶段身份，可单独复用 |

两者都消费“已发布”的静态 TTF，因此调整其中一个不会触发无关基础格式重编译。

## 7. Nerd Font 与 CJK 阶段

- **Nerd Font**：由 `pipeline/nerd_fonts.py` 调用 `font_ops/nerd_font.py`，默认以预构建基座合并，必要时回退到 FontForge 修补器；详见 [Nerd Font 补丁](06-nerd-font-patching.md)。
- **CJK**：由 `pipeline/cjk_outputs.py` 与 `cjk/` 共同完成，阶段名形如 `cn-static`、`nf-cn-static`、`cn-variable`、`nf-cn-variable`；静态输出写入 `fonts/<LOCALE>/` 或 `fonts/NF-<LOCALE>/` 等目录。详见 [CJK 字体合并](07-cjk-font-merge.md)。

## 8. 失败语义

- 阶段异常会向上传播，调用方与测试可据此识别失败阶段；
- 只有 `BuildDependencyError` 会被 `main()` 转成日志 + 退出码 1；
- `build-config.json` 在构建开始前写入，成功结束时重写；
- `build-cache.json` 只在完整流水线成功后写入；失败构建可能留下“新配置 + 旧缓存/无缓存”的组合，但不会被伪装成已完成缓存。

## 9. 相关文档

- 配置如何归一化：[配置系统](02-config-system.md)
- 阶段身份与并行执行：[并行构建与缓存](08-parallel-build.md)
- 入口函数签名：[构建入口参考](../references/build-entrypoint.md)
