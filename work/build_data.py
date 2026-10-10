# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas"]
# ///
"""把 data/ 的三個 CSV 整理成網頁可直接載入的 docs/data.js。"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "data.js"
read = lambda name: pd.read_csv(ROOT / "data" / name, encoding="utf-8-sig", dtype=str, keep_default_na=False)

enr = read("enrollment.csv")
enr["count"] = enr["count"].astype(int)
enr = enr.groupby(["semester", "college", "dept", "degree", "gender"], as_index=False)["count"].sum()

leave = read("leave.csv")
leave[["new_leave", "on_leave_end"]] = leave[["new_leave", "on_leave_end"]].astype(int)
leave = leave.groupby(["semester", "college", "dept", "degree", "gender", "reason"], as_index=False)[
    ["new_leave", "on_leave_end"]].sum()

depts = read("dept_mapping.csv")
depts["aliases"] = depts["aliases"].map(lambda s: [a.strip() for a in s.split(";") if a.strip()])

# 欄位名稱只寫一次，每列用陣列，檔案較小；網頁端用 cols 對應欄位
table = lambda df: {"cols": list(df.columns), "rows": df.values.tolist()}
data = {
    "enrollment": table(enr),  # count = 在學人數
    "leave": table(leave),     # new_leave = 學期間休學，on_leave_end = 學期底休學狀態
    "depts": table(depts),     # dept, college, aliases[]
}
OUT.write_text("window.DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

total = int(enr.loc[enr.semester == "114-1", "count"].sum())
print(f"114-1 在學人數合計 {total}", "OK" if total == 10035 else "不符！")
print(f"enrollment {len(enr)} 列, leave {len(leave)} 列, depts {len(depts)} 列")
print(f"{OUT} {OUT.stat().st_size / 1024:.0f} KB")
