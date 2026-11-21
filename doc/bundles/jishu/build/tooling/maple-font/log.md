# Maple Mono OKF Bundle 生成日志

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
