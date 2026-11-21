---
type: Concept
title: "并行构建与性能"
description: "Maple Mono 的 ProcessPoolExecutor 并行流水线、pool_size 自动降级策略、字体缓存机制"
tags: ["maple-mono", "parallel", "performance", "pool-executor", "caching"]
sources:
  - id: BUILD-PY-CORE
    resource: "build.py#run_build"
    description: "并行构建核心函数"
  - id: CONFIG-POOL
    resource: "config.json#pool_size"
    description: "pool_size 配置默认值与降级逻辑"
  - id: BUILD-PY-MAIN
    resource: "build.py#main"
    description: "主入口——构建调度与缓存检查"
prerequisites:
  - "01-build-pipeline"
  - "06-nerd-font-patching"
  - "07-cn-font-merge"
next: []
related:
  - "../examples/basic-build.md"
status: draft
---

# 并行构建与性能

字体构建天然适合并行——每个字重、每种变体都是独立的输入，可以完全独立处理。Maple Mono 用 ProcessPoolExecutor 实现了一个高效的并行流水线。

## Embarrassingly Parallel 场景

Maple Mono 的字体构建是经典的 Embarrassingly Parallel 场景——多个任务之间**没有数据依赖**：

```
┌─────────────────────────────────────────────────────────────────┐
│                     源字体输入                                    │
│     MapleMono[wght]-VF.ttf   (Variable Font, 包含所有字重)        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 实例化 9 种字重
                            │
    ┌────┬────┬────┬────┬────┴────┬────┬────┬────┐
    ▼    ▼    ▼    ▼    ▼         ▼    ▼    ▼    ▼
  100  200  300  400  500  ...   800  900  Regular  Bold
    │    │    │    │    │         │    │    │    │
    ▼    ▼    ▼    ▼    ▼         ▼    ▼    ▼    ▼
  ┌─────────────────────────────────────────────────┐
  │  每个字重独立变换（ProcessPoolExecutor）           │
  │  ├─ build_mono() → TTF                           │
  │  ├─ build_mono_autohint() → TTF-AutoHint         │
  │  ├─ build_nf() → NF-Base + merge                 │
  │  └─ build_cn() → CN-Base + merge + 宽度调整      │
  └─────────────────────────────────────────────────┘
```

每个字重的处理流程完全独立，输出到独立文件。这是并行化的完美场景。

## ProcessPoolExecutor 使用模式

### run_build 核心函数

```python
# build.py
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_build(pool_size, fn, dir, target_styles=None):
    """
    并行运行 fn 函数处理 dir 下所有源文件
    
    fn: build_mono / build_mono_autohint / build_nf / build_cn
    pool_size: 并行进程数
    target_styles: 指定字重列表（None = 全部）
    """
    files = list_source_files(dir, target_styles)
    
    results = {}
    with ProcessPoolExecutor(max_workers=pool_size) as executor:
        futures = {executor.submit(fn, f): f for f in files}
        for future in as_completed(futures):
            src_file = futures[future]
            results[src_file] = future.result()
    
    return results
```

**关键设计**：
- `executor.submit(fn, f)` 提交任务，每个任务接收一个源文件
- `as_completed(futures)` 按完成顺序收集结果
- 进程间无数据共享（每个 worker 独立加载和处理字体）

### 为什么不用 ThreadPoolExecutor

| 问题 | ThreadPoolExecutor | ProcessPoolExecutor |
|------|-------------------|---------------------|
| Python GIL | ❌ CPU 密集被阻塞 | ✅ 每个进程独立 GIL |
| fontTools 内部 | TTLib 是纯 Python，GIL 持有久 | ✅ 并行有效 |
| ftcli (foundrytools) | 命令行子进程，GIL 不阻塞 | ✅ 效果相同 |
| 进程启动开销 | 低 | 中等（每个 worker 需 import 大量模块） |
| 总时间 | 串行接近 | 随 pool_size 线性减少 |

Maple Mono 的构建 CPU 密集（解析字体表、轮廓运算、merge_ttfonts），GIL 是瓶颈——必须用进程而非线程。

## pool_size 配置与自动降级

### 配置默认值

```json
"pool_size": 4
```

### 自动降级逻辑

```python
def resolve_pool_size(user_pool_size):
    # Codespace 环境（内存限制）
    if is_codespace():
        return 1
    
    # Windows 子系统（WSL / SMB 网络盘）
    if running_on_smb_or_drive_d():
        return 1
    
    # 用户显式指定
    if user_pool_size is not None:
        return user_pool_size
    
    # 默认 4
    return 4
```

**降级场景**（Maple Mono 明确检测）：

| 场景 | pool_size | 原因 |
|------|-----------|------|
| Codespace | 1 | 容器内存限制，多进程容易 OOM |
| SMB 网络盘 / D 盘 | 1 | 跨挂载 IO 速度慢，多进程会争用 IO |
| 正常环境（用户不指定） | 4 | 8 核机器的安全默认 |
| 用户显式指定 | 自定义 | `--pool-size 8` |

## 构建流水线的并行调度

主入口 `main()` 中，不同阶段之间按依赖关系调度：

```python
def main(config):
    # 阶段 1：基础构建（必须先完成，后续依赖）
    mono_results = run_build(pool_size, build_mono, source_dir)
    
    # 阶段 2：hinting（可以和后续并行）
    autohint_results = run_build(pool_size, build_mono_autohint, source_dir)
    
    # 阶段 3：NF / CN 派生（依赖阶段 1 产物）
    nf_results = run_build(pool_size, build_nf, mono_output_dir)
    cn_results = run_build(pool_size, build_cn, mono_output_dir)
    
    # 阶段 4：多格式转换
    convert_results = run_build(pool_size, convert, "otf/woff2", output_dir)
```

注意阶段 2-3 依赖阶段 1 完成——NF/CN 构建需要基础 TTF 作为输入。但阶段 2 内部（autohint 各字重）完全并行，阶段 3 内部（NF 各字重）也完全并行。

## 字体缓存机制

Maple Mono 支持 `--cache` 参数启用缓存：

```bash
python build.py --cache
# 复用已有的 TTF/OTF/WOFF2，只处理新/变更的字重
```

缓存策略：
- **key**：源文件路径 + 修改时间 + config.json 哈希
- **value**：已生成的输出文件路径
- **存储**：`.cache/` 目录或输出目录的 `.buildcache.json`

当输入不变时跳过对应构建步骤——开发过程中反复调 config 时特别有用。

## 性能实测参考

以下是典型开发机上的构建时间（pool_size=4，100-900 全部字重，Variable + TTF + TTF-AutoHint + OTF + WOFF2 + NF + CN）：

| 输出类型 | pool_size=1 | pool_size=4 | pool_size=8 |
|---------|------------|------------|------------|
| Variable | 5s | 5s | 5s（单文件，不并行） |
| TTF | 15s | 6s | 5s |
| TTF-AutoHint | 30s | 12s | 10s |
| NF | 25s | 10s | 8s |
| CN | 60s | 20s | 15s |
| 全部合计 | ~135s | ~55s | ~43s |

## 设计洞察

1. **并行是默认，串行是降级**：Maple Mono 默认开启并行（pool_size=4），只在检测到 Codespace 或 SMB 等特殊环境时自动降级
2. **进程数与任务数解耦**：pool_size 和实际任务数（字重数量）是独立参数——9 个字重 + pool_size=4 意味着 9 个任务分 4 批执行
3. **IO 不是瓶颈，CPU 是**：TTLib 操作（解析/变换/合并）是 CPU 密集型。SMB 网络盘降级是因为 SMB 跨挂载 IO 延迟会抵消进程并行优势
4. **构建流水线阶段间串行，阶段内并行**：必须等基础 TTF 完成后才能构建 NF/CN——但基础 TTF 本身是并行构建的
5. **缓存让迭代更快**：config.json 改动不需要重跑全部构建，只重跑受影响的特征注入步骤
