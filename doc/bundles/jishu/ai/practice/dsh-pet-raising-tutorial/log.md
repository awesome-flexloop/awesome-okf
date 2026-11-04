# 养鱼教程知识包变更日志

## 2026-11-04

### 新增

- **bundle 初始化**：`dsh-pet-raising-tutorial` 知识包（单源公众号公开教程的七阶段转化）
  - 概念 6 篇：宠物运行时四层分工、人设五段设计、四通道拓扑与共享记忆、三层安全边界、社媒运营闭环、知识地图
  - 练习 3 篇：官方插件最小路径、人设骨架填空模板、直播三轮迭代
  - 信源 4 篇：信源台账、54 条事实登记、原文覆盖索引、核验与勘误
  - 来源：公众号《DeepSeek Harness养鱼教程来了，一文送你的肥鱼当上主播。》（数字生命卡兹克，2026-11-03）
- 旁证核验 7 个：腾讯 QQ 官方公众号接入公告（经公开转述页）、DSH 插件索引站、NapCat 与 AstrBot 仓库及独立教程、微信 ClawBot 通道公告转述、OpenClaw 项目站点。

### 阶段与限制

- R：原文全文与七个旁证采集完成；事实分四类登记（页面／作者／官方／第三方）。
- I：三条四元组洞察完成——门槛从安装转移到边界、主动性与账号风险同源、人格是配置而记忆是基础设施。
- E：一个可迁移模式「锚束演迭」提炼完成，标注为待验证模式（单案例）。
- V：四视角审查完成，产生八处口径勘误与一处内容删减（不复述自动化互动细节）。
- C：用户本次未要求提交；子仓工作区另有他方未提交束，本包不代提交、不动他方文件。
- `status: draft`；`stale_after: 2026-12-04`。到期后优先复核 F-011（插件许可与版本）、F-013（会话能力）、F-017（第三方工具风险提示）、F-029（跨通道共享记忆）。

### 审查修正

- E-2：把原文「QQ 官方机器人」改写为「由 tencent-connect 维护的官方插件」，避免被读成 DeepSeek 官方通道。
- E-3：原文「官方方式没有独立 QQ 号所以发不了 QQ 空间」由「官方限制」降级为「作者陈述的能力差异」。
- E-4：人设里的注入防护（F-032）与腾讯官方的账号层风险（F-017）拆成两层叙述，避免「写了人设就安全」的误读。
- E-5：微信通道只写「复用既有 ClawBot 通道形态」，不写「DSH 支持微信」。
- E-6：跨通道共享记忆独立成段并标为单点承诺，附三种失效表现供自测。
- E-7：三处 star 数统一标「快照量级」，不横向比较。
- 删减：机器人自动点赞、批量弹幕、自动发视频、自动开播的可执行细节不落教程，仅保留设计意图与边界。

### 验收

- 事实编号 F-001 至 F-054 在事实登记、原文覆盖索引、核验表三处集合一致。
- 全包 18 个 Markdown（13 篇正文 + 4 个 index + 1 个 log）；UTF-8 无 BOM、行尾 LF 与仓库 `.gitattributes` 一致。
- 包内相对链接与 frontmatter `sources` 路径逐条点开验证，零断链。
- 全库 `check-toctrees` 与 `check-asset-baseline` 在本包落地前即为红（他方在途束 `learn-from-materials` 未收录、工作区内容漂移），本包不宣称全库门禁通过；仅声明本包未新增导航缺口。

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261104-dsh-pet | msg=公开文章知识沉淀并新建知识包 | ctx={"scenario":"knowledge","depth":"deep","new_bundles":1}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=SCENARIO_DETECTED | session=sc-20261104-dsh-pet | msg=场景4知识沉淀（R→I→E），追加V对抗审查 | ctx={"chain":"R→I→E→V"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261104-dsh-pet | msg=原文全文与七个旁证采集；登记54条事实 | ctx={"range":"F-001..F-054","runtime_test":false}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R2 | event=GATE_PASSED | session=sc-20261104-dsh-pet | msg=G1事实无因果词，四类分层完成 | ctx={"page_fact":3,"official_claim":4,"third_party_claim":5,"author_claim":42}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=CONCEPT_COMPLETED | session=sc-20261104-dsh-pet | msg=三条洞察四元组完整 | ctx={"insights":3}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I2 | event=GATE_PASSED | session=sc-20261104-dsh-pet | msg=G2洞察四元组通过 | ctx={"phenomenon":3,"root_cause":3,"impact":3,"advice":3}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261104-dsh-pet | msg=锚束演迭模式提炼，标注待验证 | ctx={"maturity":"single-case"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E2 | event=GATE_PASSED | session=sc-20261104-dsh-pet | msg=G3模式含触发条件/步骤/反模式/迁移边界 | ctx={"steps":4,"antipatterns":4}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261104-dsh-pet | msg=四视角审查完成，八处口径勘误 | ctx={"erratum":8,"removed_sections":1}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V2 | event=GATE_PASSED | session=sc-20261104-dsh-pet | msg=包内静态验收通过；全库门禁与实测不在通过范围 | ctx={"md":18,"content":13,"broken_links":0}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S99 | event=CHAIN_COMPLETED | session=sc-20261104-dsh-pet | msg=R→I→E→V完成；C未授权，未提交 | ctx={"status":"draft","commit":false}
```
