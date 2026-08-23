# 示例索引

Agent Learning Hub 是一个学习路线图项目，不包含可运行的源代码示例。项目的"示例"体现为两类实践指引：

## 阶段产出物（Stage Deliverables）

每个学习阶段都定义了一个可交付的产出物，作为掌握该阶段技能的验证标准：

| 阶段 | 产出物 |
|------|--------|
| Stage 0 | 一页短笔记：回答"我的场景为什么需要 agent，而不是普通 workflow？" |
| Stage 1 | 一个 50-150 行的最小 agent，可选择工具、执行工具、返回最终答案 |
| Stage 2 | 一个资料研究助手，输入主题后自动搜索、筛选、总结并输出引用链接 |
| Stage 3 | 一个可调试的 agent harness demo，含 README、运行步骤、示例输入输出和失败记录 |
| Stage 4 | 一个小型多 agent 系统，例如 research → write → review → revise |
| Stage 5 | 一个可复用 skill，例如 code-review、research-report、migration-helper |
| Stage 6 | 一个只操作公开网页的 browser agent |
| Stage 7 | 一个 agent eval 表格，至少包含 20 个任务、期望结果、实际结果、失败分类 |
| Stage 8 | 一个别人能 clone 下来跑的 agent 项目 |

## 项目阶梯（Project Ladder）

11 级递进式项目建议，从简单到复杂：

1. Calculator Agent（最小 tool call loop）
2. Web Research Agent（搜索、筛选、引用、总结）
3. PDF QA Agent（RAG 全流程）
4. Coding Review Agent（读取 diff、风险排序）
5. Browser Agent（页面观察与操作）
6. Claude Code-like Nano Agent（shell、文件编辑、权限）
7. OpenClaw-like Gateway（channel、routing、session、memory）
8. Reusable Skill Pack（SKILL.md、脚本、smoke test）
9. Multi-Agent Writer（planner、writer、reviewer 协作）
10. Personal Agent（记忆、skills、消息入口）
11. Production Harness（evals、trace、权限、CI、回放）

## 参考项目

路线图各阶段推荐了大量开源项目作为学习参考，完整列表见 [核心资源分类](../concepts/resource-curation.md) 中的"项目地图"和"GitHub 仓库"部分。
