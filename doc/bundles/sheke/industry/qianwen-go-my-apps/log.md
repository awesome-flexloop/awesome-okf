# 变更日志

## 2026-10-23

- 内容敏感度预检：用户提供的 `mp.weixin.qq.com` 文章，无登录、验证码、邀请码或付费墙，判为**公开内容（Public）**，入 `doc/bundles/sheke/industry/`。
- 采集：`defuddle parse --md` 提取正文；从页面 HTML 读取 `msg_title`、`nickname`、`createTime`、`ct` 元数据；外部核验经 WebSearch/WebFetch 取得新京报、DOIT、新浪财经、中国经济网、中国金融信息网，以及阿里云产品动态、秒悟计费文档与官网。
- 按 `wechat-public-okf` 契约执行 R → I → E → V：
  - R：建立[采集台账](references/source-manifest.md)，登记 S1~S9 与未采集项；[事实清单](references/article-source.md) F-001~F-051，连续无跳号。
  - P0：完成 C1~C18 核验、E1~E4 口径差异、G1~G10 缺口，判定 `status: flagged`。
  - I：建立[知识地图](references/knowledge-map.md)，事实/机制/迁移三层分离；机制层四条洞察均含四元组并标「假设」。
  - E：生成 `index.md`、6 篇 concepts、4 篇 references、`log.md`；更新父级导航与计数面。
- 操作可复现性两问均不满足（无步骤/提示词/入口/价格；需邀测资格），**不创建 `examples/`**。
- 未实测：未取得邀测资格，未验证生成、数据持久化、分享或云端 Pro。

### 门禁结果

- `check-utf8.py`：**通过**，14 个文件均为有效 UTF-8。
- `check-toctrees.py`：全库报 42 处预存问题，与 `qianwen-go-my-apps` 相关 0 处（`grep` 计数 0）；本包可导航、无断链。
- `check-bundles-index.py`：报 3 处 +2 漂移（总索引 673 vs 树 675、sheke 77 vs 79、industry 表合计 77 vs 79），全部由其他会话未跟踪 bundle 引起，与本包无关。
- F 编号连续性：**通过**，F-001~F-051 共 51 条，无缺号、无跳号、无重复，表格行数与 ID 集合一致。
- 包内相对链接与 frontmatter：**通过**，异常 0 处。

### 已知环境基线

- 工作树中存在**其他会话**新增的未跟踪 bundle `sheke/industry/toutiao-monetization` 与 `sheke/industry/zhihu-salt-author-platform`，以及 `jishu/ai/frameworks/ai-agent/zhihu-open-platform` 缺 index.md 的预存问题。
- 本 bundle 的计数更新按**干净检出真值**计算（673 束 / 77 束 sheke / 31 束 industry）；全量 gate 可能因上述未跟踪 bundle 报 +2 漂移与不可达，属预存基线，不计入本包缺陷。
- 未执行 Git 提交，等待用户明确提交请求。
