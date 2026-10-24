---
type: reference
title: 信源台账与编号事实清单（F-001–F-096）
description: 秒悟 Meoo 产品增长 Skill 包教程束的 S1–S4 信源台账、F-001–F-096 编号事实、24/22/25 口径归一、两层命名映射、缺口清单与转写噪声登记
tags: [meoo, miaowu, growth-skill, source-ledger, facts, wechat-article]
generated:
  by: seven-concepts-cmd+wechat-public-okf
  at: "2026-10-24T12:00:00+08:00"
status: draft
stale_after: "2027-04-24"
sources:
  - id: wx-5g
    resource: https://mp.weixin.qq.com/s/5g_cjKUxV2YGZEMB4kyaVg
    title: 从产品想法到第一批用户：秒悟Meoo增长Skill包怎么选、怎么用？
    author: 秒悟Meoo
    last_modified: 2026-10-15
  - id: bounty-plaza
    resource: /jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/index.md
    title: 秒悟应用赏金广场（AI Builder Growth 共创计划）·同库既有束
  - id: meoo-skills
    resource: https://meoo.com/skills
    title: 秒悟 Meoo 技能市场
  - id: meoo-docs-skill-market
    resource: https://docs.meoo.com/features/skill-marketplace
    title: 秒悟 Meoo 官方文档 · 技能市场
---

# 信源台账与编号事实清单（F-001–F-096）

本文件是本束一切具体声明的唯一出处。事实严格分为三层：**页面事实**（文章写了什么）、**作者主张**（作者的判断、建议、演示输出）与**执行者洞察**（见 `concepts/04-insights-and-boundaries.md`，不进入本表）。

## 1. 信源台账（Source Manifest）

| source_id | URL | 标题 | 账号/归属 | 日期 | 可访问性 | 归属证据 | 状态 |
|---|---|---|---|---|---|---|---|
| `S1` | `https://mp.weixin.qq.com/s/5g_cjKUxV2YGZEMB4kyaVg` | 从产品想法到第一批用户：秒悟Meoo增长Skill包怎么选、怎么用？ | 微信公众号「秒悟Meoo」 | 2026-10-15 16:36 | 公开可访问，无需登录、验证码或邀请码 | 页面 `#js_name` 显示「秒悟Meoo」；`og:title` 与页面标题一致 | 已采集（正文 + 15 张配图） |
| `S2` | `/jishu/ai/ecosystems/miaowu/miaowu-bounty-plaza/index.md` | 秒悟应用赏金广场（AI Builder Growth 共创计划） | 本知识库同组既有束（转引自 `events.meoo.com`） | 2026-10-17 | 库内文件 | 同库既有束，含 25 条条目与七阶段分类 | 用于跨页对账（非独立第三方） |
| `S3` | `https://meoo.com/skills` | 秒悟 Meoo 技能市场 | 秒悟 Meoo 平台 | 抓取 2026-10-24 | 公开可访问 | 页面自述为秒悟 Meoo 技能集合页；技能条目显示作者 handle | 已采集（首屏技能条目） |
| `S4` | `https://docs.meoo.com/features/skill-marketplace` | 技能市场（官方文档） | 秒悟 Meoo 官方文档 | 抓取 2026-10-24 | 公开可访问 | 文档站侧边栏归属「功能特性 → 扩展能力」 | 已采集（机制说明） |

> **公开性预检结论**：`S1` 为公开文章，URL 不含 `share?code=`、`token=` 等访问控制参数，未触发登录墙或验证码；采集过程未绕过任何访问限制，也未保存全文镜像。

## 2. 编号事实清单（F-001–F-096）

### 2.1 页面与背景（F-001–F-013）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 文章标题为《从产品想法到第一批用户：秒悟Meoo增长Skill包怎么选、怎么用？》 | page_fact | S1 | 页面标题 / `og:title` | verified |
| F-002 | 发布账号为微信公众号「秒悟Meoo」 | page_fact | S1 | 页面 `#js_name` | verified |
| F-003 | 页面显示的发布时间为「2026年10月15日 16:36」 | page_fact | S1 | 页面 `#publish_time` | verified |
| F-004 | 文章公开地址为 `https://mp.weixin.qq.com/s/5g_cjKUxV2YGZEMB4kyaVg` | page_fact | S1 | URL | verified |
| F-005 | 文章于 2026-10-24 经无登录通道可正常读取正文与配图 | page_fact | S1 | 采集记录 | verified |
| F-006 | 文章开头列举四类困境：想法不确定有没有人需要；应用准备上线但介绍素材没做；链接发出去了找不到试用用户；收了一堆反馈但下一版不知道先改什么 | page_fact | S1 | 开头导语 | verified |
| F-007 | 秒悟 Meoo 联合 22 位博主共创一套产品增长 Skill 技能包 | author_claim | S1 | 第 1 段 | single-source |
| F-008 | 技能包覆盖需求验证、产品构建、官网与商店物料、首发内容、视频与封面、用户获取、增长诊断、成本定价、反馈迭代等任务 | page_fact | S1 | 第 1 段 | verified |
| F-009 | 文章主张的使用方式：把产品和具体问题带进来，借助对应 Skill 准备物料、梳理判断、拆解行动；先选眼前需要的一项即可开始 | author_claim | S1 | 第 2 段 | single-source |
| F-010 | 文章给出「当前情况 → 可以先用」七行对照表（详见 `concepts/01-skill-catalog.md` 表 1） | page_fact | S1 | 「先找到你的问题」表 | verified |
| F-011 | 七行对照表之后，文章提示「完整技能包还有更多选择，先收藏这张清单」 | page_fact | S1 | 表后一句 | verified |
| F-012 | 完整清单图的标题区为「Meoo × 22 位共创博主」「产品增长 Skill 全清单」「按场景找技能，按任务选方法」 | page_fact | S1 | 配图（全清单） | verified |
| F-013 | 完整清单图脚注为「按共创方向汇总，具体以技能详情页为准」 | page_fact | S1 | 配图（全清单）脚注 | verified |

### 2.2 五类分组与 22 条技能行（F-014–F-040）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-014 | 清单第一类为「01 需求与产品构思」，共 6 条 | page_fact | S1 | 配图（全清单） | verified |
| F-015 | 清单第二类为「02 产品构建与展示」，共 3 条 | page_fact | S1 | 配图（全清单） | verified |
| F-016 | 清单第三类为「03 发布与内容传播」，共 6 条 | page_fact | S1 | 配图（全清单） | verified |
| F-017 | 清单第四类为「04 获客与增长诊断」，共 4 条 | page_fact | S1 | 配图（全清单） | verified |
| F-018 | 清单第五类为「05 商业化与反馈迭代」，共 3 条 | page_fact | S1 | 配图（全清单） | verified |
| F-019 | 阿东玩AI｜需求先验：调研与验证 | page_fact | S1 | 配图 01 类第 1 行 | verified |
| F-020 | 北峰Agent｜产品判断：验证需求 | page_fact | S1 | 配图 01 类第 2 行 | verified |
| F-021 | yan（ai赚钱版）｜真需求诊断 | page_fact | S1 | 配图 01 类第 3 行 | verified |
| F-022 | 设计师雪梨｜产品评审：收敛 MVP | page_fact | S1 | 配图 01 类第 4 行 | verified |
| F-023 | 南洋理工DAN讲AI｜真需求验证：测试购买 | page_fact | S1 | 配图 01 类第 5 行 | verified |
| F-024 | 西瓜在创作｜业务内容转互动产品 | page_fact | S1 | 配图 01 类第 6 行 | verified |
| F-025 | 职场懒人｜调研结论转产品第一版 | page_fact | S1 | 配图 02 类第 1 行 | verified |
| F-026 | 斑马MVP实验室｜产品官网设计与制作 | page_fact | S1 | 配图 02 类第 2 行 | verified |
| F-027 | 空格的键盘｜应用商店文案与截图 | page_fact | S1 | 配图 02 类第 3 行 | verified |
| F-028 | 菜头Prompt.AI｜应用首发图文与脚本 | page_fact | S1 | 配图 03 类第 1 行 | verified |
| F-029 | 李叔聊AI｜文字脚本转白板动画 | page_fact | S1 | 配图 03 类第 2 行 | verified |
| F-030 | 是树小姐｜笔记封面与标题设计 | page_fact | S1 | 配图 03 类第 3 行 | verified |
| F-031 | 一起Vibe｜多平台推广视频制作 | page_fact | S1 | 配图 03 类第 4 行 | verified |
| F-032 | 塔斯海｜GitHub 项目诊断与介绍优化 | page_fact | S1 | 配图 03 类第 5 行 | verified |
| F-033 | 蔡不菜（AI版）｜热点选题与推广内容 | page_fact | S1 | 配图 03 类第 6 行 | verified |
| F-034 | 桃子AI｜应用冷启动方案 | page_fact | S1 | 配图 04 类第 1 行 | verified |
| F-035 | 陈乔维Justin｜首批用户获取计划 | page_fact | S1 | 配图 04 类第 2 行 | verified |
| F-036 | 小E爱学习（AI提效）｜增长诊断与实验卡 | page_fact | S1 | 配图 04 类第 3 行 | verified |
| F-037 | 花叔｜增长瓶颈与优先行动 | page_fact | S1 | 配图 04 类第 4 行 | verified |
| F-038 | 古希腊掌管代码的神｜AI 应用成本核算与定价 | page_fact | S1 | 配图 05 类第 1 行 | verified |
| F-039 | 海明Dev｜App 付费流程与套餐优化 | page_fact | S1 | 配图 05 类第 2 行 | verified |
| F-040 | 许多的数码世界｜用户反馈转增长实验 | page_fact | S1 | 配图 05 类第 3 行 | verified |

### 2.3 六个重点技能与示例（F-041–F-064）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-041 | 文章称「下面选取六个重点技能详细介绍，并附上使用示例」 | page_fact | S1 | 六例引导句 | verified |
| F-042 | 阿东玩AI 的「需求先验·模拟用户调研」围绕产品想法，检索近期可获取的用户抱怨、替代方案评价和付费线索，辅助判断需求、取舍功能；主要产出为需求判断、功能取舍、7 天验证计划 | author_claim | S1 | 技能 1 | single-source |
| F-043 | 该例输入为一句想法：「我要做 agent 团队，用来解决办公问题。」 | page_fact | S1 | 技能 1 示例 | verified |
| F-044 | 该例给出的当前判断是「暂不够判」，理由为缺少目标用户的一手反馈；建议先聚焦一条文档生成流程，并安排 7 天验证计划、访谈 20 位真实办公用户后再决定是否增加功能 | author_claim | S1 | 技能 1 示例 | single-source/flagged |
| F-045 | 菜头Prompt.AI 的「菜头应用首发素材包」根据产品链接、截图或说明，提炼人群、场景与卖点，为新品上线、公测招募准备介绍材料；主要产出为内部产品价值卡和简短证据表、首发图文、社群和朋友圈短介绍 | author_claim | S1 | 技能 2 | single-source |
| F-046 | 该例以模拟产品 FlowPilot AI 测试，得到 6 张已生成图文卡片，以及包含推荐标题、小红书正文、短介绍和演示脚本的首发文案包 | author_claim | S1 | 技能 2 示例 | single-source/flagged |
| F-047 | 该例提示需打开图片预览效果，再核对文案、补上真实产品截图和体验链接后继续发布准备 | author_claim | S1 | 技能 2 示例 | single-source |
| F-048 | 陈乔维Justin 的「首批用户获取」帮助已能演示或试用的产品明确首批用户画像与试用动机、选择触达渠道、准备沟通材料；主要产出为首批用户画像、沟通话术、反馈问题、七天冷启动计划 | author_claim | S1 | 技能 3 | single-source |
| F-049 | 该例建议把试用人群聚焦到有固定日报任务、手上已有 Excel 数据的电商运营负责人；试用任务明确为「上传自己的 Excel，成功导出或复制第一份日报」 | author_claim | S1 | 技能 3 示例 | single-source/flagged |
| F-050 | 该例的观察指标为：能否在 3 分钟内得到结果、第二天是否主动回来、是否愿意为稳定性和权限功能付费 | author_claim | S1 | 技能 3 示例 | single-source/flagged |
| F-051 | 花叔的「产品增长负责人」结合产品情况、现有数据和已做动作，分析当前增长瓶颈；主要产出为三件优先事项、暂缓事项、复检条件 | author_claim | S1 | 技能 4 | single-source |
| F-052 | 该例把问题定位到「注册之后」：模拟数据中 32,450 人注册、18,760 人完成首次应用创建、13,690 人未完成这一步；据此把「帮助用户做出第一个能用的应用」列为优先关注环节 | author_claim | S1 | 技能 4 示例 | single-source/flagged |
| F-053 | 该例对缺失数据明确标注「留存率填不出来，不估」，并提示补充数据后继续判断 | author_claim | S1 | 技能 4 示例 | single-source |
| F-054 | 蔡不菜（AI版）的「菜菜的冲浪Skill」以小红书为默认阵地，为产品寻找有原帖依据的传播机会，比较选题，再根据选择生成内容；主要产出为传播机会、选题比较、推广内容 | author_claim | S1 | 技能 5 | single-source |
| F-055 | 该例一篇稿件提供备选标题、封面文案、620 字正文和 6 页画面安排，并注明哪些页面可以设计、哪些需要实拍 | author_claim | S1 | 技能 5 示例 | single-source/flagged |
| F-056 | 该例另一篇稿件围绕后续修改需求展开、安排 5 页内容；并提供两篇稿件的对照说明、效果观察方法与收到不同反馈后的修改建议 | author_claim | S1 | 技能 5 示例 | single-source/flagged |
| F-057 | 该例的工作简报保存目标受众、希望读者采取的行动、发布账号身份和可用素材，以减少重复交代背景 | author_claim | S1 | 技能 5 示例 | single-source/flagged |
| F-058 | 海明Dev 的「海明 App 商业化」面向开发中或已上线的移动 App，结合项目材料和可核实竞品信息，检查引导、付费墙、会员权益及套餐设计；主要产出为商业化评估、付费转化优化建议 | author_claim | S1 | 技能 6 | single-source |
| F-059 | 该例把「注册后还没完成关键操作就离开」「缺少免费体验」「企业版功能与价格不匹配」列为优先问题 | author_claim | S1 | 技能 6 示例 | single-source/flagged |
| F-060 | 该例提出免费版与分档定价建议，规划个人、企业用户的上手路径与付费提示时机，并列出实施清单、测试场景和观察指标 | author_claim | S1 | 技能 6 示例 | single-source/flagged |
| F-061 | 文章给出开始方式：打开对应技能页 → 安装技能 → 提供材料、说明任务 | page_fact | S1 | 「选好了，怎么开始？」 | verified |
| F-062 | 文章建议从一份首发素材、一组试用用户或一次最小实验开始，先完成眼前这一步 | author_claim | S1 | 结尾段 | single-source |
| F-063 | 文章给出技能市场入口 `https://meoo.com/skills`，并称暂仅支持电脑访问、可复制链接至电脑浏览器打开 | page_fact | S1 | 结尾入口 | verified |
| F-064 | 文章末尾提到秒悟 Meoo 团队版，面向希望把 AI 融入团队日常工作、把团队经验沉淀为可复用、可共享 Skill 的读者 | page_fact | S1 | 结尾段 | verified |

### 2.4 配图补充事实（F-065–F-066）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-065 | 云栖大会现场图含文字「Meoo Skill 共创计划」「22 位博主共创的增长 Skill，今天交付」 | page_fact | S1 | 配图（现场） | verified（图内文字，未核年份） |
| F-066 | 首页横幅图含「产品增长加速器」「Hot」「24个技能」，以及「从真需求诊断、冷启动获客、热点自传播到内容产品化…」 | page_fact | S1 | 配图（横幅） | verified（图内文字） |

### 2.5 作者主张与演示边界（F-067–F-072）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-067 | 文章与清单图均以「22 位博主/共创博主」作为创作者口径 | author_claim | S1 | 第 1 段、清单图标题 | single-source |
| F-068 | 首页横幅图以「24 个技能」作为技能数量口径，与清单图 22 行不同；差异已由 F-096 与核验项 23 归因为聚合层级（多算空格的键盘 2 个平台变体） | author_claim | S1 | 配图（横幅） | modeled |
| F-069 | 六个重点技能的示例均基于模拟产品与模拟数据，不是真实产品运营数据 | author_claim | S1 | 各示例段与图内标注 | single-source |
| F-070 | 「暂不够判」「留存率填不出来，不估」等是 Skill 在演示输入下的输出，不构成对任何真实产品或需求的既成结论 | author_claim | S1 | 技能 1 / 技能 4 示例 | single-source/flagged |
| F-071 | 配图中标注「模拟产品素材示例 \| 图片内容发布前需核对」 | page_fact | S1 | 技能 2 配图底部 | verified |
| F-072 | 文章建议以最小起步方式开始：一份首发素材、一组试用用户或一次最小实验 | author_claim | S1 | 结尾段 | single-source |

### 2.6 跨页对账与平台机制（F-073–F-078）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-073 | 同库既有束登记的「应用赏金广场 · AI Builder Growth 共创计划」按七个增长阶段收录 25 条技能条目、22 位创作者 | page_fact | S2 | 既有束 `concepts/02-skills-catalog.md` | 库内交叉 |
| F-074 | 该 25 条条目的阶段分布为 4 / 3 / 5 / 2 / 3 / 3 / 5 | page_fact | S2 | 既有束阶段统计表 | 库内交叉 |
| F-075 | 该 25 条条目含两组系列族：空格的键盘 ×3、一起Vibe ×2；25 − 3 = 22，与本文 22 行去重口径吻合 | page_fact | S2 | 既有束系列族说明 | 库内交叉 |
| F-076 | 平台技能市场首屏可检索到与本文对应的技能条目及作者 handle，包括「菜头应用首发素材包 @菜头Prompt」「产品第一版 @懒人哥」「海明 App 商业化 @黄明远」「SignalMine｜用户反馈转增长实验 @Z_wk」「AI产品调研 @北峰Agent」「菜菜的冲浪Skill @caibucai」「产品增长负责人 @花叔」「应用首发包助手 @桃子_0616」「西瓜业务产品化 @西瓜🍉」「GitHub星标增长器 @常成」 | page_fact | S3 | 技能市场首屏条目 | verified（抓取时点） |
| F-077 | 官方文档说明技能市场支持 AI 语义搜索、全部技能/我创建的两视图、七类标签筛选、添加后「使用技能」、详情页按官方/他人与自有分权限、本地 zip 上传发布 | page_fact | S4 | 技能市场文档 | verified |
| F-078 | 平台与技能市场均以「秒悟 Meoo」自称，技能市场地址为 `https://meoo.com/skills` | page_fact | S3+S4 | 页面标题与文档 | verified |

### 2.7 命名统一与口径归一（F-079–F-096）

> 采集方式：在公开技能市场页 `https://meoo.com/skills` 加载全部技能卡片（2026-10-24 共 252 张），按「作者 handle + 技能名 + 主题」三项交叉匹配。**不包含登录后可见的收藏集合页**；`24` 的集合卡片本身未公开，归一模型见 [verification.md](verification.md) 第 23 项。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-079 | 市场公开页存在「需求先验｜模拟用户调研」@张振东 | page_fact | S3 | 技能卡片 | verified |
| F-080 | 市场公开页存在「AI产品调研」@北峰Agent | page_fact | S3 | 技能卡片 | verified |
| F-081 | 市场公开页存在「西瓜业务产品化｜xigua-service-productization」@西瓜🍉 | page_fact | S3 | 技能卡片 | verified |
| F-082 | 市场公开页存在「产品第一版」@懒人哥 | page_fact | S3 | 技能卡片 | verified |
| F-083 | 市场公开页存在「网页应用宣传物料」@空格的键盘 | page_fact | S3 | 技能卡片 | verified |
| F-084 | 市场公开页存在「手机 APP 宣传物料制作」@空格的键盘 | page_fact | S3 | 技能卡片 | verified |
| F-085 | 市场公开页存在「菜头应用首发素材包」@菜头Prompt | page_fact | S3 | 技能卡片 | verified |
| F-086 | 市场公开页存在「GitHub星标增长器」@常成 | page_fact | S3 | 技能卡片 | verified |
| F-087 | 市场公开页存在「菜菜的冲浪Skill」@caibucai | page_fact | S3 | 技能卡片 | verified |
| F-088 | 市场公开页存在「应用首发包助手」@桃子_0616 | page_fact | S3 | 技能卡片 | verified |
| F-089 | 市场公开页存在「首批用户获取」@anyu1888888 | page_fact | S3 | 技能卡片 | verified |
| F-090 | 市场公开页存在「AI变现诊断」@小E爱学习 | page_fact | S3 | 技能卡片 | verified |
| F-091 | 市场公开页存在「产品增长负责人」@花叔 | page_fact | S3 | 技能卡片 | verified |
| F-092 | 市场公开页存在「AI应用定价算盘」@古希腊掌管代码的神 | page_fact | S3 | 技能卡片 | verified |
| F-093 | 市场公开页存在「海明 App 商业化｜haiming-app-monetization」@黄明远 | page_fact | S3 | 技能卡片 | verified |
| F-094 | 市场公开页存在「SignalMine｜用户反馈转增长实验」@Z_wk | page_fact | S3 | 技能卡片 | verified |
| F-095 | 文章 22 行中有 7 行未在市场公开页按作者或同名主题检索到：yan（ai赚钱版）·真需求诊断、设计师雪梨·产品评审、南洋理工DAN讲AI·真需求验证、斑马MVP实验室·产品官网、李叔聊AI·白板动画、是树小姐·笔记封面、一起Vibe·推广视频 | page_fact | S3 | 252 张卡片全量匹配 | verified（抓取时点） |
| F-096 | 空格的键盘在市场公开页有 2 个物料技能（网页应用、手机 APP），广场束登记其 3 条系列条目（I/II/III）；两组数量差 1，说明广场按「条目」计、市场按「已公开技能」计 | page_fact | S2+S3 | 卡片列表 + 广场目录 | verified |

## 3. 缺口与放弃核验清单

| # | 缺口 | 处置 | 原因 |
|---|---|---|---|
| 1 | 「24 个技能」与清单 22 行、广场 25 条的差额来源 | **已归一为层级模型**：22 行 + 空格的键盘 2 个额外平台变体 = 24；24 + 一起Vibe 1 条重复投稿条目 = 25 | 24 的集合卡片为登录后页面，未直接观测；该模型与 F-075、F-096 的系列族算术完全自洽，标 `modeled` |
| 2 | 各 Skill 的实际输入契约、安装体积、运行耗时、失败率 | 不登记 | 文章只给演示级输入输出，未提供可复现规格 |
| 3 | 每个 Skill 的收费、额度、权限与数据留存政策 | 不登记 | 文章与首屏未披露；需逐技能详情页核验 |
| 4 | 「暂仅支持电脑访问」的技术原因与移动端可用性 | 保留为文章口径 | 未做移动端实测 |
| 5 | 云栖大会现场图的年份与活动场次 | 不推断 | 图内只有「APSARA 云栖大会」与口号，无年份 |
| 6 | 「22 位博主」的完整名单与账号归属 | **已建立两层命名**：文章层为共创博主显示名，平台层为技能作者 handle；15/22 已匹配，7 行仅文章口径 | 文章未给统一账号表；博主与作者可能不是同一人，映射表见 [01-skill-catalog.md](../concepts/01-skill-catalog.md) §4 |
| 7 | 示例数字的真实性 | 一律标注为模拟 | 文章与截图均明示「模拟产品测试」「模拟产品素材示例」 |
| 8 | 24 集合卡片的直接页面证据 | 未采集 | 需登录后可见，按公开性边界不绕过登录；仅以算术模型归一 |

## 4. 转写噪声登记

- 配图文字由视觉识读转录，个别字词（如「拍下运营早上的第一个小时」）保留截图原样，未按语义改写。
- 文章正文以 DOM 提取为主、浏览器元数据为辅；两者标题一致，未发现正文缺失段。
- 图片本身不入库；本束只保留对图内文字与结构的转述（遵循项目「图片不落库」约束）。
- 文章中的「秒悟 Meoo」与「Meoo」为同一平台的不同写法，引用时保留原文。
