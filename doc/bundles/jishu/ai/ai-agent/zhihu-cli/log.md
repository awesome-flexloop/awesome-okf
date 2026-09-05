# 变更日志

## 2026-09-05 — 官方 API 文档补全（v2）

- 新增来源：S7 知乎开发者官方文档（6 篇 API 文档：OAuth 集成、用户内容、用户关注、用户收藏、收藏夹列表、收藏夹内容）
- R 阶段：新增 15 条事实登记（F-136~F-150），新增 6 项 P0 核验（P0-020~P0-025，全部 ✅）
- 新增文档：`references/official-api-reference.md`（官方 API 接口参考手册）
- 更新文档：
  - `index.md`：事实基数 135→150、P0 核验 19→25、官方文档验证 30→45
  - `concepts/03-core-capabilities.md`：个人数据能力扩展为 5 个 API + OAuth 授权说明 + 统一鉴权模式
  - `concepts/02-security-credentials.md`：时间戳核验从 ⚠️ 升级为 ✅；新增 X-OAuth-Token 扩展鉴权、OAuth 2.0 安全设计
  - `references/article-source.md`：新增 F-136~F-150 共 15 条事实
  - `references/verification.md`：新增 P0-020~P0-025 共 6 项核验（全部通过）

### 关键核验结论

- ✅ OAuth 2.0 Authorization Code Flow 流程与参数已通过官方文档确认
- ✅ X-Request-Timestamp 秒级时间戳校验已通过官方 API 文档确认（原 P0-006 从 ⚠️ 升级为 ✅）
- ✅ 用户数据 5 个接口（内容/关注/收藏/收藏夹列表/收藏夹内容）参数、响应、错误码全部确认
- ✅ X-OAuth-Token 请求头机制：不传查本人、传入查授权用户
- ✅ 所有用户数据 API 统一归属 user_data 额度项

## 2026-09-04 — 初始生成（v1）

- 来源：6 篇公开文章（S1 腾讯云开发者社区、S2 觉醒AI博客、S3 知乎官方开放平台、S4 知乎问题页、S5 老狼知乎专栏、S6 老狼知乎回答）
- 按 blog-article-to-okf-bundle 模式生成（技术教程完整骨架，含 concepts/examples/references 三层）
- R 阶段：105 条事实登记（F-001~F-105），14 项 P0 核验（3 ✅ 11 ⚠️ 0 ❌），3 条勘误（E-001~E-003）
- I 阶段：6 concepts + 3 examples + 3 references
- E 阶段：生成 14 个文件
  - index.md（bundle 首页）
  - concepts/index.md + 00-platform-overview + 01-access-architecture + 02-security-credentials + 03-core-capabilities + 04-practical-playbooks + 05-ecosystem-integration
  - examples/index.md + 01-setup-installation + 02-core-commands + 03-agent-integration
  - references/index.md + article-source + verification
  - log.md
- 文件名全部使用英文 kebab-case
- Mermaid 图表：2 张（接入方式架构图、安全校验流程图）
- status: verified；stale_after: 2026-12-31

### 关键核验结论

- ✅ L1-L5 内容分级体系多源交叉验证确认
- ✅ 邀测阶段与 2026-09 时点一致
- ✅ v0.5.0 版本号与时点一致
- ⚠️ 接入方式勘误：源文称两种，实际三种（API + Skill + MCP）[E-001]
- ⚠️ 免费额度时效：2026 年 5 月为 1000 次/天，Q3 扩容至 5000 次/天 [E-002]
- ⚠️ 官方 Skills 数量勘误：4 套独立 Skills + 1 个统一 CLI [E-003]
- ⚠️ 全网搜索技术参数（百亿索引、600ms 延迟、分钟级更新）均为厂商自述
- ⚠️ X-Request-Timestamp 时间戳校验待官方文档进一步确认
- ⚠️ P2/安全为作者评估结论，非官方审计报告
