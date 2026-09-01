# Echo Kernel 教程更新日志

## 2026-08-22

- 初始版本生成，基于 echo-kernel v0.4.0（兼容 JupyterLite 0.7.0）
- 完成 R→I→E→V→C 五阶段工作流
- 生成 3 个 references 信源文档
- 生成 5 个 concepts 概念文档
- 生成 2 个 examples 示例文档
- 生成根索引、子目录索引和更新日志
- 核心覆盖模块：
  - 插件注册机制（JupyterFrontEndPlugin、Token依赖注入、IKernelSpecs）
  - BaseKernel抽象类与模板方法模式
  - EchoKernel类实现（kernelInfoRequest、executeRequest）
  - Jupyter内核消息协议
  - TypeScript编译与labextension打包
  - hatchling + hatch-jupyter-builder 双构建系统
  - 自定义内核开发完整教程（Uppercase Kernel示例）
