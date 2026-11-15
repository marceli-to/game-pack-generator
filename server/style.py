"""Load style.json (the machine-readable twin of STYLE.md)."""
from __future__ import annotations

import json
from functools import lru_cache

from .paths import STYLE_JSON


@lru_cache(maxsize=1)
def load_style() -> dict:
    return json.loads(STYLE_JSON.read_text())


def reload_style() -> dict:
    load_style.cache_clear()
    return load_style()


def dump_style(style: dict) -> str:
    """JSON with 2-space indent, but lists of scalars and small flat objects on one line."""
    import json as _json

    def flat(v):
        return not isinstance(v, (dict, list)) or (
            isinstance(v, dict) and all(not isinstance(x, (dict, list)) for x in v.values()) and len(v) <= 6
        )

    def enc(v, ind):
        pad, pad2 = "  " * ind, "  " * (ind + 1)
        if isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
            items = [_json.dumps(x, ensure_ascii=False) for x in v]
            line = "[" + ", ".join(items) + "]"
            if len(line) <= 100:
                return line
            rows, row = [], []
            for it in items:
                if row and len(", ".join(row + [it])) > 96:
                    rows.append(", ".join(row))
                    row = []
                row.append(it)
            rows.append(", ".join(row))
            return "[\n" + ",\n".join(pad2 + r for r in rows) + "\n" + pad + "]"
        if isinstance(v, list):
            return "[\n" + ",\n".join(pad2 + enc(x, ind + 1) for x in v) + "\n" + pad + "]"
        if isinstance(v, dict):
            if flat(v) and ind > 0:
                line = "{ " + ", ".join(f"{_json.dumps(k)}: {_json.dumps(x, ensure_ascii=False)}" for k, x in v.items()) + " }"
                if len(line) <= 110:
                    return line
            return "{\n" + ",\n".join(f"{pad2}{_json.dumps(k)}: {enc(x, ind + 1)}" for k, x in v.items()) + "\n" + pad + "}"
        return _json.dumps(v, ensure_ascii=False)

    return enc(style, 0) + "\n"
