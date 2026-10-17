# 更新日志

## 2026-10-18

**New Bundle**: 新增知识束 `miaowu-cli-open-guide`（秒悟 CLI 部署与开放平台集成指南）

* **R 阶段（事实采集）**：WebFetch 匿名采集 4 个官方页面（均 HTTP 200、无重定向）——`/features/cli`、`/features/cli-aliyun`、`/open`、`/open/guides/cli`，转存于会话暂存区并逐页通读；以四重证据（HTTP/title/面包屑/正文分页）确认 `/features/cli` 与 `/open/guides/cli` 为**两个非重复页**，据此采用四源分立而非去重合并。G1 事实门：命令、环境变量、端点、版本矩阵、套餐数字一律逐字摘录，营销性表述不混入事实表。
* **I 阶段（洞察）**：冻结 4 条跨页四元组洞察——①「凭证签发权/业务操作权双层分离」（AK/SK 只签发、短期 token 才操作，F-033/F-048/F-058）；②「Node 三口径按环境分层而非矛盾」（本机 20+/集成 18+/云端镜像 24.15.0，语境标注不调和）；③「命令成功 ≠ 资源就绪」（云服务开通 2-3 分钟延迟，F-020）；④ BYOC 的「部署工具与资源归属解耦」（ROS 编排归 Meoo、资源账单归客户，F-059/F-060）。
* **E 阶段（萃取）**：落盘 7 篇概念页（00 开放平台总览、01 CLI 定位、02 安装登录、03 静态/全栈部署、04 本地工作流、05 阿里云 BYOC、06 团队集成）、3 条命令流示例（静态/全栈、BYOC、团队 token/CI，顶部均声明文档级复现未运行验证）、references 三件套（F-001–F-074 共 74 条事实 + 13 项 P0 核验）。
* **V 阶段（对抗核验）**：P0 逐字回验 9 项通过；Node 三口径判为语境差异并列；套餐 1/4/8 与集成权益/AK SK/OAuth/数据库支持 5 条标 dated；转写残片（`_4d3c6c660f48`、punycode 乱码域名、`http://team.member.read/`、`http://skill.md/`、「Secr」截断、视频时间轴）全部隔离在台账「转写噪声登记」，禁入正文；独立 fresh-context 评审结果见 spec 目录 review.md。
* **V 阶段整改闭环（独立评审后）**：fresh-context 独立评审首轮结论 fail（7 issue，无 P0），归属本束 3 项当日全部整改——① I-01：concepts/05:138 正文残留采集哈希串 `_4d3c6c660f48` 已删除并改为无残片表述，同一污染正则复扫 concepts/+examples/ 0 命中；② I-04：verification.md 核验项十三首轮「0 命中」自检失实，已改写为两轮扫描据实记录（漏扫→命中→整改→复扫 0 命中）；③ I-02：束根 index 姊妹束死链前缀 `../../`→`../`（Test-Path 通过）。整改明细与复审命令记录见本束 verification.md「独立评审整改复审记录」；`sphinx-build -E -W` 全量构建本束 0 告警。
* **C 阶段**：四层索引注册与计数对账见组/分类/域/总索引（miaowu 3→5、ecosystems 95→97、jishu/ai 247→249、total 645→647，`check-bundles-index.py` 五面对账 exit 0）。
* **缺口声明**：HMAC 签名算法细节、token 响应完整字段、错误码/协议、三流程指南、OAuth 端点、ROS 模板内容与单价均在本束 4 源之外，登记于 source-ledger「放弃核验清单」，未做推断补全。
* **方法局限**：WebFetch HTML→Markdown 转换丢失截图与视频内容；全部为厂商单源，无第三方交叉。
