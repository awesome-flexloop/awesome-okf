---
type: Reference
title: "源码登记与版本固定"
description: "cnblogs-skills 仓库（cnblogs-publish skill）的信源固定信息、12 个文件清单与 SHA256、四模块结构、依赖与测试基线。"
tags: ["cnblogs", "source-code", "reference", "provenance", "skill"]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T10:40:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T10:40:00Z" }
status: stable
stale_after: "2027-11-10T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
---

# 源码登记与版本固定

本文件登记 `cnblogs-skills` 仓库及其唯一 skill `cnblogs-publish` 的固定版本与文件清单，作为本束所有概念文档的溯源基线。

## 版本固定

| 属性 | 值 |
|------|-----|
| 仓库 | `https://github.com/cnblogs/cnblogs-skills` |
| 提交 | `6f446adb7459df1d983b0c9a2088417f01ffba41` |
| 提交时间 | 2026-11-10 15:24:34 +08:00 |
| 分支 | `main`（`origin/main` 同点） |
| Tag | 无（`git tag --list` 为空），按 commit hash 固定 |
| 仓库结构 | 根目录每个文件夹是一个 skill；当前仅 `cnblogs-publish` |
| 许可 | 仓库未提供 LICENSE 文件（以仓库现状为准） |

采集现场为主仓库中被 `.gitignore` 忽略的本地克隆（`external/dao/cnblogs-skills`）。该路径不作为文档引用目标：本束只引用本文件登记的 commit 与文件哈希，需要复核时按 commit 重新检出即可复现。

## 文件清单（12 个文件，3,775 行）

行数由脚本对 UTF-8 文本执行 `splitlines()` 统计；字节数与 SHA256 为文件原始内容。

| 文件 | 行数 | 字节 | SHA256 |
|------|------|------|--------|
| `README.md` | 9 | 425 | `d9ecd1949b618470fdff0b77b6bef733f05417a8da738579e3e617d091f47301` |
| `cnblogs-publish/SKILL.md` | 240 | 12716 | `a244a50a588c486fee221c042ec2e53d3edf3f1fe47d41fb6e83c58cba70b1ef` |
| `cnblogs-publish/README.md` | 91 | 3976 | `adf9be816ad57974cc133522ceaf862eb8c6e7a0e5c80ee144def60c4a7c1c2c` |
| `cnblogs-publish/.gitignore` | 3 | 34 | `abb8edff56ab7d94b4839a59ecbd5547c8030b37a5a4f78989246cb2acd08b78` |
| `cnblogs-publish/references/metaweblog-api.md` | 151 | 7025 | `390be88d140c3ec479ea39024d6329c98d35d7e66550a856ac8c1ae0f6657567` |
| `cnblogs-publish/references/security.md` | 124 | 5962 | `217caf843bf7e5459d544ea74d6bce7dc30c96d7dab3501ab57b551cd35c76f4` |
| `cnblogs-publish/scripts/cnblogs.py` | 1346 | 52331 | `b4a84cba7ae8aa70c154bac60379359101a01050770bc8f9cf4fdf986754af33` |
| `cnblogs-publish/scripts/dialogs.py` | 203 | 7437 | `7e50e50f41f63f5d7ee9caf698dcd85e73be8d668fe305cf47e637e0762b94f5` |
| `cnblogs-publish/scripts/md2html.py` | 350 | 12132 | `b3f03c4f11ccc3d2fa8722ce851b2cd434a3533d61dc1fb7a2540bd4eb1a9a1e` |
| `cnblogs-publish/scripts/secretstore.py` | 417 | 15847 | `523c0f7417782c7be21c02f6ed48778dd701ab95bc3f3dba046f9fa62b2c174f` |
| `cnblogs-publish/tests/README.md` | 43 | 2131 | `dd2610e85c09bb7cc01790f2ac7f0d72c315647f149b356c6e4104043aac502a` |
| `cnblogs-publish/tests/test_local.py` | 798 | 35042 | `8aed203a8834d08ebe89f80e08e7963714fbe19c4c1db56f740d80f578f406d3` |

## 模块结构

```text
cnblogs-skills/
├── README.md                       # 仓库说明：博客园官方 Skills 仓库
└── cnblogs-publish/
    ├── SKILL.md                    # Skill 定义与使用约束（240 行）
    ├── README.md                   # 产品向介绍文章（91 行）
    ├── references/
    │   ├── metaweblog-api.md       # MetaWeblog 端点/方法/博客园约定
    │   └── security.md             # 凭据安全设计与平台差异
    ├── scripts/
    │   ├── cnblogs.py              # CLI + 业务流程（1,346 行，49 函数/4 类）
    │   ├── secretstore.py          # 4 种系统凭据后端（417 行）
    │   ├── dialogs.py              # 跨平台原生输入对话框（203 行）
    │   └── md2html.py              # 零依赖 Markdown→HTML 子集（350 行）
    └── tests/
        ├── README.md               # 多平台测试说明
        └── test_local.py           # 15 类 / 50 个测试方法（798 行）
```

## 依赖与运行环境

- 运行时仅用 Python 标准库：`argparse`、`xmlrpc.client`、`ctypes`、`subprocess`、`urllib`、`ssl`、`json`、`re` 等（F-007）。
- Linux 的 `keyring` 是可选依赖；优先 `secret-tool`。
- 调用方式示例：`python scripts/cnblogs.py <command>`；Windows 用 `python` 或 `py -3`。
- 入口 `main()` 捕获 `UserError`、`DialogError`、`SecretStoreError`、`xmlrpc.client.Fault/ProtocolError`、超时与 `OSError`，统一经 `_fail` 脱敏后输出。

## 测试基线

在采集环境（Windows，Python 3）执行：

```text
python -m unittest discover -s tests -v
Ran 50 tests in 0.633s
OK (skipped=1)
```

跳过项为 `test_linux_secret_tool_real_subprocess`（POSIX shell helper 在 Windows 不可用）。测试类共 15 个，测试方法 50 个（F-042/F-043）。

## 相关文档

- [MetaWeblog 接口与博客园约定](/references/api-and-conventions.md)
- [凭据安全设计](/references/security-design.md)
- [项目概览](/concepts/00-overview.md)
