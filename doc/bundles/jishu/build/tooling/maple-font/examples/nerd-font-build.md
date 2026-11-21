---
type: Example
title: "Nerd Font 补丁构建"
description: "从基础字体打补丁得到带终端图标的 Nerd Font 版——预构建基座路径 + font-patcher 回退"
tags: ["maple-mono", "nerd-font", "icons", "terminal", "font-patcher"]
sources:
  - id: BUILD-NF
    resource: "build.py#build_nf"
    description: "NF 构建两条路径实现"
  - id: TASK-NF
    resource: "task.py#nerdfont"
    description: "NF 基座版本检测与更新"
prerequisites:
  - "basic-build.md"
  - "../concepts/06-nerd-font-patching.md"
status: draft
---

# 示例 3：Nerd Font 补丁构建

本示例展示如何构建带图标的 Maple Mono Nerd Font 版——包含 Font Awesome、Devicons、Octicons 等终端图标。

## 快速构建（预构建基座，最快）

```bash
# 一行搞定
python build.py --nf
```

这条命令会：
1. 检查本地 `MapleMono-NF-Base.ttf` 是否存在
2. 如果存在且版本匹配，用 merge_ttfonts 合并到基础字体
3. 输出带图标的 TTF / NF 版

**预期输出**：

```
fonts/
├── NF/                ← 新增：Nerd Font 输出
│   ├── MapleMono-NF-Regular.ttf
│   ├── MapleMono-NF-Bold.ttf
│   └── ...
├── NF-Mono/           ← 可选：Mono 模式
└── NF-Propo/          ← 可选：Propo 模式
```

## 使用 font-patcher 运行时修补（自定义场景）

如果需要自定义图标子集或使用最新版本的 Nerd Font：

```bash
# 强制走 font-patcher 路径
python build.py --font-patcher --nf

# 需要系统级安装 FontForge
# macOS: brew install fontforge
# Ubuntu: sudo apt install fontforge
```

或通过 config.json 配置：

```json
{
  "nerd_font": {
    "enable": true,
    "use_font_patcher": true,
    "glyphs": ["--complete"],
    "extra_args": []
  }
}
```

## 三种宽度模式

```bash
# 默认：自适应等宽格子
python build.py --nf

# Mono：所有图标固定等宽（推荐终端用）
python build.py --nf --nf-mono

# Propo：按自然宽度显示
python build.py --nf --nf-propo
```

**优先级**：`nf-propo` 覆盖 `nf-mono`——同时指定两个时 Propo 生效。

## 检查 NF Base 版本

```bash
# 查看当前 NF Base 版本
python task.py nf --check

# 强制更新到最新匹配版本
python task.py nf --pull
```

如果 `python task.py nf` 提示本地版本不匹配，构建时会自动触发更新。

## 实战：构建终端字体

### Alacritty 终端配置示例

```bash
python build.py --nf --nf-mono --width narrow --feat cv01,ss07
```

效果：
- NF 图标等宽对齐（终端整齐）
- narrow 宽度更紧凑（一屏多几行）
- cv01 品牌化字形 + ss07 箭头变体

### 安装到 Alacritty

```yaml
# ~/.config/alacritty/alacritty.yml
font:
  normal:
    family: Maple Mono NF Mono
    style: Regular
  bold:
    family: Maple Mono NF Mono
    style: Bold
  size: 14.0
```

验证：打开一个支持 Nerd Font 的 prompt（如 Starship、Powerlevel10k），图标应该正确显示。

## NF-CN 双重补丁

同时需要图标和中日韩字形：

```bash
python build.py --nf --cn

# 或 config.json
{
  "nerd_font": {"enable": true},
  "cn": {"enable": true, "with_nerd_font": true}
}
```

**构建顺序**：基础字体 → merge NF Base → merge CN Base → 宽度调整 → 输出 NF-CN 版。

**预期输出**：

```
fonts/
├── NF-CN/
│   └── MapleMono-NF-CN-Regular.ttf  ← 同时带图标 + 中日韩
└── NF-Mono-CN/
    └── ... (mono 图标模式)
```

## 性能对比

| 路径 | 预期耗时 | 依赖 |
|------|---------|------|
| 预构建基座（默认） | ~10 秒/字重 | 无额外依赖 |
| font-patcher | ~60 秒/字重 | FontForge |

FontForge 的 Python API 比较慢——加载一个字体就需要 10-20 秒，修改又要 30-40 秒。预构建基座路径快 5-6 倍。

## 常见问题

### NF Base 下载失败？

手动下载：
```bash
# 从 GitHub Release 下载对应版本的 MapleMono-NF-Base.ttf
# 放到 source/ 目录下
```

或换 GitHub 镜像：
```json
"github_mirror": "mirror.ghproxy.com"
```

### font-patcher 找不到 FontForge？

验证 FontForge 安装：
```bash
fontforge --version
python -c "import fontforge; print('OK')"
```

如果命令行有但 Python 找不到，可能是多 Python 环境问题。确认 `which python` 指向安装依赖时用的那个。

### NF 图标显示为方块？

这是最常见的问题——应用使用的字体不是 NF 版。
- 确认终端/编辑器的 font-family 指向 `Maple Mono NF` 或 `Maple Mono NF Mono`
- 某些应用需要显式配置 fallback fonts
- 用 `fc-match "Maple Mono NF"`（Linux）确认安装正确
