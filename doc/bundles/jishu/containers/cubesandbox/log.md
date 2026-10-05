# CubeSandbox Bundle 生成日志

> 记录本 bundle 的完整生成过程，供审计与回溯使用。

---

## 任务元信息

| 项目 | 内容 |
|------|------|
| 任务 | 全面学习 CubeSandbox 源码并生成 OKF v0.2 Wiki 教程 |
| 方法链 | seven-concepts-cmd 场景 4（知识沉淀）：Stage0 信源稳定性门 → R → I → E → V → C |
| 质量门 | G1（事实无因果词）→ G2（洞察四元组）→ G3（信源先行/分批生成）→ G4（独立验证）→ G5（沉淀） |
| 源码位置 | `d:\spaces\SpecWeave\external\dao\runtime\tencent\CubeSandbox`（本地克隆） |
| 官方仓库 | https://github.com/TencentCloud/CubeSandbox |
| 信源 pin | tag **v0.7.2**，commit `f1aaa737fb3862202b1731e0e0d844c28779f930`（2026-09-24） |
| 工作树 | v0.7.2 + 11 commits（HEAD `e02976ae`）；post-release 文件以 `git show v0.7.2:<path>` blob 为准 |
| 内容级别 | 公开（Public） |
| 归属路径 | `jishu/containers/cubesandbox/` |
| 生成时间 | 2026-10-04 |

---

## Stage 0：信源稳定性预检

- 确认 remote `git@github.com:TencentCloud/CubeSandbox.git`，固定 release tag **v0.7.2**（2026-09-24，commit `f1aaa737`）。
- 规则：tag 后新增/修改文件（CubeAPI handlers/services、sdk/go/envd.go、openapi.yml、CubeS3lvol C 源、deploy/one-click 等；online-install.sh 工作树已删除）一律以 v0.7.2 blob 为准；hypervisor/block_util 新增内容排除。
- 登记信源 S1~S5 与 5 条信源瑕疵（见 [references/01-source-map.md](references/01-source-map.md)）。

---

## R 阶段（事实采集）

- **数量**：244 条（F-001 ~ F-244），分 14 主题面。
- **产出**：`.trae/specs/cubesandbox/facts.md`（含信源表 S1~S5 与主题面映射）。
- **主题面**：总览/架构/部署（F-001~036）、CubeAPI（F-037~059）、CubeMaster（F-060~068）、Cubelet（F-069~093）、cube-hypervisor（F-094~140）、cube-agent（F-141~157）、CubeShim（F-158~165）、CubeNet（F-166~184）、网关（F-185~196）、存储（F-197~214）、CubeOps/CLM/TemplateCenter（F-215~225）、SDK（F-226~233）、生命周期（F-234~238）、模板/日志/版本（F-239~244）。
- **G1 预检**：事实句无因果推断词；计数与常量逐条登记。
- **返工记录**：初版主题映射编号错位（CubeAPI 误标 F-027 起，实为 F-037 起）且残留占位段，已修复——编号一次排定，写完按映射表逐组核对。

---

## I 阶段（架构洞察）

- **产出**：`.trae/specs/cubesandbox/insights.md`，含 5 个洞察四元组与知识地图。

| # | 现象 | 根因 | 影响 | 建议 |
|---|---|---|---|---|
| I-1 | 冷启动 <60ms | pauseVM 池化 + 内存快照克隆恢复 | 单并发 60ms；50 并发均值 67/P95 90/P99 137ms | 关注池容量与快照模板匹配 |
| I-2 | MicroVM 可被 containerd 直接编排 | CubeShim 实现 Shim v2（`io.containerd.cube.v2`），依赖 containerd-shim 0.9.0 | 标准容器任务语义接入既有生态 | 排障先查 shim 版本与注解 |
| I-3 | 出向安全强制且可审计 | 独立 Guest 内核 + eBPF TC 接管 + OpenResty L7 裁决三层 | 默认拒绝、策略可配、L7 mark 分流 | 分层排障：VM→eBPF→Egress |
| I-4 | 空闲回收且访问可秒级唤醒 | 控制/运维分离；CLM 经 Redis Stream 选主执行 pause/resume | 五状态生命周期、自动唤醒 | 部署多节点须保证 Redis 与 CLM |
| I-5 | 快照克隆即时且免独立账本 | reflink FICLONE CoW + 索引扫描重建；S3 后端走 SPDK NVMe/TCP | 本地极速、S3 可跨机/云 | 按场景选后端，快照不跨后端 |

- 知识地图含每篇覆盖 F 编号、学习路径与洞察交叉矩阵；过 G2。
- **返工记录**：I-5 曾误写"cube-agent 侧封装 11 个 rcow_*"，已修正为"cubecow S3 引擎封装 11 个、C 侧注册 9 个"。

---

## E 阶段（信源先行，分批生成）

### E-1 references/（信源先行，4 文件）

| 文件 | 内容 |
|------|------|
| `references/01-source-map.md` | 版本 pin、21 行组件地图、5 条信源瑕疵 |
| `references/02-anchor-index.md` | F-001 ~ F-244 逐条锚点表（14 主题面） |
| `references/03-glossary.md` | 五类术语表 |
| `references/index.md` | 子目录 toctree |

### E-2 concepts/ 第一批（7 篇并行）

| 文件 | 覆盖 F |
|------|--------|
| `concepts/01-overview.md` | F-001 ~ F-009 |
| `concepts/02-architecture.md` | F-010 ~ F-013 + 端口事实 |
| `concepts/03-deployment.md` | F-014 ~ F-036 |
| `concepts/04-cubeapi.md` | F-037 ~ F-059（另验证 axum 0.7 依赖真实存在） |
| `concepts/05-cubemaster.md` | F-060 ~ F-068、F-235、F-237 |
| `concepts/06-cubelet.md` | F-069 ~ F-093 |
| `concepts/07-hypervisor.md` | F-094 ~ F-140 |

### E-3 concepts/ 第二批（6 篇并行）

| 文件 | 覆盖 F |
|------|--------|
| `concepts/08-agent-shim.md` | F-141 ~ F-165 |
| `concepts/09-network.md` | F-166 ~ F-184 |
| `concepts/10-gateways.md` | F-185 ~ F-196 |
| `concepts/11-storage.md` | F-197 ~ F-214 |
| `concepts/12-ops-lifecycle.md` | F-215 ~ F-225、F-234 ~ F-238、F-241 ~ F-244 |
| `concepts/13-sdk-ecosystem.md` | F-226 ~ F-233、F-239 ~ F-240 |

### E-4 examples/（4 篇并行）

| 文件 | 覆盖 F |
|------|--------|
| `examples/01-sdk-workflow.md` | F-226 ~ F-233、F-056、F-213 |
| `examples/02-cluster-deploy.md` | F-014 ~ F-036 |
| `examples/03-template-build.md` | F-023、F-049、F-239、F-240 |
| `examples/04-pause-resume-policy.md` | F-050 ~ F-051、F-234 ~ F-238 |

### E-5 索引（最后写）

- `concepts/index.md`、`examples/index.md`、`index.md`（根，完整 frontmatter）。
- 更新域索引 `jishu/containers/index.md`：表格 + toctree 追加 cubesandbox。

**G3**：信源先行、每批 ≤7 文件、Index 最后写。

---

## V 阶段（独立验证）

### V-1 链接与结构机械检查

| 检查项 | 结果 | 说明 |
|---|---|---|
| Markdown 相对链接 | ✅ | 194 条相对链接全部可达；首轮发现 8 处断链（02-architecture.md 猜测 slug），已全部修正 |
| frontmatter 结构 | ✅ | 根 index 完整键、13 concepts + 4 examples 内容文档完整键、4 个子目录 index 最小 frontmatter |
| toctree 块 | ✅ | 根/concepts/references/examples 四级 index 均含 toctree；内容文档无 toctree |
| 绝对路径 | ✅ | 无 file:/// 引用 |
| 格式参照 | — | 根 index/log 参照 dolt，子目录 index 参照 buildah |

### V-2 源码事实与计数断言（v0.7.2 tag blob 级）

| 断言 | 复核结果 |
|---|---|
| cube-hypervisor workspace members | **勘误：29 个**（R 阶段误记 28，名单漏 block_util）——F-098 已更正 |
| C 侧 rcow_* RPC 注册 | **勘误：30 个不同名 RPC**（R 阶段误将核心 9 个当作总数）——F-212 已更正；9 个核心卷管理 RPC 为其子集 |
| Rust s3.rs rcow_* 调用 | ✅ 11 个 |
| WebUI 页面 | **勘误：19 个 .tsx、main.tsx 注册 18 条路由、主导航 15 页面**（R 阶段误记"共 15 页面"）——F-244 已更正；另勘正技术栈为 React+TSX（误写 Vue） |
| openapi paths | **勘误：26 个**（含 /health；R 阶段误记 25）——F-058 已更正 |
| 事实总数 | ✅ 244 条（F-001 ~ F-244） |
| AgentService 8 方法 | ✅ 8 个全部存在于 proto（完整服务含 30+ RPC，文档已改为"聚焦 8 个"口径） |
| L7 mark 0xCE010000/0xCE020000 | ✅ miscs.go:38 确认 |
| 就绪通知 0x680 / MMIO 0x09030000 | ✅ rpc.rs:1958/1977 确认 |
| 固定地址 169.254.68.6 / 网关 .5 | ✅ config.toml:83/86 确认 |
| Egress 192.168.0.1:8080/8443、Proxy 8080/8081/9090 | ✅ nginx.conf 确认 |
| runtime_type cube.rs / cube.v2 | ✅ main.rs:54、config.toml:149/154 确认 |
| 130409 → 409 恢复被拒链 | ✅ lifecycle.md:281 确认 |
| CubeOps :3010 / envd 49983 | ✅ Dockerfile/ envd_sidecar.go:18 确认 |
| maxSessions 1048576、ESTABLISHED 3h | ✅ reaper.go:21/118 确认 |
| envd 嵌入 16MB/ELF magic | ✅ Makefile:70/74 确认 |
| CIDR 192.168.0.0/18、s3fs refCount | ✅ start.sh:66、s3-volume.md:174-177 确认 |
| WriteTimeout 35s / resume context 25s | ✅ server.go:76 及 handleResume 确认 |

### V-3 仓库级质量门

| Gate | 结果 |
|---|---|
| check-toctrees.py（全库） | ✅ 全部 index 引用有效、内容文档可达 |
| check-utf8.py（全库 10906 文件） | ✅ |
| check-bundles-index.py（9 域/61 组/586 束） | ✅ 五面一致 |
| Sphinx dummy 构建 | ✅ 退出码 0，全树（含本束 22 文件）无报错（2026-10-04） |

**G4 结论**：静态门全部通过；4 项计数/表述勘误已闭环（facts.md ↔ 束内文档 ↔ insights.md 三处同步）。

---

## C 阶段（沉淀）

- **验证报告**：即本 log 的 V 阶段记录——G1→G4 全部通过，4 项勘误闭环。
- **模式沉淀**：引用既有 `source-code-to-okf-wiki` 工作流（信源稳定性门/信源先行/分批/Index 最后写），不新建模式。
- **新增教训（候选回填点，不独立建模式）**：计数断言（workspace members / RPC 注册数 / 路由数）不能以 R 阶段人工枚举为准，必须对 tag blob 写独立正则复核脚本；人工枚举在三次断言中全部漏项（28→29、9→30、15→18/19）。
- **提交状态**：未经用户明确指令，未执行 git commit/push；产物位于 awesome-okf-xs submodule 工作树。
