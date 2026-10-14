# 变更日志

## 2026-10-14

- 使用 `seven-concepts-cmd` 执行知识沉淀链路：R → I → E → V（V 由独立 Review 阶段承担）。
- 使用 browser_use 提取微信公众号正文（#js_content 文字层），并对正文内嵌 4 张 960×1280 图文卡片逐张视觉识读（innerText 不承载图卡文字）；临时图片在门禁阶段清理，不入包。
- 登记 F-001 至 F-038（文字层 14 条、图卡层 24 条）；spec 侧 `facts.md` 与 `references/article-source.md` 双份编号集合经正则比对一致（各 38 条，无差集）。
- 按操作可复现性两问判定为商业分析/个人自述复盘，不创建 `examples/`。
- P0 核验结论：全部经营数字零独立信源；同篇 110 万与 180 万营收口径冲突、70 万到手与外包网络规模存在成本张力、9.9 块/9.9 万须带单位、三修辞比例无统计来源；五项内部算术核对成立；Coze（coze.cn）仅作技术名词背景源。
- 通过 G1（事实/观点/建议分层）、G2（建议假设化、含指标与证伪）、G3（单源自述"结构学习"模式可迁移）检查；bundle 状态设为 `flagged`。
- 接入三级索引（组/域/总）；磁盘已有 3 个束目录未登记于组索引的既存漂移未在本次修复，仅在此注记。
- invoke 集合因环境缺少 invocations 包元数据无法加载；已绕过 invoke 直接运行仓库官方门禁脚本（与 gates.* 同一实现）：
  - `scripts/check-utf8.py`：通过，doc/ 下 11555 个文件均为有效 UTF-8；本束 7 个 .md 另做 strict roundtrip 全部通过。
  - `scripts/check-bundles-index.py`：通过，9 域/61 组/634 束五面一致（本束接入时总登记数为 633；并行会话随后新增 1 个技术束，磁盘当前态为 634，脚本复核仍绿；本束贡献为 sheke 66→67、industry 24→25）。
  - `scripts/check-toctrees.py`：报告 82 处问题，逐条核对全部来自并行会话在途束（deepseek-harness、agent-self-evolution-evaluation、microsoft-mxc-agent-containment、wifit3、tauri、wecom-5-0-12-release）与 3 个既存未登记漂移束（telecom-token-operation、telecom-ai-pilot-base、ling-3-1-flash-first-test）；本束 9 个文件零命中、全部可达。
- 手动补充项：双份 F 集合 38=38 零差集、concepts 引用的 38 个 F 编号全部在域；两条主题关联相对链接 Test-Path 均 True；file 协议链接与家目录路径零出现；束目录无任何图片/html；临时图片目录 `%TEMP%/okf-article-imgs` 已删除。
- 未执行 Git 提交，等待用户明确提交请求。
