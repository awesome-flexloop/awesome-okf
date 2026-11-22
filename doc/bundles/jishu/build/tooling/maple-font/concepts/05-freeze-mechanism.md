---
type: Concept
title: "特征冻结机制"
description: "enable / disable / ignore 三态如何在源准备期改变字形与 calt，并解释静态与变量输出的一致冻结边界"
tags: ["feature-freeze", "calt", "cv", "ss", "variation"]
sources:
  - id: build-options-freeze
    resource: https://github.com/subframe7536/maple-font/blob/variable/documentation/build-options.md
    title: Build Options — OpenType Feature Freezing
  - id: apply-source
    resource: https://github.com/subframe7536/maple-font/blob/variable/scripts/feature/apply.py
    title: scripts/feature/apply.py
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-22" }
status: draft
---

# 特征冻结机制

## 1. 要解决的问题

`cv01`、`ss07`、`zero` 等特征需要用户在应用或编辑器中手动开启。对不提供 OpenType 特性开关的终端、IDE 或网页，这层配置负担很高。冻结（freeze）把“选择哪个变体”前移到构建阶段，让用户拿到的字体就是目标形态。

## 2. 三种模式

`config.json` 的 `feature_freeze` 为每个特征保存一个值：

| 模式 | 行为 | 用户侧效果 |
|------|------|------------|
| `enable` | 强制启用该特征，类似默认连字 | 不需要开启 `cvXX` / `ssXX` / `zero` 即可看到变体 |
| `disable` | 从 `cvXX` / `ssXX` / `zero` 中移除该特征 | 即使手动开启也不生效 |
| `ignore` | 保持默认行为 | 特征仍作为普通 OpenType 特征存在，按需开启 |

默认 `config.json` 中所有特征均为 `ignore`。

CLI 的 `--feat` 是 `enable` 的批量写法，逗号分隔，例如：

```sh
uv run build.py --feat zero,cv01,ss07,ss08
```

## 3. 生效时机：源准备期，而非成品后处理

v8 的默认路径在 Fontmake 编译之前完成冻结：

1. `prepare_fontmake_sources` 加载 regular / italic 的 Designspace 与 UFO；
2. 应用构建度量与特征配置；
3. **对每个 master** 执行启用的单一替换：把目标字形轮廓与前进宽度复制到源字形；
4. 启用的上下文/连字查找挂到 `calt`；
5. `disable` 的规则被删除；
6. 物化到一次性工作区，再交给 Fontmake 编译。

这一顺序带来两个关键性质：

- **静态与变量一致**：变量字体由同一批 master 构建，冻结结果在 `gvar` 插值下保持同构，不会出现“静态对了、变量没对”。
- **无需运行时特性开关**：单一替换已变成字形本身，渲染器无需理解 `cvXX`。

## 4. `calt` 承载上下文规则

单一替换可以直接改轮廓；但上下文连字（如 `->`、`>>`、`[TODO]`）依赖前后文，不能简单替换轮廓。v8 的处理是：

- 把 `enable` 的上下文/连字规则移入 `calt`；
- 由于 `calt` 默认启用，这些规则在大多数渲染器中直接生效；
- 若构建时 `is_calt=False`（对应 `--no-liga` 路径），则保留空 `calt` 或移除相关规则。

`feature/compiler.py` 中的 moving-rule 列表（`get_freeze_moving_rules()`）定义了哪些规则需要移入 `calt`；`task.py fea` 会同步更新该列表与 `scripts/in_browser.py`。

## 5. 与 `calt` 开关的关系

| 构建选项 | 对冻结的影响 |
|----------|--------------|
| `--liga`（默认） | 保留全部连字，`calt` 承载上下文规则 |
| `--no-liga` | 移除全部连字，发布名带 `NL` 后缀 |
| `--remove-tag-liga` | 仅移除 `[TODO]` 一类纯文本标签连字 |
| `--no-infinite-arrow` | 不生成无限箭头规则 |

注意：`--feat` 冻结的是**字形变体**；连字的开合由 `--liga` 系列控制，两者不要混淆。

## 6. 文件式路径的冻结边界

`--apply-fea-file` 走另一条路径：

- 读取 `sources/features/regular.fea` / `italic.fea`；
- `include` 在冻结规则之前解析；
- 仍然在源准备期应用，因此静态与变量输出一致。

CJK 静态字体的冻结边界更晚：

- CJK 基座与拉丁基座合并后，才选用 `regular_cn.fea` / `italic_cn.fea`；
- 只冻结 CJK 专属替换（如 `cv96`–`cv99`）；
- 这正是 `feature_freeze` 与 CJK 预设中的 `freeze_feature` 需要分开配置的原因。

## 7. 其他相关开关

- **`--standard-zero`**：改变默认零号与 `zero` 特征的语义映射。默认 `0` 为斜零、启用 `zero` 显示点零；加上此开关后默认点零、启用 `zero` 显示斜零。
- **`--legacy-thin-weight-class`**：不是特征冻结，但同样属于“构建期固化偏好”，把 Thin/ExtraLight 的字重类改为 250/275。
- **`--normal`**：换用另一组字形集合，并默认启用 12 个特征；它改变的是冻结的输入集合，而不是冻结机制本身。

## 8. 验证方法

1. 运行 `uv run build.py --dry`，确认 `feature_freeze` 与 `feat` 的解析结果；
2. 构建后用字体检查工具查看 `GSUB` 中目标 `cvXX` / `ssXX` 是否仍存在（`disable` 应消失）；
3. 在文本编辑器或终端中不开启任何特性，直接输入目标字符，确认 `enable` 的变体已生效；
4. 若修改了生成器源码或特征文件，去掉 `--cache` 再构建，避免旧阶段被误判命中。

## 9. 相关文档

- 特征规则如何组织：[特征系统](03-feature-system.md)
- 生成器 API：[特征 AST 生成器](04-feature-ast-generator.md)
- 动手配置：[自定义特征构建示例](../examples/custom-feature-build.md)
