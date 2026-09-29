# 变更日志

## 2026-09-05 — 导航优化与跨域案例沉淀（v6）

- **导航优化**：技术域总索引 `jishu/index.md` 从 17 组平铺改为 6 大类分组展示，降低认知负担
- **首页精选**：`doc/index.md` 新增精选推荐区，将本知识包列为 AI 域代表案例
- **跨域案例**：`doc/bundles-knowledge-system.md` 新增技术域案例段落，与《老子》著作形成人文+技术双案例对照，论证 OKF 方法论的跨学科通用性
- 同步更新 frontmatter sources、参考链接列表

## 2026-09-05 — 对抗审查与可验证性强化（v5）

- **P0-049 补全**：补充 F-214（问题-回答结构化逻辑）的核验覆盖
- **5 项 ⚠️ 跟进方案落地**：
  - P0-047：新增 `examples/05-api-latency-benchmark.md` 完整性能测试指南（Python 脚本 + 4 组用例 + 结果解读）
  - P0-049：在 00-platform-overview.md 两处加 ⚠️ 标注和验证提示
  - P0-053：多模态能力节补充 📌 跟进方式（官方产品页链接）
  - P0-054：文档智能四大能力表新增"API 实现状态"列，明确标注 ✅ 已实现 / ⚠️ 规划中
- **直答模式区分强化**：在 03-core-capabilities.md 中新增"产品模式 vs API 模型"对比表，从 6 个维度区分 Simple/Deep/DeepSearch 与 zhida-fast/thinking/agent，选型建议 + "对应关系仅为推测"声明
- verification.md 新增"⚠️ 项跟进方案"小节，4 项待核验均有明确跟进路径与可核验方式

### 关键核验结论
- ✅ F-201~F-235 全部有 P0 核验覆盖（修复 F-214 遗漏）
- ✅ 5 项 ⚠️ 全部落实到对应 wiki 文档章节，形成主表→跟进方案→概念章节三层呼应
- ✅ 直答三档产品模式与 API 模型 ID 区分清晰度达标

## 2026-09-05 — 产品介绍页内容整合（v4）

- 新增来源：S8 知乎开放平台产品介绍页（5 个页面：首页、知乎搜索、热榜、直答、工具）
- R 阶段：新增 35 条事实登记（F-201~F-235），新增 10 项 P0 核验（P0-046~P0-055，5 ✅ 5 ⚠️）
- 更新文档：
  - `index.md`：事实基数 200→235、P0 核验 45→55、信源 S7→S8、已知边界新增第 6 条
  - `concepts/00-platform-overview.md`：内容质量保障扩充（深度分级+创作者构成+专业背书三重机制）、核心能力概览补全 6 大能力
  - `concepts/03-core-capabilities.md`：
    - 搜索：可信度三保障+专业背书三机制+L3+硬核分级+8个应用场景
    - 热榜：两大价值+性能三优势+数据源三优势
    - 直答：新增三档产品模式（Simple/Deep/DeepSearch）
    - 工具：新增能力全景 Mermaid 图、多模态能力标注、文档智能四大能力
  - `references/article-source.md`：新增 F-201~F-235 共 35 条事实（6 个分类组）
  - `references/verification.md`：新增 P0-046~P0-055 共 10 项产品页核验

### 关键核验结论
- ✅ 产品定位与核心功能描述与 API 文档一致
- ⚠️ 5 项厂商自述数据（性能指标/用户构成/多模态能力等）已标注，待后续验证
- ⚠️ 多模态能力（图片理解/视频分析）仅产品页展示，API 尚未开放，列入已知边界

## 2026-09-05 — 知识库与文档工具 API 补全（v3）

- 新增来源：S7 知乎开发者官方文档（6 篇 API 文档：知识库列表、知识库内容列表、知识库文件上传、知识库检索、PDF 解析、PPT 生成）
- R 阶段：新增 50 条事实登记（F-151~F-200），新增 20 项 P0 核验（P0-026~P0-045，全部 ✅）
- 更新文档：
  - `index.md`：事实基数 150→200、P0 核验 25→45、官方文档验证 45→95、核心能力从 4 个扩展为 6 个
  - `concepts/03-core-capabilities.md`：新增"四、知识库 RAG 能力"和"五、文档工具能力"两大章节（原四/五/六顺延为六/七/八）
  - `references/official-api-reference.md`：新增第十四到第十九章（知识库 4 接口 + PDF 解析 + PPT 生成），含完整参数表、响应结构、错误码、cURL 示例
  - `references/article-source.md`：新增 F-151~F-200 共 50 条事实
  - `references/verification.md`：新增 P0-026~P0-045 共 20 项核验（全部通过）

### 关键核验结论

- ✅ 知识库 4 个 API（列表/内容列表/文件上传/语义检索）参数、响应、错误码全部确认
- ✅ 知识库 RAG 闭环完整：上传→解析切块→向量入库→检索返回片段
- ✅ 文档工具异步任务模式通用化：pending/running/succeeded/failed 四状态机 + progress + result/error + Idempotency-Key
- ✅ PDF 解析 4 步流程：上传文件→创建任务→轮询状态→下载 JSON 结果（按页+blocks，支持 text/title/formula/figure 四种块类型）
- ✅ PPT 生成 3 步流程：提交知乎链接+页数→创建任务→轮询→下载 PPTX（支持 3 种 URL 格式，6~21 页）
- ✅ 额度池合并规则验证：knowledge 池（4 个知识库 API 共用）、tools 池（PDF 解析+PPT 生成共用）
- ✅ P0-014"工具/知识库边界不清晰"问题已解决，从已知边界移除

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
