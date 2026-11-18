# 更新日志

## 2026-11-09（V 阶段独立复核）

- **审查维度**：A 断言真实性（对 concepts/examples 中具名类、函数、常量、配置键、路径与默认值在 vendor 固定 commit 上逐项 Grep）、B F 编号范围与语义一致性、C 事实条数实测、D 结构合规（frontmatter / type / okf_version / stale_after 等）、E Markdown 链接与 toctree 可达性、F 示例免责声明。
- **条数核验**：`references/facts.md` 实测 172 条（F-001–F-172，无跳号、无重复），与 index、references/index、log 所述一致。
- **发现与修复 14 处**：虚构实体 3 处——`Client::execute()` 实为 `Client::run(argv)`；`EndpointCatalog` 被误述为「网关与扫码两套地址」，实为内建端点的覆盖目录（未覆盖回落到 `CatalogKey::builtin_default`）；「缓存只存在于进程内、无磁盘持久化 / 跨进程不共享」与 `registry/cache.rs` 事实相反，已改为内存 + 磁盘两层、可跨进程复用。F 编号错配 8 处——02 文档 F-065→F-073、F-051→F-056，§四 表格三行（F-069 / F-070、F-071 / F-073）按实际语义重排，束根 index 删除误引的 F-072，examples/03 的 F-090→F-051，sources 的越界引用 F-235 改为无编号表述。链接 3 处——`03-auth-and-session.md` 指向不存在的文件，改为 `03-auth-session.md`。
- **结构/免责声明**：14 篇非保留文档 frontmatter 齐全，`okf_version` 仅见于束根 index；3 篇示例均含「未在本机实跑」，0 缺陷。
- **结论**：通过 V 复核；14 篇文档 `status` 由 draft 转 stable 并补写 `verified`。

## 2026-11-09（G5 模式沉淀）

- **模式**：企业微信三层接入读法——同一厂商的多仓生态按「执行层（本束 CLI）/ 路由层（wecom-unified）/ 协议层（wecom-aibot-python-sdk）」分束，束间只做相对链接，不复制内容。
- **触发场景**：面对同厂商 CLI + Skill + SDK 多仓组合，需要判断先读哪一束、事实如何互证。
- **步骤**：①`git ls-tree -r HEAD --name-only` 固化每仓受控文件数并按仓分束；②每束独立编号事实（F-001 起），再据事实写洞察；③每束固定 `references/{facts,insights,sources}.md` 三件套；④束根 index 只写定位、导航与边界，不写实现细节；⑤跨束用 `../<束>/index.md` 相对链接。
- **反模式**：①以文档自述取代目录实测（本仓 `docs/skills.md` 称 14 个 Skill，目录实为 15 个）；②把多版本号强行归一（须双写并置）；③概念文档写未在源码中出现的类名（V 阶段修掉 3 处虚构实体）；④把子模块空工作树误判为「仓库无内容」。
- **迁移**：同法适用于腾讯生态内其他多仓组合（如会议 CLI 与套件 Skill 的配对阅读）。

## 2026-11-09

- **R（事实）**：沿用固定基线的 172 条事实登记（F-001–F-172），覆盖 8 个主题节。
- **I（洞察）**：保留 6 条机制洞察，均以 F 编号作证据。
- **E（表达）**：补齐 8 篇概念、3 篇示例，以及 concepts、examples、references 三个索引、bundle 根索引、信源登记与更新日志。
- **约束**：本次仅处理 `wecom-cli` bundle；未修改 `tencent` 或全局索引。示例均未在本机实跑。
- **状态**：已通过 2026-11-09 的 V 阶段独立复核，`status` 已由 draft 转 stable 并补写 `verified`。
