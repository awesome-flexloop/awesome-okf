# 更新日志

## 2026-11-10 · 首轮建束

**信源**：`https://github.com/cnblogs/cnblogs-skills`，commit `6f446adb7459df1d983b0c9a2088417f01ffba41`（2026-11-10 15:24:34 +08:00，main）。仓库无 release tag，按 commit hash 固定；本地克隆位于被主仓库 `.gitignore` 忽略的 `external/dao/`，文档不引用该路径。

**流程**：七概念 R→I→E→V（知识沉淀场景）叠加 source-code-to-okf-wiki 五阶段。

**新增内容**

- concepts/：8 篇（00 概览、01 架构、02 安全模型、03 首次配置、04 发布流水线、05 可见性与审核、06 CLI 参考、07 跨平台与测试）
- examples/：3 篇（非公开草稿、公开与首页推荐、维护与图片）
- references/：3 篇（源码登记与 SHA256 清单、MetaWeblog 约定、安全设计）
- 导航：根 index、concepts/examples/references 三个 index、本 log

**事实与核验**

- R 阶段共 48 条编号事实（F-001~F-048），落于工作区事实清单，未随束发布。
- 数量类事实均用脚本计数：12 文件 / 3,775 行；4 个 Python 模块 / 2,316 行；12 个 CLI 子命令；8 个实际调用的 XML-RPC 方法（参考文献列 9 个）；6 个退出码；7 个配置键；15 个测试类 / 50 个测试方法。
- 本机运行 `python -m unittest discover -s tests -v`：`Ran 50 tests ... OK (skipped=1)`，跳过项为 Windows 下不可用的 POSIX helper。
- API 真实性：文档只引用源码中出现的 `cmd_*`、`HANDLERS`、XML-RPC 方法名与参数顺序；未引入源码中不存在的方法。
- 安全扫描：全束未包含真实用户名、博客名、令牌或端点；示例统一使用 `<博客名>` / `<postid>` 占位。

**已知边界**

- 未在真实博客园账号上执行发布；审核行为以仓库自带参考文档为准。
- 仓库未提供 LICENSE 文件，本束未对许可做推断。
- 文档只覆盖 `cnblogs-publish`；仓库未来新增 skill 需另建束。
