---
type: spec
title: "事实清单 (Facts)"
---

# 事实清单 (Facts)

> 采集自 torch-rechub v0.8.0 源码，零推测。每条事实可追溯到具体源文件。

## 项目元信息

- F-001: 项目名称为 `torch-rechub`，版本 `0.8.0`，许可证 MIT，作者 Datawhale。来源：`pyproject.toml`
- F-002: 项目描述为 "A lightweight, efficient, and easy-to-use PyTorch recommendation system framework."。来源：`pyproject.toml`
- F-003: 核心运行依赖为 `torch>=1.10.0`、`numpy>=1.19.0`、`pandas>=1.2.0`、`scikit-learn>=0.24.0`、`tqdm>=4.60.0`。来源：`pyproject.toml`
- F-004: 可选依赖组包括 annoy、faiss、milvus、generative、bigdata、onnx、visualization、tracking、test、benchmark、all。来源：`pyproject.toml`
- F-005: Python 版本要求 `>=3.9`。来源：`pyproject.toml`
- F-006: 顶层包 `torch_rechub` 导出子模块 `basic`、`models`、`trainers`、`utils`。来源：`torch_rechub/__init__.py`
- F-007: GitHub 仓库地址为 https://github.com/datawhalechina/torch-rechub。来源：`pyproject.toml`

## 包结构

- F-010: `torch_rechub/basic/` 包含 activation.py、callback.py、features.py、initializers.py、layers.py、loss_func.py、metaoptimizer.py、metric.py、tracking.py。来源：目录扫描
- F-011: `torch_rechub/models/` 下有四个子包：`ranking/`、`matching/`、`multi_task/`、`generative/`。来源：目录扫描
- F-012: `torch_rechub/trainers/` 包含 ctr_trainer.py、match_trainer.py、mtl_trainer.py、seq_trainer.py、rqvae_trainer.py。来源：目录扫描
- F-013: `torch_rechub/data/` 包含 dataset.py、convert.py，提供 Parquet 流式数据集。来源：目录扫描
- F-014: `torch_rechub/serving/` 包含 base.py、annoy.py、faiss.py、milvus.py，提供向量索引构建器。来源：目录扫描
- F-015: `torch_rechub/utils/` 包含 data.py、match.py、model_utils.py、mtl.py、onnx_export.py、quantization.py、visualization.py、hstu_utils.py。来源：目录扫描

## 特征系统 (basic/features.py)

- F-020: `SparseFeature` 类表示稀疏类别特征，属性包括 name、vocab_size、embed_dim、shared_with、padding_idx、initializer。来源：`basic/features.py:42`
- F-021: `SequenceFeature` 类表示序列/多热特征，额外属性 pooling（支持 "mean"/"sum"/"concat"）。来源：`basic/features.py:5`
- F-022: `DenseFeature` 类表示稠密数值特征，属性 name、embed_dim（默认1）。来源：`basic/features.py:74`
- F-023: SparseFeature 和 SequenceFeature 在 embed_dim 为 None 时调用 `get_auto_embedding_dim(vocab_size)` 自动计算维度。来源：`basic/features.py:25`
- F-024: `get_auto_embedding_dim` 公式为 `floor(6 * num_classes^0.25)`，源自 DCN 论文。来源：`utils/data.py:86`
- F-025: 特征对象通过 `get_embedding_layer()` 方法创建 `nn.Embedding` 层。来源：`basic/features.py:36`

## 基础层 (basic/layers.py)

- F-030: `EmbeddingLayer` 类管理所有特征的嵌入表，使用 `nn.ModuleDict` 存储，通过 `embed_dict` 属性访问。来源：`basic/layers.py:33`
- F-031: `EmbeddingLayer.forward(x, features, squeeze_dim=False)` 接收 dict 输入，返回稀疏嵌入和稠密值。squeeze_dim=True 时将嵌入展平拼接。来源：`basic/layers.py:77`
- F-032: `InputMask` 类根据 padding_idx 或 -1 生成掩码。来源：`basic/layers.py:130`
- F-033: 池化层包括 `AveragePooling`、`SumPooling`、`ConcatPooling`。来源：`basic/layers.py:192-251`
- F-034: `MLP` 类是多层感知机，每层包含 Linear→BatchNorm1d→activation→Dropout，可选 output_layer 追加最终 Linear(...,1)。来源：`basic/layers.py:254`
- F-035: `FM` 类实现因子分解机二阶交互。来源：`basic/layers.py:295`
- F-036: `LR` 类实现逻辑回归（线性层+可选sigmoid）。来源：`basic/layers.py:164`
- F-037: `PredictionLayer` 根据 task_type（"classification"用sigmoid，"regression"直接返回）输出预测。来源：`basic/layers.py:12`
- F-038: `CIN` 类实现压缩交互网络（xDeepFM）。来源：`basic/layers.py:322`
- F-039: `CrossNetwork`、`CrossNetV2`、`CrossNetMix` 实现 DCN 系列交叉网络。来源：`basic/layers.py:390-506`
- F-040: `SENETLayer` 实现 SENet 特征门控。来源：`basic/layers.py:509`
- F-041: `BiLinearInteractionLayer` 实现 FFM 风格双线性交互。来源：`basic/layers.py:532`
- F-042: `MultiInterestSA` 实现自注意力多兴趣提取（ComiRec）。来源：`basic/layers.py:568`
- F-043: `CapsuleNetwork` 实现胶囊网络多兴趣提取（MIND/ComiRec），支持 bilinear_type 0/1/2。来源：`basic/layers.py:612`
- F-044: `FFM` 类实现域感知因子分解机。来源：`basic/layers.py:714`
- F-045: `CEN` 类实现 Compose-Excitation Network（FAT-DeepFFM）。来源：`basic/layers.py:749`
- F-046: `HSTULayer` 和 `HSTUBlock` 实现 HSTU 序列转换单元，含 SiLU 激活、相对位置时间偏置、因果掩码。来源：`basic/layers.py:792-970`
- F-047: `InteractingLayer` 实现 AutoInt 的多头自注意力交互层。来源：`basic/layers.py:973`
- F-048: `ActivationUnit` 类（在 ranking/din.py 中）实现 DIN 的目标注意力，拼接 [target, history, target-history, target*history]。来源：`models/ranking/din.py:58`

## 激活函数与初始化 (basic/)

- F-050: `Dice` 激活函数来自 DIN 论文，含可学习 alpha 参数。来源：`basic/activation.py:5`
- F-051: `activation_layer` 工厂函数支持 sigmoid、relu、dice、prelu、softmax、leakyrelu。来源：`basic/activation.py:28`
- F-052: 嵌入初始化器包括 `RandomNormal`、`RandomUniform`、`XavierNormal`、`XavierUniform`、`Pretrained`。来源：`basic/initializers.py`
- F-053: 默认初始化器为 `RandomNormal(0, 0.0001)`。来源：`basic/features.py:21`

## 损失函数 (basic/loss_func.py)

- F-060: `RegularizationLoss` 统一实现 L1/L2 正则，区分 embedding 参数和 dense 参数，跳过归一化层参数。来源：`basic/loss_func.py:6`
- F-061: `BPRLoss` 实现 Bayesian Personalized Ranking 成对损失。来源：`basic/loss_func.py:95`
- F-062: `HingeLoss` 实现合页损失，可选基于物品数的对数排名加权。来源：`basic/loss_func.py:71`
- F-063: `NCELoss` 实现噪声对比估计损失，支持 temperature 和 ignore_index。来源：`basic/loss_func.py:110`
- F-064: `InBatchNCELoss` 实现批内 NCE 损失，接收 user embeddings、item embeddings、targets。来源：`basic/loss_func.py:180`

## 排序模型 (models/ranking/)

- F-070: 排序模型包括 `WideDeep`、`DeepFM`、`DCN`、`DCNv2`、`EDCN`、`AFM`、`FiBiNet`、`DeepFFM`、`FatDeepFFM`、`BST`、`DIN`、`DIEN`、`AutoInt`。来源：`models/ranking/__init__.py`
- F-071: `DeepFM` 构造参数为 `(deep_features, fm_features, mlp_params)`，由 LR（一阶）+ FM（二阶）+ MLP（深度）三部分组成，输出 sigmoid。来源：`models/ranking/deepfm.py:14`
- F-072: `DIN` 构造参数为 `(features, history_features, target_features, mlp_params, attention_mlp_params)`，使用 ActivationUnit 做目标注意力，MLP 激活用 dice。来源：`models/ranking/din.py:16`
- F-073: 排序模型的 forward 方法接收 `x: dict`，返回 sigmoid 后的预测值。来源：`models/ranking/deepfm.py:34`

## 匹配/召回模型 (models/matching/)

- F-080: 匹配模型包括 `DSSM`、`FaceBookDSSM`、`YoutubeDNN`、`YoutubeSBC`、`MIND`、`GRU4Rec`、`NARM`、`SASRec`、`SINE`、`STAMP`、`ComirecDR`、`ComirecSA`。来源：`models/matching/__init__.py`
- F-081: `DSSM` 构造参数为 `(user_features, item_features, user_params, item_params, temperature=1.0)`，含 user_mlp 和 item_mlp 双塔。来源：`models/matching/dssm.py:16`
- F-082: `DSSM` 暴露 `user_tower(x)` 和 `item_tower(x)` 方法，分别返回 L2 归一化的嵌入。来源：`models/matching/dssm.py:54-72`
- F-083: `DSSM` 有 `mode` 属性，设置为 "user"/"item" 时 forward 只返回对应塔嵌入，None 时返回内积 sigmoid 分数。来源：`models/matching/dssm.py:38-52`
- F-084: `ComirecSA` 使用 `MultiInterestSA`，`ComirecDR` 使用 `CapsuleNetwork`（bilinear_type=2）。来源：`basic/layers.py:568,612`

## 多任务模型 (models/multi_task/)

- F-090: 多任务模型包括 `SharedBottom`、`ESMM`、`MMOE`、`PLE`、`AITM`。来源：`models/multi_task/__init__.py`
- F-091: `MMOE` 构造参数为 `(features, task_types, n_expert, expert_params, tower_params_list)`，含 n_expert 个专家 MLP、n_task 个门控 MLP（softmax激活）、n_task 个塔。来源：`models/multi_task/mmoe.py:15`
- F-092: `MMOE.forward` 返回 `torch.cat(ys, dim=1)`，形状 [batch_size, n_task]。来源：`models/multi_task/mmoe.py:39-58`
- F-093: `PLE` 构造参数为 `(features, task_types, n_level, n_expert_specific, n_expert_shared, expert_params, tower_params_list)`，由多层 `CGC`（Customized Gate Control）堆叠。来源：`models/multi_task/ple.py:15`
- F-094: `CGC` 类包含 task-specific experts、shared experts、task-specific gates，最后一层不包含 shared gate。来源：`models/multi_task/ple.py:60`
- F-095: `ESMM` 在 MTLTrainer 中被特殊处理，只计算 ctr 和 ctcvr 任务的损失（loss_list[1:]）。来源：`trainers/mtl_trainer.py:119`

## 生成式模型 (models/generative/)

- F-100: 生成式模型包括 `HSTUModel`、`HLLMModel`、`RQVAEModel`，`TIGERModel` 为延迟导入（需 transformers）。来源：`models/generative/__init__.py`
- F-101: `HSTUModel` 由 `HSTUBlock` 堆叠构成，forward 接收 `(seq_tokens, seq_time_diffs)`，输出 (B, L, V) logits。来源：`basic/layers.py:919`，`trainers/seq_trainer.py:212`

## Trainer 系统

- F-110: `CTRTrainer` 用于单任务排序，默认损失 BCELoss，默认评估 roc_auc_score。来源：`trainers/ctr_trainer.py:11,68-69`
- F-111: `CTRTrainer` 构造参数包括 model、optimizer_fn、optimizer_params、regularization_params、scheduler_fn、scheduler_params、n_epoch、earlystop_patience、device、gpus、loss_mode、model_path、model_logger。来源：`trainers/ctr_trainer.py:33`
- F-112: `CTRTrainer.fit(train_dataloader, val_dataloader=None)` 执行训练循环，早停后保存 model.pth。来源：`trainers/ctr_trainer.py:110`
- F-113: `CTRTrainer` 支持 `loss_mode=True`（模型只返回预测）和 `loss_mode=False`（模型返回 (y_pred, other_loss)）。来源：`trainers/ctr_trainer.py:67,86-91`
- F-114: `MatchTrainer` 支持三种训练模式：mode=0 point-wise（BCELoss/CrossEntropyLoss）、mode=1 pair-wise（BPRLoss）、mode=2 list-wise（CrossEntropyLoss）。来源：`trainers/match_trainer.py:84-92`
- F-115: `MatchTrainer` 支持 in-batch negative sampling，要求模型有 `user_tower` 和 `item_tower` 方法。来源：`trainers/match_trainer.py:71-78`
- F-116: `MatchTrainer` 有 `inference_embedding(model, mode, data_loader, model_path)` 方法，mode 为 "user"/"item"。来源：`trainers/match_trainer.py:250`
- F-117: `MTLTrainer` 构造参数含 `task_types` 列表（"classification"/"regression"），使用 `get_loss_func` 和 `get_metric_func` 按任务类型获取损失和指标。来源：`trainers/mtl_trainer.py:34,92-93`
- F-118: `MTLTrainer` 支持三种自适应损失加权方法：uwl（Uncertainty Weighting）、metabalance、gradnorm。来源：`trainers/mtl_trainer.py:63-86`
- F-119: `MTLTrainer.fit(train_dataloader, val_dataloader, mode='base', seed=0)` 必须提供 val_dataloader，保存 model_{mode}_{seed}.pth。来源：`trainers/mtl_trainer.py:165,209`
- F-120: `SeqTrainer` 用于 HSTU 等序列生成模型，默认损失 CrossEntropyLoss，也支持 NCE loss（loss_type='nce'）。来源：`trainers/seq_trainer.py:82-90`
- F-121: `SeqTrainer` 数据批次为 `(seq_tokens, seq_positions, seq_time_diffs, targets)` 四元组。来源：`trainers/seq_trainer.py:204`
- F-122: `SeqTrainer._compute_next_token_loss` 实现自回归下一 token 预测，左填充感知。来源：`trainers/seq_trainer.py:169`
- F-123: RQVAE 的 Trainer 类名为 `Trainer`（位于 rqvae_trainer.py），评估指标为 collision_rate。来源：`trainers/rqvae_trainer.py:9`
- F-124: 所有主 Trainer 都暴露 `export_onnx(...)` 和 `visualization(...)` 方法。来源：各 trainer 文件
- F-125: 所有 Trainer 使用 `EarlyStopper` 做早停，基于验证集 AUC 提升。来源：`basic/callback.py:4`
- F-126: `EarlyStopper` 属性包括 best_auc、best_weights、trial_counter、patience。来源：`basic/callback.py:11`
- F-127: Trainer 支持多 GPU DataParallel，当 gpus 列表长度>1 时自动包装。来源：各 trainer 文件
- F-128: Trainer 支持 `model_logger` 参数，可为单个 logger 或列表，通过 `_iter_loggers()` 统一迭代。来源：各 trainer 文件

## 多任务优化器 (basic/metaoptimizer.py, utils/mtl.py)

- F-130: `MetaBalance` 优化器继承 `torch.optim.Optimizer`，通过梯度缩放平衡多任务梯度，参数 relax_factor（默认0.7）、beta（默认0.9）。来源：`basic/metaoptimizer.py:9`，`utils/mtl.py:40`
- F-131: `shared_task_layers(model)` 函数将模型参数拆分为共享层和任务层，支持 SharedBottom、MMOE、PLE、AITM。来源：`utils/mtl.py:7`
- F-132: `gradnorm(loss_list, loss_weight, share_layer, initial_task_loss, alpha)` 实现 GradNorm 自适应加权。来源：`utils/mtl.py:103`

## 数据管道

- F-140: `TorchDataset` 继承 `torch.utils.data.Dataset`，封装 `(x_dict, y)`，`__getitem__` 返回 `({k: v[index]}, y[index])`。来源：`utils/data.py:14`
- F-141: `PredictDataset` 用于推理，只含 x_dict，无标签。来源：`utils/data.py:28`
- F-142: `DataGenerator` 封装 train/val/test DataLoader 生成，支持 split_ratio 自动切分。来源：`utils/data.py:61`
- F-143: `MatchDataGenerator` 为匹配模型生成 train_dataloader、test_dataloader、item_dataloader。来源：`utils/data.py:41`
- F-144: `SeqDataset` 返回 `(seq_tokens, seq_positions, seq_time_diffs, target)` 四元组。来源：`utils/data.py:396`
- F-145: `SequenceDataGenerator` 封装 SeqDataset，支持 split_ratio 切分。来源：`utils/data.py:455`
- F-146: `EmbDataset` 加载 .npy 或 .pt 嵌入文件。来源：`utils/data.py:544`
- F-147: `TigerSeqDataset` 用于 TIGER 生成式检索模型，处理语义 ID 序列。来源：`utils/data.py:599`
- F-148: `ParquetIterableDataset`（data/dataset.py）流式读取 Parquet 文件，支持多 worker 分片，输出 dict[str, Tensor]。来源：`data/dataset.py:17`
- F-149: `pa_array_to_tensor` 将 PyArrow Array 转为 PyTorch Tensor，支持标量和定长列表。来源：`data/convert.py:10`
- F-150: `df_to_dict` 将 pandas DataFrame 转为 `{col: np.array}` 字典。来源：`utils/data.py:219`
- F-151: `generate_seq_feature` 为排序模型生成序列特征和负样本，滑动窗口构造。来源：`utils/data.py:122`
- F-152: `generate_seq_feature_match` 为匹配模型生成序列特征，支持 point-wise/pair-wise/list-wise 三种模式。来源：`utils/match.py:164`
- F-153: `gen_model_input` 合并 user_profile/item_profile，填充 hist_ 和 tag_ 前缀序列列。来源：`utils/match.py:32`
- F-154: `pad_sequences` 等价于 Keras 的 pad_sequences，支持 pre/post 填充和截断。来源：`utils/data.py:245`
- F-155: `negative_sample` 支持4种负采样方法：0随机、1 word2vec频次（0.75次方）、2 log(count+1)、3 腾讯 RALM。来源：`utils/match.py:61`
- F-156: `neg_sample`（utils/data.py）从非点击历史中随机采样一个负样本。来源：`utils/data.py:238`

## 实验跟踪 (basic/tracking.py)

- F-160: `BaseLogger` 抽象基类定义 `log_metrics`、`log_hyperparams`、`finish` 接口。来源：`basic/tracking.py:12`
- F-161: 提供三种 logger 实现：`WandbLogger`、`SwanLabLogger`、`TensorBoardXLogger`。来源：`basic/tracking.py:56,106,153`

## ONNX 导出

- F-170: `ONNXExporter` 类（utils/onnx_export.py）是 ONNX 导出主类，构造参数 `(model, device='cpu')`。来源：`utils/onnx_export.py:79`
- F-171: `ONNXExporter.export(output_path, mode=None, dummy_input=None, batch_size=2, seq_length=10, opset_version=14, dynamic_batch=True, verbose=False, onnx_export_kwargs=None)` 执行导出，返回 bool。来源：`utils/onnx_export.py:129`
- F-172: `ONNXWrapper` 将 dict 输入模型包装为位置参数模型，兼容 ONNX 要求。来源：`utils/onnx_export.py:26`
- F-173: `extract_feature_info(model)` 通过反射从模型属性（features、deep_features、user_features 等）提取特征列表。来源：`utils/model_utils.py:28`
- F-174: `generate_dummy_input(features, batch_size, seq_length, device)` 根据特征类型生成 dummy 张量：SparseFeature→[B]、SequenceFeature→[B,L]、DenseFeature→[B,embed_dim]。来源：`utils/model_utils.py:112`
- F-175: `generate_dynamic_axes` 生成 ONNX dynamic_axes 配置，batch 维和序列维动态。来源：`utils/model_utils.py:190`
- F-176: ONNX 导出器优先尝试 dynamo 导出器，失败后自动回退到 legacy 导出器。来源：`utils/onnx_export.py:273-286`
- F-177: 双塔模型导出支持 mode="user" / mode="item" 分别导出用户塔和物品塔。来源：`utils/onnx_export.py:191-198`
- F-178: `SeqTrainer.export_onnx` 直接使用位置参数 (seq_tokens, seq_time_diffs)，不经过 ONNXWrapper。来源：`trainers/seq_trainer.py:267`
- F-179: RQVAE Trainer 的 `export_onnx` 导出双输出（output 重建 + indices 语义码）。来源：`trainers/rqvae_trainer.py:238`

## ONNX 量化 (utils/quantization.py)

- F-180: `quantize_model(input_path, output_path, mode='int8', ...)` 支持 INT8 动态量化和 FP16 转换。来源：`utils/quantization.py:26`
- F-181: INT8 模式使用 `onnxruntime.quantization.quantize_dynamic`，权重类型支持 qint8/quint8。来源：`utils/quantization.py:77-110`
- F-182: FP16 模式使用 `onnxconverter_common.float16.convert_float_to_float16`，keep_io_types=True 保持输入输出为 float32。来源：`utils/quantization.py:112-126`

## 模型可视化 (utils/visualization.py)

- F-190: `visualize_model` 函数基于 torchview.draw_graph，自动提取模型特征生成 dummy input。来源：`utils/visualization.py:86`
- F-191: `display_graph` 在 Jupyter 中展示 ComputationGraph。来源：`utils/visualization.py:46`
- F-192: 可视化支持 save_path 保存为 .pdf/.svg/.png，可设置 dpi。来源：`utils/visualization.py:236-252`

## 向量检索服务 (serving/)

- F-200: `BaseBuilder` 抽象基类定义 `from_embeddings(embeddings)` 和 `from_index_file(index_file)` 两个上下文管理器方法。来源：`serving/base.py:11`
- F-201: `BaseIndexer` 抽象基类定义 `query(embeddings, top_k)` 和 `save(file_path)` 方法。来源：`serving/base.py:68`
- F-202: `builder_factory(model, **builder_config)` 工厂函数支持 "annoy"、"faiss"、"milvus" 三种后端。来源：`serving/__init__.py:12`
- F-203: `AnnoyBuilder` 参数 d（维度）、metric（angular/euclidean/dot）、n_trees、threads、searchk。来源：`serving/annoy.py:30`
- F-204: `FaissBuilder`、`MilvusBuilder` 分别实现 FAISS 和 Milvus 后端。来源：serving 目录
- F-205: `utils/match.py` 中另有旧版 `Annoy`、`Faiss`、`Milvus` 类，提供 fit/query 接口。来源：`utils/match.py:252-497`

## 评估指标 (basic/metric.py)

- F-210: `auc_score` 封装 sklearn roc_auc_score。来源：`basic/metric.py:20`
- F-211: `gauc_score` 计算分组 AUC（按用户分组加权平均）。来源：`basic/metric.py:47`
- F-212: `topk_metrics(y_true, y_pred, topKs)` 返回 NDCG、MRR、Recall、Hit、Precision 五个指标。来源：`basic/metric.py:112`
- F-213: 便捷函数 `ndcg_score`、`hit_score`、`mrr_score`、`recall_score`、`precision_score` 封装 topk_metrics。来源：`basic/metric.py:77-109`
- F-214: `log_loss` 计算对数损失。来源：`basic/metric.py:198`
- F-215: 超越准确率指标包括 `diversity_score`（ILD）、`coverage_score`（目录覆盖率）、`novelty_score`（自信息）。来源：`basic/metric.py:203,254,280`
- F-216: `get_loss_func(task_type)` 返回 BCELoss（classification）或 MSELoss（regression）。来源：`utils/data.py:104`
- F-217: `get_metric_func(task_type)` 返回 roc_auc_score 或 mean_squared_error。来源：`utils/data.py:113`

## 批内负采样 (utils/match.py)

- F-220: `inbatch_negative_sampling(scores, neg_ratio=None, hard_negative=False, generator=None)` 从相似度矩阵采样负例索引，支持 hard negative（top-k）。来源：`utils/match.py:104`
- F-221: `gather_inbatch_logits(scores, neg_indices)` 从分数矩阵中提取正例对角线和负例分数，返回 [B, 1+K] logits。来源：`utils/match.py:150`

## 类型定义

- F-230: `FilePath = Union[str, os.PathLike]` 定义在 `torch_rechub/types.py`。来源：`types.py:5`
