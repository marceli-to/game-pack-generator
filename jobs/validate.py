"""Check the open .blend against every rule in style.json (STYLE.md §12).

args: { spec?: {...} }   -> { ok, valid, hard: [...], soft: [...], info: [...], stats }
`ok` means the job ran; `valid` means no hard violations.
"""
from lib import measure as M


def run(args):
    spec = args.get("spec")
    m = M.measure(spec)
    v = M.violations(m, spec)
    return {"valid": not v["hard"], **v, "stats": m}
