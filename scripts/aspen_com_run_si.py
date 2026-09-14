# -*- coding: utf-8 -*-
"""
aspen_com_run_si.py — Aspen Plus V14 COM 全 SI 封装模板（生产实战）

【为什么有这份模板】Aspen COM 接口硬边界（2026-09 实测）：
  - COM 节点没有 Units 属性；写 Input 的 Value 永远按 bkp 内部英制解释
    （实测：写 REACTOR Input TEMP Value=215.0 → R_TEMP=101.7°C，即被当作 215°F）；
  - 读 Input 返回存储原值（不随单位集换算）；
  - 读 Output 随单位集换算（INSET=SI-CBAR 时直接 kg/hr / °C / W）。
【本模板作用】业务代码 100% 用 SI（°C / bar / kg/h / kmol/h / kW），
  换算全部收进 set_/get_ 封装函数，调用方与日志不出现任何英制。

【前提】模型 bkp 的 "IN-UNITS" INSET 已设为 SI-CBAR（读 Output 免换算）。
"""
import win32com.client
import pythoncom
import time

# ---------------- 单位换算（引擎内部英制，封装函数专用） ----------------
def _to_F(degC):      return degC * 9.0 / 5.0 + 32.0
def _to_psia(bar):    return bar * 14.5038
def _to_lbmolhr(kmolhr): return kmolhr * 2.20462
def _kg_hr_to_lbmol_hr(kg_hr, MW): return kg_hr / MW * 2.20462
def _to_C(degF):      return (degF - 32.0) * 5.0 / 9.0
def _to_bar(psia):    return psia / 14.5038

# ---------------- SI 封装：写参数（业务层只出现 SI 值） ----------------
def set_temp(tree, path, degC):
    """按 °C 写温度节点"""
    tree.FindNode(path).Value = _to_F(degC)

def set_pres(tree, path, bar):
    """按 bar 写压力节点"""
    tree.FindNode(path).Value = _to_psia(bar)

def set_flow(tree, path, kmolhr):
    """按 kmol/h 写摩尔流量节点"""
    tree.FindNode(path).Value = _to_lbmolhr(kmolhr)

def set_kgflow(tree, path, kg_hr, MW):
    """按 kg/h 写质量流量节点（需组分摩尔质量 MW）"""
    tree.FindNode(path).Value = _kg_hr_to_lbmol_hr(kg_hr, MW)

# ---------------- SI 封装：读结果（SI-CBAR 下 Output 已自动换算） ----------------
def get_massflow_kg_hr(tree, stream, comp):
    """读组分质量流量，返回 kg/hr（INSET=SI-CBAR 时引擎已返回 kg/hr）"""
    return tree.FindNode(r"Data\Streams\%s\Output\MASSFLOW3\%s" % (stream, comp)).Value

def get_total_molar_kmol_hr(tree, stream):
    """读液相总摩尔流量，返回 kmol/hr"""
    return tree.FindNode(r"Data\Streams\%s\Output\L1_FLOW" % stream).Value

def get_qcalc_kw(tree, block):
    """读块热负荷，返回 kW（注意 SI-CBAR 下引擎返回 W，÷1000）"""
    return tree.FindNode(r"Data\Blocks\%s\Output\QCALC" % block).Value / 1000.0

def get_block_temp_c(tree, block):
    """读块出口温度，返回 °C（SI-CBAR 下引擎已返回 °C）"""
    return tree.FindNode(r"Data\Blocks\%s\Output\R_TEMP" % block).Value

# ---------------- 主流程模板 ----------------
def run_case(bkp, params_si, out_stream="REAC-OUT"):
    """
    params_si 示例（全部 SI）：
      {"T_degC": 215.0, "P_bar": 18.42, "H2O_kmolhr": 53.85, "OIL_kmolhr": 5.316}
    返回 dict（全部 SI）。
    """
    pythoncom.CoInitialize()
    doc = win32com.client.Dispatch("Apwn.Document.40.0")
    doc.SuppressDialogs = True  # 必须：抑制引擎弹窗
    try:
        doc.InitFromFile(bkp)
        tree = doc.Tree
        eng = doc.Engine

        # ---- 业务代码：全部写 SI 值，无一处英制 ----
        if "T_degC" in params_si:
            set_temp(tree, r"Data\Blocks\REACTOR\Input\TEMP", params_si["T_degC"])
        if "P_bar" in params_si:
            set_pres(tree, r"Data\Blocks\REACTOR\Input\PRES", params_si["P_bar"])
        if "H2O_kmolhr" in params_si:
            set_flow(tree, r"Data\Streams\FEED\Input\FLOW\MIXED\H2O", params_si["H2O_kmolhr"])
        if "OIL_kmolhr" in params_si:
            set_flow(tree, r"Data\Streams\FEED\Input\FLOW\MIXED\TRIOLEIN", params_si["OIL_kmolhr"])

        eng.Reinit()          # 顺序不能错：Reinit → Run2 → 轮询
        doc.Run2(1)
        t0 = time.time()
        while eng.IsRunning and time.time() - t0 < 120:
            time.sleep(2)

        return {
            "油酸_kg_hr": get_massflow_kg_hr(tree, out_stream, "OLEIC"),
            "水_kg_hr":   get_massflow_kg_hr(tree, out_stream, "H2O"),
            "三油酸甘油酯_kg_hr": get_massflow_kg_hr(tree, out_stream, "TRIOLEIN"),
            "液相总摩尔_kmol_hr": get_total_molar_kmol_hr(tree, out_stream),
            "反应温度_C": get_block_temp_c(tree, "REACTOR"),
            "冷却负荷_kW": get_qcalc_kw(tree, "COOL"),
        }
    finally:
        try:
            doc.Close()
        except Exception:
            pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    BKP = r"<你的模型路径>\hydrolysis_example.bkp"
    # 示例工况（SI，模拟数据）：215°C / 18.42 bar / 水 24.43 kmol/hr / 油 2.411 kmol/hr
    result = run_case(BKP, {"T_degC": 215.0, "P_bar": 18.42, "H2O_kmolhr": 24.43, "OIL_kmolhr": 2.411})
    for k, v in result.items():
        print("%-22s %s" % (k, v))
