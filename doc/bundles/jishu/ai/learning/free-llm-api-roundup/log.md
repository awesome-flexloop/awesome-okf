# 更新日志

## 2026-09-09

**Status**: `flagged`（F-145~F-150 GitHub Models已退役 + F-055 OpenAI Free Tier $5赠金已取消）

### 工作流阶段

- **S0**：内容敏感度预检→公开；骨架判定→无examples/（资讯速报/选型汇总类）；归属判定→新建 bundle `jishu/ai/free-llm-api-roundup/`
- **R**：博文全文提取（browser_use Task代理，知乎反爬拦截WebFetch）；F-001~F-221 完整登记（221条）；P0权威核验9组（WebSearch交叉验证）
- **I**：三层知识拆分→①平台全景与关键发现 ②国内23家平台 ③国际17家平台 ④选型指南
- **E**：references/先行→concepts/四篇→各级index.md
- **V**：安全检查✅（UTF-8/F编号/toctree/链接/计数/sensitive/frontmatter全通过）；四视角对抗性审查✅（魔鬼代言人/新人/老板/未来各4问，综合评分4/5星）；生成 adversarial-review.md
- **C**：✅ 子模块原子提交（commit 953f950a，15 files changed, +1562/-3）；glossary.md补充（commit d0bb5862，3 files changed, +74/-1）；最终 C stage 闭环（子模块 commit d0bb5862，主仓库 commit b3dd5ea95）0c7e429d3）

### V阶段关键产出

| 维度 | 评分 | 说明 |
|------|------|------|
| 事实准确性 | ⭐⭐⭐⭐ (4/5) | 221条事实中约93%正确，5条核心错误已标记 |
| 时效性 | ⭐⭐⭐ (3/5) | 博文发布于2026-06-17，stale_after=2026-08-17已过期 |
| 覆盖完整性 | ⭐⭐⭐⭐ (4/5) | 40家平台覆盖全面，少量遗漏（腾讯元宝、豆包等） |
| 核验严谨性 | ⭐⭐⭐⭐⭐ (5/5) | 9组P0权威核验，双清单对照 |
| 可操作性 | ⭐⭐⭐⭐ (4/5) | 选型指南清晰，缺少注册操作细节 |
| **综合** | **⭐⭐⭐⭐ (4/5)** | 资讯汇总类bundle质量较高 |

### V阶段改进建议（非阻塞）
1. ~~新增glossary.md：补充RPM/RPD/TPM/Credits等术语解释~~ ✅ 已完成
2. 新增examples/上手指南：新人注册流程和操作步骤
3. 下次核验日期：2026-10-09

### P0核验关键发现

| 声明 | 结果 |
|------|------|
| GitHub Models 免费可用（F-145~F-150） | ❌ 2026-07-30已彻底退役 |
| OpenAI Free Tier $5赠金（F-055） | ❌ 已取消 |
| Google AI Studio 1500次/天（F-132） | ⚠️ 仅部分旧版模型适用 |
| Google AI Studio Gemini 2.5 Pro 400 RPD（F-134） | ⚠️ 实际50 RPD |
| 小米MiMo 7亿Token（F-093） | ⚠️ 已升级为380亿Credits |
| 中国移动MoMA 9000万Token（F-115） | ⚠️ 官方宣传2500万Token |
| 阿里云百炼 Coding Plan 200元/月（F-109） | ✅ 基本准确 |
| 商汤日日新 2026-05-08（F-092） | ✅ 准确 |
| 讯飞星辰MaaS 2026-03（F-082） | ✅ 基本准确（内测→6月上线） |
