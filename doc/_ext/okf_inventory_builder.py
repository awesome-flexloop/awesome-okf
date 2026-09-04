"""Sphinx extension: register a lightweight OKFInventoryBuilder(name='inventory').

Why a separate extension instead of conf.py `def setup(app)`:
  Sphinx application.py init order:
    1) read conf.py (config values populated incl. extensions list)
    2) setup_extension for all builtin_extensions (html/dummy/etc. builders registered)
    3) setup_extension for all self.config.extensions (user extensions — THIS step)
    4) preload_builder(buildername) — looks up name in registry.builders
    5) self.config.setup(self)  ←  conf.py `def setup` runs HERE, TOO LATE for step 4

  So builder registration must happen in an extension referenced by the
  `extensions` list. This tiny module is that extension.

Usage (conf.py):
    extensions = [..., "_ext.okf_inventory_builder"]
    # and doc/ directory must be on sys.path (ROOT/doc inserted at conf.py L8)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx.builders import Builder
from sphinx.util.inventory import InventoryFile

if TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx


class OKFInventoryBuilder(Builder):
    name = "inventory"
    format = "inventory"
    epilog = "OKF inventory builder: objects.inv only (no HTML rendering)"
    allow_parallel = True

    def init(self) -> None:  # pragma: no cover - trivial
        pass

    def get_outdated_docs(self) -> set[str]:
        return self.env.found_docs

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return f"{docname}.html"

    def write_doc(self, docname: str, doctree: "nodes.document") -> None:  # pragma: no cover
        pass

    def finish(self) -> None:
        InventoryFile.dump(self.outdir / "objects.inv", self.env, self)


def setup(app: "Sphinx"):
    app.add_builder(OKFInventoryBuilder, override=True)
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
