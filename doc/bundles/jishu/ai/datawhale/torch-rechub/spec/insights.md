# 核心洞察 (Insights)

> 基于 facts.md 中编号事实提炼，解释 torch-rechub 的架构设计与关键机制。

## 洞察一：特征描述符驱动的统一模型输入契约

torch-rechub 的所有排序、匹配、多任务模型共享同一套**特征描述符体系**：`SparseFeature`、`SequenceFeature`、`DenseFeature`（F-020~F-023）。模型构造时接收特征对象列表，内部通过 `EmbeddingLayer` 统一管理嵌入表（F-030），forward 时接收 `dict[str, Tensor]` 输入（F-073）。

这一设计带来三个关键效果：
1. **嵌入共享**：通过 `shared_with` 属性，多个特征可复用同一嵌入表（F-020），典型如用户历史物品 ID 与目标物品 ID 共享物品嵌入。
2. **自动维度推断**：embed_dim 为 None 时按 `6*vocab^0.25` 公式自动计算（F-024），降低调参负担。
3. **反射式导出/可视化**：`extract_feature_info` 通过遍历模型上约定命名的属性（features、deep_features、user_features、history_features 等12个属性名，F-173）自动提取特征元信息，使 ONNX 导出和模型可视化无需模型侧任何配合代码（F-174、F-190）。

## 洞察二：四类 Trainer 按任务范式正交分工，共享训练骨架

Trainer 层不是单一巨型类，而是按推荐系统任务范式拆分为四个独立类（F-110~F-123）：

| Trainer | 适用场景 | 输入批次格式 | 损失模式 |
|---------|---------|-------------|---------|
| `CTRTrainer` | 单任务二分类（CTR预估） | `(x_dict, y)` | BCELoss，支持模型返回附加损失 |
| `MatchTrainer` | 双塔召回/匹配 | `(x_dict, y)` 或成对 | point/pair/list-wise 三模式 + in-batch负采样 |
| `MTLTrainer` | 多任务学习 | `(x_dict, ys)` | 每任务独立损失，支持 uwl/metabalance/gradnorm 自适应加权 |
| `SeqTrainer` | 序列生成（HSTU） | `(tokens, positions, time_diffs, target)` | 自回归 CrossEntropy/NCE |

尽管分工不同，它们共享相同的骨架：优化器/调度器配置、EarlyStopper 早停、DataParallel 多GPU、RegularizationLoss 正则化、model_logger 实验跟踪（F-125~F-128），且全部提供 `export_onnx()` 和 `visualization()` 方法（F-124）。这种"骨架一致、范式可插拔"的设计让新增任务类型时只需关注损失计算和批次解包逻辑。

## 洞察三：双塔模型的 mode 切换机制实现训练-导出一体化

匹配模型（如 DSSM）在训练时需要计算 user-item 相似度分数，而在服务时需要分别导出 user 塔和 item 塔独立推理。torch-rechub 通过一个简洁的 `mode` 属性解决了这一矛盾（F-083）：

- `mode=None`：forward 返回完整相似度分数（训练用）
- `mode="user"`：forward 只返回 user 塔嵌入（导出/推理用）
- `mode="item"`：forward 只返回 item 塔嵌入（导出/推理用）

这一机制贯穿到 ONNX 导出：`MatchTrainer.export_onnx("user.onnx", mode="user")` 导出时临时切换模型 mode，导出后自动恢复（F-177、F-082）。`inference_embedding` 方法也依赖此模式批量生成用户/物品嵌入向量（F-116）。这避免了为训练和服务维护两套模型代码。

## 洞察四：非侵入式 ONNX 导出通过 ONNXWrapper 桥接 dict 输入

PyTorch ONNX 导出器要求位置参数输入，但 torch-rechub 模型统一使用 dict 输入。`ONNXWrapper`（F-172）通过将位置参数重新组装为 dict 来桥接这一差异，且完全不需要修改模型代码。导出流程为：

1. `extract_feature_info` 反射获取特征列表和顺序（F-173）
2. `generate_dummy_input` 按特征类型生成正确形状的 dummy tensor（F-174）
3. `ONNXWrapper` 将位置 args 映射回 dict
4. 优先尝试 dynamo 导出器，失败自动回退 legacy（F-176）
5. 动态轴配置支持动态 batch 和序列长度（F-175）

配套的 `quantize_model` 提供 INT8 动态量化和 FP16 转换（F-180~F-182），形成完整的"训练→导出→量化"部署链路。

## 洞察五：多任务学习的专家-门控架构族系

多任务模型形成一个从简到繁的清晰谱系（F-090~F-094）：

- `SharedBottom`：共享底层 MLP + 任务独立塔
- `MMOE`：n_expert 个共享专家 + n_task 个 softmax 门控（F-091）
- `PLE`：多层 CGC，每层含 task-specific experts 和 shared experts，通过门控选择性融合（F-093、F-094）
- `ESMM`：基于任务依赖关系（CTCVR = CTR × CVR）的特殊损失计算（F-095）
- `AITM`：自适应信息迁移模块

配合 `MTLTrainer` 的三种自适应损失加权（uwl 不确定性加权、MetaBalance 梯度平衡、GradNorm 梯度归一化，F-118），以及 `shared_task_layers` 对共享/任务参数的精确拆分（F-131），构成了完整的多任务建模工具链。
