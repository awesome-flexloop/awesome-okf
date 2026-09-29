# 变更日志（Log）

## 2026-09-16 · 初始生成（博文转化 R→I→E→V）

- **触发**：微信公众号「极客之家」推文《一个悄然崛起的国产开源项目，让 AI Agent 跑满 200 小时不掉线》（作者丛林，2026-09-03）经 blog-article-to-okf-wiki 七阶段工作流转化；方法论编排走七概念场景 4（知识沉淀 R→I→E→V）
- **spec**：主仓库 `.trae/specs/okf-wiki-ecosystem/loopx-long-horizon-agent-okf-wiki/`（spec.md + facts.md）
- **事实登记**：F-001~F-049 连续 49 条（博文 36 条含 11 处作者观点标注 + 核验补充 13 条；V 阶段发现初稿 F-010 跳号，已将 F-011~F-050 统一下移重排）；双份登记（spec facts.md ↔ references/article-source.md）编号集合一致
- **P0 核验**（核验日 2026-09-16）：12 项 → 10 ✅ / 2 ⚠️ / 0 ❌
  - ⚠️ 勘误①：博文"v0.4.x 阶段"滞后——发文当日 PyPI 最新 0.5.4（0.5 线始于 08-19）；核验时最新 1.0.5（09-15）
  - ⚠️ 勘误②：博文"纯 Python/无三方依赖"为 0.4/0.5 发货口径；TS 内核迁移 RFC 2026-08-15 已 Accepted，1.0（09-06）起需 Node.js 22.18+
  - ✅ 关键证据：200h OpenViking 公开 PR 序列实测 169 PR（最早 2026-07-17）+ 官方边界逐字对应；star 5818（09-13）支持"5000+"；安装/quota/门禁/宿主命令逐字一致
- **骨架判定**：操作可复现性两问皆"是"（作者实测安装链路，有版本/平台/预期输出）→ 含 examples/（2 篇，限定博文覆盖范围）
- **文件**：12 个（root index/log + concepts 4 + examples 3 + references 3）
- **状态**：stable；stale_after=2026-11-30（周级迭代 + 内核迁移进行中，缩短复核窗口）
- **V 阶段机械门禁**（直接运行仓库 stdlib 脚本，未经 invoke/invocations，故不声称 `invoke gates.*` 结论）：
  - ✅ `scripts/check-bundles-index.py`：通过，9 域/59 组/543 束五面一致（本束贡献 +1；同步 ai 分组导航表与 toctree）
  - ✅ `scripts/check-utf8.py`：通过，10295 个文件均为有效 UTF-8（本束无 BOM、strict roundtrip 无乱码）
  - ✅ `scripts/check-toctrees.py`：本束 12 文件零问题（无断链、无孤立、根 index 已接入 ai 组 toctree）；脚本当次报出的 28 处问题全部属于他会话进行中的 WIP（wigolo / uumit-a2a-marketplace / gpt6-astra-usage-guide / llama-cpp-local-inference），按"谁添加谁对账"未代为修改
  - ✅ 相对链接逐验：bundle 内 21 条 Markdown 相对链接全部可达（V 中发现并修复根 index 主题关联 5 条链接层级错误：根文件应为 `../<sibling>/` 而非 `../../`）
  - ✅ 双份 F 编号集合一致：facts.md ↔ article-source.md 均为 F-001~F-049 连续 49 条（初稿 F-010 跳号，已重排）；正文引用的 F 编号全部存在登记，无未注册引用
  - ✅ 敏感路径零残留（无 C:\Users / /Users/ / file:/// 绝对路径）
  - 并发备注：制作期间至少 3 个他会话并行落盘（sheke/marketing/sell-before-build-validation、ai-agent/openviking、uumit-a2a-marketplace、wigolo 等），总索引计数在 539→543 间移动，曾出现一次 ai 行数字段并发撞车（`| 191 |189 |`），已修复；最终计数按交付瞬间目录树地面真值 543/410/191 落账，后续他会话新增束需再行对账
  - `jishu/index.md` 正文"111 个一级束 / ai 45"为既有陈旧散文计数（不在 check-bundles-index 五面对账范围内），按最小变更未改动
