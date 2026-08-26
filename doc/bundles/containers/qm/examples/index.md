# QM 示例文档索引

可直接复制使用的实战示例，按从基础到进阶顺序排列：

| 序号 | 示例 | 说明 |
|------|------|------|
| 01 | [创建 QM 虚拟机环境](/bundles/containers/qm/examples/01-vm-setup.md) | 在 QEMU/KVM 虚拟机中安装 AutoSD/CentOS Stream、部署 QM 环境、验证安装、使用 qmctl 工具的完整步骤 |
| 02 | [KVM 子系统使用](/bundles/containers/qm/examples/02-kvm-subsystem.md) | 安装 KVM 子系统、启用嵌套虚拟化、在 QM 内运行硬件加速虚拟机、使用 libvirt 管理 VM、性能对比与排障 |

## 前置依赖

- 示例 01 是基础环境搭建，建议先完成
- 示例 02 依赖示例 01 的 QM 环境，且需要 CPU 支持硬件虚拟化
