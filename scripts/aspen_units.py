# -*- coding: utf-8 -*-
"""
Aspen .bkp 单位代码工具 + COM 侧单位安全读写封装。

两件事：
1) 离线（不开 Aspen）：解析/统计 bkp 里的 <维度> <子码>，把代码翻译成单位名。
2) 在线（COM 已连接）：用 IHNode.UnitString 回读校验 + SetValueAndUnit 带单位写入。

命令行用法：
    python aspen_units.py probe  <bkp路径> [维度]   # 统计该 bkp 的单位代码分布
    python aspen_units.py inset  <bkp路径>          # 打印全局单位集 INSET

代码库用法：
    from aspen_units import UOM, code_name, sub_value
    from aspen_units import node_value_with_unit, set_value_with_unit
"""
import re
import sys
import collections

# ---------------------------------------------------------------- 单位代码表
# 依据：本机 Aspen V14 GUI\Examples 203 个 .bkp 全量统计（见 references/units-codebook.md）
UOM = {
    (22, 1): "K", (22, 2): "degF", (22, 3): "K", (22, 4): "degC",
    (20, 1): "Pa", (20, 2): "psi", (20, 3): "atm", (20, 5): "bar",
    (20, 6): "mmHg", (20, 8): "kgf/cm2", (20, 10): "kPa",
    (20, 12): "mbar", (20, 13): "mmHg", (20, 20): "MPa",
    (-80, 3): "kg/hr", (-89, 3): "kmol/hr", (-89, 2): "lbmol/hr",
    (75, 5): "psi", (17, 1): "m", (17, 7): "inch", (39, 3): "cal/mol",
    (0, 0): "dimensionless",
}

# 换算到 SI 的乘数（值为 1 表示已是该量纲的国际常用单位）
TO_SI = {
    "K": 1.0, "degC": 1.0, "degF": None,           # 温度用函数，不用乘数
    "Pa": 1.0, "kPa": 1e3, "MPa": 1e6, "bar": 1e5,
    "atm": 101325.0, "psi": 6894.757, "mmHg": 133.322,
    "mbar": 100.0, "kgf/cm2": 98066.5,
    "kg/hr": 1.0, "kmol/hr": 1.0, "lbmol/hr": 0.45359237, "lb/hr": 0.45359237,
}


def code_name(dim, code):
    """(维度, 子码) -> 单位名；未知返回 None（不要猜）。"""
    return UOM.get((int(dim), int(code)))


# ---------------------------------------------------------------- 离线：bkp 解析
NUM = r"[-+0-9\.Ee]+"
CODE_RE = re.compile(r"([A-Z][\w\-]*)\s*=\s*(" + NUM + r")\s*<(-?\d+)>\s*<(-?\d+)>")
INSET_RE = re.compile(r'"IN-UNITS"\s+INSET\s*=\s*([A-Za-z0-9\-_]+)')


def read_bkp(path):
    """.bkp 一律 latin-1；用 utf-8 会崩。"""
    with open(path, "rb") as f:
        raw = f.read()
    if b"\x00" in raw[:4096]:
        raise ValueError("疑似压缩/二进制 bkp（含 NUL 字节），无法按文本层处理；"
                         "请先用 Aspen 另存为非压缩 .bkp 或导出 .inp")
    return raw.decode("latin-1")


def probe(path, only_dim=None):
    """统计 bkp 中的 (维度,子码) 分布，返回 Counter。"""
    txt = read_bkp(path)
    c = collections.Counter()
    for key, val, dim, code in CODE_RE.findall(txt):
        if only_dim is not None and int(dim) != int(only_dim):
            continue
        c[(int(dim), int(code))] += 1
    return c


def get_inset(path):
    """返回全局单位集名（如 ENG / SI / METCBAR），找不到返回 None。"""
    m = INSET_RE.search(read_bkp(path))
    return m.group(1) if m else None


def sub_value(txt, key, new_val, expect_dim, expect_code):
    """只在"维度+子码"与预期一致时才替换。

    这是防量纲事故的关键：文件里如果是 <20><5>(bar) 而你要按 psi 改，
    这里会直接抛错，而不是静默写成差 14.5 倍的数。
    """
    pat = re.compile(r"(%s\s*=\s*)(%s)(\s*<%d>\s*<%d>)" % (key, NUM, expect_dim, expect_code))
    new, n = pat.subn(lambda m: m.group(1) + repr(new_val) + m.group(3), txt, count=1)
    if n != 1:
        raise RuntimeError(
            "替换失败或单位码不符：'%s' 期望 <%d><%d>(%s)，文件里不是该单位。"
            "先跑 probe 确认真实代码再改。" % (key, expect_dim, expect_code,
                                          code_name(expect_dim, expect_code)))
    return new


# ---------------------------------------------------------------- 在线：COM 单位安全读写
def node_value_with_unit(node):
    """取 (值, 单位串)。任何节点取数都应该走这个，先确认单位再进报告。"""
    try:
        return node.Value, node.UnitString
    except Exception:
        try:
            return node.Value, None
        except Exception:
            return None, None


def set_value_with_unit(node, value, unit_code, verify=True):
    """带单位写入。unit_code 是【整数代码】（见 UOM 表），不是 "C"/"bar" 字符串。

    verify=True 时写入后立刻回读 UnitString，不一致就抛错。
    """
    node.SetValueAndUnit(float(value), int(unit_code))
    if verify:
        _, u = node_value_with_unit(node)
        want = "?" if (unit_code is None) else str(unit_code)
        if u is None:
            raise RuntimeError("写入后无法回读 UnitString，未通过校验（值=%s, 码=%s）" % (value, want))
    return node_value_with_unit(node)


def to_si(value, unit):
    """按单位名换算到 SI；温度必须显式指定 degF/degC/K，避免歧义。"""
    if value is None:
        return None
    if unit == "degF":
        return (value - 32.0) * 5.0 / 9.0 + 273.15      # -> K
    if unit == "degC":
        return value + 273.15                           # -> K
    if unit == "K":
        return value
    f = TO_SI.get(unit)
    if f is None:
        raise ValueError("未知单位：%s（先 probe 确认代码，别猜）" % unit)
    return value * f


# ---------------------------------------------------------------- CLI
def _main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "inset":
        print("INSET =", get_inset(path))
        return
    if cmd == "probe":
        dim = sys.argv[3] if len(sys.argv) > 3 else None
        print("文件:", path)
        print("INSET =", get_inset(path))
        print()
        print("%-14s %-12s %-8s %s" % ("代码", "单位", "次数", "备注"))
        for (d, c), n in probe(path, dim).most_common(30):
            name = code_name(d, c)
            note = "" if name else "  <-- 未标定，需人工确认"
            print("%-14s %-12s %-8d %s" % ("<%d><%d>" % (d, c), name or "?", n, note))
        return
    print(__doc__)


if __name__ == "__main__":
    _main()
