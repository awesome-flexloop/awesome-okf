---
type: Concept
title: "配置系统"
description: "Maple Mono config.json 声明式配置 + CLI 参数双层覆盖的合并顺序、优先级与完整 Schema 解读"
tags: ["maple-mono", "config", "json-schema", "cli", "configuration"]
sources:
  - id: CONFIG-JSON
    resource: "config.json"
    description: "默认构建配置文件"
  - id: CONFIG-SCHEMA
    resource: "source/schema.json"
    description: "完整 JSON Schema 定义（含字段说明、枚举、默认值）"
  - id: FONT-CONFIG-CLASS
    resource: "build.py#FontConfig"
    description: "配置加载与合并逻辑"
prerequisites:
  - "00-introduction"
  - "01-build-pipeline"
next:
  - "03-feature-system"
related:
  - "../references/font-config-class.md"
  - "../examples/custom-feature-build.md"
status: draft
---

# 配置系统

Maple Mono 的构建系统采用**声明式配置 + 命令覆盖**双层架构，这是理解其灵活性的关键。

## 双层架构设计

```
┌─────────────────────────────────────────────────────┐
│                  最终生效配置                         │
└───────────────────────────┬─────────────────────────┘
                            │ 从高到低优先级
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌─────────────────┐  ┌───────────────┐  ┌───────────────┐
│  CLI 参数       │  │ config.json   │  │ FontConfig    │
│  python build.py │  │ 版本化 JSON   │  │ 默认值        │
│  --nf --width   │  │ git-tracked   │  │ 代码硬编码     │
│  slim --feat    │  │ 可共享        │  │ 不可变         │
└─────────────────┘  └───────────────┘  └───────────────┘
```

**合并顺序**（FontConfig.__init__ 内部）：
1. 初始化代码硬编码的默认值
2. 用 config.json 的值覆写（同名字段）
3. 用 CLI 参数覆写（同名字段）

```python
class FontConfig:
    def __load_config(self):
        """第 1 层：从 config.json 加载"""
        with open("config.json") as f:
            data = json.load(f)
        for prop in ["family_name", "use_hinted", "nerd_font", "cn", ...]:
            if prop in data:
                val = data[prop]
                setattr(self, prop, val if type(val) is not dict
                               else {**getattr(self, prop), **val})

    def __load_args(self, args):
        """第 2 层：CLI 参数覆写"""
        self._apply_build_options(args)
        self._apply_feature_options(args)
        self._apply_nerd_font_options(args)
        self._apply_cn_options(args)
```

**关键约束**：CLI 覆盖 config.json，但 config.json 始终存在且被 git 追踪——这是构建可复现性的保障。

## 完整配置字段解读

### 顶层字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `family_name` | string | `"Maple Mono"` | 字体族名 |
| `use_hinted` | bool | `true` | 用 hinted TTF 作为 NF/CN 构建的基座 |
| `pool_size` | int | `4` | 并行任务数（Codespace 自动降为 1） |
| `enable_ligature` | bool | `true` | 是否启用 calt 连字 |
| `line_height` | float | `1.0` | 行高缩放因子 |
| `width` | enum | `"default"` | `default`(600) / `narrow`(550) / `slim`(500) |
| `infinite_arrow` | bool/null | `null` | 无限箭头连字（null=hinted禁用、unhinted启用） |
| `github_mirror` | string | `"github.com"` | GitHub 下载镜像 |

### feature_freeze 三模式配置

这是最强大也最容易忽略的配置段——控制每个 OpenType 特征的处理方式：

```json
"feature_freeze": {
  "cv01": "ignore",    // 不处理，保持动态
  "ss08": "enable",    // 固化为默认字形（自动生效）
  "zero": "disable"    // 移除该特征（即使手动启用也无效）
}
```

| 模式 | 行为 | 典型用途 |
|------|------|---------|
| `ignore` | 不处理，保留原特征 | 默认配置 |
| `enable` | 规则移入 calt，固化为默认字形 | 我就要这个变体当默认值 |
| `disable` | 从字体表中移除该特征 | 我不想要这个连字/变体 |

CLI 对应：`--feat cv01,ss07,zero` 会把列出的特征置为 `enable`。

### nerd_font 配置段

```json
"nerd_font": {
  "enable": true,
  "version": "3.4.0",
  "mono": false,        // 固定宽度图标
  "propo": false,       // 可变宽度图标（覆盖 mono）
  "use_font_patcher": false,  // 用预构建基座 vs 运行时修补
  "glyphs": ["--complete"],   // 符号字体参数
  "extra_args": []
}
```

**关键决策**：`use_font_patcher` 控制 NF 构建路径：
- `false`（默认）：下载预构建 `MapleMono-NF-Base.ttf` → merge_ttfonts 合并（快）
- `true`：调用 font-patcher 运行时修补（慢但灵活，需 FontForge）

### cn 配置段

```json
"cn": {
  "enable": false,
  "with_nerd_font": true,    // CN 版是否同时打 NF 补丁
  "narrow": false,           // 压缩中文字形宽度
  "scale_factor": 1.0,       // 中文字形缩放（可用 [1.2,1.1] 分别设宽高）
  "use_static_base_font": true
}
```

`narrow: true` 会让字体**不再是等宽字体**——IntelliJ IDEA / Windows 记事本等应用可能渲染异常。配置里有明确的风险提示。

## CLI 参数速查表

CLI 分为两组：Feature Options（影响字形/特征）和 Build Options（影响构建行为）。

### Feature Options

| 参数 | 效果 | 影响 config 字段 |
|------|------|-----------------|
| `-n / --normal` | 启用 Normal 预设 | feature_freeze 中 12 项置 enable |
| `--feat cv01,ss07` | 启用指定特征 | feature_freeze 中列出项置 enable |
| `--hinted / --no-hinted` | 切换基座 hinting | use_hinted |
| `--liga / --no-liga` | 切换连字 | enable_ligature |
| `--infinite-arrow` | 强制启用无限箭头 | infinite_arrow |
| `--width {default,narrow,slim}` | 三档字形宽度 | width |
| `--nf-mono / --nf-propo` | NF 图标宽度 | nerd_font.mono / nerd_font.propo |
| `--cn-narrow` | 压缩中文字形 | cn.narrow |
| `--cn-scale-factor 1.1` | 中文字形缩放 | cn.scale_factor |

### Build Options

| 参数 | 效果 |
|------|------|
| `--nf / --no-nf` | 构建 NF 版 |
| `--cn / --no-cn` | 构建 CN 版 |
| `--ttf-only` | 只输出 TTF（跳过 OTF/WOFF2） |
| `--least-styles` | 只构建 Regular/Bold/Italic/BoldItalic |
| `--font-patcher` | 强制用 font-patcher 构建 NF |
| `--cache` | 复用已有 TTF/OTF/WOFF2 缓存 |
| `--archive` | 打包为 zip 归档（含 config + license） |

## 设计洞察

1. **JSON Schema 即文档**：`source/schema.json` 完整声明了所有字段的类型、枚举、默认值、说明文字——既是运行时验证依据，也是最权威的 API 文档
2. **Config 可复现性**：config.json 版本化提交，同一 config.json 产出同一字体。CLI 参数用于 CI 快速调整
3. **布尔三态**：`infinite_arrow`、`cn.use_static_base_font` 等字段支持 `null`/`true`/`false` 三态——允许"根据其他参数自动决策"的语义
4. **嵌套字典合并**：dict 类型字段（nerd_font、cn）采用 `{**默认, **配置}` 合并模式——只覆写指定子字段，其他保留默认
