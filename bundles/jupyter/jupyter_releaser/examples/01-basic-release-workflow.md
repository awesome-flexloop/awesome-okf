---
type: Example
title: "典型发布流程全步骤"
description: "从版本准备到发布完成的完整操作示例，展示维护者的实际操作步骤和工作流触发方式"
tags: [workflow, release, end-to-end]
stage: "入门"
prerequisites:
  - "/concepts/01-getting-started.md"
  - "/concepts/05-release-pipeline.md"
sources:
  - /facts.md
---

# 典型发布流程全步骤

本示例演示一个 Python + npm 混合项目（如 Jupyter Lab Extension）的完整发布流程。

## 前置条件

- 项目已接入 jupyter_releaser（工作流文件已配置）
- ADMIN_GITHUB_TOKEN、NPM_TOKEN、PyPI OIDC 已配置
- CHANGELOG.md 中包含 START/END 标记
- tbump.toml（或 hatch/bump2version）已配置

## 步骤一：触发 Prep Release

**方式 A：通过标签触发**

1. 打开 GitHub 仓库的 Issues 页面
2. 创建一个新 Issue，标题为 "Release v1.2.0"（标题任意）
3. 添加 `prep-release` 标签
4. 等待 GitHub Actions 自动运行 Prep Release 工作流

**方式 B：通过 workflow_dispatch 触发**

1. 进入仓库 Actions 页面
2. 选择 "Step 1: Prep Release" 工作流
3. 点击 "Run workflow"
4. 选择分支（通常是 `main`）
5. version_spec 填入 `next`（或具体版本号如 `1.2.0`）
6. since_last_stable 勾选
7. 点击 "Run workflow"

## 步骤二：审核 Changelog PR 和 Draft Release

Prep 工作流完成后：

1. **检查 Changelog PR**：
   - 会有一个新 PR，标题类似 "Publish 1.2.0"
   - 分支名为 `changelog-<uuid>`
   - 检查 CHANGELOG.md 中的变更内容是否正确
   - 检查贡献者是否被正确标注
   - 确认版本号正确

2. **检查 Draft Release**：
   - 进入仓库 Releases 页面
   - 找到新创建的 Draft Release（tag: v1.2.0）
   - 检查 Release Notes（changelog 内容）
   - 检查 Target branch 是否正确
   - 检查 "This is a pre-release" 勾选状态

3. **如有问题，修正后重新触发**：
   - 删除 Draft Release
   - 关闭 Changelog PR
   - 修正问题（如手动编辑 changelog 标记位置）
   - 重新触发 Prep

## 步骤三：合并 Changelog PR

确认 Changelog PR 内容正确后：
1. 合并 Changelog PR 到 main 分支
2. 删除 Changelog PR 分支（GitHub 会提示）
3. 等待 main 分支的 CI 通过

## 步骤四：触发 Populate Release

1. 进入 Releases 页面，打开刚才的 Draft Release
2. 编辑 Draft Release（点击编辑按钮，不需要修改任何内容）
3. 直接点击 "Update release"（这会触发 `release.edited` 事件）
4. 或者：在 Draft Release 上添加 `publish-release` 标签

Populate 工作流将自动运行：
- 构建 npm 包
- 检查 npm 包
- 构建 Python 包
- 检查 Python 包
- 创建 release commit 和 tag
- 上传资产到 Draft Release

## 步骤五：审核资产

Populate 工作流完成后：

1. 回到 Draft Release 页面
2. 检查 Assets 区域是否有：
   - `{name}-1.2.0.tar.gz`（Python sdist）
   - `{name}-1.2.0-py3-none-any.whl`（Python wheel）
   - `{name}-1.2.0.tgz`（npm 包，如果有 npm 项目）
   - `asset_shas.json`（SHA256 校验文件）
3. 下载 .whl 文件，本地安装验证：
   ```bash
   pip install path/to/downloaded/{name}-1.2.0-py3-none-any.whl
   ```
4. 检查 tag v1.2.0 是否正确创建

## 步骤六：发布 Release

1. 确认所有资产正确
2. 如果需要最后修正（如手动更新 release notes），编辑 Draft Release
3. 点击 **"Publish release"** 按钮（不是 Save draft！）

这会触发 Finalize 工作流：
- 下载并验证资产 SHA256
- 发布 .tgz 到 npm
- 发布 .whl/.tar.gz 到 PyPI（通过 OIDC Trusted Publishing）
- 创建 forwardport Changelog PR
- 将 GitHub Release 从 Draft 转为 Published

## 步骤七：验证发布结果

发布完成后验证：

1. **PyPI**：访问 `https://pypi.org/project/{name}/1.2.0/`，确认版本存在
2. **npm**：访问 `https://www.npmjs.com/package/{name}?activeTab=versions`，确认版本存在
3. **GitHub Release**：确认 Release 已发布（不再是 Draft）
4. **Forwardport PR**：检查是否有新的 Changelog forwardport PR，合并它
5. **本地安装验证**：
   ```bash
   pip install {name}==1.2.0
   npm install {name}@1.2.0
   ```

## 步骤八：后处理

1. 合并 forwardport Changelog PR
2. 关闭 Release Issue（如果有创建）
3. 通知社区（论坛、Twitter、Discord 等）
4. 在里程碑页面关闭对应 milestone

## 常见问题处理

### Changelog PR 内容不正确

```
解决方案：
1. 关闭 Changelog PR
2. 删除 Draft Release
3. 检查 since 参数是否正确
4. 检查 START/END 标记在 CHANGELOG.md 中的位置
5. 重新触发 prep-release，指定正确的 since 参数
```

### Populate 阶段资产构建失败

```
解决方案：
1. 查看 Actions 日志找到失败原因（通常是构建依赖问题）
2. 修复代码问题
3. 删除 Draft Release 和已创建的 tag（如果有）
4. 重新触发 prep-release
```

### Finalize 阶段 npm/PyPI 发布失败

```
解决方案：
1. 确认 NPM_TOKEN 有效且是 Automation 类型
2. 确认 PyPI OIDC Publisher 配置正确
3. 如果是网络问题，可以重新运行 Finalize workflow
4. 已成功上传的包会跳过（E409 幂等处理）
```
