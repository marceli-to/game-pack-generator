"""Stats of the open .blend (STYLE.md §12 inputs).  args: { spec?: {...} }"""
from lib import measure as M


def run(args):
    m = M.measure(args.get("spec"))
    return {"stats": m}
