---
type: Concept
title: "中英文字体合并"
description: "Maple Mono 如何通过 Resource Han Rounded 基字体下载 + merge_ttfonts 合并 + 2:1 宽度对齐得到中日韩完整支持"
tags: ["maple-mono", "cjk", "chinese", "font-merge", "resource-han"]
sources:
  - id: BUILD-PY-CN
    resource: "build.py#build_cn"
    description: "build_cn 函数——中文基字体下载、合并与宽度调整"
  - id: CONFIG-CN
    resource: "config.json#cn"
    description: "cn 配置段"
  - id: TASK-PY-CN
    resource: "task.py#cn"
    description: "cn 子命令——拉取与重建中文基字体"
  - id: CN-README
    resource: "source/cn/README.md"
    description: "中文基字体说明与版本更新流程"
prerequisites:
  - "01-build-pipeline"
  - "06-nerd-font-patching"
next:
  - "08-parallel-build"
related:
  - "../examples/cn-font-build.md"
status: draft
---

# 中英文字体合并

Maple Mono 的中文版（CN 版）不重绘中文字形——这是一个**关键的工程决策**。原因很简单：完整的中日韩字形集（约 28000+ 字形）绘制工作量远超拉丁字母集（约 800 字形）。

Maple Mono 采用的方案是**组件化组合**：基础等宽拉丁字体 + 外挂中文基字体。

## 整体策略

```
┌──────────────────┐   ┌──────────────────────┐
│  Maple Mono Base │   │  Resource Han Rounded │
│  等宽拉丁 + 标点   │   │  中日韩全量字形         │
│  (800+ glyphs)   │   │  (28000+ glyphs)      │
└────────┬─────────┘   └────────┬─────────────┘
         │                       │
         ▼                       ▼
    ┌──────────────────────────────────────────┐
    │  下载 + 校验                              │
    │  Resource Han Rounded 预构建静态包        │
    │  含 SHA256 哈希校验                       │
    └────────────────────┬─────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────┐
    │  merge_ttfonts() 合并                     │
    │  拉丁等宽网格 + 中文 2:1 对齐              │
    └────────────────────┬─────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────┐
    │  宽度调整                                  │
    │  默认中文宽度 = 2 × 拉丁宽度               │
    │  可通过 narrow / scale_factor 调整         │
    └──────────────────────────────────────────┘
                         │
                         ▼
              MapleMono-NF-CN[wght].ttf
```

## 中文基字体选择

Maple Mono 选择的中文基字体是 **Resource Han Rounded**（思源黑体圆角版）：

| 对比项 | Resource Han Rounded | 思源黑体（Noto Sans CJK） | 霞鹜文楷等 |
|--------|---------------------|--------------------------|-----------|
| 风格 | 圆角现代 | 直角中性 | 手写/传统 |
| 等宽适配 | ✅ 有开源等宽版本 | ❌ 非等宽 | ❌ 非等宽 |
| Open Font License | ✅ | ✅ | ✅ |
| 中文字数 | 28000+ | 28000+ | 约 12000 |
| 构建复杂度 | 中等 | 高 | 低 |

选择 Resource Han Rounded 的核心理由：**圆角风格与 Maple Mono 设计语言一致**（@$%等字形都是圆角）。

## 两种中文基字体来源

Maple Mono 提供两种中文基字体来源，通过 `cn.use_static_base_font` 切换：

### 静态基字体（默认）

从 GitHub Release 下载预构建好的静态 TTF 包（约 40MB）：

```bash
python build.py --cn
# 自动下载 cn-base-static.zip → 解压到 source/cn/ → SHA256 校验 → 合并
```

版本锁定：`source/cn/static.sha256` 记录了当前版本的哈希值，构建时校验防止损坏或版本漂移。

**优点**：
- 快（直接用，不需要重新构建）
- 稳定（版本锁定，可复现）
- 无外部依赖（不需要 RoboFont / Glyphs）

**缺点**：
- 图标数量随基字体固定（约 28000）
- 字体风格跟随 Resource Han Rounded（不可自定义）

### 从变量字体重建

通过 `task.py cn --rebuild` 从 Resource Han Rounded Variable Font 实例化：

```bash
python task.py cn --pull       # 拉取最新变量字体
python task.py cn --rebuild    # 实例化出各字重
```

**触发条件**：需要最新版 Resource Han Rounded，或需要微调某些字重的表现。

## 2:1 宽度对齐

这是中文等宽字体的经典问题。ASCII 字符在等宽字体中是 1 cell 宽，但中文字形默认宽度通常是 2 cell（更宽）。Maple Mono 的处理：

```
┌──────────┬──────────┐
│ 拉丁 1 cell 宽  │ 中文 2 cell 宽 │
└──────────┴──────────┘
┌──────────┬──────────┐
│ abc123好的世界│ 等宽显示        │
└──────────┴──────────┘
```

**默认行为**：中文字形宽度 = 2 × 拉丁字形宽度，保持 2:1 对齐。

### narrow 模式

```json
"cn": {"narrow": true}
```

中文字形宽度压缩为 1.5 × 拉丁宽度——视觉更紧凑，但不再严格等宽：

```
┌──────────┬──────────┬──────────┐
│ 拉丁 1 cell │ 窄中文 1.5 cell │ 不再严格等宽 │
└──────────┴──────────┴──────────┘
```

**风险提示**（Maple Mono config.json 中明确标注）：narrow 模式产生的字体**不是严格等宽字体**。IntelliJ IDEA 等应用可能渲染异常。

### scale_factor 模式

```json
"cn": {"scale_factor": [1.2, 1.1]}
```

分别控制宽度和高度缩放——精细调整中文字形与拉丁字形的视觉匹配度。

## merge_ttfonts 的特殊处理

中英合并比 NF 合并更复杂，因为中文字形数是拉丁的 35 倍：

```python
# 伪代码
def merge_cn(base_font, cn_base):
    # 1. 检查 glyph id 空间
    #    中文基字体的 glyph id 可能从 0 开始，与 base 冲突
    #    需要重新编号
    
    # 2. 查找冲突字形
    #    base 和 cn_base 可能有相同的 ASCII 字形
    #    统一用 base 的拉丁字形（Maple Mono 有更好的设计）
    #    cn_base 只贡献中文字形
    
    # 3. 宽度调整
    #    中文字形 hmtx.width = base_em_width * (scale_factor[0] * 2)
    
    # 4. OS/2 表更新
    #    usWinAscent / usWinDescent / sTypoAscender / sTypoDescender
    #    取两者中较大的值，保证行高正确
```

## 构建时间影响

由于中文字形数量巨大，CN 版构建时间明显更长：

```
基础 TTF（拉丁）：     ~2-3 秒/字重
NF 版（拉丁+图标）：    ~3-5 秒/字重（merge_ttfonts）
CN 版（拉丁+28000 中文）： ~10-15 秒/字重
NF-CN 版：             ~15-20 秒/字重
```

## 设计洞察

1. **组件化是字体工程的务实选择**：重绘 28000+ 中文字形不现实——用现成的高质量开源基字体组合，是唯一可持久化的方案
2. **哈希校验保证可复现性**：`static.sha256` 锁定基字体版本，与主版本绑定，避免下载到损坏或不兼容的包
3. **2:1 对齐是等宽字体的硬约束**：放弃等宽（narrow 模式）要显式声明风险——Maple Mono 在配置注释中明确警告，不隐式降级
4. **CN 基字体可以独立拉取和重建**：`task.py cn --pull --rebuild` 允许在 Maple Mono 主版本不变的情况下，单独更新中文基字体版本
