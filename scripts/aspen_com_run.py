# -*- coding: utf-8 -*-
"""
Aspen Plus V14 COM 批量工况扫描模板（参数化）。
用法：
  python aspen_com_run.py <bkp路径> <工况表.json>
工况表 JSON：
{
  "blocks": {"SEP1": {"TEMP": ["110","120","130","140"]}},
  "read": [
    {"name": "FAME", "path": "Data\\Streams\\PRODUCT\\Output\\MASSFLOW3\\MEOLEATE"},
    {"name": "MEOH", "path": "Data\\Streams\\RECYCLE\\Output\\MASSFLOW3\\METHANOL"}
  ],
  "output": "results.csv"
}
只扫一个块的一个参数时，"blocks" 里放一个键即可；多个块参数会做笛卡尔积。
"""
import sys, json, time, csv, itertools
import win32com.client, pythoncom


def getval(tree, path):
    try:
        return tree.FindNode(path).Value
    except Exception:
        return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    bkp, cfg_path = sys.argv[1], sys.argv[2]
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    blocks = cfg.get("blocks", {})
    reads = cfg.get("read", [])
    out = cfg.get("output", "results.csv")

    pythoncom.CoInitialize()
    doc = win32com.client.Dispatch("Apwn.Document.40.0")
    doc.SuppressDialogs = True
    doc.InitFromFile(bkp)
    tree = doc.Tree
    eng = doc.Engine

    # 构造工况笛卡尔积：{block: {param: [values]}} -> list of (block, param, value)
    combos = []
    for blk, params in blocks.items():
        for param, values in params.items():
            combos.append((blk, param, values))
    keys = [f"{b}.{p}" for b, p, _ in combos]
    grid = list(itertools.product(*[vals for _, _, vals in combos]))

    rows = []
    for g in grid:
        for (blk, param, _), val in zip(combos, g):
            tree.FindNode(rf"Data\Blocks\{blk}\Input\{param}").Value = float(val)
        eng.Reinit()
        doc.Run2(1)
        while eng.IsRunning:
            time.sleep(2)
        row = dict(zip(keys, g))
        for r in reads:
            row[r["name"]] = getval(tree, r["path"])
        rows.append(row)
        print(row)

    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys + [r["name"] for r in reads])
        w.writeheader()
        w.writerows(rows)

    doc.Close()
    pythoncom.CoUninitialize()
    print("saved:", out)


if __name__ == "__main__":
    main()
