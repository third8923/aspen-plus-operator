# -*- coding: utf-8 -*-
"""
Aspen 英制 -> SI 单位换算函数库。
模型内部（COM/bkp）为英制；汇报交付国内一律转 SI。
用法示例：
  from unit_convert import f_to_c, psia_to_kpa, lbh_to_kgh, btuh_to_kw
  print(f_to_c(212))            # 100.0
  print(psia_to_kpa(7.35))      # 50.68
  print(lbh_to_kgh(1000))       # 453.59
  print(btuh_to_kw(100000))     # 29.31
"""
import math


def f_to_c(f):
    return (f - 32) * 5.0 / 9.0


def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0


def f_to_k(f):
    return (f - 32) * 5.0 / 9.0 + 273.15


def psia_to_kpa(psia):
    return psia * 6.8948


def psia_to_bar(psia):
    return psia * 0.0689476


def psia_to_mpa(psia):
    return psia * 0.00689476


def lbh_to_kgh(lbhr):
    return lbhr * 0.453592


def lbmolh_to_kmolh(lbmolhr):
    return lbmolhr * 0.453592


def btuh_to_kw(btuhr):
    return btuhr * 0.000293071


def btuh_to_kjh(btuhr):
    return btuhr * 1.05506


def cuft_to_m3(cuft):
    return cuft * 0.0283168


def lbcuft_to_kgm3(lbcuft):
    return lbcuft * 16.0185


def btulb_to_kjkg(btulb):
    return btulb * 2.326


def round_sig(x, n=4):
    if x is None or not math.isfinite(x):
        return x
    return round(x, n - int(math.floor(math.log10(abs(x)))) - 1)
