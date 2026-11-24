---
okf_version: "0.2"
type: Reference
title: "skylinevpn-proxylist 信源层索引"
description: "事实登记、核验报告与本束引用纪律——引用任何数字或行为结论前的必读入口"
---

# 信源层索引

| 文件 | 内容 | 何时读 |
|------|------|--------|
| [facts.md](facts.md) | F-001 ~ F-068，分 A 仓库与版本 / B 数据文件 / C 编译管线 / D 发布工作流 / E 治理与边界五节 | 引用任何数字、路径、正则、命令前 |
| [verification.md](verification.md) | 口径歧义 C-1 ~ C-5、对抗审查 D-1 ~ D-8、不可核验边界、复核触发条件 | 下判断、写对外材料、质疑结论时 |
| [import-verification.md](import-verification.md) | 导入后验证报告：变更清单、五面对账、三条门禁原样输出、结构与内容完整性、遗留项 | 验收、复核导入结果、对外交付前 |

## 引用纪律

1. **数字不复制**：提交数、条目数、tag 数、文件大小等易腐数字只在 `facts.md` 维护，正文以 `F-编号` 引用。
2. **区分性质**：`[事实]` 可直接核对源码与 git 元数据；`[清点]` 是本次对数据文件的统计或抽样；`[文档口径]` 是仓库文档的自我描述。
3. **不越界**：仓库不含匹配器与客户端，任何关于「命中后是否可达」「代理效果如何」的描述都不属于本束可主张的范围。
4. **运行时缺席**：本包未联网执行构建、未访问 Release 页面、未接入客户端，见 [verification.md](verification.md) 第一节。

## 一手信源

| 信源 | 路径（相对仓库根） |
|------|------------------|
| 数据产物 | `proxy.list` |
| 编译器 | `scripts/merge.py` |
| 取料器 | `scripts/build.sh` |
| 发布工作流 | `.github/workflows/release.yml` |
| 用户文档 | `README.md` |
| 许可 | `LICENSE` |
| 忽略规则 | `.gitignore` |

## 统计口径

- 条目数 = 「非空且不以 `#` 开头」的行数。
- 节归属 = 最近一个 `## <name>` 标题之后的条目。
- 行号 = 1 基，按 PowerShell `Get-Content` 的行序。

```{toctree}
:hidden:
:maxdepth: 7

facts
verification
import-verification
```
