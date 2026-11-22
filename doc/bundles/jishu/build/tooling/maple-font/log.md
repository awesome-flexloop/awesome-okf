# Maple Mono OKF Bundle 生成日志

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
