---
title: 第十三章 智能旅行助手
type: reference
bundle: /datawhale/hello-agents
chapter: 13
part: 第四部分：综合案例进阶
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter13/第十三章%20智能旅行助手.md
---

# 第十三章 智能旅行助手

## 章节概要

首个综合实战项目，构建包含智能行程规划、地图可视化、预算计算的完整旅行助手应用，展示MCP协议与多Agent协作的真实世界应用。

## 核心功能
1. **智能行程规划**：根据目的地、日期、偏好自动生成景点+餐饮+酒店完整行程
2. **地图可视化**：标注景点位置、绘制游览路线
3. **预算计算**：自动计算门票、酒店、餐饮、交通费用
4. **行程编辑**：添加/删除/调整景点，实时更新
5. **导出功能**：PDF或图片导出

## 技术架构
前后端分离四层架构：

```
前端层（Vue3+TypeScript）
    ↓
后端层（FastAPI）：API路由、数据验证、业务逻辑
    ↓
智能体层（HelloAgents）：4个专门Agent
    ↓
外部服务层：高德地图API、Unsplash API、LLM API
```

### Agent分工
- 景点搜索Agent
- 天气查询Agent
- 酒店推荐Agent
- 行程规划Agent

各Agent通过**MCP协议**调用外部API。

### 数据流转
用户填表 → 后端验证 → 调用Agent系统 → 各Agent依次通过MCP调用外部API → 整合结果 → 前端渲染

## 项目结构
```
helloagents-trip-planner/
├── backend/
│   ├── app/
│   │   ├── agents/       # 智能体实现
│   │   ├── api/          # API路由
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 服务层
│   │   └── config.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── views/
        ├── services/
        ├── types/
        └── router/
```

## 教学价值
- 将前12章知识融会贯通的首个完整项目
- 展示MCP协议在真实场景中的应用
- 多Agent协作模式的具体落地
- 前后端分离的工程化实践
