# dh CLI Bundle 生成日志

> 记录本 bundle 的完整生成过程，供审计与回溯使用。

---

## 任务元信息

| 项目 | 内容 |
|------|------|
| 方法链 | source-code-to-okf-wiki（知识沉淀场景 R→I→E→V→C） |
| 质量门 | G0（信源稳定性）→ G1（事实无推断）→ G2（洞察四元组）→ G3（信源先行）→ G4（无虚构 API + 计数断言） |
| 信源 | dolthub/cli 本地源码 `external/dao/action/DoltHub/cli`（commit `2ef50ab`） |
| 分析基线 | commit `2ef50ab87632b40c08782f43573e2b3c43ebfbd9`（2026-09-08），`git describe` = `v0.0.1-2-g2ef50ab` |
| 归属路径 | `jishu/data/dolthub-cli/`（data 分组直挂束，与 dolt 束同级） |
| 生成时间 | 2026-09-09 |

---

## 执行步骤

### 阶段 0：信源稳定性预检（G0）

- **信源分类**：`external/dao/action/DoltHub/cli` 为带完整 `.git` 的官方源码克隆（origin `git@github.com:dolthub/cli.git`），非 `.chaos/`/`.tmp/` 临时克隆，属 stable 信源。
- **版本固定**：记录 commit hash `2ef50ab` + tag `v0.0.1` + `git describe` 输出，引用只指 stable 位置，无绝对路径指向临时目录。
- **结论**：G0 通过。

### R 阶段：源码深度阅读与事实采集

- **范围**：通读入口（`cmd/dh/main.go`、`internal/app/app.go`）、命令树（`pkg/cmd/root/root.go`）、工厂（`pkg/cmd/factory/default.go`、`pkg/cmdutil/factory.go`）、领域层（`internal/dolthub/*`、`internal/credentials/*`、`internal/oauth/*`、`internal/authflow/*`、`internal/httptransport/*`、`internal/upload/*`、`internal/operationwaiter/*`、`internal/pagination/*`、`internal/repository/*`）、命令实现（`pkg/cmd/sql`、`pkg/cmd/table/import`、`pkg/cmd/auth/login`、`pkg/cmd/browse` 等）。
- **产出**：60 条事实（F-001~F-060），写入 [references/source.md](references/source.md)，十组分类。
- **G1 预检**：全部事实句为客观陈述（"X 是/有/含/调用"），无"用于/目的是/设计为"等推断词。

### I 阶段：架构洞察与知识地图

- **5 个核心洞察**（陈述 + 证据 + 反常识 + 行动）：
  1. gh 架构范式迁移（go-gh 依赖 + Factory 聚合 11 能力）
  2. 凭据安全是重头戏（OAuth PKCE + 双源回退 + 轮换 + 脱敏）
  3. 异步操作统一抽象（Operation + 指数退避轮询）
  4. 安全边界优先的 HTTP 客户端（URL 逃逸/同源/控制字符过滤）
  5. 可测试性贯穿始终（IO/网络/时间/浏览器可注入）
- **知识地图**：concepts/ 6 篇（概述→架构→认证→SQL/导入→协作→输出/异步）+ examples/ 4 篇（认证/SQL/导入/PR）。

### E 阶段：信源先行生成

- **信源先行**：先写 [references/source.md](references/source.md)（F-001~F-060 事实登记），再写 concepts/ 与 examples/，最后写各级 index.md。
- **分批生成**：concepts/ 分 6 个文件，examples/ 分 4 个文件，均 ≤7 文件/批。

### V 阶段：独立验证

- **Grep API 验证**：对文档引用的关键类名/方法名（`Factory`、`IOStreams`、`FallbackStore`、`TokenSource`、`operationwaiter.Waiter`、`pagination.Collect`、`upload.File`、`tableprinter.Table`、`AddJSONFlags`、`RunSQLRead`、`RunSQLWrite`、`CreateImportUpload` 等）逐一 Grep 源码确认存在性，无虚构。
- **计数断言**：14 命令组（root.go AddCommand 逐一点数）；150 个 `.go` 文件（`git ls-files "*.go"` 实测）；F-001~F-060 共 60 条。
- **frontmatter**：内容文档均含 `type` frontmatter；子目录 index.md 无 frontmatter；根 index.md 含 `okf_version`。
- **toctree**：根/concepts/examples/references 四级 toctree 完整。
- **链接**：交叉引用统一 `/` 开头 bundle-relative 路径。

### C 阶段：索引接入与提交

- `jishu/data/index.md`：导航表 + toctree 新增 `dolthub-cli` 条目，束数 2 → 3。
- `jishu/index.md`：data 行束数 10 → 11。
- `bundles/index.md`：total_bundles 同步 +1。

---

## 核心洞察记录

| # | 洞察 | 反常识 | 行动 |
|---|------|--------|------|
| 1 | dh 是 gh 架构范式迁移 | 看似"又一个 CLI"，实为把成熟 GitHub CLI 工程范式迁移到数据领域 | 学 Go CLI 工程化以 dh 为精简范本 |
| 2 | 凭据安全是重头戏 | CLI 难点不在发请求，在安全管身份 | 自建 OAuth CLI 直接借鉴 credentials 层 |
| 3 | 异步操作统一抽象 | REST 的"写"不是同步的 | 统一 Operation 抽象而非各命令各写轮询 |
| 4 | 安全边界优先的 HTTP 客户端 | 最"无聊"的 URL 校验是防凭据泄露第一道防线 | 带凭据客户端必做同源校验防 SSRF |
| 5 | 可测试性贯穿始终 | CLI 也能高单测覆盖 | 从第一天设计 IO 抽象与依赖注入 |

---

## G 质量门检查记录

| 质量门 | 检查项 | 结果 |
|--------|--------|------|
| G0 | 信源稳定性（stable + 固定 commit） | ✅ 通过 |
| G1 | 事实句无因果推断词 | ✅ 全部通过 |
| G2 | 洞察四元组完整 | ✅ 5 个洞察均含陈述/证据/反常识/行动 |
| G3 | 信源先行 + 分批 ≤7 文件 + index 最后写 | ✅ 通过 |
| G4 | 无虚构 API（Grep）+ 计数断言 + 链接 + frontmatter | ✅ 通过 |
