# 更新日志

## 2026-10-08

- 新增 `src-001` 来源登记及 F-001 至 F-028 共 28 条事实索引（6 条页面事实、17 条作者主张、5 条第一人称自述经历；F 编号区间连续）。
- 公开性门检通过：单次浏览器 UA GET 返回 200，无登录/邀请码/验证码/付费门槛；未保存全文，原始 HTML 仅作采集中间件留存主仓库 `.temp/`。
- 操作可复现性第二问为否（写作→收入/关注增长无独立可验证输入输出），不设 `examples/`；三层拆分为 concepts×3 + knowledge-map + references×3。
- P0/核验：无外部日期/版本/官方表态/研究引文，零可证伪硬错误；但全部收入/人数/转化自述降级 `single-source/flagged`，F-014/F-015 拆为"机制层可验证 + 公平性框架 flagged"，F-028 年龄焦虑修辞标注不采纳。
- 四视角对抗审查 10 个攻击点（幸存者偏差、相关≠因果、自我背书闭环、新人裸辞风险、人设诚实、年龄/金钱标尺、人际工具化、平台依赖、平台时效、页面易失），采纳 9 项修正，详见 references/verification.md。
- 归入 sheke/personal-growth 分组；更新分组（10→11 束，含并行会话 naval-learn-build-link）、sheke 域（57→59 束）、知识包总索引（591→593）。
- 机械门禁：以子模块官方脚本 `scripts/check-bundles-index.py`（目录树地面真值）+ `check-toctrees.py` + `check-utf8.py` 复核；另做 F 编号双份集合比对、相对链接可达、无 file:///、frontmatter 完整。
