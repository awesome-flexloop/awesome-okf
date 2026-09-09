---
type: example
title: "开发一个自定义 SKILL"
description: "按 SKILL.md 单文件约定创建自定义技能、注册到 skills.config.json 式注册表、经 SkillManager 同步与自动路由接入 Agent 的完整演练。"
tags: [lobsterai, skill, skillmd, example]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:vendor-grep", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: LobsterAI 源码事实清单（R 阶段，基线 2026.9.4）
  - id: insights
    resource: /references/insights.md
    title: LobsterAI 架构洞察（I 阶段，基线 2026.9.4）
---

# 开发一个自定义 SKILL

本演练基于 LobsterAI 技能系统的真实接口（概念背景见 [/concepts/09-skill-system.md](../concepts/09-skill-system.md)），演示从"写一个 SKILL.md"到"Agent 自动路由调用"的完整链路。

## 第一步：创建技能目录与 SKILL.md

技能的本体是**单个 SKILL.md 文件**。约定常量 `SKILLS_DIR_NAME = 'SKILLs'`、`SKILL_FILE_NAME = 'SKILL.md'`（F-la-036），即每个技能是 `SKILLs/<skill-name>/SKILL.md` 的一目录一文件结构（F-la-065）。创建 `SKILLs/weekly-report/SKILL.md`：

```markdown
---
name: weekly-report
description: 汇总本周会话与工作目录产出，生成结构化周报
official: false
version: 1.0.0
---

# weekly-report

当用户要求"生成本周周报"时：

1. 调用 local-tools 读取本周修改过的文档；
2. 按「完成事项 / 进行事项 / 风险」三段式组织；
3. 输出 Markdown 周报。
```

frontmatter 四字段为约定全部：`name`、`description`、`official`、`version`（F-la-067）。`description` 写得越具体，下一步的自动路由越准。

## 第二步：在注册表中登记运行时旋钮

`skills.config.json` 的 `defaults` 每条形如 `{ "order": <n>, "enabled": <bool> }`（F-la-066），只登记排序与启停，不复制元数据。内置 29 个条目的 order 最高用到 300（skill-creator，F-la-068），自定义技能选择不冲突的段：

```json
{
  "defaults": {
    "skill-creator": { "order": 300, "enabled": true },
    "weekly-report": { "order": 310, "enabled": true }
  }
}
```

登记后应满足一致性不变量：**目录 Glob 计数 == 注册表条目数**。内置基线是 29 == 29（F-la-065、F-la-066）；新增 1 个技能后两边都应为 30。README 声称"28 built-in skills"而实测 29 的偏差（F-la-007）正是这条断言能拦截的文档过期案例。

## 第三步：同步到用户数据目录

内置技能随包分发，但运行时使用 userData 下的副本——`SkillManager.syncBundledSkillsToUserData()` 负责把随包技能同步过去（F-la-033），形成"内置随包、用户态独立演化"的双层结构。渲染层与同步相关的 `skills:*` 通道族（F-la-037）：

```ts
// preload 暴露的 skills 门面（F-la-037），签名忠实于 preload.ts
window.skills.detectFromOpenClaw();          // → ipcRenderer.invoke('skills:detectFromOpenClaw')
window.skills.syncFromOpenClaw();            // → ipcRenderer.invoke('skills:syncFromOpenClaw')
window.skills.list();                        // → ipcRenderer.invoke('skills:list')
window.skills.setEnabled('weekly-report', true);  // → ipcRenderer.invoke('skills:setEnabled', …)
```

反向同步同样存在：`detectSkillsFromOpenClaw` / `syncSkillsFromOpenClaw` 让运行时（OpenClaw）侧新增的技能回流到产品层（F-la-033），`SkillManager` 还导出 `SkillRecord` 类型承载同步记录（F-la-033）。

## 第四步：接入自动路由

`SkillManager.buildAutoRoutingPrompt()` 基于技能 description 构建自动路由提示词（F-la-033）。用户输入"帮我写本周周报"时，路由提示词中的 weekly-report 描述命中，Agent 决定加载该技能。这一步**不需要任何代码**——路由素材就是第一步写好的 `description`。

## 第五步：从市场分发（可选）

技能也可经市场下载分发，对应生命周期方法（F-la-033）：

```ts
// SkillManager 方法面（F-la-033）
downloadSkill(source);            // 下载技能包
confirmPendingInstall(pendingId, action);  // 安装需人工确认后生效
upgradeSkill(skillId, downloadUrl);        // 升级
startWatching();                  // 监听技能目录变更
```

渲染层对应 `skills:download` / `skills:upgrade` / `skills:confirmInstall` 通道（F-la-037）。`confirmPendingInstall` 的显式确认环节是供应链防护：下载完成不等于安装完成。

## 要点回顾

1. 技能 = 一目录 + 一份 SKILL.md（四字段 frontmatter）；
2. 注册表只存 `{order, enabled}`，目录计数与注册表计数互相校验；
3. `syncBundledSkillsToUserData` 完成随包技能到用户态的落地；
4. 自动路由的素材就是 description，写好描述即完成接入。

## 相关概念

- [/concepts/09-skill-system.md](../concepts/09-skill-system.md)
- [/concepts/02-ipc-channel-contracts.md](../concepts/02-ipc-channel-contracts.md)
