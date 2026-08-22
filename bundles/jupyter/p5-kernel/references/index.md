# p5-kernel 信源参考

本目录登记 p5-kernel 教程中所有事实的源码来源，每个 API、类名、方法签名均可通过本目录文件追溯到具体源码位置。

## 信源清单

| 信源文件 | 覆盖范围 | 源码路径 |
|---------|---------|---------|
| [项目元信源](metasource.md) | 版本、依赖、目录结构、构建配置 | `package.json`, `pyproject.toml`, `lerna.json` |
| [P5Kernel 类信源](kernel-source.md) | P5Kernel 类的完整 API、构造选项、私有字段 | `packages/p5-kernel/src/kernel.ts` |
| [P5Executor 类信源](executor-source.md) | P5Executor 类方法、MIME 渲染、内置文档 | `packages/p5-kernel/src/executor.ts` |
| [扩展注册信源](extension-source.md) | JupyterLab 插件注册、CDN 配置、KernelSpec | `packages/p5-kernel-extension/src/index.ts` |
