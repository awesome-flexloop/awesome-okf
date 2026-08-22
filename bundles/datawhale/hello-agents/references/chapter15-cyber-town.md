---
title: 第十五章 构建赛博小镇
type: reference
bundle: /datawhale/hello-agents
chapter: 15
part: 第四部分：综合案例进阶
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter15/第十五章%20构建赛博小镇.md
---

# 第十五章 构建赛博小镇

## 章节概要

探索Agent技术与游戏引擎结合的新方向，构建拥有智能NPC的2D像素风格AI小镇，展示记忆系统和好感度系统在社交模拟中的应用。

## 核心功能
1. **智能NPC对话**：自然语言对话，NPC根据角色设定和记忆回应
2. **记忆系统**：短期记忆+长期记忆，记住与玩家的互动历史
3. **好感度系统**：NPC态度随互动变化（陌生→熟悉→友好→亲密）
4. **游戏化交互**：2D像素办公室场景，自由移动与NPC互动
5. **实时日志**：所有对话和互动记录，便于调试分析

## 技术架构
游戏引擎+后端服务分离架构：

```
前端层：Godot 4.5游戏引擎
  - 游戏渲染、玩家控制、NPC显示、对话UI
    ↓ HTTP API
后端层：FastAPI
  - API路由、NPC状态管理、对话处理、日志记录
    ↓
智能体层：HelloAgents
  - 每个NPC = 一个SimpleAgent实例
  - 独立记忆和状态
    ↓
外部服务层：
  - LLM API、Qdrant向量数据库、SQLite数据库
```

## 数据流转
玩家按E键互动 → Godot发送HTTP请求 → FastAPI调用SimpleAgent → Agent从记忆系统检索历史 → LLM生成回复 → 更新NPC状态和好感度 → 记录日志 → 返回Godot显示

## 项目结构
```
Helloagents-AI-Town/
├── helloagents-ai-town/          # Godot项目
│   ├── project.godot
│   ├── scenes/                   # 游戏场景
│   │   ├── main.tscn             # 主场景（办公室）
│   │   ├── player.tscn           # 玩家角色
│   │   ├── npc.tscn              # NPC角色
│   │   └── dialogue_ui.tscn      # 对话UI
│   └── scripts/                  # GDScript脚本
│       ├── main.gd
│       └── ...
└── backend/                      # FastAPI后端
```

## 应用前景
- **教育游戏**：NPC扮演历史人物、科学家进行互动教学
- **虚拟办公室**：NPC扮演同事、导师提供帮助
- **心理健康**：NPC作为陪伴者进行情感交流
- **传统游戏增强**：为游戏NPC增加真正的AI能力

## 教学价值
- Agent记忆系统在游戏场景的具体应用
- 游戏引擎与AI后端的集成
- 多NPC实例的独立状态管理
- 向量数据库+关系数据库的混合存储
- 展示Agent技术在游戏/娱乐领域的潜力
