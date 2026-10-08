# 实战示例

LobsterAI 实战演练，共 3 篇，分别对应技能系统、IPC 数据访问与定时任务投递三条主线，全部基于 tag 2026.9.4（7592cd0）基线的真实接口编写。

* [开发一个自定义 SKILL](custom-skill-development.md) — 按 SKILL.md 单文件约定创建技能、注册到 skills.config.json 式注册表、经 SkillManager 同步与自动路由接入 Agent 的完整演练。
* [通过 IPC 通道查询会话消息](query-session-messages-ipc.md) — 渲染层经 cowork:session:* 通道分页拉取会话列表与消息历史、订阅 cowork:stream:* 流式事件、以 CoworkStore 方法面理解主进程侧数据出口。
* [定时任务配置与投递流程](scheduled-task-delivery.md) — 创建 cron 定时 Agent turn 任务、配置投递/会话/唤醒三组旋钮、经 CronJobService 轮询对账并把结果投递到 IM 会话的完整链路。

```{toctree}
:hidden:
:maxdepth: 7

custom-skill-development
query-session-messages-ipc
scheduled-task-delivery
```
