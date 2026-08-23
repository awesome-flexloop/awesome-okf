---
type: Example
title: 项目更新工作流
description: 使用 copier update 更新已有项目、处理冲突、版本迁移、最佳实践
tags: [copier, update, workflow, conflict-resolution, migrations, recopy, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-22T11:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: copier-src
    resource: /references/copier-source.md
    title: "Copier 源码"
---

# 项目更新工作流

本示例展示 Copier 的项目更新能力——当模板发布新版本后，已有项目可以智能更新，保留本地修改的同时应用模板变更。这是 Copier 区别于 Cookiecutter 等一次性脚手架工具的核心能力。[^copier-src]

## 1. 更新前置条件

要使用 `copier update`，目标项目必须满足：

1. 项目目录中存在 `.copier-answers.yml` 文件
2. answers 文件中包含 `_src_path`（原始模板路径/URL）
3. answers 文件中包含 `_commit`（使用的模板版本）
4. 如果要保留本地演化，目标项目应该是一个 Git 仓库（非必须但强烈推荐）

典型的 `.copier-answers.yml`：
```yaml
_commit: v1.0.0
_src_path: https://github.com/myorg/python-template.git
project_name: my-app
package_name: my_app
author_name: Zhang San
python_version: "3.12"
use_docker: false
```

## 2. 基本更新流程

```bash
# 进入项目目录
cd my-app

# 检查是否有更新
copier check-update
# 输出: New template version available. Current version is v1.0.0, latest version is v2.0.0.

# 执行更新（交互式）
copier update
```

更新时 Copier 会：
1. 读取 `.copier-answers.yml` 获取模板来源和当前版本
2. 克隆/拉取最新模板
3. 比较新旧模板差异（基于 PEP440 版本）
4. 询问之前未回答或新增的问题
5. 执行 before 迁移任务
6. 三向合并文件变更（旧模板→新模板 vs 旧模板→当前项目）
7. 执行 after 迁移任务
8. 更新 `.copier-answers.yml` 中的 `_commit`

## 3. 非交互式更新

CI/CD 或自动化场景中使用非交互模式：

```bash
# 使用上次答案和默认值，不询问任何问题
copier update --defaults --skip-answered --trust

# 或者强制覆盖所有变更
copier update --defaults --trust

# 预演更新（不实际修改文件）
copier update -n --defaults --trust
```

### 更新选项组合

| 场景 | 命令 |
|------|------|
| 全交互更新 | `copier update` |
| 仅回答新问题 | `copier update --skip-answered` |
| 全自动更新 | `copier update -lA --trust` |
| 全量覆盖（丢弃本地修改） | `copier recopy -f --trust` |
| 检查更新（脚本中） | `copier check-update -q` |

## 4. 冲突处理

当本地修改和模板变更冲突时，Copier 提供两种冲突解决方式。

### inline 模式（默认）

```bash
copier update --conflict inline
```

冲突文件中会插入内联合并标记：

```python
# config.py
<<<<<<< before update
DEBUG = True  # 本地修改
=======
DEBUG = False  # 模板新默认值
>>>>>>> after update
DATABASE_URL = "sqlite:///./app.db"
```

需要手动编辑解决冲突，然后删除标记行。

### rej 模式

```bash
copier update --conflict rej
```

不修改原文件，而是生成 `.rej` 文件（unified diff 格式）记录无法自动合并的变更：

```diff
--- a/config.py
+++ b/config.py
@@ -1,3 +1,3 @@
-DEBUG = True
+DEBUG = False
```

`.rej` 文件可以使用 `patch` 命令手动应用，或逐个审查。

### 上下文行数

`--context-lines N` 控制冲突检测时考虑的上下文行数：

```bash
# 更多上下文 = 更精确但可能产生更多冲突
copier update -c 10

# 更少上下文 = 更宽松，冲突更少但可能错误合并
copier update -c 1
```

默认值 3 通常是较好的平衡点。

## 5. 版本迁移脚本

当模板新版本需要对已有项目做数据迁移时（如重命名文件、修改配置格式），使用 `_migrations`。

### 场景：v1 → v2 重命名配置文件

模板 v2 的 `copier.yml`：

```yaml
_migrations:
  # v2.0.0 迁移：将 config.yaml 重命名为 config.yml
  - version: "2.0.0"
    when: "{{ _stage == 'before' }}"
    command: |
      if [ -f config.yaml ]; then
        mv config.yaml config.yml
        echo "Renamed config.yaml to config.yml"
      fi

  # v2.0.0 后：安装新依赖
  - version: "2.0.0"
    when: "{{ _stage == 'after' }}"
    command: "pip install -e '.[dev]'"
```

执行 `copier update` 时：
1. 检测到当前版本 v1.0.0 < 2.0.0 ≤ 新版本
2. before 阶段：运行重命名命令
3. 渲染新模板文件
4. after 阶段：安装新依赖

### 场景：v2 → v3 数据格式转换

```yaml
_migrations:
  - version: "3.0.0"
    when: "{{ _stage == 'before' }}"
    command: ["python", "-c", "import json,yaml; yaml.safe_dump(json.load(open('config.json')), open('config.yaml','w'))"]
    working_directory: "."
```

使用 argv 列表格式执行 Python 代码进行数据格式迁移，更安全。

## 6. recopy vs update

| 操作 | 本地修改 | 迁移任务 | 答案保留 | 适用场景 |
|------|---------|---------|---------|---------|
| `copier update` | ✅ 保留 | ✅ 执行 | ✅ 保留 | 常规更新，保留本地演化 |
| `copier recopy` | ❌ 丢弃 | ❌ 不执行 | ✅ 保留 | 想重置到模板状态但保留答案 |
| `copier copy` | ❌ 覆盖/询问 | ✅ 执行 | ❌ 需重新回答 | 全新创建或完全重置 |

```bash
# 保留本地修改的智能更新
copier update --trust

# 保留答案但丢弃所有本地修改（重置）
copier recopy -f --trust

# 完全从头开始（相当于删了重建）
rm -rf my-app && copier copy -f --trust template/ my-app
```

## 7. 更新最佳实践

### 1. 项目必须用 Git 管理

```bash
# 更新前确保工作区干净
git status  # 应该是 clean 状态或已提交
git checkout -b template-update  # 创建更新分支
copier update --trust
# 审查变更
git diff
# 解决冲突后
git add . && git commit -m "Update template to v2.0.0"
```

### 2. 使用 --pretend 预演

```bash
copier update -n --defaults --trust
# 查看将要创建/覆盖/冲突的文件，不实际修改
```

### 3. 固定模板版本（CI 场景）

```bash
# 项目初始时指定版本
copier copy -r v1.0.0 gh:org/tpl my-project

# 更新时显式指定目标版本
copier update -r v2.0.0 --trust
```

### 4. check-update 自动化检查

```bash
#!/bin/bash
# 定期检查模板更新脚本
if copier check-update -q 2>/dev/null; then
    echo "Project is up to date"
else
    echo "Update available!"
    copier check-update --output-format json
fi
```

在 CI 中可以配置为：有更新时创建 PR 或发送通知。

### 5. 处理答案变更

新版本模板可能新增问题。使用 `--skip-answered` 跳过已有答案的问题，只回答新增的：

```bash
copier update -A --trust
```

如果想重新回答某些问题，使用 `--ask`：

```bash
# 强制询问所有 db_ 开头的问题
copier update --ask "db_*" --trust
```

### 6. 大版本跳跃更新

从 v1 直接更新到 v3 时，v2 的迁移任务也会执行（如果版本范围匹配）。确保迁移脚本是幂等的：

```yaml
_migrations:
  - version: "2.0.0"
    when: "{{ _stage == 'before' }}"
    command: |
      # 使用条件检查确保幂等
      [ -f old_config.json ] && python migrate_v1_to_v2.py || echo "Already migrated"
```

## 8. 更新后验证

更新完成后验证项目完整性：

```bash
# 运行测试
pytest

# 检查应用是否正常启动
python -c "import my_app; print('Import OK')"

# 检查 answers 文件已更新
grep _commit .copier-answers.yml
```

## 相关概念

* [Worker 与生命周期](../concepts/05-worker-and-lifecycle.md)
* [VCS 集成与版本管理](../concepts/06-vcs-integration.md)
* [任务与迁移](../concepts/07-tasks-and-migrations.md)
* [问题与答案系统](../concepts/03-questions-and-answers.md)
* [CLI 命令参考](../concepts/08-cli-reference.md)
* [任务与自动化钩子示例](tasks-and-hooks.md)

[^copier-src]: Copier 源码，见本 bundle 信源登记 [references/copier-source.md](/references/copier-source.md)。
