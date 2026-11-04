# 更新记录

## 2026-11-04

- 创建 Super-agent 双层协作架构概念教程，依据指定导读与两篇公开报道原创组织；未保存全文镜像。
- 公开性预检通过：指定导读正文可公开阅读。上游出现验证码即停止；GitHub CLI 缺少凭证，未获得原始仓库证据。
- R：登记 30 项事实，区分 page_fact 与 author_claim；G1 仅确认归因清楚，不能证明每项来源声明为真。
- I：记录三个四元组机制假设；操作可复现性两问未通过，不建 examples。
- E：形成单案例待验证模式，不宣称多案例实证或方法论成熟入库。
- V：完成四个独立视角的审查并按下表修补；未直接核验的 P0 数字保留 flagged。机械门禁结果另列，不以审查完成代替实测。
- C：用户未要求提交，不执行 Git 提交或推送。
- 轻量子项目采用 bundle 内 facts.md 单一事实登记，不另建主仓公共 spec 或重复 article-source.md；verification.md 对全部编号逐项覆盖。避免双份事实漂移，但本项不同于博文技能主仓 spec 双份模板。

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261104-super-agent | msg=公开导读知识沉淀 | ctx={"scenario":"knowledge","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261104-super-agent | msg=R-I-E-V；C等待用户明确授权
[CMD-LOG] | level=WARN | cmd=seven-concepts | step=R1 | event=GATE_FAILED | session=sc-20261104-super-agent | msg=原始研究及实验未读；核心证据门未通过；保持flagged
```

## 后续复核

内容维护者在 2026-12-04 前正常获取上游材料后，核读实验、仓库归属、固定版本和许可；未获取则保持 flagged。运行原型需要另行授权，不为满足交付范围擅自安装或接入凭证。

## 四视角审查与修补

以下为本次独立审查结果的归纳，审查范围是教程与台账的一致性，不包含未取得的原始研究或源码。四视角均未报告 P0/P1；这不代表上游事实已获官方核验。

| 视角 | 发现 | 级别 | 采纳修补与复查位置 |
|---|---|---|---|
| 证据反方 | Router 共享背景、状态分离、Watchdog 描述与所引事实项归因不完整 | P2 | facts.md 的 F-008、F-012、F-013 补入已读二手报道及定位；未新增编号或升为原始证据 |
| 证据反方 | log 的审查完成声明没有具体留痕 | P2 | 本表记录发现与采纳项，机械结果单列 |
| 新人 | CI、线程、状态、执行环境、外部副作用、token 等缺少入门解释 | P2 | 02-events-and-recovery.md 与 03-evaluation-and-safety.md 补术语 |
| 新人 | 练习缺支架、案例未贯穿、父导航缺入口 | P2 | 00-attention-and-scope.md 补四列练习，02 补错别字修复消息链；DeepSeek 父索引增加概念解读导航 |
| 新人 | 两问及四元组术语对初学者不透明 | P3 | knowledge-map.md 补解释，明确教学假设与实证的差别 |
| 业务安全 | 授权有效范围、撤销、凭证保护及常驻总成本不充分 | P2 | 02 补主体/任务/资源/有效期与恢复重验；03 补最小权限、撤销轮换、周期成本与停止责任人 |
| 业务安全、未来 | 扩展阅读链接多上跳一级 | P2 | 根 index.md 改为 ../../../practice/ai-engineering-methodology/index.md，交由链接门复验 |
| 未来 | 原型单仓范围、旧报道状态的时效和模式升级判据不明确 | P2 | 00 补媒体限定范围；verification.md 补版本/日期复核；knowledge-map.md 补同基线、净收益及否定条件 |

## 机械验证

| 检查 | 实测结果 | 范围与限制 |
|---|---|---|
| 本包导航 | PASS | 复用 scripts/check-toctrees.py 的 run_scan 对本包执行断链、全部文档可达、目录清单及根 index 检查 |
| 本包链接 | PASS | check-links.py --paths 显式枚举 12 个 Markdown 文件，--check-frontmatter-paths；36 个本地引用存在，未重复检查外部页面 |
| 元数据与来源 | PASS | 12 个文件 UTF-8 无 BOM；9 个 frontmatter 可解析且 type 非空；21 个 sources 条目有 resource，内部路径均存在 |
| F 编号守恒 | PASS | facts.md 表行严格为 F-001 至 F-030；verification.md 编号区间展开后逐项等于该集合，无重复或遗漏 |
| invoke gates.utf8 | PASS | 当次扫描 12803 个文档；这是共享工作区时点数，不是本包文件数或 HEAD 资产基线 |
| invoke gates.bundles | PASS（复验时点） | 首次被并发 pagekin 的一束差额拦截；他方完成计数接线后复验为 707 束、64 组、9 域，五面一致；未回滚共享索引前移 |
| invoke gates.toctrees | FAIL（全库） | 首次 16 项均属 pagekin；复验时该束已接入，改为 doubao-work-remotion-photo-video 在途目录的 10 项未收录/缺 index 问题；本包独立检查通过 |
| invoke gates.assetbaseline | FAIL（全库） | 工作区已跟踪内容相对 HEAD 的归一字节残差 +272118；doc/index.md 与 README.md 仍声明 702 束。未提交、stash 或修改他方资产来消除全库债务 |
| git diff --check | PASS | 仅显示 CRLF 将归一为 LF 的提示，无空白错误；不表示变更已经提交 |
| 本包 HTML 渲染 | PASS | sphinx-build -b html -c doc -D master_doc=index 以本包为源；12 篇均生成非空 HTML，退出 0；仅有 jieba 的 pkg_resources 弃用提醒 |
| 全库 HTML 构建 | 未完成 | invoke build --target 指向系统临时目录；解析上万文档期间主动结束，改为本包限定渲染；未宣称全站构建通过 |

首次以目录参数执行主仓链接脚本时，因默认排除 projects 而扫描到 0 个文件；该“通过”无效，已改为显式文件列表复跑。额外的只读计数归因探针在共享索引并发前移后断言失败，随后改用原 gates.bundles 实测复验；未将探针断言失败记为内容缺陷。

```text
[CMD-LOG] | level=INFO | cmd=link-check | step=S0 | event=CMD_START | session=lnk-20261104-super-agent | msg=本包显式十二文件链接检查 | ctx={"check_external":false}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261104-super-agent | msg=四视角审查修补完成；本包导航与事实覆盖通过
[CMD-LOG] | level=WARN | cmd=seven-concepts | step=V2 | event=GATE_FAILED | session=sc-20261104-super-agent | msg=全库导航与资产基线仍受并发在途资产及既有声明漂移影响；不声称全库门禁通过
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V3 | event=CONCEPT_COMPLETED | session=sc-20261104-super-agent | msg=本包十二文档渲染完成；交付概念教程，保留上游flagged与单案例模式限定；C未授权
```
