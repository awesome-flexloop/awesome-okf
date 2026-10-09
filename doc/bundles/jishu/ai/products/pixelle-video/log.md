# 变更日志（Log）

## 2026-10-08 · 初始生成（微信推文转化 R→I→E→V→C）

- **触发**：微信公众号「赛博煎蛋」第 134 期《【134期】阿里居然把它开源了！》（2026-09-25 23:25，正文仅 478 字、20 行，截图驱动短帖）经 wechat-public-okf 七阶段工作流转化；方法论编排走七概念场景 4（知识沉淀 R→I→E→V→C），CMD-LOG session `sc-20261008-wechat-article-okf`
- **公开性预检**：公开内容（无验证码/token，Chrome UA 直取 HTML 3.48MB）→ 标准工作流，产出物入 bundles/
- **信源特殊性**：**全文未点名项目、无仓库地址**，结尾"关注公众号私信自动获取"+打赏声明；项目身份经五特征合取推断（🚩 flagged 高置信，非页面直述）
- **事实登记**：F-001~F-040 连续 40 条，六层分节（A 信源元信息 / B 作者主张 / C 身份归属 / D 架构功能 / E 生态辨析时效 / F 方法边界），page_fact 与 author_claim/【博】【官】分层；第三方营销数字（日更 5 条/2500→5 元/月费 69）无具名来源，F-040 隔离不采信
- **P0 核验**（GitHub API 实测日 2026-10-08）：13 项 → 10 ✅ / 2 ⚠️ / 1 🚩 flagged / 0 ❌
  - 🚩 flagged：项目身份为推断（帖文无名称无链接），五特征（阿里开源/全自动短视频/数字人+批量+模板/整合包+免费本地/DeepSeek+克隆音色）唯一合取 Pixelle-Video
  - ⚠️ 口径①：帖称界面模式"快速创作"，官方准确名为"AI 生成内容"模式（近似转述）；"固定文案内容"模式帖文未提
  - ⚠️ 口径②："免费本地化部署"省略官方同段前提"本地有显卡"；无 GPU 用户实际走付费云路径
  - ✅ 关键证据：仓库 `ATH-MaaS/Pixelle-Video`（AIDC-AI 整体更名，旧名 301 可解析），star 28,745 / fork 4,178 支持帖"28.4k"；Apache-2.0；v0.1.15（2026-01-27）与 main 0.2.0 未发版；templates 竖屏 25 HTML、selfhost 8 工作流、runninghub 21 工作流均目录实测；五步清单与 README 逐字一致；MoneyPrinterTurbo 经核实为 harry0703 个人项目（README「参考项目」），排除张冠李戴
- **骨架判定**：帖文两问不满足（无版本/命令/预期输出，纯截图配文），examples 不含"照帖复现"；2 篇实操的安装/配置细节全部来自官方 README 与仓库文件实测，并在篇首声明未真机执行
- **文件**：12 个（root index/log + concepts 4 含 index + examples 3 含 index + references 3）
- **状态**：stable；stale_after=2026-12-31（release 停在 0.1.x、main 0.2.0 待发，工作流/模板高频增删，给约一个季度窗口）
- **V 阶段机械门禁**（直接运行仓库 stdlib 脚本，未经 invoke/invocations，故不声称 `invoke gates.*` 结论）：
  - ✅ `scripts/check-bundles-index.py`：通过，9 域 / 61 组 / **595 束**五面一致（本束贡献 +1；同步 products 导航表/toctree、ai 组计数与总索引 mermaid/节标题/分组表；落账时总索引基线已被他会话从 592 推进至 594，按目录树地面真值落 595）
  - ✅ `scripts/check-utf8.py`：通过，11022 个文件均为有效 UTF-8（本束无 BOM、无乱码）
  - ✅ `scripts/check-toctrees.py`：全部 index.md 引用有效、所有内容文档可达（本束零问题，当次运行全库亦零报错）
  - ✅ 相对链接逐验：bundle 内 30 条 Markdown 相对链接全部可达
  - ✅ F 编号：article-source.md 登记 F-001~F-040 连续 40 条；正文引用 38 个编号全部已登记，无跳号、无未注册引用（2 条登记事实未被正文引用属正常）
  - ✅ 敏感路径零残留（无真实 C:\Users / file:/// 绝对路径；log 内为描述性文本）
- **并发备注**：products 目录为多会话共用区，计数以交付瞬间目录树地面真值落账（本束贡献 products 19→20、ai 216→217、jishu 437→438；总索引落账瞬间基线为他会话推进后的 594，本束后 595）；`jishu/index.md` 散文陈旧计数不在门禁五面内，按最小变更未改动
