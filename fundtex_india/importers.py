"""Indian market data importers. Local files only; never assume unadjusted close is total return."""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import zipfile

from .market import validate_rows, validate_symbol

_MAX_ARCHIVE_BYTES = 25_000_000


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _day(raw):
    raw=str(raw or "").strip()
    if not raw:
        raise ValueError("Missing trade date")
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%b-%Y",
                "%m/%d/%Y %H:%M:%S", "%m/%d/%Y", "%Y%m%d"):
        try:
            return dt.datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unrecognized trade date: {raw[:40]}")


def _normalize(rows, symbol):
    clean=validate_rows(rows)
    return [{"date":row["date"],"symbol":symbol,"close":row["close"],
             "volume":row["volume"] if row["volume"] is not None else ""}
            for row in clean]


def import_googlefinance(path, symbol):
    """Convert an archived Google Finance style CSV. Unverified historical source."""
    symbol=validate_symbol(symbol)
    path=Path(path)
    if path.stat().st_size > _MAX_ARCHIVE_BYTES:
        raise ValueError("Oversized price file")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader=csv.DictReader(handle)
        if not reader.fieldnames or not {"Date","Close"}.issubset(reader.fieldnames):
            raise ValueError("Expected Date,Close columns in Google Finance-style CSV")
        rows=[{"date":_day(row["Date"]),"close":row["Close"],
               "volume":row.get("Volume")} for row in reader]
    normalized=_normalize(rows, symbol)
    return {
        "rows":normalized,
        "input_manifest":[{"filename":path.name,"sha256":_digest(path)}],
        "source_kind":"THIRD_PARTY_GOOGLEFINANCE_ARCHIVE_UNVERIFIED",
        "note":"Historic Google Finance-derived export; rights, total-return adjustments and completeness unverified."
    }


def import_nse_udiff(paths, symbol, *, series="EQ"):
    """Parse user-supplied NSE UDiFF capital-market ZIP files without extracting to disk.

    Requires one unambiguous EQ instrument/ISIN per ticker; changes to ISIN
    require explicit analyst reconciliation. Never downloads archives or bypasses
    exchange access restrictions.
    """
    symbol=validate_symbol(symbol)
    if not symbol.endswith(".NS"):
        raise ValueError("NSE UDiFF importer supports .NS symbols only")
    if not paths or len(paths)>2000:
        raise ValueError("Provide 2..2000 local NSE zip archive paths")
    target=symbol[:-3]
    records=[]
    manifests=[]
    isins=set()
    for raw_path in paths:
        path=Path(raw_path)
        if not path.is_file() or path.stat().st_size>_MAX_ARCHIVE_BYTES:
            raise ValueError("NSE ZIP missing or exceeds 25MB")
        with zipfile.ZipFile(path) as archive:
            candidates=[x for x in archive.infolist()
                        if not x.is_dir() and x.filename.lower().endswith(".csv")]
            if len(candidates)!=1:
                raise ValueError("NSE UDiFF ZIP must contain exactly one CSV")
            entry=candidates[0]
            if entry.file_size>_MAX_ARCHIVE_BYTES:
                raise ValueError("Oversized decompressed bhavcopy")
            with archive.open(entry) as stream:
                payload=stream.read(_MAX_ARCHIVE_BYTES+1)
                if len(payload)>_MAX_ARCHIVE_BYTES:
                    raise ValueError("Bhavcopy decompressed size too large")
            reader=csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
            required={"TradDt","TckrSymb","SctySrs","ClsPric"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError("Unexpected UDiFF columns; verify file version against NSE")
            found=[]
            for row in reader:
                if row["TckrSymb"].strip().upper()!=target or row["SctySrs"].strip().upper()!=series:
                    continue
                found.append(row)
            if len(found)!=1:
                raise ValueError(f"{path.name}: expected one {series} row for {target}, found {len(found)}")
            match=found[0]
            if match.get("ISIN"):
                isins.add(match["ISIN"].strip().upper())
            records.append({"date":_day(match["TradDt"]),"close":match["ClsPric"],
                            "volume":match.get("TtlTradgVol")})
            manifests.append({"filename":path.name,"sha256":_digest(path),
                              "trade_date":_day(match["TradDt"])})
    if len(isins)>1:
        raise ValueError("Multiple ISINs detected; reconcile security identity before import")
    return {
        "rows":_normalize(records,symbol),
        "input_manifest":manifests,
        "isin":next(iter(isins),None),
        "source_kind":"USER_PROVIDED_NSE_UDIFF_EXCHANGE_REPORT_UNADJUSTED",
        "note":"NSE UDiFF input files have not been independently authenticated. Prices unadjusted for corporate actions, dividends, fees or delistings."
    }


def export_prices(imported, out):
    path=Path(out).expanduser()
    manifest_path=path.with_suffix(path.suffix+".manifest.json")
    if path.exists() or manifest_path.exists():
        raise FileExistsError("Refusing to overwrite existing prices or manifest")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create: no races or silent replacement.
    with path.open("x", newline="", encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=["date","symbol","close","volume"])
        writer.writeheader()
        writer.writerows(imported["rows"])
    metadata={k:v for k,v in imported.items() if k!="rows"}
    metadata.update({"output":str(path),"rows_written":len(imported["rows"]),
                     "output_sha256":_digest(path),
                     "quality":"SOURCE_FORMAT_PARSED_NOT_AUTHENTICATED"})
    path.with_suffix(path.suffix+".manifest.json").write_text(
        json.dumps(metadata,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return metadata
