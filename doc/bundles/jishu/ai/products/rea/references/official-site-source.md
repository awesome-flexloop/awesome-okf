---
type: Reference
title: "REA 中文官网全站信源与覆盖台账"
description: "2026-10-12 中文站 17 页的采集范围、知识归属、固定证据资产与未执行边界"
sources:
  - id: official-site
    resource: https://rea.tools/zh-CN/
  - id: sitemap
    resource: https://rea.tools/sitemap.xml
  - id: site-source
    resource: https://github.com/morluto/rea/tree/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website
generated: {by: "process:seven-concepts-r", at: "2026-10-12"}
status: draft
---

# 中文官网全站信源与覆盖

采集日期为 2026-10-12。以下页面均通过公开访问获取 HTML，并提取 Markdown 后读完正文。官网是在线快照；固定仓库提交是可重复检查的证据资产，两者不能无条件视为同一部署版本。页面和证据文件属于同一上游，不计作相互独立的信源。

## 页面登记

| ID | URL | 已读章节或主题 | 知识归属 | 状态 |
|---|---|---|---|---|
| W01 | https://rea.tools/zh-CN/ | 定位、安装入口、人工与助手调查、恐龙、计算器 | 入门与实验 | 正文已读 |
| W02 | https://rea.tools/zh-CN/get-started/ | 助手连接、CLI、Ghidra/Hopper/IDA、故障检查 | 安装教程 | 正文已读 |
| W03 | https://rea.tools/zh-CN/first-investigation/ | Notes ZIP、导出路径、CSV 预测与验证、错误追踪 | 首次调查示例 | 正文已读 |
| W04 | https://rea.tools/zh-CN/faq/ | 产品、目标域、依赖、权限、限制 | 入门边界 | 正文已读 |
| W05 | https://rea.tools/zh-CN/guides/ | native/JavaScript/browser 路径选择 | 指南导航 | 正文已读 |
| W06 | https://rea.tools/zh-CN/guides/native/ | DX-Ball 函数、指令、声像规则、验证 | 原生调查 | 正文已读 |
| W07 | https://rea.tools/zh-CN/guides/javascript/ | Notes 模块、preload、IPC、CSV、静态图 | JavaScript 调查 | 正文已读 |
| W08 | https://rea.tools/zh-CN/guides/browser/ | 已启动浏览器、目标发现、网络窗口、脚本源 | 浏览器调查 | 正文已读 |
| W09 | https://rea.tools/zh-CN/showcase/ | 五项案例及各自验证摘要 | 案例导航 | 正文已读 |
| W10 | https://rea.tools/zh-CN/showcase/dx-ball/ | 原始指令、重建 C、3205 用例、63 字节匹配 | DX-Ball 示例 | 正文已读 |
| W11 | https://rea.tools/zh-CN/showcase/notion/ | 动态桥、IPC、剪贴板格式、本地 payload、SQLite port | Notion 示例 | 正文已读 |
| W12 | https://rea.tools/zh-CN/showcase/th04/ | DOS 地址、环形角度、完整 helper、历史编译器 | TH04 示例 | 正文已读 |
| W13 | https://rea.tools/zh-CN/showcase/aegis/ | APK helper、时间块、HMAC、截断、133 用例 | Aegis 示例 | 正文已读 |
| W14 | https://rea.tools/zh-CN/showcase/ctf/ | mask 解码、方程、假设、正负例与唯一性局限 | CTF 示例 | 正文已读 |
| W15 | https://rea.tools/zh-CN/examples/dino-lab/ | 速度模块、更新次数、交互游戏、许可 | 恐龙实验 | 正文已读 |
| W16 | https://rea.tools/zh-CN/blog/ | 东方重建文章索引 | 进阶导航 | 正文已读 |
| W17 | https://rea.tools/zh-CN/blog/touhou-reconstruction/ | TH04/TH08 历史、比较器漏检、状态归属、现代移植 | 重建验证方法 | 正文已读 |

## 覆盖口径

对 sitemap XML 的 URL 去重并筛选中文路径得到 17 页；从每页 HTML 的 `href` 提取站内中文链接，按该来源页自己的 URL 解析相对地址，去除片段与查询参数后去重，亦得到 17 页。两集合差集为空。语言副本、站外页面及 ZIP/脚本资源不计作中文内容页。

同时盘点 HTML 的 `details/summary`，读取安装平台说明、案例证据与完整代码、博客里程碑和生成器说明。FAQ 的 15 个 details 包含语言选择器，不能称为 15 个 FAQ 问题。折叠节点数量不是页面数量，也不是独立事实数量。

缓存只作本轮采集辅助，不作为知识包永久引用。没有失败页计入已读。图片内文字未做 OCR；本轮未通过浏览器操作官网游戏，交互结果以已读实现与上游证据记录为准。

## 固定证据资产

以下链接均锚定 `eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a`，路径位于实际官网资产 `website/`，不能以 `docs/` 的 VitePress 配置代替：

| 资产 | 固定来源 | 证据用途 |
|---|---|---|
| 计算器与恐龙 | [calculator-and-dino.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/calculator-and-dino.md) | 目标身份、人工辅助选择、控制实验与教学规则范围 |
| 三类指南 | [guide-examples.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/guide-examples.md) | Notes 静态图、formatter、外部浏览器 controller |
| DX-Ball | [dx-ball-sound-pan.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/dx-ball-sound-pan.md) | 数值范围、函数 extent、编译匹配局限 |
| Notion | [notion-clipboard.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/notion-clipboard.md) | partial trace、额外源码阅读、stub harness 边界 |
| TH04 | [th04-bullet-ring.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/th04-bullet-ring.md) | 地址换算、教学摘要与 compiler-sensitive helper |
| Aegis | [aegis-login-code.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/aegis-login-code.md) | APK 版本、Java 提取方法、133 用例范围 |
| CTF | [ctf-masked-squares.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/ctf-masked-squares.md) | 26 方程、额外约束、原程序正负例、未证唯一性 |
| 东方重建 | [touhou-reconstruction-method.md](https://github.com/morluto/rea/blob/eaf88aca2af2b8ad7a277c09d0b45f6e2de8ac4a/website/evidence/touhou-reconstruction-method.md) | 历史归属、时间统计口径、比较器浮点数据漏检 |

## 版本与验证边界

本地 REA 基线为 6.4.0；多数官网记录来自 REA 4.1.0，Aegis 来自 6.1.0。上游实验记录不等于本知识包本机验证。静态调查、提取函数测试、字节匹配、目标 UI 与整程序游玩是不同证据层级。

本轮不安装 REA、Ghidra、JADX、Electron 或求解器，不启动被分析应用，不执行 CTF 原程序。公开教学算法若在现有 Node 环境运行，只能证明该模块的输出，不能证明历史目标应用的行为。本地处理文件也不保证模型客户端不会将证据发送给模型服务商。

## 相关概念

- [既有信源台账](source-manifest.md)
- [编号事实](facts.md)
- [知识地图](insights.md)
