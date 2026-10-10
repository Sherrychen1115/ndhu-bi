# /// script
# requires-python = ">=3.10"
# dependencies = ["xlrd", "pandas"]
# ///
"""把 114-1 在學生人數統計表（.xls 第一個工作表）轉成整齊的 CSV。"""
import re
from pathlib import Path

import pandas as pd
import xlrd

ROOT = Path(__file__).resolve().parent.parent
SRC = next((ROOT / "東華大學統計資料" / "在學人數統計表").glob("114-1*.xls"))
OUT = ROOT / "work" / "enrollment_114-1.csv"

# 區段標題（A 欄）-> program_raw
SECTIONS = {"博士班": "博士班", "碩士班": "碩士班", "碩專班": "碩士在職專班", "學士班": "學士班"}
COL_DEPT_COLLEGE, COL_DEPT, COL_F, COL_M = 1, 2, 5, 6

sheet = xlrd.open_workbook(SRC).sheet_by_index(0)
text = lambda r, c: str(sheet.cell_value(r, c)).strip()
strip_note = lambda s: re.sub(r"[（(].*?[)）]", "", s).strip()

rows, program, college, dept = [], None, "", ""
for r in range(3, sheet.nrows):
    a = text(r, 0)
    if a.startswith("備註"):
        break
    m = re.match(r"(\S+)\s*合計", a)
    if m:  # 合計列，切換學制並重置合併儲存格的延續值
        program, college, dept = SECTIONS[m.group(1)], "", ""
        continue
    if program is None:  # 「總計=...」列
        continue
    # 合併儲存格只在第一格有值，空白代表沿用上一列
    college = text(r, COL_DEPT_COLLEGE) or college
    dept = text(r, COL_DEPT) or dept
    # 報表瑕疵：博士班物理學系的名稱寫在合併範圍的中間列，
    # 第一列（應用物理博士班一般組）會被誤歸到上一個系所，用分組名稱校正
    if not text(r, COL_DEPT) and text(r, 3).startswith("應用物理"):
        dept = "物理學系"
    for gender, col in (("女", COL_F), ("男", COL_M)):
        rows.append((strip_note(college), dept, program, gender, int(sheet.cell_value(r, col))))

df = pd.DataFrame(rows, columns=["college", "dept_raw", "program_raw", "gender", "count"])
df = df.groupby(["college", "dept_raw", "program_raw", "gender"], sort=False, as_index=False)["count"].sum()
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"{len(df)} rows, total={df['count'].sum()} -> {OUT}")
