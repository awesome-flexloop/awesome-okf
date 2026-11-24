"""注册 OpenType Feature File（FEA）词法器。

Pygments 不内置 ``fea`` 词法器，文档中以 ```` ```fea ```` 标注的代码块
会触发 ``misc.highlighting_failure`` 告警。本扩展用 Sphinx 的
``add_lexer`` 注册一个轻量 ``RegexLexer``，使 FEA 片段获得语法高亮，
同时消除该告警类别中的 ``fea`` 来源。

FEA 语法要点（Adobe OpenType Feature File Specification）：
- ``#`` 起注释；
- ``feature`` / ``lookup`` / ``sub`` / ``pos`` 等为关键字；
- 字形名后接 ``'`` 表示该字形在规则中的角色标记；
- ``{ }`` 界定 lookup/feature 块，``[ ]`` 为字形类。
"""
from pygments.lexer import RegexLexer
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Punctuation,
    String,
    Text,
)

KEYWORDS = (
    r"\b(?:feature|lookup|lookupflag|script|language|table|subtable|markClass|"
    r"parameters|exclude_dflt|include_dflt|useExtension|ignore|"
    r"sub|substitute|pos|position|enum|enumerate|rsub|rclt|by|from|through|"
    r"base|ligature|cursive|mark|mkmk|GDEF|GPOS|GSUB|"
    r"SingleSubst|MultipleSubst|AlternateSubst|LigatureSubst|"
    r"SinglePos|PairPos|CursivePos|MarkBasePos|MarkLigPos|MarkMarkPos|"
    r"ContextPos|ChainContextPos|ContextSubst|ChainContextSubst|ReverseChainSingleSubst)\b"
)


class FeaLexer(RegexLexer):
    """OpenType Feature File 的轻量词法器。"""

    name = "OpenType Feature File"
    aliases = ["fea"]
    filenames = ["*.fea"]

    tokens = {
        "root": [
            (r"#[^\n]*", Comment.Single),
            (KEYWORDS, Keyword),
            (r"\b(?:true|false|NULL)\b", Keyword.Constant),
            (r"[A-Za-z_][A-Za-z0-9_.]*'", Name.Tag),
            (r"\\[0-9A-Fa-f]+", Name.Constant),
            (r"@[A-Za-z_][A-Za-z0-9_.]*", Name.Variable),
            (r"[A-Za-z_][A-Za-z0-9_.\-]*", Name),
            (r"-?\d+(?:\.\d+)?", Number),
            (r'"[^"]*"', String),
            (r"[{}\[\]();,<>]", Punctuation),
            (r"[=+\-*/]", Punctuation),
            (r"\s+", Text),
        ]
    }


def setup(app):
    """向 Sphinx 注册 ``fea`` 词法器。"""
    app.add_lexer("fea", FeaLexer)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
