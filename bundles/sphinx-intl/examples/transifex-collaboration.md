---
type: example
title: "Transifex 协作翻译"
description: "使用 Transifex 云端平台进行多人协作翻译的完整配置和工作流，包括 tx CLI 安装、项目配置、推送拉取"
tags: [transifex, collaboration, cloud, tx-cli, team-translation]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T14:52:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-21T14:52:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: transifex-api
    resource: /references/transifex-api.md
    title: "transifex.py Transifex 集成 API 参考"
  - id: commands-api
    resource: /references/commands-api.md
    title: "CLI 入口 API 参考"
  - id: official-docs
    resource: "https://sphinx-intl.readthedocs.io"
    title: "sphinx-intl 官方文档"
---

# Transifex 协作翻译

当翻译团队有多个人协作时，手动传递 PO 文件效率低下且容易冲突。[Transifex](https://www.transifex.com) 是一个流行的云端翻译协作平台，提供 Web 翻译界面、翻译记忆、术语表、团队权限管理等功能。sphinx-intl 提供了自动配置 Transifex CLI 的功能。

## 前置条件

1. 已完成基本翻译环境搭建（参见[基本翻译全流程](basic-translation.md)的步骤 1-3）
2. Transifex 账号（在 <https://www.transifex.com> 注册）
3. Transifex 上已创建组织和项目

## 步骤 1：安装 Transifex CLI

sphinx-intl 的 Transifex 功能依赖外部 `tx` 命令行工具：

```bash
# Linux/macOS
curl -o- https://raw.githubusercontent.com/transifex/cli/master/install.sh | bash

# 验证安装
tx --version
# 应输出: TX Client=1.x.x
```

sphinx-intl 要求 Transifex CLI 版本 ≥ 1.2.1。

## 步骤 2：配置认证

推荐使用 `TX_TOKEN` 环境变量（现代方式）：

1. 在 Transifex 网站上：User Settings → API Tokens → Generate a token
2. 设置环境变量：

```bash
# Bash/Zsh
export TX_TOKEN=your_api_token_here

# PowerShell
$env:TX_TOKEN = "your_api_token_here"
```

或者将 token 写入 `~/.transifexrc` 文件（传统方式，不推荐）：

```bash
sphinx-intl create-transifexrc --transifex-token your_api_token_here
```

> **注意**：`create-transifexrc` 命令已标记为废弃（DeprecationWarning），建议使用 `TX_TOKEN` 环境变量。

## 步骤 3：初始化 Transifex 配置

在 Sphinx 项目根目录执行：

```bash
# 创建 .tx/config 初始化文件
sphinx-intl create-txconfig
```

这会创建 `.tx/config` 文件，初始内容：

```ini
[main]
host = https://www.transifex.com
```

## 步骤 4：自动注册资源

假设你的 Transifex 组织名为 `my-org`，项目名为 `my-docs`：

```bash
sphinx-intl update-txconfig-resources \
  --transifex-organization-name my-org \
  --transifex-project-name my-docs \
  --pot-dir _build/gettext \
  --locale-dir locale
```

如果已经配置了 conf.py 并能自动检测到 pot_dir 和 locale_dir，可以简化为：

```bash
sphinx-intl update-txconfig-resources \
  --transifex-organization-name my-org \
  --transifex-project-name my-docs
```

执行过程中会显示进度条：

```
adding pots...  [####################################]  100%  _build/gettext/refs.pot
```

执行后 `.tx/config` 文件会被更新，为每个 POT 文件添加资源段：

```ini
[main]
host = https://www.transifex.com

[o:my-org:p:my-docs:r:index]
file_filter = locale/<lang>/LC_MESSAGES/index.po
source_file = _build/gettext/index.pot
source_lang = en
type = PO

[o:my-org:p:my-docs:r:install]
file_filter = locale/<lang>/LC_MESSAGES/install.po
source_file = _build/gettext/install.pot
source_lang = en
type = PO
```

### 资源名处理规则

sphinx-intl 会自动处理 Transifex 的资源命名限制：

1. **路径分隔符**：`docs/index` → `docs--index`（`/` 和 `\` 替换为 `--`）
2. **非法字符**：`chapter1.section2` → `chapter1_section2`（非字母数字/`-`/`_` 替换为 `_`）
3. **保留名冲突**：`glossary` → `glossary_`（追加下划线避免保留 slug）

### 空 POT 文件自动跳过

如果某个 POT 文件不包含任何可翻译消息（如仅包含 toctree 指令的索引页），sphinx-intl 会输出提示并跳过：

```
_build/gettext/toc.pot is empty, skipped
```

## 步骤 5：上传源文件到 Transifex

配置完成后，使用 `tx` 命令上传 POT 源文件：

```bash
tx push -s
```

- `-s` 表示推送源文件（source，即英文 POT）
- 如果要同时推送已有的翻译，使用 `tx push -s -t -l ja`（推送源文件+日语翻译）

上传后，登录 Transifex 网站可以看到项目和资源已创建，翻译团队可以开始在线翻译。

## 步骤 6：拉取翻译

当翻译人员在 Transifex 上完成翻译后，将翻译拉回本地：

```bash
# 拉取所有语言的翻译
tx pull -a

# 只拉取日语和简体中文，且只拉取翻译完成度≥80%的
tx pull -l ja,zh_CN --minimum-perc=80

# 拉取时包含 fuzzy 翻译（默认只拉取已审校的翻译）
tx pull -l ja --use-git-timestamps
```

拉取后，PO 文件会被更新到 `locale/<lang>/LC_MESSAGES/` 目录。

## 步骤 7：编译和构建

拉取翻译后的操作与本地翻译相同：

```bash
# 编译 MO
sphinx-intl build

# 构建日语文档
make -e SPHINXOPTS="-Dlanguage='ja'" html
```

## 完整协作工作流

```
┌──────────────────────────────────────────────────────────────────┐
│                        文档作者（本地）                           │
│  1. 编辑 RST 文件                                                │
│  2. make gettext → 更新 POT                                      │
│  3. sphinx-intl update-txconfig-resources → 更新 .tx/config       │
│  4. tx push -s → 上传新的源文件到 Transifex                      │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Transifex 云端平台                             │
│  5. 翻译人员在 Web 界面翻译                                       │
│     - 翻译记忆（TM）自动匹配相似字符串                              │
│     - 术语表保持术语一致性                                         │
│     - 审校流程（翻译→审校→发布）                                   │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      构建维护者（本地）                           │
│  6. tx pull -l ja -l zh_CN → 拉取已翻译的 PO                      │
│  7. sphinx-intl build → 编译 MO                                  │
│  8. make html SPHINXOPTS="-Dlanguage=ja" → 构建发布              │
└──────────────────────────────────────────────────────────────────┘
```

## 日常更新命令（Makefile 集成）

在 Makefile 中添加便捷目标：

```makefile
# Transifex 操作
tx-push:
    make gettext
    sphinx-intl update-txconfig-resources \
        --transifex-organization-name my-org \
        --transifex-project-name my-docs
    tx push -s

tx-pull:
    tx pull -l ja,zh_CN --minimum-perc=80
    sphinx-intl build

tx-pull-all:
    tx pull -a
    sphinx-intl build
```

日常使用：

```bash
make tx-push    # 文档更新后推送新的源文件
make tx-pull    # 翻译完成后拉取并编译
```

## 常见问题

### Q: tx push 报错 "Authentication failed"？

检查 `TX_TOKEN` 环境变量是否正确设置：
```bash
echo $TX_TOKEN  # Linux/macOS
echo $env:TX_TOKEN  # PowerShell
```
确保 token 没有多余空格或换行。

### Q: update-txconfig-resources 报错 "Could not run tx"？

说明 Transifex CLI 未安装或不在 PATH 中。重新安装并确保 `tx --version` 能正常输出。

### Q: 资源名包含非法字符导致 Transifex 报错？

sphinx-intl 的 `normalize_resource_name()` 已自动处理大部分情况，但如果你的 POT 文件名包含特殊字符（如中文），可能需要手动在 `.tx/config` 中调整 resource slug。

### Q: 如何在 CI/CD 中自动拉取翻译？

在 GitHub Actions 等 CI 环境中：

```yaml
- name: Pull translations
  env:
    TX_TOKEN: ${{ secrets.TX_TOKEN }}
  run: |
    tx pull -l ja,zh_CN
    sphinx-intl build
```

将 `TX_TOKEN` 配置为仓库的 Secret。

## 相关概念

- [Transifex 平台集成](/concepts/07-transifex-integration.md)
- [基本翻译全流程](basic-translation.md)
- [CLI 命令体系详解](/concepts/02-cli-commands.md)
