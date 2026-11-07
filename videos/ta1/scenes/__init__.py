"""Scene registry: each module registers draw functions with @scene('id')."""
REG = {}
def scene(sid):
    def deco(fn):
        REG[sid] = fn; return fn
    return deco
from . import s_open, s_c1, s_c2, s_c3, s_c4a, s_c4b, s_c5, s_c6, s_c7, s_c8  # noqa
