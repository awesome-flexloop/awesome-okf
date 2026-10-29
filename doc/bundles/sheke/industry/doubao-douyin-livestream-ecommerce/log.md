# 变更日志

## 2026-10-29

- 内容敏感度预检：用户提供的 `mp.weixin.qq.com` 文章，无登录、验证码、邀请码或付费墙，判为**公开内容（Public）**，入 `doc/bundles/sheke/industry/`。
- 采集：微信反爬拦截 WebFetch（返回「环境异常，完成验证后即可继续访问」），改用 `agent-browser` 打开页面并提取 `#js_content` 全文；标题经 `agent-browser get title` 校验。
- 按 `blog-article-to-okf-bundle` 模式执行 R → I → E → V：
  - **R**：[事实清单](references/article-source.md) F-001~F-043，连续无跳号；口径分 `page_fact` / `reporter_test` / `author_claim` 三类。
  - **P0**：完成 C1~C17 核验（9 项多源通过、8 项未能核验）、E1~E4 口径差异、G1~G10 缺口，判定 `status: flagged`。
  - **I**：三层拆分——事件/时间线层、转化与补贴机制层、竞争格局层；机制层判断（F-026、F-039~F-043）显式标「观点」。
  - **E**：生成 `index.md`、3 篇 concepts、2 篇 references（+两篇 index）、`log.md`；更新父级导航与计数面。
- 操作可复现性两问均不满足（无可照做的安装/配置/代码流程；价格对比为不可复现的单次实测），**不创建 `examples/`**。
- 未实测：未在豆包内实际下单，价格（17.43/27.9 元）与直播间推荐机制均未复现。

### 核验摘要

- ✅ 通过：QuestMobile 4.19 亿月活 / 月均 72 次（C1、C2）、美团智能掌柜 130 万商家（C3）、千问与淘宝互通（C4）、美团小团 2.0（C5）、京东「东东」（C6）、京麦 AI 经营中心（C7）、直播间嵌入多源转述（C8）。
- ⚠️ 未通过/未能核验：价格实例 17.43 vs 27.9 元（C10）、「双11问豆包」标签（C11）、消费券进入红果短剧/头条（C12）、时间线 2026-03/04（C13）、袋鼠管家/超脑 3.0/千问办公电商版（C14~C16）。
- 口径差异 4 组（京麦上线时间、CatPaw 名称、豆包电商起步描述、QuestMobile 数据归属）。

### 门禁结果

- `invoke gates.utf8` / `invoke gates.toctrees` / `invoke gates.bundles`：见下方「执行记录」。

### 已知环境基线

- 计数更新按**干净检出真值 + 本包 +1** 计算：总索引 `total_bundles` 691→**692**、`sheke` 域 83→**84**、`industry` 分组 35→**36**。
- 本包未执行 Git 提交前，等待用户明确提交请求。

## 2026-10-29 · 门禁执行记录

`invoke gates.*` 依赖不可用，按等价命令在 `projects/awesome-okf-xs/` 下直接执行底层脚本，全部通过：

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 12580 个文件均为有效 UTF-8 |
| toctree | `python scripts/check-toctrees.py` | ✅ 全部 index.md 引用有效，所有内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 63 组 / 692 束，五面一致 |
| 资产基线口径 | `python scripts/check-asset-baseline.py` | ✅ 校验通过（total_bundles 单一真相源 692，三处规模数字一致，行尾归一自证成立） |
| Python 红线 | `python -m pytest tests/unit/test_no_future_annotations.py -q` | ✅ 11 passed |
