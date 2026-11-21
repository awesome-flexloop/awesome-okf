---
type: Concept
title: "Nerd Font 补丁策略"
description: "Maple Mono 预构建 NF Base 字体 vs font-patcher 运行时修补的权衡决策与三种输出模式"
tags: ["maple-mono", "nerd-font", "font-patcher", "icons", "terminal"]
sources:
  - id: BUILD-PY-NF
    resource: "build.py#build_nf"
    description: "build_nf 函数——NF 构建的两条路径"
  - id: CONFIG-NF
    resource: "config.json#nerd_font"
    description: "nerd_font 配置段"
  - id: TASK-PY-NF
    resource: "task.py#nerdfont"
    description: "NF 基座更新子命令"
prerequisites:
  - "01-build-pipeline"
  - "02-config-system"
next:
  - "07-cn-font-merge"
related:
  - "../examples/nerd-font-build.md"
status: draft
---

# Nerd Font 补丁策略

Nerd Font 是将 [Font Awesome](https://fontawesome.com/)、[Devicons](https://devicon.dev/)、[Octicons](https://primer.style/octicons/) 等图标字体合并到编程字体的工具链。Maple Mono 将 Nerd Font 作为**一等公民**支持——构建时直接产出带图标的版本。

## 三条路径的决策树

Maple Mono 的 Nerd Font 构建有三条路径，由 `config.json` 的 `nerd_font` 配置段和 CLI 参数共同决定：

```
                         nerdfont.enable=true?
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
                   否                      是
                    │                       │
              跳过 NF 构建          nerdfont.use_font_patcher=true?
                                            │
                                ┌───────────┴───────────┐
                                ▼                       ▼
                               否                      是
                                │                       │
                   ┌────────────┴─────┐        ┌────────┴────────┐
                   ▼                  ▼        ▼                 ▼
              预构建基座路径      自定义 glyph   font-patcher 路径  FontForge 依赖
           merge_ttfonts 合并   列表差异检测   运行时修补           最慢
```

### 路径 1：预构建基座（默认，最快）

```python
# build.py build_nf()
def build_nf(...):
    nf_base = find_nf_base_font()  # MapleMono-NF-Base.ttf
    nf_extra = find_nf_extra()     # MapleMono-NF-Ext.ttf（如果有）
    # merge_ttfonts 合并到基础 TTF
    merge_ttfonts(base_font, nf_base, nf_extra)
```

**来源**：Maple Mono 仓库维护了一个定期更新的 `MapleMono-NF-Base.ttf`——包含所有需要的图标字形，提前用 font-patcher 修补好。构建时直接 merge。

**优点**：
- **快**：不调用 FontForge，纯 fontTools 表合并
- **可预测**：输出始终一致
- **无外部依赖**：不需要 FontForge 安装

**缺点**：
- 图标版本跟随 Maple Mono 版本（不是最新 Nerd Font release）
- 无法自定义图标子集

### 路径 2：font-patcher 运行时（自定义场景）

```python
def build_nf_font_patcher(...):
    import subprocess
    subprocess.run([
        "font-patcher", base_font,
        "--glyphs", "complete",
        "--output", output_path,
        "--fontawesome", "--devicons",
        # ... extra args
    ])
```

**触发条件**：`nerd_font.use_font_patcher=true` 或 `python task.py nf` 发现本地 NF Base 与期望版本不匹配。

**优点**：
- 图标永远是最新 Nerd Font release
- 支持 `--glyphs` 自定义子集（如只装 Octicons）
- 支持 `--extra-args` 传递 font-patcher 原生参数

**缺点**：
- **慢**：FontForge 加载 + 修补一个字体通常需要 30-60 秒
- **依赖 FontForge**：需要系统级别安装
- **可能失败**：font-patcher 有边缘情况 bug

### 路径 3：自动切换

Maple Mono 在 `task.py nf` 中实现版本检测：

```python
# 伪代码
def check_nf_base_version():
    local_base_version = read_base_nf_version()
    expected_version = nerd_font_version_from_config()
    if local_base_version != expected_version:
        # 下载新的 NF Base 或重新修补
        download_or_repatch()
```

## 三种输出模式

Nerd Font 图标有三种宽度策略，由 `nerd_font.mono` / `nerd_font.propo` 控制：

| 模式 | 效果 | 默认 |
|------|------|------|
| **默认**（mono=false, propo=false） | 图标自适应等宽格子 | ✅ |
| **Mono**（mono=true） | 所有图标固定一个等宽格子 | 终端更整齐 |
| **Propo**（propo=true，覆盖 mono） | 图标按自然宽度显示 | 视觉更自然但可能导致终端错位 |

CLI 对应：`--nf-mono` / `--nf-propo`

## merge_ttfonts 合并机制

无论是预构建基座路径还是 font-patcher 路径，最终都需要把图标字形合并到基础字体。这个操作由 `merge_ttfonts()` 完成：

```
┌──────────────────┐   ┌──────────────────┐
│  基础 TTF        │   │  Nerd Font 基座   │
│  Maple Mono      │   │  Nerd Font Icons │
│  等宽拉丁 + 中英  │   │  纯图标字形       │
└────────┬─────────┘   └────────┬─────────┘
         │                       │
         ▼                       ▼
    ┌───────────────────────────────────────┐
    │         merge_ttfonts()                │
    │  ┌─────────────────────────────────┐  │
    │  │  遍历 GSUB 表中所有 sub 规则      │  │
    │  │  按 glyph id 或 name 去重合并    │  │
    │  │  合并 name / head / OS / hmtx    │  │
    │  └─────────────────────────────────┘  │
    └───────────────────────────────────────┘
                         │
                         ▼
              带图标的 Maple Mono NF 版
```

合并的关键是**避免字形 ID 冲突**：两个字体可能有相同 glyph id 但不同字形。`merge_ttfonts` 先检查 glyph name，按名称匹配合并，重命名冲突项。

## NF-CN 双重补丁

当中文版同时需要 Nerd Font 图标时，构建顺序是：

```
源字体 → build_mono() → merge NF Base → merge CN Base → adjust CN width → 输出
```

配置：

```json
"nerd_font": {"enable": true},
"cn": {"enable": true, "with_nerd_font": true}
```

产物：`MapleMono-NF-CN[wght].ttf`（同时带图标和中日韩字形）。

## 设计洞察

1. **预构建 vs 动态生成的经典权衡**：预构建快但不灵活，动态生成灵活但慢。Maple Mono 的答案是"默认快，需要灵活时才慢"
2. **版本一致性**：预构建基座的版本与 Maple Mono 主版本绑定，用 `task.py nf` 自动检查更新——避免图标版本漂移
3. **合并顺序敏感**：先 NF 再 CN（或反过来？）会影响最终字形的宽度和定位。Maple Mono 通过 merge_ttfonts 的实现处理这个问题
4. **font-patcher 是"最后选择"**：不是首选方案，但始终存在作为兜底——当预构建基座不可用或需要高度定制时，font-patcher 保证功能可用
