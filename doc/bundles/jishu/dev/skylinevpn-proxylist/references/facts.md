---
type: Reference
title: "事实登记：skylinevpn-proxylist F-001 ~ F-068"
description: "分五节登记仓库与版本、数据文件、编译管线、发布工作流、治理与边界的事实，每条附依据来源"
generated: { by: "seven-concepts-cmd", at: "2026-11-21T17:00:00+08:00" }
status: stable
---

# 事实登记

> **引用纪律**：正文不复制易腐数字，一律以 `F-编号` 引用本页。编号只追加、不复用、不重排。
>
> **性质标注**：`[事实]` = 可直接对照源码/配置/git 元数据；`[清点]` = 本次对数据文件的统计或抽样；`[文档口径]` = 仓库文档的自我描述。

## A. 仓库与版本（F-001 ~ F-012）

| 编号 | 事实 | 性质 | 依据 |
|------|------|------|------|
| F-001 | HEAD 为 `9c6567cf6f94e960cbfe6db02b33b08bc50a64c6` | 事实 | `git rev-parse HEAD` |
| F-002 | 仓库共 7 次提交；首次 `effb8c5`（2026-10-16），最新 `9c6567c`（2026-11-16） | 事实 | `git log --format='%h\|%ad\|%s' --date=short` |
| F-003 | 当前分支 `main` 跟踪 `origin/main`，工作区无未提交改动 | 事实 | `git branch -vv`、`git status --porcelain` |
| F-004 | 远端为 `git@github.com:skyline-projext/skylinevpn-proxylist.git` | 事实 | `git remote -v` |
| F-005 | 共 7 个 tag：`latest`、`v20261016`、`v20261019`、`v20261026`、`v20261102`、`v20261109`、`v20261116` | 事实 | `git tag -l` |
| F-006 | `v20261109` 指向 `85eb82d`（2026-11-02 的提交），仓库内不存在 2026-11-09 的提交 | 事实 | `git rev-list -n1 v20261109`、`git log` |
| F-007 | 受版本控制的文件共 7 个：`README.md`、`LICENSE`、`.gitignore`、`proxy.list`、`scripts/build.sh`、`scripts/merge.py`、`.github/workflows/release.yml` | 事实 | `git ls-tree` / 目录清点 |
| F-008 | 初始提交 `effb8c5` 新增 `proxy.list` 25,715 行（另含 6 个文件） | 事实 | `git show --stat effb8c5` |
| F-009 | 提交 `51fd521`（2026-10-16）改动 `proxy.list`：+237 / −7 | 事实 | `git show --stat 51fd521` |
| F-010 | 提交 `53bfff1`（2026-10-16）改动 `proxy.list`：+766 / −20 | 事实 | `git show --stat 53bfff1` |
| F-011 | 四次自动周更的改动量依次为 +1（10-19）、+8（10-26）、+5（11-02）、+1（11-16） | 事实 | `git show --stat` 各提交 |
| F-012 | 当前 `proxy.list` 大小 389,288 字节 | 事实 | 文件元数据 |

## B. 数据文件（F-013 ~ F-024）

| 编号 | 事实 | 性质 | 依据 |
|------|------|------|------|
| F-013 | 文件头为两行固定注释：`# skylinevpn-proxylist` 与 `# License: Skyline Networking Tech LLC` | 事实 | `proxy.list` 第 1~2 行；F-042 生成逻辑 |
| F-014 | 第三节固定为 `domain_suffix`、`exact`、`regex`，顺序不可变 | 事实 | `proxy.list`；`merge.py` 的 `SECTIONS`（F-032） |
| F-015 | 条目数：`domain_suffix` 26,447、`exact` 84、`regex` 167，合计 26,698 | 清点 | 本次按「非空且非 `#` 开头」统计 |
| F-016 | 节标题位于第 4、26,453、26,539 行；文件总行数 26,706（PowerShell 行计数；`wc -l` 得 26,703，差异来自换行处理） | 清点 | `Select-String`、`Get-Content` |
| F-017 | 全文件 0 行含非 ASCII 字符 | 清点 | 正则统计 |
| F-018 | `domain_suffix` 节内升序排列，起始条目为 `000webhost.com`、`01.org`、`02weqj32.com` | 清点 | 抽样 |
| F-019 | `exact` 节同时含 IP 形态（`85.17.73.31`）与主机形态（`1password.drift.click`、`a4e8s8k3.map2.ssl.hwcdn.net`） | 清点 | 抽样 |
| F-020 | `regex` 节含两类形态：`(^\|\.)…$`（如 `(^|\.)13mei[5-7]\.buzz$`）与 `^…$`（如 `^hses[1-7]?\.akamaized\.net$`、`^epicgames-download\d\.akamaized\.net$`） | 清点 | 抽样 |
| F-021 | 条目覆盖新闻、社交、AI、流媒体、金融、成人内容等多类站点 | 清点 | 抽样（仅陈述覆盖面，不作价值判断） |
| F-022 | 文件内无 schema 版本号、无生成时间戳、无条目总数 | 事实 | 全文检索 |
| F-023 | 除两行文件头与三个节标题外，其他注释在每次重建时被清除 | 事实 | F-042 的写入逻辑 |
| F-024 | `domain_suffix` 与 `exact` 条目均为小写；`regex` 保持原样 | 事实 | F-039 |

## C. 编译管线（F-025 ~ F-044）

| 编号 | 事实 | 性质 | 依据 |
|------|------|------|------|
| F-025 | `build.sh` 使用 `set -euo pipefail` | 事实 | `scripts/build.sh` 第 3 行 |
| F-026 | `SRC_URL` 默认 `https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt`，可由环境变量覆盖 | 事实 | `build.sh` 第 5 行 |
| F-027 | 下载使用 `curl -fsSL --retry 3` | 事实 | `build.sh` 第 12 行 |
| F-028 | 上游内容经 `base64 -d` 解码后落临时文件 | 事实 | `build.sh` 第 12 行 |
| F-029 | `merge.py` 以 `<上游临时文件> <目标清单>` 两个位置参数调用 | 事实 | `build.sh` 第 13 行 |
| F-030 | 临时文件由 `mktemp` 创建，`trap ... EXIT` 清理 | 事实 | `build.sh` 第 9~10 行 |
| F-031 | 目标清单默认为仓库根 `proxy.list`，可由第一个位置参数覆盖 | 事实 | `build.sh` 第 7 行 |
| F-032 | 三节元组定义为 `("domain_suffix", "exact", "regex")` | 事实 | `merge.py` 第 11 行 |
| F-033 | `host_of()`：去前导竖线 → 去 `http(s)://` → 按 `[/^:]` 取首段 → `strip(".")` → `lower()` | 事实 | `merge.py` 第 14~17 行 |
| F-034 | `wildcard_to_regex()` 生成 `(^|\.)host$`，其中 `*` 转成 `[^.]*` | 事实 | `merge.py` 第 20~21 行 |
| F-035 | `parse_upstream()` 跳过空行、以 `[`、`!`、`@@` 开头的行 | 事实 | `merge.py` 第 28 行 |
| F-036 | URL 正则仅支持含 `blogspot` 的一条，转成 `. +blogspot\..+$`；其余打印 `skip unsupported regex` 到 stderr 并丢弃 | 事实 | `merge.py` 第 30~35 行 |
| F-037 | 单竖线 `\|http://host` 进 `exact`；双竖线 `\|\|host` 与裸关键词进 `domain_suffix` | 事实 | `merge.py` 第 42~45 行 |
| F-038 | `parse_sections()` 以 `## ` 开新节；未知节的条目触发 `sys.exit` | 事实 | `merge.py` 第 52~58 行 |
| F-039 | 入集合时除 `regex` 外统一转小写 | 事实 | `merge.py` 第 59 行 |
| F-040 | `covered()` 遍历主机的所有父级后缀；后缀集合用 `include_self=False`，`exact` 集合用 `include_self=True` | 事实 | `merge.py` 第 62~65、75~76 行 |
| F-041 | 先精简 `suffix` 集合，再用它过滤 `exact` 集合 | 事实 | `merge.py` 第 74~76 行 |
| F-042 | 输出为两行文件头 + 每节 `## <name>` + `sorted()` 排序条目 | 事实 | `merge.py` 第 79~84 行 |
| F-043 | 以 `open(list_path, "w")` **就地覆写**原文件；结束时打印三节计数 | 事实 | `merge.py` 第 79、86 行 |
| F-044 | 无备份、无临时文件、无原子替换（无 `os.replace`） | 事实 | `merge.py` 全文 |

## D. 发布工作流（F-045 ~ F-058）

| 编号 | 事实 | 性质 | 依据 |
|------|------|------|------|
| F-045 | 定时触发为 `cron: "0 0 * * 1"`（每周一 00:00 UTC） | 事实 | `release.yml` 第 4~5 行 |
| F-046 | 推送触发限定 `branches: [main]` 且 `paths: [proxy.list]` | 事实 | `release.yml` 第 6~8 行 |
| F-047 | 支持 `workflow_dispatch` 手动触发 | 事实 | `release.yml` 第 9 行 |
| F-048 | 权限为 `contents: write`，使用默认 `GITHUB_TOKEN` | 事实 | `release.yml` 第 11~12、32~33 行 |
| F-049 | 运行环境 `ubuntu-latest`，检出使用 `actions/checkout@v4` | 事实 | `release.yml` 第 16~18 行 |
| F-050 | 合并步骤直接执行 `./scripts/build.sh proxy.list` | 事实 | `release.yml` 第 20~21 行 |
| F-051 | 提交身份固定为 `skyline-projext` / `176280006+skyline-projext@users.noreply.github.com` | 事实 | `release.yml` 第 25~26 行 |
| F-052 | 仅当 `git diff --cached --quiet` 为假时才提交，提交信息为 `Update proxy.list <UTC 日期>` | 事实 | `release.yml` 第 27~28 行 |
| F-053 | 提交后执行 `git push` | 事实 | `release.yml` 第 29 行 |
| F-054 | tag 名为 `v$(date -u +%Y%m%d)` | 事实 | `release.yml` 第 35 行 |
| F-055 | Release notes 中的规则数由 `grep -vcE "^(#\|$)" proxy.list` 统计 | 事实 | `release.yml` 第 36 行 |
| F-056 | 发布前先删除同日同名 Release（`--yes --cleanup-tag`，失败被 `\|\| true` 忽略） | 事实 | `release.yml` 第 38 行 |
| F-057 | `gh release create` 附带 `proxy.list`、`--target HEAD`、`--latest` | 事实 | `release.yml` 第 39~43 行 |
| F-058 | 发布后执行 `git tag -f latest HEAD` 并 `git push -f origin refs/tags/latest` | 事实 | `release.yml` 第 46~47 行 |

## E. 治理与边界（F-059 ~ F-068）

| 编号 | 事实 | 性质 | 依据 |
|------|------|------|------|
| F-059 | `.gitignore` 共 51 行，分「秘密 / 本地草稿 / 编辑器与系统」三块 | 事实 | `.gitignore` 全文 |
| F-060 | 秘密类排除含 `.env*`、`*.pem`、`*.key`、`*.token`、`*.p12`、`id_rsa*`、`id_ed25519*`、`secrets/`、`.netrc`、`.git-credentials` | 事实 | `.gitignore` 第 1~15 行 |
| F-061 | AI/Agent 文件排除含 `CLAUDE.md`、`AGENTS.md`、`.claude/`、`.cursor/`、`.windsurf/`、`.codex/`、`.aider*`、`.continue/`、`.copilot/` 等 | 事实 | `.gitignore` 第 20~45 行 |
| F-062 | 本地草稿排除含 `w.list`、`proxy-not-in-gfwlist.txt`、`image.png` | 事实 | `.gitignore` 第 16~18 行 |
| F-063 | `LICENSE` 共 6 行有效文本，声明版权归 Skyline Networking Tech LLC，按 AS IS 提供，不承担使用责任 | 事实 | `LICENSE` 全文 |
| F-064 | `README.md` 共 15 行，仅含下载 URL、`curl` 示例与许可指向，不含格式说明 | 文档口径 | `README.md` 全文 |
| F-065 | README 中的仓库属主字符串 `skyline-projext` 与远端地址一致 | 事实 | `README.md` 第 6、10 行；F-004 |
| F-066 | 仓库无测试、无校验和文件、无 schema 定义、无依赖清单 | 事实 | 文件清点 |
| F-067 | 仅一个工作流文件；无 Issue 模板、无 PR 模板、无 CODEOWNERS | 事实 | `.github/` 目录清点 |
| F-068 | 仓库无 `docs/` 目录，除 README 外无任何格式或使用说明文档 | 事实 | 目录清点 |

## 版本锚点

- 本页全部事实对应仓库 `HEAD 9c6567c`（2026-11-16）。
- 复核时间：2026-11-21。
- 数据文件统计为**当时快照**；每周自动构建后 `proxy.list` 的分段计数会变化，引用前应按 [01 规则文件格式](../concepts/01-rule-file-format.md) 的口径重新统计。
