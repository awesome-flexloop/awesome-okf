---
type: Concept
title: "构建流水线"
description: "Maple Mono 四阶段构建流水线——源字体加载→配置解析→并行构建→OpenType Feature 注入与冻结"
tags: ["maple-mono", "pipeline", "build", "architecture"]
sources:
  - id: BUILD-PY
    resource: "build.py"
    description: "主构建脚本——FontConfig/BuildOption 类与 build_mono/build_nf/build_cn 函数"
  - id: TASK-PY
    resource: "task.py"
    description: "开发辅助子命令入口"
prerequisites:
  - "00-introduction"
next:
  - "02-config-system"
related:
  - "../references/build-entrypoint.md"
  - "../examples/basic-build.md"
status: draft
---

# 构建流水线

Maple Mono 将源字体变换为多格式输出，经历一个**四阶段流水线**。理解这个流水线是理解整个构建系统的基础。

## 流水线全景

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         源字体输入（source/）                            │
│   MapleMono[wght]-VF.ttf   MapleMono-Italic[wght]-VF.ttf                │
│   MapleMono-NF-Base.ttf    MapleMono-NF-Base-Mono/Propo.ttf            │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │ 阶段1: 配置解析 │ config.json → FontConfig → CLI 覆写
                    │ FontConfig     │ 层合并 → BuildOption 路径规划
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ 阶段2: 基础构建 │ run_build(PoolExecutor)
                    │ 并行多格式      │ TTF → 修正 → 去 hint → 变换宽度
                    │                │ TTF → AutoHint → 提示优化
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ 阶段3: 派生构建 │ build_nf() → NF 版（merge_ttfonts）
                    │                │ build_cn() → CN 版（merge_ttfonts + 宽度调整）
                    │                │ convert TTF → OTF / WOFF2
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ 阶段4: Feature  │ patch_font_feature()
                    │ 注入与冻结     │ freeze_feature_static()
                    └───────┬───────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   多格式输出（fonts/）                                    │
│  Variable/ · TTF/ · TTF-AutoHint/ · OTF/ · Woff2/ · NF/ · NF-Mono/      │
│  NF-CN/ · NF-Mono-CN/ · NF-Propo/CN 等                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 各阶段详解

### 阶段 1：配置解析（FontConfig）

入口：`build.py` 的 `parse_args()` + `FontConfig.__init__()`

构建系统的第一件事是**合并两层配置**：

1. **config.json**（声明式配置）：默认值、版本化、可共享
2. **CLI 参数**（运行时覆盖）：快速实验、CI 流水线

```python
class FontConfig:
    def __init__(self, args, version=None):
        self.__load_config()     # 先读 config.json
        self.__load_args(args)   # 再覆写 CLI 参数
        self._update_family_names()
```

合并顺序固定：Config 默认 → CLI 参数覆写。最终生成 `BuildOption` 对象，规划输出目录结构。

> 详见 [02-配置系统](02-config-system.md)。

### 阶段 2：基础构建（run_build）

入口：`build.py` 的 `run_build()` 函数。

这是流水线中**计算最密集**的阶段——将源字体实例化为多字重 TTF 格式，同时修正字形质量问题：

```python
def run_build(pool_size, fn, dir, target_styles=None):
    with ProcessPoolExecutor(max_workers=pool_size) as executor:
        futures = {executor.submit(fn, f): f for f in files}
```

每个基础 TTF 经过以下变换（`build_mono()`）：
1. `ftcli fix italic-angle` — 修正斜体角度
2. `ftcli fix monospace` — 等宽验证与修正
3. `ftcli name strip-names` — 清理冗余 name 表
4. `ftcli font correct-contours` — 轮廓修正
5. `ftcli ttf dehint` — 去 hint（unhinted 版）
6. `ftcli fix transformed-components` — 组件变换修正

然后并行运行 `build_mono_autohint()` 生成 hinted 版（低分辨率屏幕优化）。

### 阶段 3：派生构建（NF + CN + 多格式）

基础 TTF 就绪后，并行构建三种派生：

**Nerd Font 版**（`build_nf()`）：
- 默认路径：预构建 `MapleMono-NF-Base.ttf` → `merge_ttfonts(base, extra)` 合并
- 自定义路径：`font-patcher` 运行时修补（需 FontForge）

**中文版**（`build_cn()`）：
- 下载预构建 CN 基字体（`cn-base-static.zip`，含 SHA256 校验）
- `merge_ttfonts(base, cn_base)` 合并
- 调整中文字形宽度（默认 2× 拉丁宽）
- 可选择 `cn.narrow` 或 `cn.scale_factor` 定制

**多格式输出**：
- TTF → OTF：`ftcli converter ttf2otf` + CFF 轮廓优化
- TTF → WOFF2：`ftcli converter ft2wf`

### 阶段 4：Feature 注入与冻结

入口：`FontConfig.patch_font_feature()` + `freeze.py` 的 `freeze_feature()`

这是**逻辑最复杂**的阶段——将 Python 生成的 OpenType Feature 规则注入到字体表中，并根据配置决定是否冻结：

```python
def patch_font_feature(self, font, ...):
    fea_str = generate_fea_string(
        is_italic=..., is_cn=..., is_calt=...,
        enable_infinite=..., remove_italic_calt=...
    )
    addOpenTypeFeaturesFromString(font, fea_str)  # 注入规则
    self.freeze_feature_static(font, is_variable)  # 冻结（仅静态）
```

- **变量字体**：特征规则移入 `calt` 查找表（动态切换）
- **静态字体**：`freeze_feature()` 根据 `feature_freeze` 配置将规则固化到字形表

> 详见 [05-特征冻结机制](05-freeze-mechanism.md)。

## 辅助流水线（task.py）

除主构建流水线外，`task.py` 提供开发辅助子命令：

```bash
python task.py nf            # 更新 Nerd Font 基座（版本检测 + 下载）
python task.py fea           # 重新生成 .fea 文件（用于 font-patcher 模式）
python task.py page          # 同步 Playground Web 前端数据
python task.py cn --pull     # 拉取中文基字体源码
python task.py cn --rebuild  # 从变量字体重新实例化 CN 基字体
python task.py release minor # 版本号递增 + 发布
python task.py publish       # 上传归档到 GitHub Release
python task.py merge         # 运行 merge_font 工具合并字体
```

## 关键设计洞察

1. **配置驱动流水线**：四个阶段由 FontConfig 控制行为，同一套代码根据配置产出不同字体
2. **优先预构建、按需动态**：NF 版默认用预构建基座（快），只有需要自定义时才回退 font-patcher（慢但灵活）
3. **并行化是一级公民**：从基础构建到派生构建，所有可独立处理的字体都通过 ProcessPoolExecutor 并行
4. **Feature 系统后置**：先构建好字形再注入 OpenType 规则，避免规则干扰字体变换
