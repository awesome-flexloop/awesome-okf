# Knocket 知识包变更日志

## 2026-10-10 · 初版生成（博文→OKF Bundle）

- **来源**：微信公众号「怪哥」《腾讯做了一个"会聊天的个人名片"》（作者怪哥，2026-10，约 2900 字）
- **方法论**：七概念场景 4 知识沉淀链路 R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段执行
- **规模**：9 文件（3 concepts + 2 references + 2 目录 index + 根 index + 本日志）；F 编号事实 45 条（博文 30 + 官方核验 15）

### R（事实采集与核验）

- 微信反爬，经本机 defuddle CLI（`defuddle parse <url> --md`）提取 `#js_content` 全文（约 2900 字，含结尾完整）
- 信源距离预判：第三方产品观察号（怪哥）；产品事实与作者观点交织，需分层
- 清晰度预检：URL 无访问控制参数 → **公开内容**，标准工作流
- P0/P1 核验 12 项（官方产品页 knocket.trtc.io 主页功能区 + templates/html-live-chat 对比页 + TRTC 官方博客交叉核验）：**8✅ / 4⚠️ / 0❌**（F 编号行级口径 ✅ 9 / ⚠️ 5 / ❌ 0）
- 4 项 ⚠️：「AI 生成页面」「AI 模型可自接」为官方未逐字确认的单源转述；腾讯"产品壳/引流"为作者分析归观点层；首发时间媒体口径不一不采信
- 依据用户决策：① 去 examples/（观点趋势文，操作可复现性两问皆"否"）；② 补充 knocket.trtc.io 官方产品页 P0 核验

### I（骨架与归属）

- 操作可复现性两问皆"否" → 商业分析/产品观察类骨架，**不设 examples/**
- 归属：`jishu/ai/products/knocket/`（腾讯系 AI 产品，与 octop/ok-platform/todesk-ai 等异形产品束先例一致，不新建分组）
- `stale_after: 2026-12-31`（产品早期增长期，年末复核免费/功能/归属/域名）

### E（bundle 生成）

- 信源先行：article-source.md → verification.md → concepts（00/01/02）→ 各级 index → 根 index
- 全部产品事实/域名/免费口径携带 F 编号；作者观点（V 型）与产品事实（O 型）分层登记于 concepts/02 与 concepts/00-01
- 四视角对抗审查与机械门禁见下（V 阶段）

### 并行会话冲突与在途状态登记（重要）

- 生成期间观测到多个并行会话在 `jishu/ai/products/index.md` 接入其他束（nav 表已含 **opencreator、image-blaster** 等行；磁盘另存在 **inkos、vidbee** 等目录）。本会话遵循最小变更，仅接入本束 **knocket**（nav 表 + toctree + 计数），不代接/修复并行束。
- 计数口径：`products/index.md` intro 计数更新为 **25**（与本束接入后 toctree 条目数一致）；`jishu/ai/index.md` products 行 24→25、域总 227→228。
- **既有聚合计数漂移（非本次引入，归入对账）**：`bundles/index.md`（608 总、ai=227、products=26）与 `jishu/index.md`（ai 描述"224 束"）中的聚合值已与并行在途束不完全一致，且与 toctree 实际条目数存在差距。此类聚合计数以 V 阶段 `check-bundles-index.py` 目录树地面真值统一对账，本会话不手动追平（遵循最小变更，避免与并行会话冲突）。

### V（对抗审查与机械门禁）

四视角审查结论与采纳（产品观察观点文）：

1. 🟡 魔鬼代言人 → 拆解"客服 vs 名片"定义分歧，观点统一落 concepts/02，产品事实落 concepts/00-01；明确"AI 生成页面/模型自接/产品壳战略"三条边界在正文不写成官方承诺
2. 🟠 老板视角 → 明确本束为闭源商业产品观察（无 examples、无 API/self-host 教程），核心产品事实以官方页为准，避免把作者观点当商业评估
3. 🔵 未来视角 → stale_after=2026-12-31 覆盖免费政策/功能集/归属域名/AI 生成页面与模型自接是否落地
4. 链接自检 → 本束内 3 concepts + 2 references 相对链接逐条可达；间束关联仅引用已存在的 todesk-ai/octop/ok-platform/uumit-a2a-marketplace

机械门禁（2026-10-10，手动等效清单）：

| 检查项 | 结果 |
|--------|------|
| 双份 F 编号正则核对（facts.md ↔ article-source.md） | ✅ 各 45、F-001~F-045 连续无跳号、集合相等 |
| UTF-8 严格编码 | ⏳ 待跑（`check-utf8.py`，Git 提交前本地验证） |
| toctree 三级完整 | ✅ 本束 4 个 index.md 指令块齐备，条目逐一对应磁盘 9 文件 |
| 相对链接可达 | ✅ 本束内/跨束链接逐一核对（跨束仅引用已存在目录） |
| frontmatter 完整 | ✅ okf_version/type/title/description/tags/generated/verified/status/stale_after/sources 齐备，多信源 |
| 敏感信息 | ✅ 无家目录绝对路径、无密钥 |
| 勘误落实 | ✅ 4 项 ⚠️ 正文均呈现官方口径并标注；"AI 生成页面/模型自接"标"仅博文单源"；"产品壳"归观点层 |
| 聚合计数（check-bundles-index.py） | ⏳ **非本会话可跑**（并行在途束使计数不稳定）；本束已接入 products/ai 两级，聚合值待全库对账

### C（提交）

- **用户决策：不提交，交付生成结果。** 子模块处于多会话并行编辑状态（products/index.md、ai/index.md、bundles/index.md、jishu/index.md 等共享索引已被并行会话同时修改，磁盘含 inkos/vidbee/image-blaster/opencreator 等多枚在途束）。
- 遵循原子提交原则，为避免将并行会话未完成/未审查变更一并卷入，本束（9 文件）与主仓库 spec（knocket-okf-wiki/）暂保持未提交状态，留待并行会话收敛后统一对账提交。提交顺序届时仍为：子模块 awesome-okf-xs（本束 + products/ai 索引）→ 主仓库 spec → 主仓库 gitlink；push 依用户指令。