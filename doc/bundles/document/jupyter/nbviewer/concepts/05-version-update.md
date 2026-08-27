---
type: Concept
title: "版本更新机制"
description: "nbviewer版本存在于两个位置（cd.yml和config/nbviewer.yaml），update-nbviewer.py自动检测更新，watch-dependencies每日开PR"
tags: [nbviewer, deploy, version, update, automation, docker-hub, chart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T12:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: update-script
    resource: "/references/cicd-source.md#scriptsupdate-nbviewerpy-更新脚本"
    title: "更新脚本信源"
  - id: watch-deps
    resource: "/references/cicd-source.md#watch-dependenciesyaml自动更新检查"
    title: "watch-dependencies信源"
---

# 版本更新机制

nbviewer.org-deploy 的版本更新涉及两个位置的版本号同步，通过 `scripts/update-nbviewer.py` 脚本自动检测和更新。

## 版本号存在位置

nbviewer的版本号同时存在于**两个地方**，必须保持同步：

| 位置 | 文件 | 变量 | 含义 |
|------|------|------|------|
| Chart版本 | `.github/workflows/cd.yml` | `NBVIEWER_VERSION` | nbviewer仓库的Git commit hash（完整40位） |
| 镜像版本 | `config/nbviewer.yaml` | `image` | Docker镜像标签（短commit hash，如`a53d108`） |

### 为什么有两个版本号？

- **Chart版本** (`NBVIEWER_VERSION`)：CI在部署时checkout jupyter/nbviewer仓库的特定commit，从中获取Helm chart。需要完整commit hash。
- **镜像版本** (`image`)：部署到Kubernetes的Docker镜像标签。Docker Hub上的镜像tag使用短commit hash（7位）。

这两个版本号应该对应同一个nbviewer commit，但存储格式不同。

## scripts/update-nbviewer.py 详解

此脚本是版本更新的核心，被watch-dependencies工作流调用，也可本地运行。

### 四个查询函数

```python
def get_current_chart():     # 从cd.yml读取当前NBVIEWER_VERSION
def get_latest_chart():      # git ls-remote获取nbviewer仓库HEAD
def get_current_image():     # 从config/nbviewer.yaml读取当前image
def get_latest_image():      # Docker Hub API获取最新tag
```

#### get_current_chart()

```python
def get_current_chart():
    with cd_yaml.open() as f:
        cd = yaml.safe_load(f)
    chart_rev = cd["env"]["NBVIEWER_VERSION"]
    return chart_rev
```

使用 `yaml.safe_load` 解析cd.yml，读取 `env.NBVIEWER_VERSION` 字段。

#### get_latest_chart()

```python
def get_latest_chart():
    out = check_output(
        ["git", "ls-remote", "https://github.com/jupyter/nbviewer", "HEAD"], text=True
    ).strip()
    return out.split()[0]
```

通过 `git ls-remote` 命令查询nbviewer远程仓库的HEAD引用，返回最新的完整commit hash。不需要clone仓库。

#### get_current_image()

```python
def get_current_image():
    with nbviewer_config_yaml.open() as f:
        config = yaml.safe_load(f)
    current_image = config["image"]
    return current_image
```

从config/nbviewer.yaml读取当前image字段（如 `jupyter/nbviewer:a53d108`）。

#### get_latest_image()

```python
def get_latest_image():
    r = requests.get("https://hub.docker.com/v2/repositories/jupyter/nbviewer/tags")
    r.raise_for_status()
    tags = r.json()
    tag = tags["results"][0]["name"]
    return f"jupyter/nbviewer:{tag}"
```

查询Docker Hub API `/v2/repositories/jupyter/nbviewer/tags`，取结果列表第一个tag（通常是最新的）。

**注意**：Docker Hub tags API默认按更新时间排序，第一个结果是最新推送的tag。

### 两个更新函数

```python
def update_chart():   # 更新cd.yml中的NBVIEWER_VERSION
def update_image():   # 更新config/nbviewer.yaml中的image
```

更新逻辑相同：
1. 获取当前版本和最新版本
2. 通过GITHUB_OUTPUT输出before/after/short变量
3. 如果版本不同，用字符串替换（`str.replace`）更新文件
4. 如果版本相同，不做任何修改

**更新方式**：使用简单的字符串替换（`replace(old, new, 1)`），只替换第一次出现。这意味着版本号格式必须精确匹配。

### 输出变量

脚本通过 `_maybe_output()` 函数输出变量，在CI中写入 `GITHUB_OUTPUT`，本地运行时打印到stdout：

| 变量 | 说明 | 用途 |
|------|------|------|
| `chart_before` | 更新前的chart commit | PR描述 |
| `chart_after` | 更新后的chart commit | PR描述 |
| `chart_short` | 新版本短hash（前7位） | PR标题 |
| `image_before` | 更新前的镜像 | PR描述 |
| `image_after` | 更新后的镜像 | PR描述 |
| `image_tag` | 新镜像tag部分 | PR描述 |

## scripts/get-prs.py PR摘要

此脚本从mybinder.org-deploy项目复制（BSD-3-Clause许可），用于提取两个commit之间的PR列表。

### 功能

1. 使用PyGithub库调用GitHub API
2. 通过 `repo.compare(start, end)` 获取两个commit之间的所有commit
3. 对每个非merge commit（单parent commit），调用 `get_pulls()` 获取关联的PR
4. 生成Markdown格式的PR列表
5. 支持写入GitHub Actions多行输出变量

### Git Ref提取

`extract_gitref()` 函数可以从多种版本格式中提取commit hash：

| 格式 | 示例 | 提取结果 |
|------|------|---------|
| 纯版本号 | `2022.02.0` | `2022.02.0`（原样） |
| chartpress格式 | `2022.02.0-90.g0345a86` | `0345a86` |
| setuptools-scm格式 | `0.2.0-n1011.hb49edf6` | `b49edf6` |
| dev格式 | `0.2.0-0.dev.git.2752.h3450e52` | `3450e52` |

这支持chartpress（Jupyter项目常用的chart构建工具）生成的版本号格式。

## 自动更新流程

```
每日UTC 5:00 (cron)
    │
    ▼
watch-dependencies.yaml 触发
    │
    ├─ python3 scripts/update-nbviewer.py
    │    │
    │    ├─ git ls-remote → 获取nbviewer最新commit
    │    ├─ Docker Hub API → 获取最新镜像tag
    │    ├─ 对比当前版本
    │    └─ 有更新? → 替换cd.yml和config/nbviewer.yaml
    │
    ├─ git diff --exit-code
    │    │
    │    └─ 无变更 → changed=false → 结束
    │
    └─ 有变更 (changed=true)
         │
         ├─ ./scripts/get-prs.py 获取PR列表
         │
         └─ peter-evans/create-pull-request@v7
              │
              ├─ 创建/更新 update-nbviewer 分支
              ├─ 提交信息: "Update nbviewer version to <short_hash>"
              └─ PR描述包含:
                   - chart版本更新
                   - 镜像版本更新
                   - 版本间PR列表
                   - 相关链接
```

## 手动更新步骤

虽然自动更新每日运行，也可以手动触发或执行：

### 方式1：手动触发workflow

在GitHub UI上手动运行 "Watch dependencies" workflow。

### 方式2：本地运行脚本

```bash
# 安装依赖
pip install -r requirements.txt

# 运行更新脚本
python3 scripts/update-nbviewer.py

# 查看变更
git diff

# 如果变更正确，提交并创建PR
git checkout -b update-nbviewer
git add .github/workflows/cd.yml config/nbviewer.yaml
git commit -m "Update nbviewer version to <short_hash>"
gh pr create --title "Update nbviewer version" --body "Manual update"
```

### 方式3：手动编辑版本号

1. 检查nbviewer最新commit：访问 https://github.com/jupyter/nbviewer/commits/main
2. 复制完整commit hash到 `.github/workflows/cd.yml` 的 `NBVIEWER_VERSION`
3. 检查Docker Hub最新tag：访问 https://hub.docker.com/r/jupyter/nbviewer/tags
4. 更新 `config/nbviewer.yaml` 的 `image` 字段为 `jupyter/nbviewer:<tag>`
5. 提交PR

## 版本更新后自动部署

版本更新PR合并到main分支后：

1. cd.yml自动触发
2. CI checkout新版本的nbviewer仓库（新的NBVIEWER_VERSION）
3. 使用新的Docker镜像部署
4. pytest冒烟测试验证
5. 如果部署成功，新版本上线
6. **如果后端IP未变，无需更新Fastly CDN**

## 注意事项

1. **等待镜像构建**：nbviewer的Docker镜像在commit合并后需要几分钟构建推送到Docker Hub。自动更新脚本通过Docker Hub API获取最新tag，如果镜像尚未推送，可能检测不到最新版本（下一次cron会重试）。

2. **两个版本号必须同步**：只更新其中一个会导致chart版本和镜像版本不一致。`update-nbviewer.py` 同时更新两者。

3. **短hash vs 完整hash**：cd.yml中使用完整40位commit hash（checkout需要），config/nbviewer.yaml中使用7位短hash（Docker tag）。脚本自动处理格式差异。

4. **PR幂等性**：自动更新使用固定分支名 `update-nbviewer`，如果已有未合并的更新PR，新的运行会更新同一PR而不是创建新PR。

5. **Fastly不需要更新**：常规版本更新只改变镜像tag，不改变后端IP地址，因此不需要运行 `invoke fastly`。

## 相关文档

- [CI/CD与自动化](04-cicd-and-automation.md)
- [Helm部署流程](06-helm-deploy-process.md)
- [手动升级示例](../examples/manual-upgrade.md)
