---
type: reference
title: 权威核验报告
description: 秒悟 CLI 部署与开放平台集成指南束的 P0 核验结论——CLI 安装命令链、Node 版本三口径、全栈云端构建矩阵、token 签发报文、MEOO_TOKEN 注入、CI 直发、套餐时效、开放平台权益红线、阿里云权限与运维命令、转写噪声处置、CLI 两页非重复，逐项给出结论、证据与核验方式
tags: [meoo, miaowu, cli, open-api, byoc, 核验报告, 信源核验]
generated:
  by: reference_agent/deepseek-v4.1-flash
  at: "2026-10-18T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-18T00:00:00+08:00"
status: stable
stale_after: "2027-01-18"
sources:
  - id: S1
    resource: https://docs.meoo.com/features/cli
    title: Meoo CLI 使用指南（功能特性 › 应用构建能力）
  - id: S2
    resource: https://docs.meoo.com/open
    title: Meoo 开放平台（Meoo开放能力）
  - id: S3
    resource: https://docs.meoo.com/open/guides/cli
    title: CLI 开放集成接入（Meoo开放能力 › 接入流程）
  - id: S4
    resource: https://docs.meoo.com/features/cli-aliyun
    title: MEOO CLI 进阶：部署到你自己的阿里云账号（功能特性 › 应用构建能力）
---

# 权威核验报告

**核验日期**：2026-10-18

**核验范围**：本束 12 项 P0 关键声明（命令/端点/版本/限额/权益边界类，逐字回验）+ 时效与冲突事项判定。核验方法为「暂存原文逐字比对」：每条 P0 与 2026-10-18 WebFetch 抓取的源页转存稿逐字符对照；本束不做运行验证（未实际安装 CLI、未签发 token、未部署云资源），所有「可复现」均为**文档级复现**。

**总结论**：12 项中，9 项 **✅ 通过（逐字一致）**；1 项 **⚠️ 语境差异并列**（Node 三口径，非矛盾、不调和）；1 项 **⚠️ dated**（套餐与权益有时效条件，源页已自我标注）；1 项 **✅ 噪声处置完成**（转写残片隔离台账；首轮自检曾漏扫概念页 1 处残片串，经独立评审指出并整改后复扫 0 命中，详见核验项十三与文末整改复审记录）。事实编号与信源台账见 [source-ledger.md](source-ledger.md)。

## 核验项一：CLI 安装与版本命令链 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-007、F-008、F-009、F-050） | 自动安装话术 `读取 meoo.com/skill-setup.md 并按照说明安装秒悟技能`；手动安装 `npm install -g @aliyun-meoo/cli`；验证 `meoo --version`；集成版安装 `npm install -g "/path/to/meoo-cli.tgz"` |
| 证据来源 | S1 第 1 节、S3 第 4 节 |
| 核验方式 | 与暂存稿逐字比对四处命令文本（含包名 `@aliyun-meoo/cli` 的 scope 拼写、`-g` 参数、tgz 引号路径），完全一致 |
| 说明 | 公网 npm 包名（S1）与 tgz 离线包（S3）是**两种不同分发形态**，对应个人用户与团队接入两种场景，非冲突 |

## 核验项二：Node.js 版本三口径 ⚠️ 语境差异（并列引用，不调和）

| 项目 | 内容 |
|------|------|
| 结论 | ⚠️ 语境差异——三处数字均逐字成立，适用环境不同，**不判对错、不互相"纠正"** |
| 三处口径 | ① F-005（S1）：CLI 安装前置「已安装 Node.js 20 或更新版本」——用户本机运行 CLI 的要求；② F-046（S3）：开放集成「运行环境：Node.js 18 或以上」——接入方 Agent/CI 环境运行「支持 MEOO_TOKEN 的 CLI 接入版本」的要求；③ F-024（S1 FAQ Q9）：全栈应用云端构建镜像「Node.js：24.15.0」（配套 npm 11.13.0/pnpm 10.33.3/Yarn 1.22.22）——Meoo 云端构建/运行容器内的固定版本 |
| 证据来源 | S1 第 1 节、S1 Q9、S3 第 2 节 |
| 核验方式 | 三处分别逐字回验通过；语境标签（本机 / 集成运行环境 / 云端构建镜像）为源页自身表述 |
| 教程处置 | 概念页中三者必须连同语境一起出现，禁止摘出单句写成「Meoo 要求 Node xx」；读者照做时按所处环境取对应口径 |

## 核验项三：全栈云端构建环境矩阵与运行约束 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-024、F-025、F-026） | OS Linux、目录 `/code`；OpenJDK 21；Node.js 24.15.0；npm 11.13.0；pnpm 10.33.3；Yarn 1.22.22；Python 3.13；Go 1.26.0；工具 `git`/`curl`/`wget`/`unzip`/`rsync`/`build-essential`/`pkg-config`；监听 `0.0.0.0:${PORT:-9000}`；`scripts/setup.sh` 远端构建执行、`scripts/start.sh` 容器启动执行；本地文件存储不持久；无需自写 Dockerfile |
| 证据来源 | S1 FAQ Q9、Q10 |
| 核验方式 | 版本号矩阵 9 项逐一与暂存稿比对一致；监听串含 `${PORT:-9000}` 的 shell 默认值语法逐字保留（反引号代码格式，不转义） |

## 核验项四：部署命令与静态/全栈选型 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-015、F-021、F-022、F-023） | 静态 `meoo deploy` 发布到 CDN；全栈首次 `meoo deploy --runtime image`、后续 `meoo deploy`；静态页不开通云服务、不消耗云服务额度 |
| 证据来源 | S1 第 4 节、FAQ Q6/Q8 |
| 核验方式 | `--runtime image` 参数逐字比对；选型表五行框架逐行有源 |

## 核验项五：成员 token 签发接口与请求报文 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-048、F-049） | `POST /open/v1/team/members/{member_id}/tokens`，`Content-Type: application/json`，请求体 `{"scopes": ["cli.compat"], "expires_in": 900}`；HMAC 签名；响应取 `access_token`、`expires_in`；权限点 `team.member.token.issue`/`team.member.read`/委托 `cli.compat`（F-045） |
| 证据来源 | S3 第 3 节、第 2 节 |
| 核验方式 | 路径模板（含 `{member_id}` 花括号）、JSON 体（scope 字符串 `cli.compat`、有效期 900 秒数字）逐字比对；权限点三串逐字比对 |
| 边界 | HMAC 签名算法细节不在本束源页（见 [source-ledger.md](source-ledger.md) 放弃核验清单），教程不补造签名头 |

## 核验项六：MEOO_TOKEN / MEOO_API_URL 注入与命令序列 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-053、F-054、F-055、F-058） | `export MEOO_TOKEN="<access_token>"`、`export MEOO_API_URL="https://meoo.com"`；`meoo --json whoami`、`meoo --json projects list`；`meoo projects use "<项目 urlId>"`、`meoo cloud status`、`meoo sandbox push`、`meoo deploy`；多用户按任务分别传 token |
| 证据来源 | S3 第 5 节 |
| 核验方式 | 两个环境变量名（含 `MEOO_` 前缀）、六条命令逐字比对；`<项目 urlId>` 占位尖括号为源页原文 |

## 核验项七：CI 直发命令 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-056） | `meoo --json deploy --project "<项目 urlId>" --skip-build --skip-push --force`；语义为使用已有构建产物直接发布；`--force` 用于自动化任务中的确认步骤 |
| 证据来源 | S3 第 5 节 |
| 核验方式 | 四个 flag（`--project`/`--skip-build`/`--skip-push`/`--force`）逐字比对；源页明示的前置条件（先完成构建并核对项目）一并保留，避免命令被断章使用 |

## 核验项八：套餐数量与开放平台权益红线 ⚠️ dated（源页自带时效条件）

| 项目 | 内容 |
|------|------|
| 结论 | ⚠️ dated——数字与红线逐字一致，但源页明确附带时效/条件限定，教程须原样保留限定语 |
| dated 事实 1（F-027） | 「目前**限时免费体验**，Free 用户可以部署 1 个全栈项目，Pro 用户 4 个，MAX 用户 8 个」——1/4/8 三个数字逐字回验通过；「限时」意味着随时可能调整 |
| dated 事实 2（F-036） | 集成权益「限制较小，仅建议用于开发和预发联调」；生产上线需等「集成版」权益套餐上线 |
| dated 事实 3（F-037、F-039） | 团队 AK/SK「暂未开放用户侧自助创建入口」，现阶段联系秒悟人工创建，Secret 仅交付一次；不提供公开创建接口 |
| dated 事实 4（F-040） | OAuth 应用「不能自行注册」，需联系 Meoo 配置并获取 `client_id` 与 Client Secret |
| dated 事实 5（F-073） | 数据库自动开通「目前」只支持 RDS MySQL，PostgreSQL/Redis/MongoDB 需自行配置 |
| 核验方式 | 数字与限定语成对回验；本束 `stale_after` 设为 2027-01-18（90 天），到期后这些条目优先复核 |

## 核验项九：凭证安全边界 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-038、F-072、F-041） | 长期凭证只能存接入方可信服务端，禁止写入浏览器、移动端、代码仓库、构建产物；阿里云数据库密码不走命令行参数（防 shell 历史/进程列表泄露），用交互式输入、环境变量或自动生成强密码存权限收紧文件；测试与生产账号/凭证/项目不得混用 |
| 证据来源 | S2「接入前须知」、S4 FAQ |
| 核验方式 | 三处安全条款逐字比对；概念页 06 将其组织为「凭证四不」检查清单，限定语不删减 |

## 核验项十：阿里云 BYOC 权限点、外部链接与运维命令 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-063、F-065、F-066、F-068、F-070） | 阿里云官方链接四条：`https://help.aliyun.com/zh/cli/install-cli`、`https://ram.console.aliyun.com/profile/access-keys`、`https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair`、`https://ram.console.aliyun.com/`；必需权限 ECS/ROS/OSS/STS，可选 RDS/SLB；命令族 `meoo aliyun update`、`meoo aliyun status --refresh`、`meoo aliyun delete`（手动输入 `DELETE` 确认）、`meoo aliyun rollback`；询价只临时用 OSS、不创建正式资源 |
| 证据来源 | S4 第 2/3/4/5 节与「上线后的常用操作」表 |
| 核验方式 | 4 条 https 链接逐字比对（域名均为 `help.aliyun.com`/`ram.console.aliyun.com`）；6 个权限名、5 条 `meoo aliyun` 子命令（含 `--refresh`）逐字比对；`DELETE` 大写确认串与源页一致 |

## 核验项十一：删除级联范围与残留核对责任 ✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过 |
| 声明（F-059、F-070、F-074） | `meoo aliyun delete` 删除 ROS 栈并**级联释放** ECS、EIP、RDS、SLB 等资源；删除后用户仍应去阿里云控制台亲自核对 ECS、EIP、SLB、RDS、OSS 是否有残留计费资源；健康检查失败不等于部署失败，先等几分钟或 `status --refresh`，不要立刻删资源 |
| 证据来源 | S4 运维表、FAQ |
| 核验方式 | 级联资源五类名称逐字比对；「控制台亲自核对」这一责任保留句不省略，防止读者把 CLI 删除当作账单侧终极保证 |

## 核验项十二：CLI 两页非重复（S1 vs S3）✅ 通过

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过——四/六重证据确认两页非重复、无重定向，作为独立两源登记合理 |
| 证据 | ①两 URL 均 HTTP 200 且最终 URL 等于请求 URL，无 3xx；②HTML title 不同（「Meoo CLI 使用指南 - Meoo」vs「CLI 开放集成接入 - Meoo」）；③面包屑不同（功能特性 › 应用构建能力 vs Meoo开放能力 › 接入流程）；④正文不同（S1：npm 公网包+浏览器授权+`meoo login`+11 条 FAQ，面向个人；S3：团队 AK/SK→HMAC→MEOO_TOKEN+CI 发布 6 节，面向接入方）；⑤分页相邻页不同（web-apps/cli-aliyun vs deploy-only/import-and-publish）；⑥两页 head 均无 `<link rel="canonical">` |
| 核验方式 | 抓取时由采集代理记录于两暂存稿「采集备注」，本报告复核引用 |
| 处置 | S1 事实用于概念页 01–05，S3 事实用于概念页 00/06 与 examples/03；两页交叉处（Node 口径、安装方式）在概念页中显式互指 |

## 核验项十三：转写噪声隔离 ✅ 通过（首轮漏扫，整改后复扫 0 命中）

| 项目 | 内容 |
|------|------|
| 结论 | ✅ 通过（整改后） |
| 声明 | 5 类转换残片（图片残留 `_4d3c6c660f48`、punycode 乱码域名、`http://team.member.read/`、`http://skill.md/`、「AccessKey Secr」截断、视频时间轴）已在 [source-ledger.md](source-ledger.md)「转写噪声登记」逐项留痕 |
| 核验方式 | 两轮机械扫描（ripgrep 正则 `aka\.doubaocdn\.com|2:01|On this page|（原文配图|\.temp/|file:///|_4d3c6c660f48|xn--|http://skill\.md/|http://team\.member\.read/|使用技[^能]`，扫描范围 `concepts/` 与 `examples/` 全部成稿）：成稿后首轮自检误判为 0 命中（漏扫）；2026-10-18 fresh-context 独立评审在 `concepts/05-aliyun-byoc-deploy.md:138` 发现 1 处 `_4d3c6c660f48` 命中（评审 I-01），当日整改删除字面残片串、改为不含残片的表述；整改后按同一正则复扫 `concepts/`+`examples/` → **0 命中**（ripgrep 无匹配退出）。「AccessKey Secret」在正文中以完整正确拼写出现，其截断事实仅保留在台账；台账与 log 中的命中为噪声登记面，不在正文门禁范围 |

## 独立评审整改复审记录（2026-10-18）

fresh-context 独立评审（报告在 spec 目录 `review.md`）首轮结论 **fail**：7 个 issue（5×P1 + 2×P2，无 P0），其中归属本束的 I-01、I-02（部分）、I-04 已全部整改并复审：

| Issue | 问题 | 整改 | 复审证据 |
|---|---|---|---|
| I-01 | `concepts/05-aliyun-byoc-deploy.md:138` 正文出现采集残片串 `_4d3c6c660f48`，违反正文噪声门禁 | 删除字面哈希，改为「仅余无意义文件名片段，已隔离登记于台账转写噪声登记」 | 同一污染正则复扫 `concepts/`+`examples/` → 0 命中（见核验项十三） |
| I-02 | 束根 `index.md:91` 姊妹束互链误用 `../../` 前缀（死链） | 改为 `../miaowu-product-guide/index.md` | PowerShell `Test-Path` 解析为 True |
| I-04 | 本报告核验项十三的「0 命中」自检结论与产物矛盾（首轮漏扫） | 核验项十三改为两轮扫描的据实记录（漏扫→命中→整改→复扫 0 命中），总结论同步订正 | 本表与核验项十三一致；扫描命令与正则可复现 |

复审命令记录（cwd 为子模块根，2026-10-18 整改后实跑）：

- `python scripts/check-bundles-index.py` → exit 0（9 域/62 组/647 束五面一致）
- `python scripts/check-toctrees.py` → exit 0；`python scripts/check-utf8.py` → exit 0（11797 文件）
- PyYAML 批量解析两束 34 个 frontmatter → `parsed: 34 bad: 0`
- 污染正则扫描 `concepts/`+`examples/` → 0 命中
- `sphinx-build -b html -E -W --keep-going doc _build/html`（-E 强制全量重读）→ 本束全部文件 0 告警（全量告警均归属存量束）

## 已知局限

- **文档级复现，无运行验证**：本束未实际安装 CLI、未登录、未签发 token、未部署任何 Meoo/阿里云资源；命令可用性以 2026-10-18 源页文字层为准。
- **全部为厂商单源**：74 条事实均来自 `docs.meoo.com` 官方页面自身，无独立第三方信源交叉；官方文档是其产品事实的权威来源，但套餐/权益/版本类条目易随发布变化。
- **截图信息不可得**：S1/S4 关键操作配有大量截图（授权页、配置示例、成功示例），WebFetch 转换仅得文字层与不可恢复的图片残片；按钮路径类细节本束不脑补。
- **开放平台深页未覆盖**：`/open/team-integration`（签名细节）、`/open/api`、`/open/authentication`、三条流程指南、`/open/protocol`、`/open/security` 均在用户清单之外，仅作延伸阅读登记。
- **时效**：`stale_after` 设为 2027-01-18。到期优先复核 F-027（1/4/8 与限时免费）、F-036/F-037/F-040（集成版权益与凭证获取路径）、F-073（数据库支持范围）、F-024（云端构建版本矩阵）。
