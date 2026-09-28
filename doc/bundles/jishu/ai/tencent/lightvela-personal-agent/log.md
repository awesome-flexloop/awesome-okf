# 变更日志

## 2026-09-28 - 初始版本

- ✅ 按方法论编排知识沉淀链路 `R→I→E→V→C` 完成（场景：知识沉淀/商业分析）。
- ✅ 内容敏感度预检：公开博文（`mp.weixin.qq.com` 无访问控制参数，36 氪有公开转载），走标准工作流。
- ✅ 微信原文经 WebFetch 直接提取成功（未触发反爬回退），并以 36 氪转载页核对标题、账号与发布时间。
- ✅ 登记博文事实 F-001～F-045；三组独立上下文子代理完成 P0 权威核验，补充 F-046～F-062（共 62 条，连续无跳号）。
- ✅ 勘误 5 处并在正文落实：①340 万为美加商店 Sensor Tower 估算、三家区间 230–430 万；②登顶为上线第 10 天；③千问 3 亿用户/Qwen 3.8/持仓部分用户；④Personal Intelligence 2026-01 发布且含 YouTube；⑤Manus 对比金句恢复官方原词“持续使用/you keep”。
- ✅ 事实补强：Muse Spark 非 Llama 与三档订阅、Hermes MIT 仓库信息、上游网关与 LightVela 适配层的通道分层、微信机器人合规边界、陈宇森人事脉络（长亭科技创始人，非实在智能）、Spark 前身 Remy 与 Mariner 关停。
- ✅ 操作可复现性两问判定为“否”，不设 `examples/`；生成 3 篇 concepts、2 篇 references、2 个子目录索引、根索引与本日志（共 9 个文件）。
- ✅ 归属 `jishu/ai/tencent/lightvela-personal-agent/`，更新 tencent 分组 index（束数 7→8）与 bundles 总 index 计数。
- ⚠️ 未运行 `invoke gates.*`（子项目可选文档依赖未必安装）；按手动等效清单执行：三级 toctree 条目核对、相对链接核对、UTF-8 strict 解码、spec/bundle 双份 F 编号集合比对，结果记入 V 阶段。
