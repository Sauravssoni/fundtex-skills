"""Fundtex workbook export using optional artifact_tool (safe local approved inputs).

The default 3.9+ skills installation never changes user dependencies. For XLSX:
install artifact_tool in an explicitly approved isolated Python runtime.
"""
from __future__ import annotations
from pathlib import Path

def write_xlsx(spec, dest):
    path=Path(dest)
    if path.exists():raise ValueError("Will not overwrite existing workbook: "+str(path))
    try:
        from artifact_tool import Workbook, SpreadsheetFile
    except ImportError:
        raise ValueError("Optional artifact_tool not installed; CSV/HTML always available. Install in an approved isolated Python environment.") from None
    wb=Workbook.create()
    cover=wb.worksheets.add("Executive")
    prices=wb.worksheets.add("Price History")
    tech=wb.worksheets.add("Indicators")
    signals=wb.worksheets.add("Historical Events")
    source=wb.worksheets.add("Sources & Limits")
    cover.merge_cells("A1:H1")
    cover.get_range("A1").values=[["FUNDTEX  /  FINANCIAL INTELLIGENCE"]]
    cover.merge_cells("A2:H2")
    cover.get_range("A2").values=[["ANALYST STUDIO  •  RESEARCH PACK"]]
    cover.get_range("A4:B10").values=[
        ["SYMBOL",spec["symbol"]],
        ["OBSERVED AS OF",spec["last_observation"]],
        ["PRICE DATA","OHLC" if spec["price_type"]=="OHLC_CANDLE" else "CLOSE-ONLY"],
        ["SOURCE QUALITY",spec["data_quality"]],
        ["PRICE SOURCE HASH",spec["source_sha256"]],
        ["DATA ACCESS","Approved local CSV — no licensed live feed"],
        ["STATUS","HISTORICAL DESCRIPTIVE ANALYSIS ONLY"]]
    cover.merge_cells("A12:H12");cover.get_range("A12").values=[["Executive notes"]]
    cover.merge_cells("A13:H13")
    cover.get_range("A13").values=[["Review original data provenance, corporate-action adjustments and full filing evidence before recommending trades."]]
    cover.merge_cells("A14:H14")
    cover.get_range("A14").values=[["Historical crossovers do NOT establish predictive alpha or investable signals."]]

    rows=spec["rows"]
    header=["Date","Open","High","Low","Close (INR)","Volume","Return (daily)","Session"]
    prices.get_range("A1:H1").values=[header]
    matrix=[]
    for r in rows:
        matrix.append([r["date"],r.get("open"),r.get("high"),r.get("low"),r["close"],r.get("volume"),None,"Historic"])
    n=len(matrix)
    if n>15000:raise ValueError("Workbook export capped at 15,000 rows")
    prices.get_range_by_indexes(1,0,n,8).values=matrix
    if n>1:
        prices.get_range("G3").formulas=[["=IFERROR(E3/E2-1,0)"]]
        if n>2:prices.get_range(f"G3:G{n+1}").fill_down()
        prices.get_range("G3:G"+str(n+1)).set_number_format("0.00%;[Red](0.00%);-")

    ti=spec["indicators"]
    tech.get_range("A1:G1").values=[["Date","Close INR","SMA 20 INR","SMA 50 INR","EMA 12 INR","EMA 26 INR","RSI 14"]]
    tech_data=[[r["date"],r["close"],ti["sma20"][i],ti["sma50"][i],ti["ema12"][i],ti["ema26"][i],ti["rsi14"][i]] for i,r in enumerate(rows)]
    tech.get_range_by_indexes(1,0,n,7).values=tech_data
    signals.get_range("A1:D1").values=[["Date","Reference close INR","Historical observation","Forecast status"]]
    events=ti["events"]
    if events:signals.get_range_by_indexes(1,0,len(events),4).values=[
        [x["date"],x["price"],x["signal"],"NOT A VERIFIED INVESTMENT SIGNAL"] for x in events]
    else:signals.get_range("A2").values=[["No 20/50 SMA cross observed in valid sample"]]
    source.get_range("A1:B7").values=[
        ["Source field","Value"],
        ["Filename","Approved local source"],
        ["SHA-256",spec["source_sha256"]],
        ["Last observation",spec["last_observation"]],
        ["Authenticity",spec["data_quality"]+" - NOT INDEPENDENTLY VERIFIED"],
        ["Adjusted prices","NOT VERIFIED (splits, dividends, restatements)"],
        ["Signal quality","HISTORICAL OBSERVATION ONLY - NO PREDICTIVE EDGE PROVEN"]]

    heading={"fill":"#132743","font":{"bold":True,"color":"#FFFFFF"},"row_height":29}
    for s in (prices,tech,signals,source):
        s.get_range("A1:H1" if s==prices else ("A1:G1" if s==tech else ("A1:D1" if s==signals else "A1:B1"))).format=heading
        s.freeze_panes.freeze_rows(1)
        s.get_range("A:A").format.column_width=21
    prices.get_range("B:F").format.column_width=15
    prices.get_range("G:H").format.column_width=20
    tech.get_range("B:G").format.column_width=19
    signals.get_range("C:D").format.column_width=43
    source.get_range("A:A").format.column_width=25;source.get_range("B:B").format.column_width=92
    cover.get_range("A1:H1").format={"fill":"#102743","font":{"bold":True,"color":"#FFFFFF","size":16},"row_height":36}
    cover.get_range("A2:H2").format={"fill":"#146b75","font":{"bold":True,"color":"#FFFFFF"},"row_height":29}
    cover.get_range("A4:A10").format={"font":{"bold":True,"color":"#365b7e"}}
    cover.get_range("A:A").format.column_width=25
    cover.get_range("B:B").format.column_width=64
    cover.get_range("A12:H12").format=heading
    try:
        chart=tech.charts.add("line",tech.get_range(f"A1:D{min(n+1,250)}"))
        chart.title_text="Historical price versus SMA 20/50"
        chart.set_position("I2","T20")
    except (ValueError,AttributeError):
        # Some older optional artifact_tool versions cannot create a chart.
        pass
    path.parent.mkdir(parents=True,exist_ok=True)
    SpreadsheetFile.export_xlsx(wb).save(str(path))
    return str(path)
