---
type: Concept
title: "并行构建与缓存"
description: "进程/线程/同步执行器的选择、可 pickle 的工作函数约束，以及 build-cache.json 的阶段身份与失败语义"
tags: ["parallel", "executor", "cache", "process-pool", "reproducibility"]
sources:
  - id: pipeline-cache
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/pipeline/README.md
    title: Cache lifecycle and executor boundaries
  - id: scripts-cache
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/README.md
    title: Cache contract
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 并行构建与缓存

## 1. 为什么需要并行

字体构建的耗时集中在三处：

- Fontmake 编译 Variable / TTF / OTF 三个分支；
- 对每个静态样式执行 AutoHint；
- 对每个 CJK 语种 × 配置档 × 样式执行实例化与合并。

这些任务彼此独立且多为 CPU 密集（轮廓运算、插值、子集化），适合进程级并行。v8 因此把执行器抽象为可替换组件，并让缓存按阶段粒度生效。

## 2. 执行器选择

```
pool_size <= 1  → SynchronousExecutor（顺序执行）
pool_size > 1   → create_process_executor(pool_size, fallback_to_threads=True)
```

- 代码默认 `pool_size` 为 1；存在 `CODESPACE_NAME` 时为 4；仓库 `config.json` 显式设为 4，因此常规构建是 4；
- 主流水线（`MapleBuildPipeline`）只按 `pool_size` 选择执行器，**不会**因为 CI 自动降为单进程；
- CJK 的 `create_font_executor()` 会在 `is_ci()` 为真时强制 `pool_size = 1`；
- 独立调用 `run_process_jobs()` 时，`pool_size <= 1` 直接顺序执行；
- 进程执行器创建失败时回退到线程，避免在不支持 `fork`/`spawn` 的环境直接崩溃。

## 3. 可 pickle 约束

进程执行器要求任务函数与任务数据类可在子进程重建，因此：

- 工作函数必须定义在**模块级**，不能是闭包或局部函数；
- 任务参数使用 frozen dataclass（如 `NerdFontBuildJob`、`NerdFontVariableBuildJob`）；
- 运行期上下文只传递必要字段，不传递打开的文件句柄或字体对象。

这条约束不是风格偏好：违反时会在运行期抛 pickle 错误，且往往只在多进程路径出现。

## 4. 并行边界

| 并行单元 | 说明 |
|----------|------|
| 基础格式分支 | Variable / TTF / OTF 从同一份已准备源并行编译 |
| AutoHint | 按静态样式分发 |
| Nerd Font | 静态 NF 任务按样式分发；变量 NF 任务独立 |
| CJK | 按 locale × profile × style 分发；静态与变量模式分别处理 |

临时工作区在 `finally` 中清理；领域异常继续向上传播，便于调用方与测试定位失败阶段。

## 5. 缓存的启用方式

缓存是**可选**的：

```sh
uv run build.py --cache
```

- 无 `--cache`：构建前清理生成的输出根目录与 WOFF2 目录；未请求 TTF 时在消费者完成后删除 `fonts/TTF/` 与 `fonts/TTF-AutoHint/`；
- 有 `--cache`：`prepare_output_root` 读取 `fonts/build-cache.json`，保留已有输出与无关目录，逐阶段校验后复用。

缓存文件只有一处：`fonts/build-cache.json`。CJK 基座缓存位于 `sources/cjk/`，两者独立。

## 6. 阶段命中条件

一个阶段被视为命中，必须同时满足：

1. 记录的**阶段身份**与当前身份一致；
2. 记录的**输出路径清单**与期望清单完全一致；
3. 每个输出文件存在；
4. 每个输出文件的**内容摘要**一致。

命中时日志输出 `Cache hit`；未命中输出 `Cache miss`。若缓存记录整体不可用，每个请求阶段会在各自日志段报告 `missing-cache-record`，而不是依赖一个全局“未命中”。

CJK 未命中时只移除该阶段自己的缓存记录，其他语种与配置档的记录和文件保持不变。

## 7. 阶段身份的组成

阶段身份包含：

- 相关解析配置；
- 目标样式；
- regular 与 italic Designspace 的维度字典；
- 生成特征文件的指纹；
- 上游阶段身份。

阶段身份**不包含**：

- 生成器源码（`scripts/` 下的 Python 代码）；
- 依赖版本（`pyproject.toml` / 锁文件）；
- UFO 轮廓内容；
- CJK 基座内容。

因此，修改上述任何未纳入身份的输入后，必须进行一次**不带 `--cache`** 的构建，否则可能得到“命中但已过期”的结果。

## 8. 失败语义

- `build-config.json` 在构建开始前写入，成功结束时重写；
- `build-cache.json` 只在完整流水线成功后由 `write_build_record()` 写入；
- 若编译或后续阶段失败，可能留下“新配置 + 旧缓存/部分失效/无缓存”的组合；
- 失败构建不会被标记为完成缓存，下一次构建会重新判定。

## 9. 实践建议

| 场景 | 建议 |
|------|------|
| 只改 `config.json` | 可继续用 `--cache`，相关阶段身份会变化 |
| 改 `scripts/feature/` 或生成器 | 必须去掉 `--cache` |
| 升级依赖 | 必须去掉 `--cache` |
| 改 UFO / Designspace 轮廓 | 必须去掉 `--cache`（维度字典未变时不会触发失配） |
| 只改 CJK 基座内容 | 主流水线缓存不会感知，需重建相关 CJK 阶段 |
| CI 环境 | 主流水线仍按 `pool_size` 并行；CJK 阶段会强制单进程 |

## 10. 相关文档

- 流水线阶段顺序：[构建流水线](01-build-pipeline.md)
- CJK 独立缓存与回退：[CJK 字体合并](07-cjk-font-merge.md)
- 配置字段：[配置系统](02-config-system.md)
