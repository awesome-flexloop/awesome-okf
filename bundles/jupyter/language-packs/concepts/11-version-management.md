---
type: Concept
title: "版本管理策略"
description: "语言包的双版本号体系——X.Y跟随JupyterLab主版本、postZ为翻译修订号，以及版本检测、合并、一致性检查的完整机制"
tags: [jupyterlab, language-pack, versioning, semver, post-release, version-consistency]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:35:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: repo-map, resource: /references/repo-map-source.md, title: "repository-map.yml 配置信源" }
  - { id: scripts, resource: /references/scripts-source.md, title: "自动化脚本信源" }
  - { id: release, resource: /references/release-process-source.md, title: "发布流程信源" }
---

# 版本管理策略

JupyterLab 语言包采用独特的版本管理策略，版本号同时反映"对应的 JupyterLab 版本"和"翻译修订次数"两个维度。版本管理是整个自动化流水线的核心驱动力——版本检测触发 POT 更新，版本一致性保证发布质量。

## 版本号格式

```
X.Y.postZ
```

| 组成 | 含义 | 示例 | 来源 |
|------|------|------|------|
| `X` | JupyterLab 主版本号 | 4 | 跟随 JupyterLab major |
| `Y` | JupyterLab 次版本号 | 5 | 跟随 JupyterLab minor |
| `.postZ` | 翻译修订号 | post3 | 每次发布递增 |

### 示例版本演进

```
4.3.post0 → 4.3.post1 → 4.3.post2 → 4.4.post0 → 4.4.post1 → 4.5.post0 → ...
```

- `4.3.post0`：JupyterLab 4.3.x 首次翻译发布
- `4.3.post1`：JupyterLab 4.3.x 翻译更新（新翻译/修正）
- `4.4.post0`：JupyterLab 升级到 4.4.x，重置 post 为 0
- `4.5.post3`：JupyterLab 4.5.x 的第3次翻译更新

### 为什么用 post 后缀？

Python 包版本规范 [PEP 440](https://peps.python.org/pep-0440/) 定义了 post-releases：
- `X.Y.postZ` 表示同一功能版本的修正版
- 适合翻译更新——功能代码未变，只是翻译数据更新
- `pip install --upgrade` 会正确升级到最新 post 版本
- 不使用 `.dev` 或 `a/b/rc` 前缀，因为语言包始终是正式版

## 双轨版本管理

语言包涉及两套版本号体系：

### 上游版本（Upstream Version）

定义在 `repository-map.yml` 的 `current-version-tag`：
- 指 JupyterLab 及其扩展的发布版本（如 `v4.6.1`）
- 由 `01_check_releases.py` 每日检测更新
- 决定从哪个版本的源码提取可翻译字符串
- 不是语言包自身的版本号

### 语言包版本（Language Pack Version）

定义在各语言包 `__init__.py` 的 `__version__`：
- 格式为 `X.Y.postZ`
- 由 `03_prepare_release.py` 在发布时统一设置
- **所有语言包版本必须完全相同**（由 `04_check_version.py` 强制保证）

## 版本检测机制

### 01_check_releases.py 的检测逻辑

每日 UTC 0:00 运行，对每个包执行：

1. **获取 tags**：通过 GitHub GraphQL API 获取最近 100 个 tag（按提交日期降序）
2. **解析版本**：使用 `packaging.version.parse()` 解析
3. **过滤**：
   - 排除 dev 版本（`version.is_devrelease == False`）
   - 排除 prerelease 版本（`version.is_prerelease == False`）
   - 版本号必须可被 semver 解析
4. **JupyterLab 特殊处理**：按主版本前缀过滤（如只匹配 `v4.*`），避免跨大版本混淆
5. **比较**：最新有效版本 > current-version-tag → 需要更新
6. **范围检查**：新版本是否在 `supported-versions` 范围内
7. **写回**：更新 repository-map.yml，创建 PR

### 版本比较细节

Python 的 `packaging.version.Version` 比较：
- `v4.5.0` < `v4.6.0` < `v4.6.1`
- `v4.6.0a1`（alpha）< `v4.6.0rc1`（rc）< `v4.6.0`（正式）
- 脚本过滤掉 alpha/beta/rc，只响应正式 release

### supported-versions 的作用

`supported-versions` 定义了"需要合并字符串的版本范围"：

```yaml
jupyterlab:
  supported-versions: '>=4.3'
```

这意味着从 JupyterLab 4.3.0 到当前最新版本（4.6.1）之间所有正式版的可翻译字符串都会被合并到 POT 中，确保翻译覆盖整个版本范围的用户。

## 多版本字符串合并

`02_update_catalogs.py` 的版本合并策略确保翻译覆盖广泛：

```python
# 1. 获取所有符合条件的版本
versions = _get_releases(package_name, package_info)
# 返回如 ["4.3.0", "4.3.1", "4.4.0", "4.5.0", "4.5.1", "4.6.0", "4.6.1"]

# 2. 对每个版本提取字符串并merge到POT
for version in versions:
    update_catalog(package_name, version, merge=True)

# 3. 最后再处理current-version-tag版本
update_catalog(package_name, current_version, merge=True)
```

### 为什么要 merge 多版本？

JupyterLab 在不同版本间可能：
- **新增字符串**：新功能带来新的可翻译字符串
- **修改字符串**：同一消息的英文原文修改
- **删除字符串**：废弃的功能字符串消失

如果只提取最新版本，旧版本用户会看到未翻译的字符串。merge 多版本确保：
- 只要字符串在任何支持版本中出现过，就会在 POT 中
- 翻译可以覆盖所有仍在使用的版本
- 版本回退的用户也能看到完整翻译

## 版本一致性强制保证

### 04_check_version.py

这是 CI 门禁脚本，逻辑简单但关键：

```python
import ast, pathlib

versions = set()
for pkg_dir in language_packs_dir.iterdir():
    init_file = pkg_dir / package_name / "__init__.py"
    content = init_file.read_text()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if target.id == "__version__":
                    versions.add(node.value.s)

if len(versions) != 1:
    print(f"ERROR: Inconsistent versions: {versions}")
    sys.exit(1)
```

- 遍历所有语言包的 `__init__.py`
- 使用 AST 解析（而非正则，更可靠）提取 `__version__`
- 如果版本集合大小≠1，CI 失败
- PR 必须通过此检查才能合并

### 为什么要求版本一致？

1. **用户体验**：用户安装语言包时，所有已安装语言的版本应该一致，避免版本错乱
2. **Crowdin 同步**：所有语言从同一个 POT 模板翻译，版本号应反映模板版本
3. **简化发布**：一次发布所有语言包，不需要跟踪单语言版本
4. **JupyterLab 期望**：JupyterLab 可能假设语言包版本与自身版本匹配

## 发布时版本提升

`03_prepare_release.py` 在发布准备时统一提升版本：

1. **解析参数**：从 `--version-tag` 获取 JupyterLab 版本（如 `v4.6.1`）
2. **确定主版本**：`X.Y` = JupyterLab 的 major.minor（如 `4.6`）
3. **确定 post 编号**：
   - 如果 X.Y 与之前不同 → `.post0`（新的 JupyterLab 次要版本）
   - 如果 X.Y 相同 → post 编号 +1（同版本翻译更新）
4. **批量更新**：遍历所有 31 个语言包，写入 `__version__ = "X.Y.postZ"`

## 依赖版本管理

除了语言包自身版本，仓库还管理两类依赖版本：

### Python 依赖（requirements.txt）

```
# 核心依赖
jupyterlab-translate>=1.2.0
hatchling>=1.4.0
copier
packaging
semantic-version
requests
PyGithub
```

- `jupyterlab-translate`：POT提取和PO编译的核心工具
- `hatchling`：PEP 517构建后端
- `copier`：项目模板更新
- `packaging`/`semantic-version`：版本号解析
- `requests`：Crowdin API调用
- `PyGithub`：GitHub API操作

由 dependabot 自动更新依赖版本。

### Node.js 依赖

虽然语言包不直接使用 Node.js，但 `jupyterlab-translate` 提取 POT 时可能需要调用 JupyterLab 的构建工具链。prepare_release 工作流安装 Node.js 20 以兼容。

## 版本兼容矩阵

| 语言包版本 | 兼容 JupyterLab 版本 | 说明 |
|-----------|---------------------|------|
| 3.x.postZ | JupyterLab 3.x | 旧版本（语言包仓库可能仍有支持）|
| 4.3.postZ | JupyterLab 4.3.x | 从4.3开始支持的范围 |
| 4.5.postZ | JupyterLab 4.3-4.5.x | 合并了>=4.3所有版本的字符串 |
| 4.6.postZ | JupyterLab 4.3-4.6.x | 当前最新 |

因为字符串是多版本合并的，较新的语言包通常向后兼容旧版 JupyterLab（只是可能包含旧版中没有的字符串，但不会缺失）。

## 相关概念

- [repository-map.yml 配置详解](03-repository-map-config.md)
- [自动化脚本体系](07-automation-scripts.md)
- [发布流程](09-release-workflow.md)
