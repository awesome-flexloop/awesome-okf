---
type: concept
title: 版本门控与向后兼容
description: scikit-build-core 的 minimum-version 机制如何实现渐进式功能启用、配置迁移和默认值变化
tags:
  - scikit-build
  - build
  - versioning
  - compatibility
generated: true
verified: false
status: stable
stale_after: "2026-12-01"
sources:
  - "external/libs/tools/scikit-build/scikit-build-core/src/scikit_build_core/settings/skbuild_read_settings.py"
---

# 版本门控与向后兼容

scikit-build-core 使用 `minimum-version` 机制实现"声明目标版本，自动适配行为"，避免配置在版本升级时静默失效或行为变化。

## 为什么需要版本门控

构建工具升级时常见的问题：

1. **新默认值**：新版本改变某个选项的默认值，旧项目行为意外改变
2. **字段重命名**：配置字段从 `cmake.minimum_version` 迁移到 `cmake.version`，旧配置不再生效
3. **新功能门控**：某些功能（如 sdist inclusion-mode）需要特定版本以上才能使用
4. **废弃警告**：使用已废弃字段应得到明确警告而非静默忽略

`minimum-version` 解决了这些问题：明确声明项目适配的最低版本，scikit-build-core 根据版本自动调整行为。

## 设置 minimum-version

```toml
[tool.scikit-build]
# 方式1：手动指定版本
minimum-version = "0.10"

# 方式2（推荐）：自动从 build-system.requires 提取
minimum-version = "build-system.requires"
```

方式2 的工作原理：

1. SettingsReader 读取 `build-system.requires` 中的 `scikit-build-core>=X.Y` 约束
2. 提取最低版本号作为 `minimum-version`
3. 无需手动维护版本号，版本约束和功能启用保持同步

```toml
# 示例：requires 写 >=0.12，minimum-version 自动为 0.12
[build-system]
requires = ["scikit-build-core>=0.12", "ninja"]

[tool.scikit-build]
minimum-version = "build-system.requires"
```

## 版本门控行为

SettingsReader 根据 `minimum-version` 执行以下处理：

### 1. 字段迁移

旧字段自动迁移到新字段名：

| minimum-version | 旧字段 | 新字段 |
|----------------|--------|--------|
| < 0.5 | `cmake.minimum_version` | `cmake.version` |
| < 0.5 | `cmake.verbose` | `build.verbose` |
| < 0.5 | `logging = "FINE"` | `logging.level = "DEBUG"` |

迁移通过 `_handle_move()` 函数实现：检测旧字段存在、新字段未设置时，自动复制值到新字段并发出 FutureWarning。

### 2. 默认值变更

| 字段 | 旧默认（低版本） | 新默认（≥指定版本） | 版本 |
|------|----------------|-------------------|------|
| `wheel.reproducible` | `false` | `true` | 0.18+ |
| `install.strip` | `false` | 根据 build-type 自动判断 | 0.18+ |
| `sdist.inclusion-mode` | `classic` | `default` | 0.12+ |

设置了合适的 minimum-version 后，新默认值自动生效。

### 3. 功能启用

某些新功能要求 minimum-version 达到指定版本才能使用：

| 功能 | 需要版本 |
|------|---------|
| `sdist.inclusion-mode = "default"` | 0.12+ |
| `sdist.resolve-symlinks` | 0.12+ |
| `cmake.verbose` → `build.verbose` 迁移 | 0.5+ |
| `minimum-version = "build-system.requires"` | 0.10+ |

如果使用了高版本功能但 minimum-version 过低，SettingsReader 会报错并提示提升版本。

### 4. 严格模式差异

| 行为 | 低 minimum-version | 高 minimum-version |
|------|-------------------|-------------------|
| 未识别选项 | 警告（向后兼容） | 错误退出 |
| 废弃字段 | FutureWarning | 错误 |
| 类型不匹配 | 尝试转换 | 错误 |

## 配置版本检查

SettingsReader.validate_may_exit() 在解析后执行版本合规检查：

1. **使用了需要更高版本的功能** → 错误：提示提升 minimum-version
2. **使用了已废弃字段** → FutureWarning（有迁移路径时自动迁移）
3. **minimum-version 过高** → 警告：声明的版本高于已安装版本（可能不兼容）

## 推荐实践

### 新项目

```toml
[build-system]
requires = ["scikit-build-core>=0.18", "ninja"]

[tool.scikit-build]
minimum-version = "build-system.requires"
```

始终使用 `"build-system.requires"` 自动同步，避免版本不一致。

### 升级版本时

1. 更新 `build-system.requires` 中的版本约束
2. 阅读 scikit-build-core 的 changelog
3. 运行 `pip install --upgrade scikit-build-core && pip install -e .` 检查是否有警告
4. 修复所有 FutureWarning（通常是字段重命名）
5. 运行构建验证功能正常

### 临时使用新功能

如果想在不提升 minimum-version 的情况下尝试新功能：

```bash
# 通过 config-settings 覆盖
pip install . -Cwheel.reproducible=true
```

但不推荐长期使用——正确的方式是提升 minimum-version。

## minimum-version 与 build-system.requires 的关系

```
build-system.requires = ["scikit-build-core>=0.12"]
                                 ↓
                       pip 保证安装版本 ≥ 0.12
                                 ↓
minimum-version = "build-system.requires"
                       自动提取 0.12
                                 ↓
                       SettingsReader 使用 0.12 的默认值和行为
```

二者应该保持一致：`requires` 约束最低安装版本，`minimum-version` 声明配置语义版本。
