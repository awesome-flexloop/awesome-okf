# 可复用模式（Patterns）

从 repo2jupyterlite 源码中提炼的可复用设计模式，可应用于按需构建服务、静态站点生成器、API客户端和文件发布系统。

## 模式列表

| 模式 | 问题 | 解决方案 | 适用场景 |
|------|------|---------|---------|
| [双重重定向规范化模式](double-redirect-canonicalization.md) | 可变引用URL无法被CDN有效缓存 | 两次重定向：补全路径 → 解析为commit SHA，生成内容寻址URL | 按需构建服务、Git仓库浏览器、内容寻址Web服务 |
| [懒构建触发与缓存雪崩防护模式](lazy-build-cache-stampede.md) | 构建恢复时数十个静态资源请求同时触发构建导致请求风暴 | 仅HTML请求触发构建，非HTML请求返回404 | 按需SSG服务、静态站点预览、JupyterLite/Binder类服务 |
| [双层LRU缓存模式](dual-layer-lru-cache.md) | API速率限制下成功/否定结果需要不同缓存策略 | 成功结果LRU+ETag长缓存，404结果短TTL缓存 | GitHub API客户端、URL元数据获取、任何有限流的API |
| [哨兵文件原子发布模式](sentinel-file-atomic-publish.md) | 多文件构建过程中消费者读到不完整内容 | 所有数据写完后再写空哨兵文件，消费者只检查哨兵 | 静态站点构建、S3批量上传、CI产物发布 |
| [零拷贝构建模式](zero-copy-build.md) | 临时目录构建再拷贝产生双倍I/O开销 | 构建工具直接输出到最终目录，配合哨兵保证原子性 | 本地文件系统构建输出、单实例部署 |
| [ContentProvider责任链模式](content-provider-chain.md) | 多种内容来源的检测和获取逻辑难以扩展 | 有序Provider列表，首个detect()匹配的负责fetch | 多源URL解析、插件化内容获取、消息处理链 |

## 模式协同关系

这些模式在BinderLite中协同工作，形成完整的按需构建系统：

```
用户请求 → 双重重定向规范化模式（生成规范URL）
              ↓
         ContentProvider责任链模式（选择仓库提供者）
              ↓
         双层LRU缓存模式（解析commit SHA，避免API限流）
              ↓
         懒构建触发模式（仅HTML触发构建，防缓存雪崩）
              ↓
         零拷贝构建模式（直接输出到最终目录）
              ↓
         哨兵文件原子发布模式（标记构建完成）
              ↓
         服务静态文件（FileResponse + HTTP缓存协商）
```

## 模式使用建议

1. **按需构建服务**：组合使用双重重定向+懒构建+哨兵文件+双层缓存，这四个模式共同解决"按需构建静态站点"的核心问题
2. **API客户端开发**：双层LRU缓存模式可独立使用，特别适用于GitHub/GitLab等有限流的API
3. **文件发布系统**：哨兵文件+零拷贝模式适用于任何需要原子性发布文件的场景
4. **插件化架构**：ContentProvider责任链是开闭原则的经典实现，适用于任何需要扩展输入类型的系统
5. **防御性设计**：懒构建模式的"仅入口请求触发昂贵操作"思想可推广到任何懒加载/懒计算场景

```{toctree}
:hidden:

content-provider-chain
double-redirect-canonicalization
dual-layer-lru-cache
lazy-build-cache-stampede
sentinel-file-atomic-publish
zero-copy-build
```
