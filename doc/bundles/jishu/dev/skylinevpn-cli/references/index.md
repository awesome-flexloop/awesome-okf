---
okf_version: "0.2"
type: Reference
title: "skylinevpn-cli 信源层索引"
description: "事实登记、核验报告与本束引用纪律——引用任何数字或行为结论前的必读入口"
---

# 信源层索引

| 文件 | 内容 | 何时读 |
|------|------|--------|
| [facts.md](facts.md) | F-001 ~ F-072，分 A 仓库与版本 / B 产品与命令面 / C 发行架构 / D 构建脚本 / E 身份与泄漏门五节 | 引用任何数字、命令、路径、正则前 |
| [verification.md](verification.md) | 口径冲突 C-1 ~ C-5、对抗审查 D-1 ~ D-7、不可核验边界、复核触发条件 | 下判断、写对外材料、质疑结论时 |

## 引用纪律

1. **数字不复制**：提交数、模式条数、资产数量等易腐数字只在 `facts.md` 维护，正文以 `F-编号` 引用。
2. **区分性质**：`[事实]` 可直接核对文件；`[文档口径]` 是仓库文档的自我描述；`[清点]` 是本次目录清点结果。
3. **不越界**：仓库不含产品源码（F-007），任何关于隧道协议、加密、节点调度的描述都不属于本束可主张的范围。
4. **运行时缺席**：本包未执行二进制、未运行安装器、未访问服务端，见 [verification.md](verification.md) 第三节。

## 一手信源

| 信源 | 路径（相对仓库根） |
|------|------------------|
| 多语言 README（6 种） | `README.md`、`README.zh-CN.md`、`README.zh-TW.md`、`README.ja.md`、`README.ru.md`、`README.fa.md` |
| 版本记录 | `CHANGELOG.md` |
| 许可 | `LICENSE` |
| 发行手册 | `tools/RELEASING.md` |
| 发布暂存 | `tools/build_release.py` |
| 身份门 | `tools/check-identity.sh`、`tools/install-hooks.sh` |
| 发布门 | `tools/publish-release.sh` |

```{toctree}
:hidden:
:maxdepth: 7

facts
verification
```
