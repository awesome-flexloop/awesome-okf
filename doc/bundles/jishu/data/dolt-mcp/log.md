# dolt-mcp Bundle 生成日志

> 记录本 bundle 的生成过程，供审计与回溯使用。

---

## 任务元信息

| 项目 | 内容 |
|------|------|
| 方法链 | seven-concepts-cmd 场景 4（知识沉淀 R→I→E）+ source-code-to-okf-wiki 五阶段 |
| 质量门 | G0 信源稳定 → G1 事实无因果词 → G2 洞察四元组 → G3 信源先行 → G4 计数断言/无虚构 |
| 信源 | `github.com/dolthub/dolt-mcp`（本地克隆 `external/dao/action/DoltHub/dolt-mcp`） |
| 分析版本 | commit `cde8e48`（Merge PR #55 fix-docker，2026-08-18）；`git describe` = `v0.3.8-5-gcde8e48` |
| 归属路径 | `jishu/data/dolt-mcp/`（与 dolt、dolthub-cli 并列于 data 分组） |
| 生成时间 | 2026-09-09 |

---

## 执行步骤

### 阶段 0（信源稳定性预检，G0）

- 信源分类：env-bound git clone（external/dao/action 用户克隆现场），非 vendor 子模块固定 tag
- 处理：文档引用一律指官方 GitHub URL；spec 工作文件记录 commit hash（cde8e48）供复现；不引用临时 file:/// 路径
- gates 基线：`invoke gates.bundles` 检测目录树比 frontmatter 多 +1——为并行会话 dolthub-cli 束（untracked、未注册）所致，非本方范围，全程不触碰其文件、不代注册

### R 阶段（事实采集，G1）

- 方式：主线程精读核心文件（server.go/database.go/config.go/dialect*.go/http_server.go/stdio_server.go/jwt_auth.go/docker*/go.mod/README）+ 3 个子代理分批逐文件采集 45 工具事实
- 数量：编号事实 162 条（F-001~F-162），登记于 `.trae/specs/okf-wiki-ecosystem/dolt-mcp-okf-wiki/facts.md`
- G1 预检：事实句均为源码客观描述，无"用于/目的是"因果推断；工具怪癖按源码如实记录（描述错绑、拼写错误等 5 处，F-147）
- 工具层以 A/B/C 三组 318 条台账交叉核对后压缩整合

### I 阶段（架构洞察，G2）

- 核心洞察 5 条（记录于 insights.md）：① 工具注解=安全元数据层 ② Dialect 三件套封装方言 ③ DoltLite 降维部署 ④ query/exec 读写边界守门 ⑤ working_database+branch 双参使调用自带上下文
- 每洞察含陈述/证据/反常识/行动四元组
- 骨架判定：两问皆满足 → 设 examples/（严格取材集成测试）

### E 阶段（批量生成，G3）

- 顺序：references/source.md 先行 → concepts 7 篇 → examples 2 篇 → 各级 index 最后
- 文档清单：根 index.md + log.md + concepts/(index+7) + examples/(index+2) + references/(index+source) = 15 文件
- 所有正文 F 编号引用均指向 /references/source.md

### V 阶段（独立验证，G4）

见下方质量门检查与验证记录。

### C 阶段（原子提交）

- 子模块内新增束 + 注册 data/index.md 与 bundles 总索引 → gates 全绿 → 子模块提交
- 主仓库：spec 工作文件 + 子模块指针提交（按当时并行会话状态分步处置）

---

## 质量门检查记录

| 质量门 | 检查项 | 结果 |
|--------|--------|------|
| G0 | 信源已固定版本、无临时路径引用 | ✅ commit cde8e48 记录 |
| G1 | 事实无推断词、全部可溯源 | ✅ F-001~F-162 逐条出处 |
| G2 | 洞察四元组完整 | ✅ 5 条洞察均含陈述/证据/反常识/行动 |
| G3 | references 先行、index 最后、分批≤7 | ✅ |
| G4 | 链接无断裂、无虚构 API、计数断言一致 | ✅ 45 工具计数经 primitive_v1.go 逐行核验；F 引用已 Grep 抽查 |
| - | toctree 完整性 | ✅ 根+concepts+examples+references 四级 toctree |
| - | 编码 | ✅ UTF-8 无 BOM |

---

## 变更记录

- **2026-09-09**：初版生成（15 文件，162 条事实，7 概念 + 2 示例）。
