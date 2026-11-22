---
type: Reference
title: "ResolvedConfig 参考"
description: "ResolvedConfig 的六组子配置字段、派生属性、BuildRuntimeContext 与 BuildPlan 的数据模型"
tags: ["api", "config", "dataclass", "resolved-config"]
sources:
  - id: config-base
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/config/base.py
    title: scripts/config/base.py
  - id: config-resolver
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/config/resolver.py
    title: scripts/config/resolver.py
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# ResolvedConfig 参考

## 1. 顶层模型

```python
@dataclass(slots=True)
class ResolvedConfig:
    behavior: BuildBehaviorConfig = field(default_factory=BuildBehaviorConfig)
    feature: FeatureBuildConfig = field(default_factory=FeatureBuildConfig)
    nerd_font: NerdFontBuildConfig = field(default_factory=NerdFontBuildConfig)
    cjk: CJKBuildSelection = field(default_factory=CJKBuildSelection)
    identity: BuildIdentityConfig = field(default_factory=BuildIdentityConfig)
    metrics: BuildMetricsConfig = field(default_factory=BuildMetricsConfig)
    feature_freeze: dict[str, str] = field(default_factory=default_feature_freeze)
```

## 2. BuildBehaviorConfig

```python
@dataclass(slots=True)
class BuildBehaviorConfig:
    archive: bool = False
    debug: bool = False
    cache: bool = False
    least_styles: bool = False
    apply_fea_file: bool = False
    cjk_output_format: CJKOutputFormat = "static"
    formats: list[BuildFormatId] = field(default_factory=lambda: list(BUILD_FORMATS))
    use_cjk_both: bool = False
```

| 字段 | 含义 |
|------|------|
| `archive` | `--archive` |
| `debug` | `--debug` |
| `cache` | `--cache` |
| `least_styles` | `--least-styles` |
| `apply_fea_file` | `--apply-fea-file` |
| `cjk_output_format` | `static` 或 `variable` |
| `formats` | 请求的基础格式；Variable 不在其中但始终构建 |
| `use_cjk_both` | `--cjk-both` |

## 3. FeatureBuildConfig

```python
@dataclass(slots=True)
class FeatureBuildConfig:
    normal: bool = False
    standard_zero: bool = False
    legacy_thin_weight_class: bool = False
    feat: list[str] = field(default_factory=list)
    hinted: bool = True
    liga: bool = True
    infinite_arrow: bool = True
    remove_tag_liga: bool = False
    line_height: float = 1.0
    width: str = "default"
```

`width` 只接受 `default` / `narrow` / `slim`，对应 `WIDTH_MAP` 的 600 / 550 / 500。

## 4. NerdFontBuildConfig

```python
@dataclass(slots=True)
class NerdFontBuildConfig:
    enable: bool = True
    version: str = "3.5.0"
    mono: bool = False
    propo: bool = False
    variable: bool = False
    use_font_patcher: bool = False
    glyphs: list[str] = field(default_factory=lambda: ["--complete"])
    extra_args: list[str] = field(default_factory=list)

    def uses_font_patcher(self) -> bool: ...
    def to_dict(self, *, include_enable: bool = True) -> dict[str, Any]: ...
```

`uses_font_patcher()` 为真当且仅当 `extra_args` 非空、`use_font_patcher` 为真，或 `glyphs != ["--complete"]`。

## 5. CJK 模型

```python
@dataclass(slots=True)
class CJKCommonBuildOptions:
    with_nerd_font: bool = True
    fix_meta_table: bool = True
    clean_cache: bool = False
    narrow: bool = False
    use_hinted: bool = False
    scale_factor: tuple[float, float] = (1.0, 1.0)
```

```python
@dataclass(slots=True)
class CJKLocaleSelection:
    cn: bool = False
    jp: bool = False
    tc: bool = False
    kr: bool = False
    custom: list[CustomCJKEntryConfig] = field(default_factory=list)

    def builtin_enabled_locales(self) -> list[BuiltinCJKLocaleId]: ...
    def set_builtin_enabled(self, locale, enabled: bool) -> None: ...
    def to_dict(self) -> dict[str, Any]: ...
```

```python
@dataclass(slots=True)
class CJKBuildSelection:
    locales: CJKLocaleSelection = field(default_factory=CJKLocaleSelection)
    common_options: CJKCommonBuildOptions = field(default_factory=CJKCommonBuildOptions)
    entries: list[ResolvedCJKBuildEntry] = field(default_factory=list)

    def selected_entries(self) -> list[ResolvedCJKBuildEntry]: ...
    def to_dict(self) -> dict[str, Any]: ...
```

`ResolvedCJKBuildEntry` 把内置或自定义条目统一为：

```python
@dataclass(slots=True)
class ResolvedCJKBuildEntry:
    entry_id: str
    locale_name: str
    build_config: CJKBuildConfig
    common_options: CJKCommonBuildOptions
    is_builtin: bool
    preset_id: BuiltinCJKLocaleId | None = None
    preset_spec: CJKPresetSpec | None = None
```

## 6. BuildIdentityConfig

```python
@dataclass(slots=True)
class BuildIdentityConfig:
    base_family_name: str = "Maple Mono"
    family_name: str = "Maple Mono"
    family_name_compact: str = "MapleMono"
    version_tag: str = "v7.9"
    version: str = "7.9"
    version_str: str = "Version 7.900"
    font_version: str | None = None
    beta: str | None = None
```

解析器 `_apply_identity()` 根据 `version_tag` 与 `beta` 派生族名、紧凑名与内嵌版本；`font_version` 在未解析前为 `None`，访问 `ResolvedConfig.font_version` 会抛 `ValueError`。

## 7. BuildMetricsConfig

```python
@dataclass(slots=True)
class BuildMetricsConfig:
    weight_mapping: dict[str, int] = field(default_factory=default_weight_mapping)
    codepoint_alias: dict[int, int] = field(default_factory=dict)
    vertical_metric: tuple[int, int] = (1020, -300)
    glyph_width: int = 600
    glyph_width_cn_narrow: int = 1000
    ttfautohint_param: dict[str, Any] = field(default_factory=dict)
    pool_size: int = 1 if not getenv("CODESPACE_NAME") else 4
    github_mirror: str = "github.com"
```

> `pool_size` 的 dataclass 默认值为 1（Codespace 下为 4），但仓库 `config.json` 显式设为 4，因此常规构建实际使用 4。

## 8. 常用派生属性

| 属性/方法 | 返回 | 说明 |
|-----------|------|------|
| `family_name`、`family_name_compact` | str | 来自 identity |
| `version`、`version_str`、`version_tag`、`beta` | str / str / str / str \| None | 版本信息 |
| `font_version` | str | 未解析时抛错 |
| `use_hinted`、`legacy_thin_weight_class` | bool | 来自 feature |
| `enable_ligature`、`infinite_arrow`、`remove_tag_liga` | bool | 来自 feature |
| `line_height`、`width` | float / str | 来自 feature |
| `pool_size`、`weight_mapping`、`codepoint_alias`、`vertical_metric` | 各种 | 来自 metrics |
| `glyph_width`、`glyph_width_cn_narrow` | int | 来自 metrics |
| `ttfautohint_param`、`github_mirror` | dict / str | 来自 metrics |
| `freeze_config_str` | str | 归一化后的冻结配置文本 |
| `get_target_width()` | int | 由 `width` 查 `WIDTH_MAP` |
| `get_width_name()` | `"NR"` / `"SL"` / `None` | 文件名宽度标记 |
| `get_selected_cjk_entries()` | list | 已选 CJK 条目 |
| `wants_format(fmt)` | bool | `fmt` 是否在 `formats` 中 |
| `needs_hinted_ttf()` | bool | 是否需要 hinted 静态基座 |
| `needs_nerd_font_static_base()` | bool | NF 是否需要静态基座 |
| `get_nf_variant()` | `NerdFontVariant` | 解析 NF 变体 |
| `get_valid_glyph_width_list(is_cjk, cjk_narrow)` | list[int] | 宽度校验允许值 |

## 9. 冻结配置辅助函数

```python
def default_feature_freeze() -> dict[str, str]: ...
def normalize_feature_freeze(config: dict[str, str], calt: bool) -> dict[str, str]: ...
def format_freeze_config(config: dict[str, str]) -> str: ...
```

- `default_feature_freeze()`：为全部 `cvXX` / `ssXX` / `zero` 生成 `ignore`；
- `normalize_feature_freeze()`：结合 `calt`（即 `liga`）决定哪些规则需要移入 `calt`；
- `format_freeze_config()`：生成可读的冻结摘要。

## 10. 与其他模型的关系

```
config.json + CLI
      │  BuildConfigResolver
      ▼
ResolvedConfig ──from_config──▶ BuildRuntimeContext
      │
      └──from_config──▶ BuildPlan ──▶ MapleBuildPipeline
```

- `BuildRuntimeContext` 只放路径与运行期能力；
- `BuildPlan` 只放阶段策略；
- 二者都不回写 `ResolvedConfig`。

## 11. 注意

- 字段默认值以 v8 `8.003` 源码为准，版本升级后可能变化；
- `font_version` 是解析产物，不要手工构造后直接读取；
- `formats` 不含 `variable`，但变量字体始终构建。

## 相关文档

- 配置来源与优先级：[配置系统](../concepts/02-config-system.md)
- 入口函数：[构建入口参考](build-entrypoint.md)
