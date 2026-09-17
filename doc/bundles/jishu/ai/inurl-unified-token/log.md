# 变更日志

## 2026-09-16

- **创建**：微信公众号推广博文《一个程序员的省钱实录：从月付 500 到 0 元》（风信旗/检校千牛卫，2026-09-02）经 blog-article-to-okf-wiki 七阶段工作流（seven-concepts 场景 4：知识沉淀 R→I→E→V）转化为 OKF v0.2 知识包。
- **事实登记**：F-001~F-043 博文事实（browser_use 提取 `#js_content` 全文，绕过微信反爬）；F-044~F-070 三独立子代理核验补充（产品站点实测 / 国内模型官方口径 / 海外定价时效），双份登记于 spec `facts.md` 与本束 `references/article-source.md`，编号连续无跳号。
- **核验结果**：P0 共 11 ✅ / 7 ⚠️ / 4 ❌（F-060 时间线矛盾、F-064 DeepSeek 免费失实、F-069 旗舰型号过时、F-070「17 家 Key + 0 元」定价冲突）。核心声明证伪 → `status: flagged`，`stale_after: 2026-12-31`。
- **文件集（12 个）**：根 `index.md`、`log.md`（2）；concepts 4 篇 + 子 index（5）；examples 1 篇 + 子 index（2）；references 2 篇（article-source/verification）+ 子 index（3）。
- **门禁（2026-09-16 实测）**：直接运行子模块脚本（Python 3.13，无需 invocations）——`check-utf8.py` 通过（10407 文件）；`check-toctrees.py` 本束 14 文件全部可达（已接入组 index 导航表 L76 + toctree），残留告警均属其他并行会话未完成 WIP（firecrawl/inurl-byok-free-models/openhuman/oracle 缺根 index 等）；`check-bundles-index.py` 本束已被工作树扫描计入（束数在他会话的 549 次扫盘时即含本目录），残留 +1 漂移为他会话新增束（如 llama.cpp）未同步，按「谁添加谁对账」不属本束债务。双份 F 编号集合机器比对一致（F-001~F-070 连续）、束内相对链接全部 Test-Pass、零 file:/// 与家目录泄露。
- **并行会话说明**：同库另有姊妹篇转化束 `inurl-byok-free-models`（同账号同产品的另一篇软文《同事偷偷用这个网站，一年省下5000块》2026-09-04）正在并行生产；两束完成后应在「主题关联」段互链（本束暂不链接其未完成根 index，避免断链）。组 index 编辑期间与他会话写入发生一次碰撞（粘连行），已修复。
