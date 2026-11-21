---
type: Reference
title: "build.py 主入口"
description: "Maple Mono 构建主入口函数签名与调用链"
tags: ["maple-mono", "build", "reference", "api"]
sources:
  - id: BUILD-PY
    resource: "build.py"
    description: "主构建脚本源码"
prerequisites:
  - "../concepts/01-build-pipeline.md"
---

# build.py 主入口

## parse_args()

CLI 参数解析入口，返回合并后的 `BuildOption` 对象。

```python
def parse_args() -> BuildOption:
    """
    解析 CLI 参数 + 加载 config.json → 返回最终构建配置
    
    返回:
        BuildOption: 包含所有构建参数的 dataclass
    """
```

### 命令行参数分组

| 分组 | 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|------|
| **Feature** | `-n / --normal` | flag | false | 启用 12 项 JetBrains Mono 风格 |
| | `--feat` | str | "" | 逗号分隔的特征列表（置 enable） |
| | `--hinted / --no-hinted` | flag | true | 是否用 hinted 基座 |
| | `--liga / --no-liga` | flag | true | 是否启用连字 |
| | `--infinite-arrow` | flag | null | 强制启用无限箭头 |
| | `--width` | enum | default | default / narrow / slim |
| | `--nf-mono / --nf-propo` | flag | false | NF 图标宽度模式 |
| | `--cn-narrow` | flag | false | 压缩中文字形 |
| | `--cn-scale-factor` | float | 1.0 | 中文字形缩放 |
| **Build** | `--nf / --no-nf` | flag | config | 是否构建 NF 版 |
| | `--cn / --no-cn` | flag | config | 是否构建 CN 版 |
| | `--ttf-only` | flag | false | 只输出 TTF |
| | `--least-styles` | flag | false | 只构建 4 种基础字重 |
| | `--font-patcher` | flag | false | 强制 font-patcher 路径 |
| | `--cache` | flag | false | 复用缓存 |
| | `--archive` | flag | false | 打包 zip |
| | `--pool-size` | int | config | 并行任务数 |

## run_build()

并行构建核心函数。

```python
def run_build(
    pool_size: int,
    fn: Callable[[Path], Any],
    dir: Path,
    target_styles: list[str] | None = None,
) -> dict[Path, Any]:
    """
    并行运行 fn 处理 dir 下所有源字体
    
    参数:
        pool_size: ProcessPoolExecutor max_workers
        fn: build_mono / build_mono_autohint / build_nf / build_cn
        dir: 源字体输入目录
        target_styles: 指定字重列表，None=全部
    
    返回:
        dict[Path, Any]: {源文件路径: fn 返回值}
    """
```

## build_mono()

基础等宽 TTF 构建函数。

```python
def build_mono(src: Path) -> Path:
    """
    将源字体实例化 + 修正 + 去 hint → unhinted TTF
    
    变换步骤:
        1. ftcli fix italic-angle
        2. ftcli fix monospace
        3. ftcli name strip-names
        4. ftcli font correct-contours
        5. ftcli ttf dehint
        6. ftcli fix transformed-components
    
    参数:
        src: 源字体文件路径（Variable Font 中的单字重实例）
    
    返回:
        输出 TTF 路径
    """
```

## build_mono_autohint()

自动 hinting 版构建函数。

```python
def build_mono_autohint(src: Path) -> Path:
    """
    在 build_mono 产物基础上叠加 ttfautohint
    
    参数:
        src: 基础 TTF 路径
    
    返回:
        hinted TTF 路径
    """
```

## build_nf()

Nerd Font 版构建函数。

```python
def build_nf(
    base: Path,
    nf_base: Path | None = None,
    nf_extra: Path | None = None,
    use_font_patcher: bool = False,
    extra_args: list[str] | None = None,
) -> Path:
    """
    将 Nerd Font 图标合并到基础字体
    
    参数:
        base: 基础 TTF 路径
        nf_base: 预构建 NF Base 字体路径
        nf_extra: 额外 glyph 字体路径（可选）
        use_font_patcher: True 则调用 font-patcher 运行时修补
        extra_args: font-patcher 原生参数
    
    返回:
        带图标的 TTF 路径
    """
```

## build_cn()

中英合并版构建函数。

```python
def build_cn(
    base: Path,
    cn_base: Path,
    narrow: bool = False,
    scale_factor: float | list[float] = 1.0,
) -> Path:
    """
    将 Resource Han Rounded 中文基字体合并到基础字体
    
    参数:
        base: 基础 TTF 路径（应为 NF 版，如 with_nerd_font=true）
        cn_base: 中文基字体路径
        narrow: 是否压缩中文字形宽度
        scale_factor: 中文字形缩放因子
    
    返回:
        中英合并 TTF 路径
    """
```

## main()

构建主入口，串联所有阶段。

```python
def main() -> None:
    """
    主构建流程：
        1. parse_args → config.json + CLI → FontConfig
        2. run_build(build_mono) 并行生成基础 TTF
        3. run_build(build_mono_autohint) 并行生成 hinted 版
        4. run_build(build_nf) 并行生成 NF 版（依赖阶段 2）
        5. run_build(build_cn) 并行生成 CN 版（依赖阶段 2 或 4）
        6. convert TTF → OTF / WOFF2
        7. 打包归档（如 --archive）
    """
```

## 调用链总览

```
main()
├── parse_args() → BuildOption
│   └── FontConfig(__load_config, __load_args)
├── run_build(pool_size, build_mono, source_dir)
│   └── ftcli fix italic-angle
│   └── ftcli fix monospace
│   └── ftcli font correct-contours
│   └── ftcli ttf dehint
├── run_build(pool_size, build_mono_autohint, mono_output)
│   └── ttfautohint
├── run_build(pool_size, build_nf, mono_output)  [if --nf]
│   └── merge_ttfonts(base, nf_base)
│   └── patch_font_feature()
├── run_build(pool_size, build_cn, nf_or_mono_output)  [if --cn]
│   └── download_cn_base()  [if needed]
│   └── merge_ttfonts(base, cn_base)
│   └── adjust_cn_width()
│   └── patch_font_feature()
└── convert_all()  → OTF / WOFF2
```
