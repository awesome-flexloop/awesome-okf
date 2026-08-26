# DeepGEMM API 参考

本章节提供 DeepGEMM 的完整 API 参考文档。

## 参考文档列表

| 文档 | 说明 |
|---|---|
| [api](/ai/deepseek/deep-gemm/references/api) | 公共 GEMM、Attention、Einsum、Hyperconnection、Layout 等核函数 API |
| [jit-system](/ai/deepseek/deep-gemm/references/jit-system) | JIT 编译系统架构（NVCC/NVRTC 编译器、内核缓存、Include 解析、设备运行时） |
| [mega-moe](/ai/deepseek/deep-gemm/references/mega-moe) | MegaMoE 对称缓冲区 MoE 核函数 API（SymmBuffer、权重变换、前向计算） |
| [runtime-config](/ai/deepseek/deep-gemm/references/runtime-config) | 运行时配置（SM 数量、TC 利用率、PDL、编译维度、Block 对齐、环境变量） |

```{toctree}
:hidden:
:maxdepth: 7

api
jit-system
mega-moe
runtime-config
```
