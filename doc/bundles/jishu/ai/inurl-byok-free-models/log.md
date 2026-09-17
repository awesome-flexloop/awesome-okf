# 更新日志

## 2026-09-16

**Status**: `flagged`（F-007 标题省钱数字查无出处；F-017 Agnes 国籍与上下文两处硬错；F-026/F-029 产品匿名运营、第三方证据为零）

### 工作流阶段（blog-article-to-okf-wiki 七阶段）

- **S0 预检**：微信公开文章（无访问控制参数）→ 公开内容；spec 落 `.trae/specs/okf-wiki-ecosystem/inurl-byok-free-models-blog-okf-wiki/`
- **R 信源+事实**：微信反爬确定，直接 browser_use 取 `#js_content`（2090 字符，两轮交叉一致）；信源距离预判为**厂商自宣**（导流软文+注册 CTA+同号系列文）；F-001~F-025 博文事实登记
- **R 核验**：4 个独立子代理分组 P0 核验（产品/Agnes/智谱+硅基/美团）+ 本库 agnes-ai、free-llm-api-roundup 既有 bundle 交叉佐证；补充 F-026~F-035；12 组 P0：✅5 / ⚠️6 / ❌3
- **I 拆分**：操作可复现性两问皆"否"（PART 04 仅口号，无代码/配置/实测）→ 无 examples/；技术综述/资讯盘点骨架；归属直挂 `jishu/ai/`（单篇不新建分组，有 mattpocock/free-llm 等先例）
- **E 生成**：references 先行（article-source + verification）→ concepts 三篇（事实/机制/资源）→ 各级 index；9 文件
- **V 审查**：四视角审查 + 机械门禁（UTF-8/双份 F 编号/toctree/相对链接/计数）；组索引与总索引接入；互链 4 个相关 bundle

### 核验关键发现

| 声明 | 结果 |
|------|------|
| 一年省 5000 块（F-007） | ❌ 官网/同号软文/全网查无；BYOK 不经手 token 售卖，归因不成立 |
| Agnes 美国（F-017） | ❌ 新加坡 Sapiens Technology（PRNewswire/App Store/Tech in Asia 三源） |
| agnes-2.5-flash 百万上下文（F-017） | ❌ 官方 512K；1M 为已废弃 2.0-flash 临时窗口（本库 agnes-ai bundle 同证） |
| Agnes 完全免费（F-017） | ⚠️ 阶段性 $0（刊例价 $0.05/$0.15）+ 20 RPM + 付费档并存 |
| GLM-4-Flash ¥0（F-018） | ✅ 250414 在线免费/128K/V0 并发 200；下线的是 GLM-4.5-Flash |
| 硅基免费通道（F-019） | ✅ 9B 开源小模型全员 0 元；⚠️ 无 GLM-4-Flash/满血 DeepSeek；¥16 券为现行政策 |
| LongCat 万亿/1M/1000 万（F-020） | ⚠️ 均限 LongCat-2.0；1000 万须实名领、30 天有效、限时 |
| inurl 加密/escrow（F-012/F-013） | ✅ 前端代码实测 PBKDF2(SHA-256,10 万)+AES-GCM256、escrow_pw/rec 双份 |
| inurl 零中转/互转/不封号（F-014/F-015） | ⚠️ 仅厂商自述；本地代理闭源（localhost:3003，启动器内嵌凭据） |
| 运营主体/第三方证据（F-026/F-029） | ❌ 无 ICP/公司/条款/联系方式；全网独立证据为零 |

### V 阶段机械门禁记录

- 双份 F 编号：spec facts.md 与 references/article-source.md 均为 F-001~F-035，集合一致、连续无跳号
- 三级 toctree：bundle 根/concepts/references 三块齐备，条目逐一对应文件；组索引追加一行一条目
- 计数同步：本组与同日多个并行转化会话共同增量，最终以子项目官方脚本三角对账为准（9 域/59 组/555 束，五面一致）——未手工估算写数
- 相对链接、UTF-8 strict、frontmatter、敏感路径手动等效清单通过；随后以子项目官方门禁脚本复跑通过（见下"并行会话协调记录"）

### 四视角对抗审查（V 阶段）

| 视角 | 关键质询 | 结论 |
|------|---------|------|
| 事实溯源 | 是否有 facts.md 之外的数字/模型名？勘误是否在正文落实？ | 所有数字带 F 编号；正文呈现官方正确值（新加坡/512K/9B 小模型/实名 30 天/匿名运营），未照搬源文错误 |
| 结构规范 | frontmatter/toctree/骨架合规？ | 无 examples（两问皆否判据留档于 spec）；三级 toctree 经 check-toctrees 全局通过 |
| 读者可用性 | 相对链接可达？无图注卡片信息是否补齐？ | 链接门禁通过；6 个 URL 与导流性质在 article-source 留档 |
| 时效边界 | 单源/时点/观点分层？ | 厂商自述提示块置顶；4 家额度标 2026-09-16 时点；6 条作者观点标 📝 不核验 |

### 并行会话协调记录（2026-09-16）

转化期间检测到另一会话正在转化**同公众号另一信源**（2026-09-02《一个程序员的省钱实录：从月付 500 到 0 元》，URL `mp.weixin.qq.com/s/dSTvvOjPIRpbSJHIqxi0gw`）为姊妹束 `inurl-unified-token/`（70 条事实，含 examples）。经用户确认两束并存（不同信源、同主题互链，比照豆包主题簇先例）：

- 共享文件 `jishu/ai/index.md` 在两会话并发写入中两次出现行级粘连；待其稳定（150s 无写入）后统一修复，并补回并行各会话丢失的 8 行导航表条目（aitokenbus/gpt6-astra/firecrawl/wigolo/uumit/loopx/两个 inurl 束）
- 两束互链已双向落地；free-llm-api-roundup、token-economy-explosion 已加反向链接
- 官方门禁复跑：`check-bundles-index.py`（9 域/59 组/555 束五面一致）、`check-toctrees.py`（全部引用有效、内容可达）、`check-utf8.py`（10412 文件）均通过

### Mermaid 安全编码修复（2026-09-16，七概念 I→F→V 轻量链路）

- 触发：用户要求修复 concepts/00 信源距离图；V 视角对抗排查扩展到同束 01 篇架构图
- 根因：① 4+2 条边标签含中文未加双引号（违反六规则之边标签 `-->|"标签"|`）；② 节点/标签内 7 处 `<br/>`（仓库 VS Code 兼容规则禁用，须单行）
- 修复：两张图节点文案改单行（冒号/逗号分层，信息无损），边标签全部双引号包裹，去除 ❌/⚠️ 表情符号改文字表述
- 验证：`.agents/scripts/repo-check.py mermaid`（projects/ 为全局排除目录，经 build/ 临时副本等效扫描）4 文件 0 错误 0 警告；临时目录已清理

### 复核安排（flagged）

- **2026-12-16 前**：① inurl 主体信息/是否出现第三方证据或安全事件；② Agnes $0 优惠是否结束、限速变化；③ LongCat 1000 万活动续期情况；④ 硅基 ¥16 券活动（官方至 2026-12-31）
