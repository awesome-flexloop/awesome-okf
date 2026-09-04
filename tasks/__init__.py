"""Invoke 任务命名空间入口——组装 docs 和 gates 两个子模块。

CLI 向后兼容：
    invoke build / invoke clean / invoke browse / invoke tree / invoke doctest
    invoke gates.utf8 / invoke gates.toctrees / invoke gates.all
"""
from invoke import Collection

from . import docs, gates

ns = Collection()

# 文档任务提升到根命名空间，保持 `invoke build` 等命令向后兼容
ns.add_task(docs.build, default=True)
ns.add_task(docs.clean)
ns.add_task(docs.browse)
ns.add_task(docs.tree)
ns.add_task(docs.doctest)
ns.add_task(docs.build_invs)

# 质量门任务作为子集合：invoke gates.utf8 / invoke gates.toctrees
ns.add_collection(Collection.from_module(gates))

ns.configure(
    {
        "sphinx": {
            "source": "doc",
            "target": "_build/html",
            "target_file": "index.html",
        }
    }
)
