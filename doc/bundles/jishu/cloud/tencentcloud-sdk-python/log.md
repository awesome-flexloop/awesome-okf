# tencentcloud-sdk-python Bundle 变更日志

## 2026-10-04 — 初始版本（R→I→E→V→C 全链路）

- 信源：TencentCloud/tencentcloud-sdk-python 固定快照 tag `3.1.185`，commit `be50b26d4d997c5d8d9c07fc84c03ee5e05ece68`（2026-10-02），工作树 clean
- R 阶段：精读 common/ 全部 20 个运行时文件 + CVM v20170312 生成样本 + setup.py/package.py/products.md/README/CHANGELOG/tox.ini + QcloudApi 遗留层 + tests/unit + examples，产出 100 条编号事实（facts.md，F-001~F-100，12 个主题面）
- I 阶段：提炼 6 条现象/根因/影响/建议四元组洞察（insights.md）：极小内核+生成层、凭证零配置链、弹性默认关闭、签名端点解耦、同步异步双栈、分包与遗留共存；附知识地图与 9 篇概念学习路径
- E 阶段：信源先行（references/source-1 源码快照、source-2 元数据），生成 9 篇概念文档与 3 篇实战示例，各级 index 最后落盘
- V 阶段：Grep 回源核验类名/方法名，Python 脚本独立复核全部计数断言（263 目录/261 产品/262 清单行/300 版本包/34 多版本产品/106 动作/286 模型类/417 错误码/1783+52 个 .py/49 示例），frontmatter 与 toctree 检查通过
- 归属：新建 `jishu/cloud/` 生态分组（云厂商开放 API SDK）承载本束，同步更新 bundles/index.md 与 jishu/index.md 计数（583→584 束、60→61 组、jishu 434→435 束/17→18 组）
- 主题覆盖：云 API 3.0 协议、TC3-HMAC-SHA256 签名、AbstractModel 序列化、五级凭证与自动刷新、重试/地域熔断、requests/httpx 双 IO 栈、SSE、CommonClient、代码生成模式、产品分包、QcloudApi v2 遗留层
