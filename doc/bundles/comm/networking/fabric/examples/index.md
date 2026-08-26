# fabric 实战示例

* [基础部署脚本](basic-deploy.md) — 使用 Connection 完成拉取代码、安装依赖、重启服务的完整部署流程。
* [多服务器组并行操作](multi-server-group.md) — SerialGroup/ThreadingGroup 批量执行命令、GroupException 部分失败处理、文件批量传输。
* [文件上传下载](file-upload-download.md) — put/get 单文件传输、file-like 对象、路径插值、底层 SFTPClient 操作。
* [跳板机隧道](tunnel-bastion.md) — gateway 跳板机连接、本地/远程端口转发、SSH config 多跳代理、数据库隧道。

```{toctree}
:hidden:
:maxdepth: 7

basic-deploy
file-upload-download
multi-server-group
tunnel-bastion
```
