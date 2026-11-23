# Maple Mono OKF Bundle 生成日志

## 2026-11-23

### 验证执行（承接 2026-11-22 节「验证计划」）

在服务器直连通道（`ssh ai@10.16.11.3`，py314）执行：

| 质量门 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | 通过：13 643 个文件均为有效 UTF-8 |
| toctree 导航 | `python scripts/check-toctrees.py` | 通过：全部 index.md 引用有效，内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | 通过：9 域 / 65 组 / 756 束，计数五面一致 |
| 构建零告警 | `sphinx-build -b html -W`（包级作用域） | 修复 1 条告警后通过，产出 23 个 HTML |

### 缺陷与修复

`concepts/04-feature-ast-generator.md:81` 的 FEA 代码块标注为 ```fea```，Pygments 不内置该词法器，构建期抛出 `misc.highlighting_failure`（`-W` 下等同构建失败）。

处置由「改写围栏语言」升级为「补齐词法器」：

- 新增 `doc/_ext/fea_lexer.py`：以 `RegexLexer` 定义 `FeaLexer`（`aliases = ["fea"]`），覆盖注释、关键字、字形类 `@Class`、字形标记 `glyph'`、数字与标点，`setup(app)` 中调用 `app.add_lexer("fea", FeaLexer)`；
- `doc/conf.py` 的 `extensions` 追加 `"_ext.fea_lexer"`，与既有 `_ext.okf_inventory_builder` 同级；
- 该代码块围栏还原为 ```fea```，保留源码语义标注。

验证装置：复用真实 `doc/conf.py`，仅做三处覆盖——`master_doc` 指向本束首页、`intersphinx_mapping` 置空（离线取证）、仅从 `suppress_warnings` 中移除 `misc.highlighting_failure` 一条；srcdir 为只含本束与 `_ext`/`_static`/`_search` 的复制目录，经 `ssh ai@10.16.11.3`（py314，Sphinx 9.2.0 + myst-parser 5.1.0）串行执行 `sphinx-build -b html -W --keep-going`。

验证结果：EXIT=0、0 条 WARNING，产物 HTML 含 `highlight-fea` 代码块与 `class="k">lookup`、`class="k">sub`、`class="k">by` 高亮片段。

反证：同一装置注销 `_ext.fea_lexer` 后 EXIT=1，于 `concepts/04-feature-ast-generator.md:81` 报 `misc.highlighting_failure`（未知词法器 `fea`），说明零告警并非抑制项所致的假阳性。

背景：全库 107 种围栏语言中 33 种未经 Pygments 注册（`mermaid` 1789 处已由 `myst_fence_as_directive` 转为指令，`ninja` 81、`shellscript` 76、`jinja2` 38、`jsonc` 30 等），逐一注册不可行，故 `misc.highlighting_failure` 仍保留在 `suppress_warnings`；`fea` 是本包正文语言，单独补齐。

### 取证边界

- 全库 `-W` 构建未取得完整证据：本地 Python 3.14 环境 Sphinx 9.1.0 与 myst-parser 4 不兼容（`SphinxUnreferencedFootnotesDetector` 注册失败）；服务器全库构建 10 分钟仍处于读取阶段（CPU 0.2%），故改用「包级作用域构建 + 三条 CI 质量门」组合取证。
- 三个子索引保留 `okf_version: "0.2"`：全仓 1394 个非根文件同为该写法，与规范 §12「仅 bundle 根可声明」的字面要求存在偏差，本包随全仓风格。

## 2026-11-22

### 触发
上游 `notebook/libs/maple-font` 已由 v7.9 更新至 v8（`v8.0-beta.3`，内嵌版本 `8.003`），并完成文档重构（#850：README 精简，构建指南迁入 `documentation/`）。旧包描述的 `source/py` 架构、`build_mono` / `build_nf` / `build_cn` 函数与 `FontConfig` / `BuildOption` 模型均已被替换。

### 方法
按七概念方法论 **知识沉淀** 场景链路 R→I→E 执行，并沿用知识包原有结构。

### 事实层（G1 事实门）
本次核对的关键客观事实：

- 仓库结构：`scripts/` 分包（config / pipeline / feature / cjk / font_ops / task / utils），入口为 `build.py` 与 `task.py`；
- 配置链路：`config.json` + CLI → `BuildConfigResolver` → `ResolvedConfig` → `BuildRuntimeContext` → `BuildPlan`；
- `ResolvedConfig` 含 behavior / feature / nerd_font / cjk / identity / metrics 六组子配置；
- 基础格式 Variable / TTF / OTF；`--format ttf,otf,woff2` 只影响静态格式，Variable 始终构建；
- 三档宽度：`default` 600 / `narrow` 550 / `slim` 500；
- 特征双轨：Python AST 生成式与 `--apply-fea-file` 文件式；
- 冻结发生在源准备期，单一替换写入每个 UFO master；上下文规则移入 `calt`；
- Nerd Font 三基座：`MapleMono-NF-Base{,-Mono,-Propo}.ttf`；`uses_font_patcher()` 判定回退；
- CJK 四语种：CN（WenYuan Rounded SC）、TC（Chiron Go Round TC）、JP（Resource Han Rounded JP）、KR（Chiron TC 过滤韩文）；
- CJK 七级回退与独立缓存 `sources/cjk/`；
- 可选缓存 `fonts/build-cache.json`，阶段身份不含生成器源码、依赖版本、UFO 轮廓、CJK 基座内容；
- 执行器：`pool_size<=1` 或 CI 用同步执行器，否则进程执行器并支持线程回退；
- 入口 7 个任务：`nf`、`fea`、`designspace`、`release`、`cjk`、`googlefonts`、`publish`；
- 依赖：Python ≥3.10，fontmake 3.12、fonttools 4.63、glyphsLib 6.13、skia-pathops 0.9、ttfautohint-py 0.6。

### 洞察层（G2 洞察门）
重写后的四元组洞察（已写入 bundle/index.md）：

1. 解析—计划—执行三段分离，使 dry-run 可审计、阶段策略可独立测试；
2. 配置归一化前移，避免默认值散落与不可复现；
3. 特征双轨 + 源准备期冻结，保证静态与变量输出同构；
4. CJK 独立子系统与七级回退，使基座可脱离主流水线维护；
5. 缓存身份是显式契约，未纳入身份的输入变更必须无缓存构建；
6. 预构建 NF 基座优先、font-patcher 兜底，换取速度与可复现性。

### 萃取层（G3 模式门）
- “意图 / 计划 / 执行”三对象分离 → 可迁移至任何多阶段构建系统；
- “解析期归一化 + 显式阶段身份” → 可迁移至增量构建与缓存设计；
- “源准备期固化 + 运行时特征保留” → 可迁移至编译期与运行期的能力分配；
- “独立子系统 + 分级回退” → 可迁移至可选资源（语言包、插件、模型权重）的装配。

### 变更清单
- 重写 `index.md`、`concepts/00`–`08`、`examples/*`、`references/*` 全部事实与路径；
- `concepts/07-cn-font-merge.md` → `concepts/07-cjk-font-merge.md`；
- `examples/cn-font-build.md` → `examples/cjk-build.md`；
- `references/font-config-class.md` → `references/resolved-config.md`；
- 更新 `concepts/index.md`、`examples/index.md`、`references/index.md` 的表格与 toctree；
- 更新上级 `jishu/build/tooling/index.md` 中本包的简介；
- frontmatter 的 `source_version` 更新为 `v8.0-beta.3 (8.003)`，`generated.at` 更新为 `2026-11-22`。

### 验证计划
- `invoke gates.utf8`、`invoke gates.toctrees`、`invoke gates.bundles`；
- 检查全部相对链接与更名后的锚点；
- 包内计数保持 9 concepts / 4 examples / 3 references。

## 2026-11-21

### 方法
按七概念方法论 **知识沉淀** 场景链路 R→I→E 执行：

1. **R（复盘）**：采集 maple-font v7.9 源码、README.md、build.py、config.json、source/schema.json、source/py/feature/、source/py/freeze.py、task.py 等文件，确认 22+ 条客观事实。
2. **I（洞察）**：形成 5 条四元组洞察（现象+根因+影响+建议）。
3. **E（萃取）**：原子化为 9 篇概念文档 + 4 篇实战示例 + 3 篇 API 参考。

### 事实层（G1 事实门）
- v7.9 版本，PyPI package，requires-python >= 3.10
- 变量字体 + 多输出格式（Variable/TTF/OTF/WOFF2）
- 配置驱动（config.json JSON Schema 完整声明）+ CLI 覆盖层
- Python AST 风格 OpenType Feature 生成
- 三模式特征冻结（enable/disable/ignore）
- 预构建 Nerd Font Base + font-patcher 回退
- 中英文字体合并（merge_ttfonts + 2:1 对齐）
- ProcessPoolExecutor 并行构建（pool_size=4）
- AST 查找表生成（calt/cv/ss）
- 下载哈希校验（cn-base static sha256）
- GitHub 镜像支持
- 宽度三档（default/narrow/slim）
- ttfautohint hinting 支持

### 洞察层（G2 洞察门）
- 5 条四元组洞察已写入 bundle/index.md 核心洞察节

### 萃取层（G3 模式门）
- 配置驱动双层架构 → 可迁移至其他构建系统
- Python DSL 嵌入通用语言 → 可迁移至代码生成领域
- OpenType Feature 时冻结 → 可迁移至编译时固化动态规则场景
- 字体组件化组合 → 可迁移至软件系统的模块化组装场景
- 预构建 vs 动态生成权衡 → 可迁移至构建加速策略

### 产出
- 位置：`jishu/build/tooling/maple-font/`
- 结构：concepts（8）+ examples（4）+ references（3）
- 格式：OKF v0.2
