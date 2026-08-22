---
type: Concept
title: "添加新扩展到翻译"
description: "如何在 repository-map.yml 中注册新的 JupyterLab 扩展使其被纳入翻译流水线——配置条目、路径规则、PR流程"
tags: [jupyterlab, language-pack, extension, contribution, configuration]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-map, resource: /references/repo-map-source.md, title: "repository-map.yml 配置信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
  - { id: crowdin-config, resource: /references/crowdin-config-source.md, title: "Crowdin 配置信源" }
---

# 添加新扩展到翻译

将一个新的 JupyterLab 扩展添加到 language-packs 翻译体系，只需要在 `repository-map.yml` 中添加几行配置。Bot 会自动完成后续所有工作（克隆仓库、提取POT、同步Crowdin、创建PR）。

## 前置条件

新扩展需要满足：

1. **是 JupyterLab 扩展**：使用 JupyterLab 扩展开发模板，支持 i18n（在源码中用 `_()` 标记字符串）
2. **公开发布**：在 GitHub 上有公开仓库，有 git tags
3. **版本规范**：使用 semver 版本号（vX.Y.Z 格式）
4. **稳定版可用**：有正式 release（非 beta/RC），最好达到 1.0 或有一定用户基础
5. **使用 jupyterlab-translate**：扩展的构建配置中集成了 `jupyterlab-translate` 用于 POT 提取

## 扩展 i18n 要求

扩展本身需要做以下准备：

```python
# Python 端：
from jupyter_server.transutils import _
# 或
from jupyterlab_translate import _

# JS/TS 端：
import { _ } from '@jupyterlab/translation';
```

扩展的 pyproject.toml 或 package.json 中需要有正确的 i18n 配置，`jupyterlab-translate` 才能正确提取字符串。

## 步骤 1：编辑 repository-map.yml

在仓库根目录的 `repository-map.yml` 中，按**字母顺序**插入新条目：

```yaml
{extension-name}:
  current-version-tag: v{current-version}
  supported-versions: '>=X.Y.Z'
  url: https://github.com/{owner}/{repo}
```

### 字段填写指南

| 字段 | 填写规则 | 示例 |
|------|---------|------|
| 键名 | kebab-case 包名（npm包名格式） | `jupyterlab-git`、`my-cool-extension` |
| `current-version-tag` | 最新稳定版 git tag（带v前缀） | `v0.50.0` |
| `supported-versions` | npm semver 范围语法 | `>=0.40.0`、`1.x`、`>=2.0 <3.0` |
| `url` | GitHub 仓库 HTTP URL | `https://github.com/jupyterlab/jupyterlab-git` |

### 命名约定

- **键名使用 kebab-case**（连字符分隔），与 npm 包名一致
- 脚本自动转换 kebab-case → snake_case 用于 extensions/ 目录名
- 如果包名本身就是 snake_case（如 `jupyterlab_widgets`），键名也用 snake_case

### supported-versions 写法建议

| 场景 | 写法 | 说明 |
|------|------|------|
| 从某个版本开始支持 | `>=0.5.0` | 最简单，覆盖该版本以上所有 |
| 仅支持某主版本 | `1.x` 或 `2.x` | 不跨主版本 |
| 有已知bug的版本 | `>=1.0 <1.2.3 \|\| >=1.2.5` | 排除有问题的版本 |
| 尚未确定范围 | `>=X.Y.Z` | 首次添加时先用当前版本 |

### 示例：添加 jupyterlab-git

```yaml
# 在其他扩展之间按字母顺序插入
jupyterlab-git:
  current-version-tag: v0.50.1
  supported-versions: '>=0.40.0'
  url: https://github.com/jupyterlab/jupyterlab-git
```

## 步骤 2：提交 PR

1. Fork `jupyterlab/language-packs` 仓库
2. 创建分支（如 `add-my-extension`）
3. 编辑 `repository-map.yml`，按字母顺序插入配置
4. 提交并创建 PR
5. PR 描述中说明：扩展是什么、为什么要添加、GitHub 仓库地址、是否已做 i18n 适配

### PR 检查清单

- [ ] 条目按字母顺序插入
- [ ] url 是 github.com URL（不是 gitlab/bitbucket）
- [ ] current-version-tag 存在且是正式版（非 beta/RC）
- [ ] 扩展已有 i18n 标记（源码中有 `_()` 调用）
- [ ] supported-versions 覆盖范围合理

## 步骤 3：CI 自动处理

PR 合并后，Bot 自动执行：

### 3.1 update_pot.yml 触发

检测到 `repository-map.yml` 变更：
1. `02_update_catalogs.py` 运行
2. `update_crowdin_config()` 自动更新 `crowdin.yml`（添加新扩展的文件映射）
3. 克隆新扩展仓库到 `repos/` 目录
4. 使用 `jupyterlab_translate.api.extract_language_pack()` 提取可翻译字符串
5. 生成 POT 文件到 `extensions/{snake_name}/locale/{snake_name}.pot`
6. 创建 POT 更新 PR

### 3.2 crowdin.yml 同步

POT 更新 PR 合并后：
1. 新 POT 文件上传到 Crowdin
2. 译者可以在 Crowdin 平台看到新扩展的字符串
3. 翻译开始积累

### 3.3 第一次翻译同步

当 Crowdin 上有翻译后（每日定时同步）：
1. Crowdin Action 下载翻译 PO 文件
2. 每个语言包目录下自动创建对应 .po 文件
3. 创建翻译 PR
4. 翻译 PR 合并后，语言包包含新扩展的翻译

## 步骤 4：包含在下次发布中

下次执行 `prepare_release` 时：
1. 新扩展的 .po 文件会被编译进每个语言包
2. 每个语言包的 wheel 中包含新扩展的 .mo/.json 文件
3. 用户安装更新后，新扩展自动获得翻译

## 目录命名映射

添加扩展后，自动化系统会自动处理目录命名：

| 配置键名 (kebab-case) | extensions/ 目录 (snake_case) | POT 文件名 | PO domain |
|----------------------|------------------------------|-----------|-----------|
| `jupyterlab-git` | `extensions/jupyterlab_git/` | `jupyterlab_git.pot` | `jupyterlab_git` |
| `my-cool-extension` | `extensions/my_cool_extension/` | `my_cool_extension.pot` | `my_cool_extension` |
| `jupyterlab_widgets` | `extensions/jupyterlab_widgets/` | `jupyterlab_widgets.pot` | `jupyterlab_widgets` |

转换逻辑在 `02_update_catalogs.py` 的 `update_crowdin_config()` 中：
```python
snake_name = package_name.replace("-", "_")
```

## 常见问题

### Q: 扩展没有做 i18n，可以添加吗？

不可以。扩展必须在源码中使用 `_()` 标记可翻译字符串，否则 `jupyterlab-translate` 提取不到任何内容。应先向扩展仓库提交 i18n 适配 PR。

### Q: 扩展不在 GitHub 上怎么办？

当前脚本只支持 github.com 的仓库（通过 GitHub API 获取 tags 和克隆）。其他平台需要扩展脚本支持。

### Q: 扩展的版本号不带 v 前缀？

大多数 JupyterLab 生态包使用 `vX.Y.Z` 格式。如果扩展的 tag 是 `X.Y.Z` 格式（不带v），current-version-tag 也应该写 `X.Y.Z`，脚本会按实际 tag 名克隆。

### Q: 如何验证扩展是否正确添加？

合并后检查：
1. `extensions/{snake_name}/locale/` 目录是否创建
2. POT 文件是否非空（有 msgid 条目）
3. Crowdin 项目中是否出现新文件
4. 翻译下载后 `language-packs/*/locale/` 中是否有对应的 .po 文件

### Q: 扩展废弃了怎么办？

从 `repository-map.yml` 中删除对应条目：
1. 创建 PR 删除配置行
2. Bot 会自动更新 crowdin.yml 移除映射
3. 旧的 POT 文件可以保留或删除（保留不影响功能，但会占空间）
4. 已有的翻译会在下次构建时被排除（没有对应的 POT 源，但历史 PO 文件仍存在）
5. 建议手动清理 extensions/ 和 language-packs/ 中的废弃文件

## 添加新语言

与添加扩展不同，添加新语言需要在 Crowdin 平台上操作：
1. 访问 Crowdin 项目设置
2. 添加新目标语言
3. 等待 Crowdin 自动创建对应目录结构
4. 译者开始翻译后，Crowdin Action 会自动创建新语言包目录（基于 cookiecutter 模板）

注意：`ach-UG` 是特殊的 in-context 伪语言，不是真正的翻译目标。

## 相关概念

- [repository-map.yml 配置详解](03-repository-map-config.md)
- [Crowdin 翻译平台集成](04-crowdin-integration.md)
- [自动化脚本体系](07-automation-scripts.md)
- [贡献翻译](../examples/03-contribute-translation.md)
