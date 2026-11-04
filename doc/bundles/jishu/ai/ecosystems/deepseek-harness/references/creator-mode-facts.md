---
type: Reference
title: 创造模式事实登记 F-017 至 F-065
description: 页面事实、作者需求、作者结果与官方说明分层登记，旧编号不重排。
source: https://mp.weixin.qq.com/s/pslQaWATxQDlhBBAZROEwg
sources:
  - { id: manifest, resource: source-manifest.md }
generated: { by: "process:seven-concepts-cmd", at: "2026-11-04T10:01:28+08:00" }
status: draft
stale_after: 2026-12-04
---

# 创造模式事实登记 F-017 至 F-065

F-001 至 F-016 保留在[旧文章事实登记](facts.md)，不代表本次已重新核验。下表新增 49 条，全部可回溯[来源台账](source-manifest.md)。`page_fact` 只说明页面元信息；`author_claim` 分为产品主张、提示词需求与结果自述；`official_claim` 表示官方当前说明，不代表独立性能验证。

P 编号是本次采集时 `#js_content p` 的 DOM 顺序，从 1 开始，不是作者自带段落编号；提示词以章节名与条目定位。页面改版后优先按章节及主张文本复核。

| F | claim | type | source_id | locator | status |
|---|-------|------|-----------|---------|--------|
| F-017 | 页面标题为《DeepSeek 再放大招，上线 Creator Mode。》 | page_fact | wx-creator | 页面标题 | page-checked |
| F-018 | 页面署名沉默王二，标记原创，时间为 2026-11-03 18:30 | page_fact | wx-creator | 账号与发布时间 | page-checked |
| F-019 | 作者把 V4.1-Flash-1017、Super-Agent 与 Creator 描述为近期更新 | author_claim | wx-creator | 导言 P2 | partially-confirmed |
| F-020 | 作者称生成过程包含插槽检查、前后端代码、安装与界面热更新 | author_claim | wx-creator | 导言 P3 | single-source |
| F-021 | 作者自述制作了五个插件 | author_claim | wx-creator | 导言 P4 | single-source |
| F-022 | 文中称创造模式有五个开启入口，正文明确空白会话的模式选择入口 | author_claim | wx-creator | 01 P5-P6 | single-source；其余入口未核验 |
| F-023 | 文中称创造模式是内置 Agent 预设，ID 为 cordis | author_claim | wx-creator | 01 P7 | single-source |
| F-024 | 文中称创造模式保留 Standard 的全部工具 | author_claim | wx-creator | 01 P8 | official-corroborated |
| F-025 | 文中列出 cordis_inspect_list 与 cordis_inspect_query | author_claim | wx-creator | 01 P8 | single-source |
| F-026 | 文中列出插件开发 Skills 与安装到当前 profile 的 plugin_manager | author_claim | wx-creator | 01 P8 | single-source |
| F-027 | 作者称模型适配、工具注册、会话日志和 Agent Loop 都是 Cordis 插件 | author_claim | wx-creator | 01 P9 | official-corroborated |
| F-028 | 倒计时需求使用 offwork-countdown，挂载聊天输入区右上角 | author_claim | wx-creator | 01 提示词条目1 | requirement-only |
| F-029 | 倒计时需求指定 HH:MM:SS、默认 18:30 且时间可调 | author_claim | wx-creator | 01 提示词条目2 | requirement-only |
| F-030 | 倒计时需求包含进度百分比、归零绿色状态与标题变化 | author_claim | wx-creator | 01 提示词条目2-3 | requirement-only |
| F-031 | 作者建议完全权限，并称插件管理器操作需要该权限 | author_claim | wx-creator | 01 P11-P12 | single-source；权限契约未核验 |
| F-032 | 作者报告看到倒计时归零后的状态 | author_claim | wx-creator | 01 P13 | reported-result |
| F-033 | Style Lab 需求指定侧栏入口、主面板与恢复默认按钮 | author_claim | wx-creator | 02 提示词条目1 | requirement-only |
| F-034 | Style Lab 需求列五套皮肤：8-Bit Pixel、Neon Grid、Green Terminal、Paper Press、Zen Glass | author_claim | wx-creator | 02 提示词条目2 | requirement-only |
| F-035 | Style Lab 需求包含全局覆盖、实时切换、本地保存和默认恢复 | author_claim | wx-creator | 02 提示词条目2 | requirement-only |
| F-036 | 8-Bit Pixel 需求指定圆角为 0px | author_claim | wx-creator | 02 提示词 8-Bit Pixel | requirement-only |
| F-037 | 作者报告出现五张主题卡，终端主题无需重启切换，像素主题去除圆角 | author_claim | wx-creator | 02 P15-P16 | reported-result |
| F-038 | Transformer Lab 需求输入 the cat sat on the，展示五个 Token | author_claim | wx-creator | 03 提示词条目1-2 | requirement-only |
| F-039 | Transformer Lab 需求列 Embed、Q K V、Attention、Mix、FFN、Logits 六阶段 | author_claim | wx-creator | 03 提示词条目2 | requirement-only |
| F-040 | 教学需求指定四维嵌入向量与两层全连接 FFN | author_claim | wx-creator | 03 提示词 Embed、FFN | requirement-only；演示维度 |
| F-041 | 提示词以 softmax(Q·K / √d) 描述注意力，并指定末尾 the 对 cat、sat 的关注 | author_claim | wx-creator | 03 提示词 Attention | requirement-only；非完整矩阵公式 |
| F-042 | Logits 需求指定 mat 0.61、floor 0.18、rug 0.09、bed 0.06、couch 0.03 | author_claim | wx-creator | 03 提示词 Logits | requirement-only；非推理结果 |
| F-043 | 作者报告旋转缩放、阶段镜头、Inspector、六阶段播放与返回聊天可用 | author_claim | wx-creator | 03 P20-P24 | reported-result |
| F-044 | 建筑场景需求列埃菲尔铁塔、长城、太和殿、斗兽场四座地标 | author_claim | wx-creator | 04 提示词 | requirement-only |
| F-045 | 建筑场景需求列 Day、Dusk、Night 三档光照及旋转、标注、重置、返回 | author_claim | wx-creator | 04 提示词条目1 | requirement-only |
| F-046 | 建筑场景需求含长城敌楼、马道、垛口以及太和殿重檐、三层台基和御道标注 | author_claim | wx-creator | 04 提示词条目2 | requirement-only；未核验建筑学准确性 |
| F-047 | 作者报告查看白天的慕田峪长城与黄昏的太和殿 | author_claim | wx-creator | 04 P27-P28 | reported-result |
| F-048 | 作者称建筑案例在官方宣传片中热度很高 | author_claim | wx-creator | 04 P25 | single-source；无热度指标 |
| F-049 | FUYU 需求为等轴测体素海岛、数量统计与一键建亭 | author_claim | wx-creator | 05 提示词条目1 | requirement-only |
| F-050 | FUYU 需求列八格工具栏：草地、沙滩、岩石、木柱、屋檐、灯笼、体素树、小羊 | author_claim | wx-creator | 05 提示词条目1 | requirement-only |
| F-051 | FUYU 初始场景需求为七棵树、三只羊与方块放置移除 | author_claim | wx-creator | 05 提示词条目2 | requirement-only |
| F-052 | FUYU 夜景需求包含双层飞檐木亭与发光灯笼 | author_claim | wx-creator | 05 提示词条目2 | requirement-only |
| F-053 | 作者报告 SUNNY NOON 起步，建造或 STARRY NIGHT 按钮能切换夜景 | author_claim | wx-creator | 05 P30-P31 | reported-result |
| F-054 | 作者以 QQ 空间作类比，并提出运行时改造软件与插件同等地位的解读 | author_claim | wx-creator | ending P33、P36-P37 | opinion；非安全保证 |
| F-055 | 官方主页说明 Creator 包含 Standard 能力及运行时检查、插件试验、预设创作指导 | official_claim | official-home | Creator mode | official-checked |
| F-056 | 官方主页说明 Cordis 管理挂载、卸载与依赖，能力由插件提供并用服务事件协作 | official_claim | official-home | Cordis kernel、Capabilities | official-checked |
| F-057 | 官方主页声明 developer preview，核心插件与 API 将继续演进 | official_claim | official-home | Join the ecosystem | official-checked |
| F-058 | 官方入门页要求设置模型、选择工作区，再发任务；审批按当前权限策略触发 | official_claim | official-start | Configure、Choose、Run | official-checked |
| F-059 | 官方基础教程示范 apply(ctx) 入口与 inject 依赖，显式资源可用 ctx.effect 返回清理函数 | official_claim | official-basic | What is a plugin、Automatic cleanup、Declare dependencies | official-checked |
| F-060 | 官方安装文档区分 npm bundle 的 dsh.bundle 与 profile 的 dsh.profile | official_claim | official-publish | Two concepts, two manifests | official-checked |
| F-061 | 官方安装页用 dsh plugin --profile demo add ./hello-plugin、dump-config 与 remove 演示安装检查卸载 | official_claim | official-publish | Install into a profile | official-checked；本次未执行 |
| F-062 | 官方安装页说明后层覆盖前层，patch 会替换该行整个 config 而非深合并 | official_claim | official-publish | The loading order | official-checked |
| F-063 | 官方 HMR 页说明旧实例卸载与新实例加载；依赖缺失时可处于 PENDING | official_claim | official-hmr | Hot module replacement、Diagnosing | official-checked |
| F-064 | 官方模型公告列 V4.1-Flash-1017，并建议 Harness v0.2.1-rc.1 或更新版本获得较佳体验 | official_claim | official-model | 公告开头 | official-checked；非 Creator 最低版本 |
| F-065 | 官方模型公告自述使用自反馈强化学习改进端到端项目开发 | official_claim | official-model | Build complete projects | official-checked；成效未独立验证 |

衍生计算及执行者建议不进入上表。概率合计、验收条件和安全建议见[核验记录](verification.md)与[知识地图](../concepts/knowledge-map.md)。
