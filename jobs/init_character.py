"""Create an empty character .blend (scene units/fps from core.json).  args: { out }"""
from lib import scene as SC


def run(args):
    SC.empty_scene()
    SC.save(args["out"])
    return {"outputs": [args["out"]]}
