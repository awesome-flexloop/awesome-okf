# 信源登记簿（References）

本目录登记本 bundle 所有内容的信源出处与核验报告。

## 信源清单

| 信源 | 说明 | 引用内容 |
|------|------|---------|
| [博文信源登记](article-source.md) | F-001~F-070 全部编号事实登记、信源距离分布、核验覆盖说明 | 全部 concepts 文档 |
| [P0 权威核验报告](verification.md) | 9 项 P0 声明逐项核验结论 + 勘误四张清单 | 全部 concepts 文档 |

## 信源核验说明

- 全部事实编号引用 spec `facts.md`（F-001~F-070），无 facts 之外的事实
- 9 项 P0 声明核验结果：7 项 ✅，1 项 ⚠️（F-042 口径需细化），1 项 ❌（F-045 勘误已补充 F-060）
- F-045 勘误：源文将 DoltHub Web UI 查询超时限制（约 1GB）泛化为 Dolt 数据库本身性能限制，官方正确口径见 verification.md 清单二、清单四

```{toctree}
:hidden:
:maxdepth: 7

article-source
verification
```
