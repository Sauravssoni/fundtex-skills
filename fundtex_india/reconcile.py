"""Fundtex dual-feed reconciliation: source disagreement detection, not source certification.

No network calls. Reads two analyst-approved dated price CSVs and compares only
overlapping dated observations. Adjusted and unadjusted series must not be
assumed equivalent; disagreement forces explicit review.
"""
from __future__ import annotations
from datetime import date, datetime, timezone
import math
import statistics
from .chart_studio import prices

def reconcile(primary, secondary, symbol, *, tolerance_bps=25.0, min_overlap=12, max_mismatches=0):
    if not isinstance(tolerance_bps,(float,int)) or isinstance(tolerance_bps,bool) or not math.isfinite(tolerance_bps) or not 0 <= tolerance_bps <= 10000:
        raise ValueError("tolerance_bps must be finite in 0..10000")
    if not isinstance(min_overlap,int) or isinstance(min_overlap,bool) or not 12 <= min_overlap <= 20000:
        raise ValueError("min_overlap must be in 12..20000")
    if not isinstance(max_mismatches,int) or isinstance(max_mismatches,bool) or not 0 <= max_mismatches <= 20000:
        raise ValueError("max_mismatches must be in 0..20000")
    if str(primary) == str(secondary):
        raise ValueError("Two different source files required; repeated file is not corroboration")
    a=prices(primary,symbol)
    b=prices(secondary,symbol)
    if a["source_sha256"]==b["source_sha256"]:
        raise ValueError("Input files have identical bytes; not independent evidence")
    ap={row["date"]:row["close"] for row in a["rows"]}
    bp={row["date"]:row["close"] for row in b["rows"]}
    start=max(min(ap),min(bp))
    end=min(max(ap),max(bp))
    if end < start:
        raise ValueError("Source time periods do not intersect")
    aa={k for k in ap if start<=k<=end}
    bb={k for k in bp if start<=k<=end}
    overlap=sorted(aa & bb)
    if len(overlap)<min_overlap:
        raise ValueError("Insufficient identical observation dates for independent comparison")
    diff=[(day,abs(ap[day]-bp[day])/((ap[day]+bp[day])/2)*10000) for day in overlap]
    mismatches=[{"date":d,"primary_close":ap[d],"secondary_close":bp[d],
                 "symmetric_difference_bps":round(v,4)}
                for d,v in diff if v>tolerance_bps]
    union=len(aa|bb)
    if union==0:raise ValueError("No comparable timestamps")
    gap_a=sorted(bb-aa)
    gap_b=sorted(aa-bb)
    max_diff=max(v for _,v in diff)
    median_diff=statistics.median(v for _,v in diff)
    status="NUMERICAL_AGREEMENT_ONLY" if len(mismatches)<=max_mismatches and not gap_a and not gap_b else "REVIEW_SOURCE_DISAGREEMENTS"
    return {
        "engine":"FUNDTEX_DUAL_SOURCE_RECONCILIATION_v1",
        "symbol":symbol.upper(),
        "comparison_basis":"same_date_close_symmetric_bps",
        "tolerance_bps":float(tolerance_bps),
        "primary":{"sha256":a["source_sha256"],"quality":a["data_quality"],"observations":len(ap)},
        "secondary":{"sha256":b["source_sha256"],"quality":b["data_quality"],"observations":len(bp)},
        "overlap_period_start":start, "overlap_period_end":end,
        "matched_dates":len(overlap),
        "within_period_coverage":round(len(overlap)/union,6),
        "max_symmetric_difference_bps":round(max_diff,4),
        "median_symmetric_difference_bps":round(median_diff,4),
        "mismatch_count":len(mismatches),
        "mismatches":mismatches[:100],
        "mismatch_result_truncated":len(mismatches)>100,
        "only_in_primary_dates":gap_b[:100],
        "only_in_secondary_dates":gap_a[:100],
        "status":status,
        "source_certified":False,
        "display_rights_verified":False,
        "research_only":True,
        "required_reviews":[
            "Resolve adjusted vs unadjusted close, splits, bonus shares and dividends before deciding one source is wrong.",
            "Confirm ISIN/exchange/series and timestamp convention, including India trading holidays.",
            "Agreement alone cannot establish truth if both sources share the same upstream data or error.",
            "Check publisher lineage, entitlement, observation freshness and redistribution rights independently."
        ]
    }
