# doltlite-python Bundle 生成日志

## 生成记录

| 时间 | 阶段 | 操作 | 详情 |
|------|------|------|------|
| 2026-09-10 | 阶段0 | 信源分类 | env-bound，固定 tag `v0.50.7`，commit `ba3b46fa6f58e42aef4b929d97a28248832079cb` |
| 2026-09-10 | R | 事实采集 | 提取 22 条编号事实（F-001~F-022），覆盖仓库元信息、_loader.py 核心机制、bootstrap 平台策略、re-exec 约束、smoke 测试 |
| 2026-09-10 | I | 洞察提炼 | 提炼 5 条核心洞察四元组：符号劫持跨平台挑战、re-exec 约束、py3-none tag 策略、bootstrap 幂等性、lockstep 版本管理 |
| 2026-09-10 | E | 批量生成 | 生成 11 个文件：index.md, log.md, references/{index,source}.md, concepts/{index,00~03}.md, examples/{index,00~01}.md |
| 2026-09-10 | V | 验证修正 | Grep 验证 _loader.py 中的类名/方法名/常量名；计数断言 22 条事实 |
| 2026-09-10 | 导航 | 索引更新 | 更新 jishu/data/index.md 加入 doltlite-python 条目 |
| 2026-09-10 | C | 清理 | 清理 .temp/spec/doltlite-python/ 临时目录 |

## 文件清单

```
doltlite-python/
├── index.md                        # 根索引（bundle-index）
├── log.md                          # 本文件
├── references/
│   ├── index.md                    # 参考索引
│   └── source.md                   # F-001~F-022 事实台账
├── concepts/
│   ├── index.md                    # 概念索引
│   ├── 00-overview.md              # 产品定位、符号劫持原理
│   ├── 01-bootstrap-mechanism.md   # bootstrap() 逻辑、幂等性
│   ├── 02-platform-strategies.md   # Linux RTLD_GLOBAL vs macOS shim
│   └── 03-wheel-and-build.md       # py3-none tag、cibuildwheel、版本锁步
└── examples/
    ├── index.md                    # 示例索引
    ├── 00-basic-usage.md           # 标准 python script.py 用法
    └── 01-jupyter-workaround.md    # Jupyter/REPL 手动设置环境变量方案
```

## 关键决策

1. **概念文档分割**：将 bootstrap 机制（幂等性、环境标记）与平台策略（Linux vs macOS 实现差异）分为两个独立概念文档，避免单篇过长
2. **示例分拆**：基本用法覆盖标准脚本场景；Jupyter 绕过作为独立示例，因为这是 doltlite 最常被问到的痛点
3. **无 driver/dumbodb 交叉引用**：doltlite-python 是独立 Python loader，与 Go 侧的 driver/dumbodb 无直接代码共享，不引入不必要的关联
