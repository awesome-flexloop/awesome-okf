---
type: Reference
title: "FontConfig 类"
description: "Maple Mono 配置加载类——双层合并、特征冻结配置、BuildOption 路径规划"
tags: ["maple-mono", "config", "reference", "api"]
sources:
  - id: BUILD-FONT-CONFIG
    resource: "build.py#FontConfig"
    description: "FontConfig 类定义与方法"
  - id: CONFIG-SCHEMA
    resource: "source/schema.json"
    description: "JSON Schema 完整字段声明"
prerequisites:
  - "../concepts/02-config-system.md"
---

# FontConfig 类

FontConfig 是 Maple Mono 构建系统的**核心配置类**——负责加载 config.json、合并 CLI 参数、驱动构建流程。

## 类签名

```python
class FontConfig:
    def __init__(
        self,
        args: argparse.Namespace | None = None,
        version: str | None = None,
    ) -> None:
        """
        初始化 FontConfig，执行三层合并
        
        参数:
            args: CLI argparse Namespace（parse_args 的返回值）
            version: 覆盖版本号（默认从 pyproject.toml 读取）
        
        合并顺序：
            1. 代码硬编码默认值
            2. config.json 覆写（__load_config）
            3. args 覆写（__load_args → _apply_*）
        """
```

## 合并方法

### __load_config()

```python
def __load_config(self) -> None:
    """
    从 config.json 加载配置到实例属性
    
    合并策略：
        - 标量字段（family_name, width, enable_ligature 等）：直接覆写
        - 嵌套 dict 字段（nerd_font, cn）：{**默认, **config} 浅合并
    
    读取的属性：
        family_name, use_hinted, pool_size, enable_ligature,
        infinite_arrow, width, github_mirror,
        feature_freeze, nerd_font, cn,
        variable, use_examples
    """
```

### __load_args() → _apply_feature_options()

```python
def _apply_feature_options(self, args) -> None:
    """
    应用 Feature 相关的 CLI 参数
    
    处理参数：
        -n/--normal → 把 normal_enabled_features 全部置 enable
        --feat cv01,ss07 → 把列出的特征置 enable
        --hinted/--no-hinted → self.use_hinted
        --liga/--no-liga → self.enable_ligature
        --infinite-arrow → self.infinite_arrow
        --width → self.width
        --nf-mono/--nf-propo → nerd_font.mono / nerd_font.propo
        --cn-narrow → cn.narrow
        --cn-scale-factor → cn.scale_factor
    """
```

### __load_args() → _apply_build_options()

```python
def _apply_build_options(self, args) -> None:
    """
    应用 Build 相关的 CLI 参数
    
    处理参数：
        --nf/--no-nf → nerd_font.enable
        --cn/--no-cn → cn.enable
        --least-styles → self.styles (过滤到 4 种)
        --pool-size → self.pool_size
        --font-patcher → nerd_font.use_font_patcher
        --cache → self.cache
        --archive → self.archive
    """
```

## patch_font_feature()

```python
def patch_font_feature(
    self,
    font: fontTools.ttLib.TTLib,
    is_italic: bool,
    is_cn: bool,
    is_variable: bool,
    remove_italic_calt: bool = False,
) -> None:
    """
    为字体注入 OpenType Feature 规则
    
    参数:
        font: fontTools TTLib 对象
        is_italic: 是否斜体字体
        is_cn: 是否中文版
        is_variable: 是否变量字体
        remove_italic_calt: 斜体时移除 calt 中特定规则
    
    流程：
        1. generate_fea_string() 生成 .fea 字符串
        2. addOpenTypeFeaturesFromString() 注入到 GSUB 表
        3. freeze_feature_static() 应用 feature_freeze 三模式
    
    副作用：
        直接修改传入的 font 对象（in-place mutation）
    """
```

## freeze_feature_static()

```python
def freeze_feature_static(
    self,
    font: fontTools.ttLib.TTLib,
    is_variable: bool,
) -> None:
    """
    根据 feature_freeze 配置冻结 OpenType Feature
    
    参数:
        font: fontTools TTLib 对象
        is_variable: 变量字体（特殊处理）
    
    三模式行为：
        ignore: 不处理
        enable: 规则从原 lookup 搬入 calt，固化为默认
        disable: 从 GSUB 表彻底删除
    """
```

## _update_family_names()

```python
def _update_family_names(self) -> None:
    """
    根据 width / cn / nf 配置更新 family_name
    
    示例：
        默认 → "Maple Mono"
        + NF → "Maple Mono NF"
        + NF + Mono → "Maple Mono NF Mono"
        + CN → "Maple Mono CN"
        + NF + CN → "Maple Mono NF CN"
    """
```

## 属性速查表

### 顶层属性

| 属性 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `family_name` | str | `"Maple Mono"` | 字体族名 |
| `use_hinted` | bool | `true` | 用 hinted 基座 |
| `pool_size` | int | `4` | 并行进程数 |
| `enable_ligature` | bool | `true` | 启用 calt |
| `infinite_arrow` | bool\|null | `null` | 无限箭头 |
| `width` | str | `"default"` | default / narrow / slim |
| `github_mirror` | str | `"github.com"` | 下载镜像 |
| `version` | str | `"7.9"` | 字体版本 |
| `cache` | bool | `false` | 启用缓存 |
| `archive` | bool | `false` | 打包归档 |
| `least_styles` | bool | `false` | 只构建 4 种字重 |

### 嵌套属性

| 属性 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `nerd_font.enable` | bool | `false` | 构建 NF 版 |
| `nerd_font.mono` | bool | `false` | NF Mono 模式 |
| `nerd_font.propo` | bool | `false` | NF Propo 模式 |
| `nerd_font.use_font_patcher` | bool | `false` | font-patcher 路径 |
| `nerd_font.version` | str | `"3.4.0"` | NF 版本 |
| `nerd_font.glyphs` | list | `["--complete"]` | 符号子集 |
| `nerd_font.extra_args` | list | `[]` | font-patcher 额外参数 |
| `cn.enable` | bool | `false` | 构建 CN 版 |
| `cn.with_nerd_font` | bool | `true` | CN 同时带 NF |
| `cn.narrow` | bool | `false` | 压缩中文宽度 |
| `cn.scale_factor` | float\|list | `1.0` | 中文缩放 |
| `cn.use_static_base_font` | bool | `true` | 预构建静态基字体 |
| `feature_freeze` | dict | 全 ignore | cv/ss/zero 三模式配置 |

## 访问器

```python
# 获取完整 BuildOption（路径规划后的产物目录结构）
config = FontConfig(args)
option: BuildOption = config.option  # dataclass，含所有输出路径规划
```
