---
type: Facts
okf_version: "0.2"
title: "pr-triage-board-bot 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, pr-bot, github-actions, typescript, triage]
sources:
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/action.yml
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/src/main.ts
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/src/project.ts
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/src/fieldconfig.ts
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/src/utils.ts
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/package.json
  - ../../../../../external/libs/jupyter/pr-triage-board-bot/README.md
---
# pr-triage-board-bot 源码事实清单

> R 阶段产出：零推测事实，每条事实指向具体源码文件与行号。

## 项目元数据

- F-001: package.json:2-4,27-29 — 包名 `pr-triage-board-bot`，版本 `0.1.0`，`"type": "module"`（ESM 项目），`engines.node` 为 `>23.0.0`
- F-002: package.json:6-20 — 运行时依赖 6 个：`@octokit/auth-app` ^8.0.2、`@octokit/core` ^7.0.3、`@octokit/plugin-paginate-graphql` ^6.0.0、`@octokit/plugin-throttling` ^11.0.1、`commander` ^14.0.0、`memoize` ^10.1.0；开发依赖：`@swc/cli`、`@swc/core`、`@types/node`、`chokidar`、`typescript` ^5.9.2
- F-003: LICENSE:1-3 — BSD 3-Clause License，Copyright (c) 2025, Yuvi
- F-004: README.md:1 — README 一级标题为 `# pr-triage-syncer`，与 package.json 包名 `pr-triage-board-bot` 不一致
- F-005: README.md:20-30 — Principles 节声明 bot 拥有 Project Fields 的 schema 与所有入板 PR 的字段值、不拥有 Project Board 的 views（tabs），人类对字段的修改会在下次运行时被还原
- F-006: README.md:32-37,148-150 — Principles 节声明字段值计算全确定性（deterministic）、bot 不编码任何具体 GitHub 组织信息；Acknowledgement 节致谢 2i2c.org 最初构建并捐赠给 Jupyter 组织

## GitHub Action 定义（action.yml）

- F-007: action.yml:2-7,35-36 — name `PR Triage Board Bot`，description "A GitHub Action to manage a GitHub Project board for PR triage"，author `yuvipanda`，branding icon `list`/color `blue`，`runs.using: 'composite'`
- F-008: action.yml:9-33 — inputs：organization、project-number、gh-app-id、gh-app-installation-id、gh-app-private-key 均 `required: true`；repositories、node-version 可选，node-version 默认 `23.x`
- F-009: action.yml:41-50 — 第一步把 `${{ github.action_path }}/package-lock.json` 复制为工作区文件 `pr-triage-bot-package-lock.json`（注释引用 actions/toolkit#1035 说明 hashFiles 仅对 WORKSPACE 内文件生效），随后用 actions/setup-node@v4 配置 node（cache: npm，cache-dependency-path 指向复制的 lockfile）
- F-010: action.yml:52-60 — 在 `${{ github.action_path }}` 下执行 `npm ci` 与 `npm run build`
- F-011: action.yml:62-66,87-90 — 将 `${{ inputs.gh-app-private-key }}` 写入 `private-key.pem`；最后一步 `rm -f private-key.pem`，条件 `if: ${{ always() }}`
- F-012: action.yml:68-85 — 运行 `node dist/src/main.js`，固定传 `--gh-app-id`、`--gh-app-installation-id`、`--gh-app-pem-file private-key.pem`；repositories 非空时额外传 `--repositories`，其后为位置参数 organization 与 project-number

## CLI 入口与认证（src/main.ts）

- F-013: src/main.ts:1-9,29-67 — 导入 octokit core/auth-app/paginate-graphql/throttling、Project、getGraphql、REQUIRED_FIELDS、commander、node:fs；`makeOctokit()` 用 `Octokit.plugin(paginateGraphQL, throttling)` 构造客户端，authStrategy 为 `createAppAuth`，auth 含 appId、installationId 与 `fs.readFileSync(keyPath).toString()` 私钥；throttle 的 `onRateLimit` 与 `onSecondaryRateLimit` 均在 `retryCount < 2` 时返回 true 重试
- F-014: src/main.ts:164-180 — commander 定义 options：`--dry-run`、`--gh-app-id <number>`（parseInt）、`--gh-app-installation-id <number>`（parseInt）、`--gh-app-pem-file <string>`、`--repositories <repos>`，以及位置参数 `<organization>` 与 `<projectNumber>`；`--repositories` 值按逗号 split 并 trim（L174）

## 核心同步逻辑（src/main.ts main()）

- F-015: src/main.ts:69-78 — main() 先 `Project.getProject(organization, projectNumber, octokit)`，dryRun 时打印 "DRY RUN MODE - No changes will be made."，随后 `verifyAndCreateFields()` 校验并创建缺失字段
- F-016: src/main.ts:82-86 — 调用 `getOpenPRs()` 拉取开放 PR、`getExistingItems()` 拉取已有看板条目，并打印两者数量
- F-017: src/main.ts:12-27 — getOpenPRs() 使用 openprs.gql；repositories 非空时构造 `repo:org/repo ... is:pr state:open archived:false`，否则构造 `org:org is:pr state:open archived:false`，经 `octokit.graphql.paginate` 分页拉取并返回 `resp.search.nodes`
- F-018: src/main.ts:90-113 — 构建 `currentPRIds` 集合与 `existingItemsByPRId` 映射；existing item 的 content.id 不在集合中时加入 `itemsToDelete`；fieldValues.nodes 中带 `field.name` 的节点转换为 field name → value 的 Map，取值优先级为 text、number、Date(date)、name（L99-102）
- F-019: src/main.ts:118-125 — itemsToDelete 按 url 排序后逐个 `deleteItem(item.id)`，`dryRun` 时仅打印不删除
- F-020: src/main.ts:132-157 — openPRs 按 url 排序后逐条处理：已有条目复用 itemId，否则非 dryRun 时 `addContent(pr.id)`；对每个 REQUIRED_FIELDS 条目比较新值与当前值（Date 用 getTime()，null 映射为 undefined），不变则 skippedCount++，变化则在非 dryRun 时 `setItemValue()` 并 updatedCount++
- F-021: src/main.ts:160 — 汇总输出 `Summary: Updated X field values, skipped Y unchanged values`

## 项目字段管理（src/project.ts）

- F-022: src/project.ts:12-42 — `SingleSelectOption`（id/name）与 `SingleSelectField`（含 options 数组、memoize 化的 findOption()）；findOption 未命中时 throw 字符串 "Learn how to error handle this properly? Or express this via types?"
- F-023: src/project.ts:59-76 — 静态方法 `getProject()` 用 project.gql 查询，含 `options` 的字段映射为 SingleSelectField，其余为 `{id, name}`
- F-024: src/project.ts:87-142 — `setItemValue()` 用字符串插值构造 mutation：Date 值用 `date: $value`（$value: Date!）、string 且字段为 SingleSelectField 时用 `singleSelectOptionId: $value`（先 `field.findOption(value).id`）、普通 string 用 `string: $value`、number 用 `number: $value`（$value: Float!）；null 改用 `clearProjectV2ItemFieldValue`（L90-91 注释 "I am creating a query via string interpolation / may i rot in hell"）
- F-025: src/project.ts:144-178,158-166 — `addContent()` 用 `addProjectV2ItemById` mutation 返回 item.id；`deleteItem()` 用 `deleteProjectV2Item` mutation 返回 deletedItemId；`getExistingItems()` 用 projectitems.gql 分页拉取并过滤掉无 content 的条目
- F-026: src/project.ts:180-267 — `createField()` 按 dataType 构造 `createProjectV2Field` mutation，SINGLE_SELECT 传 singleSelectOptions 并期望返回 ProjectV2SingleSelectField，成功后 push 到 this.fields；`verifyAndCreateFields()` 对比 this.fields 名称与 REQUIRED_FIELDS，缺失时调用 createField()

## 字段配置（src/fieldconfig.ts）

- F-027: src/fieldconfig.ts:10 — `FieldDataType` 为 "TEXT" | "NUMBER" | "DATE" | "SINGLE_SELECT"
- F-028: src/fieldconfig.ts:18-64 — `FIELD_CONFIGS` 定义 7 个字段：Author Kind（SINGLE_SELECT，5 选项）、Opened At（DATE）、Total Lines Changed（NUMBER）、Maintainer Engagement（SINGLE_SELECT，3 选项）、CI Status（SINGLE_SELECT，2 选项）、Merge Conflicts（SINGLE_SELECT，2 选项）、Approval Status（SINGLE_SELECT，2 选项）
- F-029: src/fieldconfig.ts:68-117 — 辅助类型 `ExtractFieldValueType` 按 dataType 推导返回值类型（SINGLE_SELECT→选项字面量、DATE→Date、NUMBER→number、TEXT→string）；`REQUIRED_FIELDS` 用映射类型 `RequiredFieldsType` 约束结构与 FIELD_CONFIGS 一致，并为每字段绑定 getValue 函数

## 字段取值器（src/fields/*.ts）

- F-030: src/fields/authorkind.ts:23-44 — getAuthorKind() 判定顺序：作者在 `["dependabot", "pre-commit-ci", "jupyterhub-bot"]` → "Bot"；在仓库协作者名单 → "Maintainer"；merged PR 数为 0 → "First Time Contributor"；<10 → "Early Contributor"；否则 "Seasoned Contributor"
- F-031: src/fields/authorkind.ts:7-21 — getMergedPRCount() 查询 `org:<org> author:<username> is:pr state:closed` 的 issueCount；memoize 且 `cacheKey: args => JSON.stringify(args)`（L18-20 注释说明默认 JS memoize 仅对首参缓存）
- F-032: src/fields/openedat.ts:4-9 + src/fields/totallineschanged.ts:4-6 — getOpenedAt() 将 pr.createdAt 转为 Date 后 `setUTCHours(0,0,0,0)` 去除时间部分；getTotalLinesChanged() 返回 `pr.additions + pr.deletions`
- F-033: src/fields/maintainerengagement.ts:4-21 — getMaintainerEngagement() 删除作者后的协作者集合与 participants 求 `Set.intersection`，大小 0/1/多 分别返回 "No/Single/Multiple Maintainer Engagement"
- F-034: src/fields/cistatus.ts:4-19 + src/fields/mergeconflicts.ts:4-17 — getCIStatus() 依 statusCheckRollup.state：SUCCESS→"Tests Passing"、FAILURE→"Tests Failing"，其余打印日志并返回 null；getMergeConflicts() 依 pr.mergeable：CONFLICTING→"Merge Conflicts"、MERGEABLE→"No Merge Conflicts"、UNKNOWN→null，default 分支注释引用 MergeableState 枚举并返回 null
- F-035: src/fields/approvalstatus.ts:4-27 — getApprovalStatus() 收集 `authorCanPushToRepository` 且非 isMinimized 的 review state；存在 CHANGES_REQUESTED → "Changes Requested"，否则存在 APPROVED → "Maintainer Approved"，否则 null
- F-036: src/fields/fileschangedtype.ts:4-8 — fileschangedtype.ts 定义 TYPE_EXTENSION_MAPPING（Documentation: .md/.rst；Python: .py；Frontend: .js/.jsx/.ts/.tsx/.css/.html/.scss）并导出 getFilesChangedType，但 fieldconfig.ts 未导入/注册该字段

## GraphQL 查询与工具（src/graphql/*.gql、src/utils.ts）

- F-037: src/graphql/openprs.gql:1-52 — 查询 `search(type:ISSUE first:30)` 的 PullRequest 节点：id、url、createdAt、lastEditedAt、deletions、additions、statusCheckRollup.state、mergeable、participants、files、reviews、repository、author、title，含 pageInfo 分页
- F-038: src/graphql/project.gql:1-23 + src/graphql/projectitems.gql:1-58 — project.gql 查 organization.projectV2(number) 的 id 与 fields(first:100)，分别取 ProjectV2Field 与 ProjectV2SingleSelectField（含 options）；projectitems.gql 分页查 items(first:100)，content 取 PullRequest 的 id/url，fieldValues(first:50) 分类型取 text/number/date 与 single select 的 name 及 field.name
- F-039: src/graphql/maintainers.gql:1-16 — 分页查询 repository.collaborators(first:100) 的 permission 与 login
- F-040: src/utils.ts:9-25 — getGraphql() 用 memoize 缓存 `fs.readFileSync(join(import.meta.dirname, "graphql", name))` 内容；getCollaborators() 用 maintainers.gql 分页查询，按 `['WRITE', 'MAINTAIN', 'ADMIN']` 过滤（L17 注释说明不统计 TRIAGE，因其不能合并 PR），cacheKey 为 `JSON.stringify(args)`

## 构建与 CI

- F-041: package.json:21-26 — scripts：start/build/build:watch 用 swc 编译 src/ 至 dist/（--copy-files --delete-dir-on-start），typecheck 用 `tsc --noEmit`
- F-042: tsconfig.json:1-11 + .swcrc:1-8 — compilerOptions：target esnext、module node16、moduleResolution node16、outDir dist、rootDir src，include `src/**.ts`；.swcrc 设置 jsc.parser.syntax typescript、target es2024
- F-043: .github/workflows/ci.yaml:1-20 — CI 在 pull_request（main）触发：checkout@v4、setup-node@v4（23.x、npm cache）、`npm ci`、`npm run typecheck`、`npm run build`
- F-044: .github/workflows/run.yaml:1-23 — 定时 cron `'13 * * * *'` 与 workflow_dispatch、push 到 main 触发；job `jupyterhub` 使用 yuvipanda/pr-triage-board-bot@main，organization `jupyterhub`、project-number `4`、gh-app-id `1793875`、gh-app-installation-id `81302562`，私钥取 secrets.GH_APP_PRIVATE_KEY
