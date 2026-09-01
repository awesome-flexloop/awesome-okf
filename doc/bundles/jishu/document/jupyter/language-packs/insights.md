---
type: Insights
okf_version: "0.2"
title: "language-packs 架构洞察"
generated: "2026-08-22"
tags: [jupyter, language-packs, i18n, localization, crowdin]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/language-packs/repository-map.yml
  - ../../../../../external/libs/jupyter/language-packs/scripts/02_update_catalogs.py
  - ../../../../../external/libs/jupyter/language-packs/scripts/03_prepare_release.py
  - ../../../../../external/libs/jupyter/language-packs/crowdin.yml
  - ../../../../../external/libs/jupyter/language-packs/language-packs/jupyterlab-language-pack-de-DE/pyproject.toml
  - ../../../../../external/libs/jupyter/language-packs/.github/workflows/release_publish.yml
  - ../../../../../external/libs/jupyter/language-packs/.github/workflows/crowdin.yml
---
# language-packs 架构洞察

## I-001：单一配置源驱动的自动化翻译管线——repository-map.yml 为唯一真相

**类型**：架构模式
**关联事实**：F-006, F-007, F-010, F-011, F-030, F-031, F-033, F-034, F-035

**洞察**：整个仓库以 `repository-map.yml` 作为唯一配置源（single source of truth），其上、下游全部产物都由它派生。该文件用「包名 → current-version-tag / supported-versions / url」三元组声明 17 个受管包（F-006, F-007）；`02_update_catalogs.py` 的 `update_crowdin_config()` 固定 jupyterlab 条目后按排序后的 map 逐包重写 crowdin.yml 的 files 列表（F-033），`update_catalog()` 则经 `jupyterlab_translate.api.extract_language_pack` 生成/合并各扩展的 .pot（F-034），并遍历 supported-versions 范围内所有 tag 做多版本合并（F-035）。这样配置与生成物之间没有人工漂移——crowdin.yml 永远与 repository-map.yml 一致，扩展增减只需改一处。

管线的数据流是单向推进的：repository-map.yml → crowdin.yml（决定 Crowdin 从哪抓源串）→ extensions/*.pot（源字符串 catalog）→ Crowdin 翻译 → language-packs/*.po（翻译产物）。`supported-versions` 用 NpmSpec 语义（F-011）表达版本范围，`01_check_releases.py` 自动 bump 只接受非 dev/prerelease 且更新的 tag（F-030, F-031），保证 map 里的版本始终是"最新稳定 tag"。值得注意的漂移点是：jupyter-chat 在 map 中但尚未生成 catalog（F-010），说明"清单声明"与"派生物实际生成"之间仍需脚本触发才同步。

```
                    ┌──────────────────────────┐
                    │  repository-map.yml (唯一真相) │
                    │  17 包 × (tag / range / url) │
                    └─────────────┬──────────────┘
                                  │ 02_update_catalogs.py
               ┌──────────────────┼───────────────────┐
               ▼                  ▼                   ▼
      update_crowdin_config  clone+checkout  extract_language_pack
      (重写 crowdin.yml)   (repos/ 缓存)      (多版本 merge，F-035)
               │                  │                   │
               ▼                  ▼                   ▼
      Crowdin 抓源串       各扩展源码        extensions/*.pot → 翻译 → language-packs/*.po
```

**复用价值**：多目标产物（翻译配置、catalog、发布清单）共用一个声明式清单文件，用脚本单向重写派生物而非人工维护，可避免配置漂移；但前提是脚本必须"只读清单、只写派生物"，且派生物（crowdin.yml）应视为构建产物而非手工编辑对象。同时需意识到声明与派生物生成是两步，缺脚本触发仍会产生漂移。

## I-002：Copier 模板 + hatch hook + entry-point 的三层语言包装配

**类型**：架构模式
**关联事实**：F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-036, F-043

**洞察**：每个语言包不是手写的，而是由 `jupyterlab-language-pack-cookiecutter` 模板经 Copier 生成（`.copier-answers.yml` 记录 `_commit: v1.1.3` 与 `_src_path`，F-022），模板变量 `language`/`locale`/`version` 决定包的元数据与目录名（F-023）。版本发布时 `03_prepare_release.py` 遍历所有语言包，用 `copier --force --vcs-ref HEAD --data version=... update` 统一回写模板（F-036），保证 31 个语言包结构同构、版本同步（F-024）。

装配分三层：其一，`pyproject.toml` 通过 `[project.entry-points."jupyterlab.languagepack"]` 注册 `de_DE = "jupyterlab_language_pack_de_DE"`（F-019）——这是 JupyterLab 运行时发现语言包的钩子；其二，hatch build hook `jupyter-translate` 依赖 `jupyterlab-translate`，在打包时把 .po 编译为 .json/.mo（F-020, F-043）；其三，wheel 打包只发布编译产物 `**/*.json` 与 `**/*.mo`，显式排除 .po 源文件（F-021）。三者合起来形成"模板生成 → 构建编译 → 运行时注册"的完整链路，且 ach-UG 伪语言包复用同一模板但改名 `jupyterlab-pseudo-language-pack`（F-025, F-026）。

```
Copier 模板 (jupyterlab-language-pack-cookiecutter)
   │ --data version / locale / language（03_prepare_release 统一回写，F-036）
   ▼
jupyterlab-language-pack-<locale>/
   ├─ pyproject.toml
   │    ├─ entry-points."jupyterlab.languagepack" → 运行时发现（F-019）
   │    ├─ hatch hook jupyter-translate (jupyterlab-translate) → .po→.json/.mo 编译
   │    └─ wheel artifacts 仅含 .json/.mo，排除 .po（F-021）
   ├─ locale/<locale>/LC_MESSAGES/*.po   (Crowdin 下载的翻译)
   └─ jupyterlab_language_pack_<locale>/__init__.py (版本号 X.Y.postZ)
```

**复用价值**：批量产物的同构性可由"模板 + 生成器 + 版本同步脚本"保证，而非逐个复制粘贴；运行时发现用 entry-point、构建期用 build hook 将"数据（翻译）"与"逻辑（编译/注册）"分层。发布时统一回写模板（copier update）比在 31 个目录里手工改版本更可靠。

## I-003：多版本合并 vs 单分支快照——源字符串提取的两种策略

**类型**：架构约束
**关联事实**：F-008, F-009, F-030, F-031, F-034, F-035

**洞察**：.pot 源字符串的提取由 `current-version-tag` 与 `supported-versions` 共同决定，呈现两种模式。当 `supported-versions` 存在时（如 jupyterlab 的 `>=4.3`，F-008），`02_update_catalogs.py` 遍历范围内的所有 tag，逐个提取并以 `should_merge=True` 合并进同一 .pot（F-035），最后再对 `current-version-tag` 做一次兜底提取（F-034）——这保证翻译在支持的多版本间保持字符串集合并集，避免某个 patch 版本新增字符串无人翻译。`01_check_releases.py` 的自动 bump 只接受非 dev/prerelease 且更新的 tag（F-030, F-031），控制合并集规模，防止版本无限膨胀。

当 `current-version-tag` 指向 branch 时则切换为"单分支快照"模式：只从 branch HEAD 提取一次、不与旧 POT 合并，`supported-versions` 被忽略。两种模式均由 01/02 两个脚本实现：01 维护 tag 的权威性（F-030, F-031），02 根据 map 选择合并或快照路径（F-034, F-035）。map 中的不统一（如 jupyterlab-recents 用单数 `supported-version`，F-009）说明解析逻辑需对键名容错，也提示清单模式应保持字段一致性。

```
supported-versions 存在（tag 模式）                current-version-tag 为 branch
  for tag in 范围内所有 tag:                       仅提取 branch HEAD 一次
    update_repo(tag) ──► extract(merge=True)       (不与旧 POT 合并)
        │  累加合并进同一 .pot                       supported-versions 被忽略
        ▼
  最后对 current-version-tag 再提取一次兜底
```

**复用价值**：为"长期维护的插件"提取翻译字符串时，"范围内多版本合并"能显著降低翻译缺失风险，但会随支持版本增多而膨胀合并成本；"分支快照"轻量但不稳定。两种模式需显式可切换，并应把"哪个 tag 是权威最新版"的判定交给自动化脚本（排除 dev/prerelease），而不是人工。

## I-004：伪语言包 ach-UG 支撑 Crowdin in-context 翻译

**类型**：设计决策
**关联事实**：F-002, F-003, F-025, F-026, F-028

**洞察**：`jupyterlab-language-pack-ach-UG` 不是真实语言，而是仓库内嵌的"翻译工作台"。Acholi (ach-UG) 被 README 两次声明为伪语言（F-002, F-003），其包名也改名 `jupyterlab-pseudo-language-pack`（F-025）以提示非正式用途。它复用与其他 30 个真实语言包相同的 Copier 模板与 entry-point 注册（`ach_UG = "jupyterlab_language_pack_ach_UG"`，F-026），但 README 明确警告"不应显式安装"（F-002）。

设计意图：Crowdin 的 in-context 翻译需要把未翻译源字符串以"伪语言"形式加载进 JupyterLab 界面，翻译者直接在界面上看到待翻译串并就地编辑，而非切换语言。因此 ach-UG 包只需承载"能展示的源串"而非"完整翻译"，其 LC_MESSAGES/ 集合与其他语言包不一致（缺 spreadsheet_editor.po，F-028）正是这一取舍的证据。它是把"翻译工具链"伪装成"一个语言包"的产物，使整个既有发布/构建流水线（matrix、PyPI 发布）无需为它做特判。

```
  JupyterLab 以 ach_UG 伪语言启动
        │  加载伪语言包（entry-point 注册，F-026）
        ▼
  界面就地显示未翻译源串
        │  in-context 编辑
        ▼
  Crowdin 捕获译文 → 写入真实语言包的 .po
```

**复用价值**：当工具链需要"特殊模式"但又不愿为它新增分支时，可以把该模式伪装成普通数据（一个伪语言包）走既有管线——前提是显式加警告与改名（F-025），避免被误用为生产语言。

## I-005：Bot 驱动的全自动发布闭环与版本一致性门禁

**类型**：架构模式
**关联事实**：F-036, F-038, F-039, F-040, F-044, F-045, F-046, F-047, F-048, F-049, F-050, F-051

**洞察**：整个仓库的更新与发布高度自动化，由多条 GitHub Actions + bot 组成闭环。闭环起点是 `check_releases.yml` 每日 cron 跑 `01_check_releases.py` 检测新 tag 并开 PR（F-049）；合并后 `update_pot.yml` 检测 repository-map.yml 变更并跑 `02_update_catalogs.py` 生成新 .pot、开 `pot-update-<sha>` 分支 PR（F-044, F-045）；随后 `crowdin.yml` 工作流在 .pot 变更或每日 cron 时上传源串、下载译文到 `l10n_crowdin_translations` 分支并开 PR（F-046, F-047, F-048，依赖 `CROWDIN_PROJECT_ID`/`CROWDIN_TOKEN` secrets）。最终 `release_publish.yml` 以 30-locale matrix 并行构建（F-050），再统一 publish 到 PyPI（F-051）。

门禁上，发布前用 `04_check_version.py` 做版本一致性校验：用 `hatch version` 读取每个包版本、以第一个为参照，任何不一致或 hatch 报错即 `raise ValueError`（F-038, F-039, F-040）——这是多包同时发布的强一致保障。发布准备由 `03_prepare_release.py`（手动触发）统一 bump 版本并生成 CONTRIBUTORS.md（F-036）。整个链路中 bot 与 secrets 被多个工作流复用，每个环节以 PR 作为人工审阅闸门。

```
cron/手动 ──► check_releases.yml ──► New releases PR ──┐
                                                        ▼
                 merge ──► update_pot.yml ──► pot-update PR ──► merge
                                                                 ▼
                                          crowdin.yml ──► 上传源串/下载译文 ──► New Crowdin updates PR
                                                                 ▼ merge（版本变化）
    release_publish.yml：check-version 门禁（F-038~F-040）──► 30-locale matrix build ──► PyPI publish
```

**复用价值**：对"一处配置驱动、多产物并行发布"的仓库，可用 bot + cron + PR 的链式自动化把从"上游版本变化"到"下游发布"的全链路串起来，每个环节以 PR 作为人工审阅闸门；并行发布前必须设统一版本一致性门禁（04_check_version 的强校验），否则多包版本漂移会在发布时难以排查。
