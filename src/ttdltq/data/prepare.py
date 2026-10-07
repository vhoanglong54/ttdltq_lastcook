from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from ttdltq.config import (
    INTERIM_DIR,
    OUTPUT_DIR,
    PROCESSED_DIR,
    RAW_DIR,
    ensure_runtime_directories,
    load_yaml,
)


NA_VALUES = ["NULL", "NA", "PS", "PrivacySuppressed", ""]

INSTITUTION_COLUMNS = [
    "UNITID",
    "INSTNM",
    "CITY",
    "STABBR",
    "ZIP",
    "MAIN",
    "NUMBRANCH",
    "PREDDEG",
    "HIGHDEG",
    "CONTROL",
    "REGION",
    "LOCALE",
    "LATITUDE",
    "LONGITUDE",
    "HBCU",
    "PBI",
    "TRIBAL",
    "ADM_RATE",
    "SAT_AVG",
    "DISTANCEONLY",
    "UGDS",
    "UGDS_WHITE",
    "UGDS_BLACK",
    "UGDS_HISP",
    "UGDS_ASIAN",
    "UGDS_AIAN",
    "UGDS_NHPI",
    "UGDS_2MOR",
    "UGDS_NRA",
    "UGDS_UNKN",
    "UGDS_MEN",
    "UGDS_WOMEN",
    "CURROPER",
    "NPT4_PUB",
    "NPT4_PRIV",
    "COSTT4_A",
    "COSTT4_P",
    "TUITIONFEE_IN",
    "TUITIONFEE_OUT",
    "INEXPFTE",
    "AVGFACSAL",
    "PFTFAC",
    "PCTPELL",
    "PCTFLOAN",
    "UG25ABV",
    "C150_4",
    "C150_L4",
    "C200_4",
    "C200_L4",
    "RET_FT4",
    "RET_FTL4",
    "RET_PT4",
    "RET_PTL4",
    "STUFACR",
    "COMP_ORIG_YR3_RT",
    "WDRAW_ORIG_YR3_RT",
    "PELL_COMP_ORIG_YR3_RT",
    "PELL_WDRAW_ORIG_YR3_RT",
    "NOPELL_COMP_ORIG_YR3_RT",
    "NOPELL_WDRAW_ORIG_YR3_RT",
    "FIRSTGEN_COMP_ORIG_YR3_RT",
    "FIRSTGEN_WDRAW_ORIG_YR3_RT",
    "NOT1STGEN_COMP_ORIG_YR3_RT",
    "NOT1STGEN_WDRAW_ORIG_YR3_RT",
    "PELL_YR3_N",
    "NOPELL_YR3_N",
    "FIRSTGEN_YR3_N",
    "NOT1STGEN_YR3_N",
]

FIELD_COLUMNS = [
    "UNITID",
    "OPEID6",
    "INSTNM",
    "CONTROL",
    "MAIN",
    "CIPCODE",
    "CIPDESC",
    "CREDLEV",
    "CREDDESC",
    "IPEDSCOUNT1",
    "IPEDSCOUNT2",
    "DISTANCE",
    "DEBT_ALL_STGP_ANY_MDN",
    "DEBT_ALL_PP_ANY_MDN",
    "EARN_MDN_1YR",
    "EARN_MDN_4YR",
    "EARN_MDN_5YR",
]

CONTROL_LABELS = {
    1: "Công lập",
    2: "Tư thục phi lợi nhuận",
    3: "Tư thục vì lợi nhuận",
}

DEGREE_LABELS = {
    0: "Không phân loại",
    1: "Chứng chỉ",
    2: "Associate",
    3: "Bachelor",
    4: "Graduate",
}

LOCALE_LABELS = {
    1: "Thành phố",
    2: "Ngoại ô",
    3: "Thị trấn",
    4: "Nông thôn",
}

DISTANCE_LABELS = {
    0: "Không hoàn toàn trực tuyến",
    1: "Có thể hoàn thành trực tuyến",
    2: "Một phần có thể hoàn thành trực tuyến",
}


def _first_csv(folder: Path) -> Path:
    candidates = sorted(folder.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV found under {folder}")
    return candidates[0]


def _available_columns(path: Path) -> list[str]:
    return pd.read_csv(path, nrows=0).columns.tolist()


def read_selected_csv(path: Path, requested: Iterable[str]) -> pd.DataFrame:
    available = set(_available_columns(path))
    selected = [column for column in requested if column in available]
    missing = sorted(set(requested) - available)
    if missing:
        print(f"Warning: {path.name} does not contain {len(missing)} requested columns")
    return pd.read_csv(
        path,
        usecols=selected,
        na_values=NA_VALUES,
        low_memory=False,
        encoding="utf-8-sig",
    )


def _coalesce(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    existing = [column for column in columns if column in frame]
    if not existing:
        return pd.Series(np.nan, index=frame.index, dtype="float64")
    result = pd.to_numeric(frame[existing[0]], errors="coerce")
    for column in existing[1:]:
        result = result.fillna(pd.to_numeric(frame[column], errors="coerce"))
    return result


def _to_numeric(frame: pd.DataFrame, exclude: Iterable[str]) -> pd.DataFrame:
    excluded = set(exclude)
    for column in frame.columns:
        if column not in excluded:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def _weighted_average(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & (weights > 0)
    if not valid.any():
        return float("nan")
    return float(np.average(values[valid], weights=weights[valid]))


def _flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame.columns = [
        "_".join(str(part) for part in column if str(part))
        if isinstance(column, tuple)
        else str(column)
        for column in frame.columns
    ]
    return frame


def prepare_institutions(
    raw: pd.DataFrame, *, completion_threshold: float
) -> pd.DataFrame:
    strings = ["INSTNM", "CITY", "STABBR", "ZIP"]
    frame = _to_numeric(raw.copy(), exclude=strings)
    frame["UNITID"] = pd.to_numeric(frame["UNITID"], errors="coerce").astype("Int64")
    frame = frame.dropna(subset=["UNITID"]).drop_duplicates("UNITID", keep="first")

    frame["completion_rate"] = _coalesce(frame, ["C150_4", "C150_L4"])
    frame["completion_200_rate"] = _coalesce(frame, ["C200_4", "C200_L4"])
    frame["retention_rate"] = _coalesce(frame, ["RET_FT4", "RET_FTL4"])
    frame["part_time_retention_rate"] = _coalesce(frame, ["RET_PT4", "RET_PTL4"])
    frame["net_price"] = _coalesce(frame, ["NPT4_PUB", "NPT4_PRIV"])
    frame["annual_cost"] = _coalesce(frame, ["COSTT4_A", "COSTT4_P"])

    frame["control_label"] = frame["CONTROL"].map(CONTROL_LABELS).fillna("Không xác định")
    frame["predominant_degree"] = (
        frame["PREDDEG"].map(DEGREE_LABELS).fillna("Không xác định")
    )
    locale_family = np.floor(pd.to_numeric(frame["LOCALE"], errors="coerce") / 10)
    frame["locale_group"] = locale_family.map(LOCALE_LABELS).fillna("Không xác định")
    frame["distance_only"] = np.where(
        frame["DISTANCEONLY"].eq(1), "Chỉ đào tạo từ xa", "Không chỉ đào tạo từ xa"
    )
    frame["is_operating"] = frame["CURROPER"].eq(1)
    frame["low_completion"] = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    eligible = frame["completion_rate"].notna()
    frame.loc[eligible, "low_completion"] = (
        frame.loc[eligible, "completion_rate"] < completion_threshold
    ).astype(int)
    frame["risk_label"] = frame["low_completion"].map(
        {1: "Tỷ lệ hoàn thành thấp", 0: "Không thuộc nhóm thấp"}
    )
    frame["log_undergrad_enrollment"] = np.log1p(frame["UGDS"].clip(lower=0))

    rename = {
        "INSTNM": "institution_name",
        "CITY": "city",
        "STABBR": "state",
        "ZIP": "zip_code",
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude",
        "UGDS": "undergrad_enrollment",
        "PCTPELL": "pell_share",
        "PCTFLOAN": "federal_loan_share",
        "STUFACR": "student_faculty_ratio",
        "CONTROL": "control_code",
        "control_label": "control",
        "TUITIONFEE_IN": "tuition_in_state",
        "TUITIONFEE_OUT": "tuition_out_state",
        "ADM_RATE": "admission_rate",
        "SAT_AVG": "sat_average",
        "INEXPFTE": "instructional_spend_per_fte",
        "AVGFACSAL": "average_faculty_salary",
        "PFTFAC": "full_time_faculty_share",
        "UG25ABV": "age_25_plus_share",
        "COMP_ORIG_YR3_RT": "completion_3yr_rate",
        "WDRAW_ORIG_YR3_RT": "withdrawal_3yr_rate",
    }
    frame = frame.rename(columns=rename)
    frame.columns = [column.lower() for column in frame.columns]
    return frame.reset_index(drop=True)


def build_equity_long(institutions: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "Nhận Pell Grant",
            "pell_comp_orig_yr3_rt",
            "pell_wdraw_orig_yr3_rt",
            "pell_yr3_n",
        ),
        (
            "Không nhận Pell Grant",
            "nopell_comp_orig_yr3_rt",
            "nopell_wdraw_orig_yr3_rt",
            "nopell_yr3_n",
        ),
        (
            "Thế hệ đầu học đại học",
            "firstgen_comp_orig_yr3_rt",
            "firstgen_wdraw_orig_yr3_rt",
            "firstgen_yr3_n",
        ),
        (
            "Không phải thế hệ đầu",
            "not1stgen_comp_orig_yr3_rt",
            "not1stgen_wdraw_orig_yr3_rt",
            "not1stgen_yr3_n",
        ),
    ]
    identity = ["unitid", "institution_name", "state", "control", "locale_group"]
    blocks: list[pd.DataFrame] = []
    for label, completion, withdrawal, count in specs:
        columns = identity + [completion, withdrawal, count]
        existing = [column for column in columns if column in institutions]
        block = institutions[existing].copy()
        block["student_group"] = label
        block = block.rename(
            columns={
                completion: "completion_3yr_rate",
                withdrawal: "withdrawal_3yr_rate",
                count: "cohort_count",
            }
        )
        for required in ("completion_3yr_rate", "withdrawal_3yr_rate", "cohort_count"):
            if required not in block:
                block[required] = np.nan
        blocks.append(block)
    result = pd.concat(blocks, ignore_index=True)
    return result.dropna(
        subset=["completion_3yr_rate", "withdrawal_3yr_rate"], how="all"
    )


def build_state_summary(institutions: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    valid_states = institutions["state"].astype("string").str.fullmatch(r"[A-Z]{2}")
    for state, group in institutions[valid_states.fillna(False)].groupby("state"):
        weights = group["undergrad_enrollment"].clip(lower=0)
        eligible = group["low_completion"].notna()
        records.append(
            {
                "state": state,
                "institution_count": int(group["unitid"].nunique()),
                "undergrad_enrollment": float(weights.sum(min_count=1)),
                "completion_rate": _weighted_average(group["completion_rate"], weights),
                "retention_rate": _weighted_average(group["retention_rate"], weights),
                "withdrawal_3yr_rate": _weighted_average(
                    group["withdrawal_3yr_rate"], weights
                ),
                "pell_share": _weighted_average(group["pell_share"], weights),
                "federal_loan_share": _weighted_average(
                    group["federal_loan_share"], weights
                ),
                "student_faculty_ratio": _weighted_average(
                    group["student_faculty_ratio"], weights
                ),
                "net_price": _weighted_average(group["net_price"], weights),
                "low_completion_institution_share": float(
                    group.loc[eligible, "low_completion"].mean()
                )
                if eligible.any()
                else float("nan"),
            }
        )
    return pd.DataFrame(records).sort_values("state").reset_index(drop=True)


def prepare_fields(raw: pd.DataFrame, institutions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    strings = ["INSTNM", "CIPDESC", "CREDDESC"]
    frame = _to_numeric(raw.copy(), exclude=strings)
    frame["UNITID"] = pd.to_numeric(frame["UNITID"], errors="coerce").astype("Int64")
    frame["CONTROL"] = frame["CONTROL"].map(CONTROL_LABELS).fillna("Không xác định")
    frame["credentials_awarded"] = pd.to_numeric(
        frame.get("IPEDSCOUNT2"), errors="coerce"
    )
    frame["previous_credentials_awarded"] = pd.to_numeric(
        frame.get("IPEDSCOUNT1"), errors="coerce"
    )
    frame["distance_program"] = (
        frame.get("DISTANCE", pd.Series(index=frame.index, dtype="float64"))
        .map(DISTANCE_LABELS)
        .fillna("Không xác định")
    )
    frame = frame.rename(
        columns={
            "CIPCODE": "cip_code",
            "CIPDESC": "field_name",
            "CREDLEV": "credential_level",
            "CREDDESC": "credential_name",
            "DEBT_ALL_STGP_ANY_MDN": "median_debt",
            "EARN_MDN_1YR": "median_earnings_1yr",
            "EARN_MDN_4YR": "median_earnings_4yr",
            "EARN_MDN_5YR": "median_earnings_5yr",
        }
    )
    frame.columns = [column.lower() for column in frame.columns]

    lookup = institutions[["unitid", "state"]].drop_duplicates("unitid")
    frame = frame.merge(lookup, how="left", on="unitid", validate="many_to_one")
    frame = frame.dropna(subset=["field_name", "credential_name"])

    national = (
        frame.groupby(
            ["field_name", "credential_level", "credential_name", "distance_program"],
            dropna=False,
        )
        .agg(
            credentials_awarded=("credentials_awarded", "sum"),
            previous_credentials_awarded=("previous_credentials_awarded", "sum"),
            institution_count=("unitid", "nunique"),
            median_debt=("median_debt", "median"),
            median_earnings_1yr=("median_earnings_1yr", "median"),
            median_earnings_4yr=("median_earnings_4yr", "median"),
            median_earnings_5yr=("median_earnings_5yr", "median"),
        )
        .reset_index()
    )
    national = national.sort_values("credentials_awarded", ascending=False)

    top_fields = set(
        national.groupby("field_name")["credentials_awarded"]
        .sum()
        .nlargest(100)
        .index
    )
    by_state = (
        frame[frame["field_name"].isin(top_fields)]
        .groupby(
            [
                "state",
                "control",
                "field_name",
                "credential_level",
                "credential_name",
                "distance_program",
            ],
            dropna=False,
        )
        .agg(
            credentials_awarded=("credentials_awarded", "sum"),
            institution_count=("unitid", "nunique"),
            median_debt=("median_debt", "median"),
            median_earnings_1yr=("median_earnings_1yr", "median"),
        )
        .reset_index()
    )
    return national, by_state


def build_ipeds_inventory(institutions: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    ipeds_root = RAW_DIR / "ipeds"
    for table_dir in sorted(path for path in ipeds_root.glob("*") if path.is_dir()):
        csv_files = sorted(table_dir.glob("*.csv"))
        for path in csv_files:
            try:
                unitids = pd.read_csv(
                    path,
                    usecols=lambda column: column.upper() == "UNITID",
                    na_values=NA_VALUES,
                    low_memory=False,
                )
                source_ids = set(
                    pd.to_numeric(unitids.iloc[:, 0], errors="coerce").dropna().astype(int)
                )
                target_ids = set(institutions["unitid"].dropna().astype(int))
                matched = len(source_ids & target_ids)
                records.append(
                    {
                        "table": table_dir.name,
                        "file": path.name,
                        "row_count": len(unitids),
                        "unique_unitid": len(source_ids),
                        "matched_scorecard_unitid": matched,
                        "scorecard_match_rate": matched / len(source_ids)
                        if source_ids
                        else np.nan,
                    }
                )
            except (ValueError, IndexError):
                records.append(
                    {
                        "table": table_dir.name,
                        "file": path.name,
                        "row_count": np.nan,
                        "unique_unitid": np.nan,
                        "matched_scorecard_unitid": np.nan,
                        "scorecard_match_rate": np.nan,
                    }
                )
    return pd.DataFrame(records)


def build_institution_history(*, completion_threshold: float) -> pd.DataFrame:
    """Create a reproducible institution-year panel from Scorecard snapshots.

    The start year in ``MERGEDYYYY_YY_PP.csv`` is stored as ``academic_year``.
    Keeping the year explicit lets the model reserve the newest year for testing
    instead of mixing observations from all years in a random split.
    """

    history_root = RAW_DIR / "scorecard" / "history"
    history_files = sorted(history_root.glob("MERGED*_PP.csv"))
    if not history_files:
        return pd.DataFrame()

    panels: list[pd.DataFrame] = []
    for path in history_files:
        match = re.search(r"MERGED(\d{4})_\d{2}_PP", path.stem, flags=re.IGNORECASE)
        if match is None:
            print(f"Warning: could not parse academic year from {path.name}; skipped")
            continue
        raw = read_selected_csv(path, INSTITUTION_COLUMNS)
        panel = prepare_institutions(raw, completion_threshold=completion_threshold)
        panel["academic_year"] = int(match.group(1))
        panel["source_file"] = path.name
        panels.append(panel)

    if not panels:
        return pd.DataFrame()
    history = pd.concat(panels, ignore_index=True)
    return history.sort_values(["academic_year", "unitid"]).reset_index(drop=True)


def quality_audit(
    institutions: pd.DataFrame,
    fields_national: pd.DataFrame,
    equity: pd.DataFrame,
    source_rows: dict[str, int],
) -> dict[str, Any]:
    rate_columns = [
        "completion_rate",
        "retention_rate",
        "pell_share",
        "federal_loan_share",
        "withdrawal_3yr_rate",
    ]
    out_of_range = {
        column: int(
            ((institutions[column] < 0) | (institutions[column] > 1)).fillna(False).sum()
        )
        for column in rate_columns
        if column in institutions
    }
    return {
        "source_rows": source_rows,
        "processed_rows": {
            "institutions": len(institutions),
            "institutions_with_completion": int(institutions["completion_rate"].notna().sum()),
            "institutions_with_coordinates": int(
                institutions[["latitude", "longitude"]].notna().all(axis=1).sum()
            ),
            "field_summary": len(fields_national),
            "equity_long": len(equity),
        },
        "duplicate_unitid": int(institutions["unitid"].duplicated().sum()),
        "out_of_range_rates": out_of_range,
        "missing_rate": {
            column: round(float(institutions[column].isna().mean()), 6)
            for column in [
                "completion_rate",
                "retention_rate",
                "pell_share",
                "student_faculty_ratio",
                "net_price",
                "latitude",
                "longitude",
            ]
        },
        "target_distribution": {
            str(int(key)): int(value)
            for key, value in institutions["low_completion"].value_counts().items()
        },
        "checks": {
            "minimum_source_rows_met": source_rows["scorecard_institution"] >= 5000,
            "unique_unitid": not institutions["unitid"].duplicated().any(),
            "rates_within_0_1": sum(out_of_range.values()) == 0,
        },
    }


def write_data_dictionary() -> None:
    rows = [
        ("unitid", "Mã cơ sở IPEDS", "identifier", "Scorecard/IPEDS", "key"),
        ("institution_name", "Tên cơ sở", "text", "Scorecard/IPEDS", "dimension"),
        ("state", "Mã bang/lãnh thổ", "code", "Scorecard/IPEDS", "geography"),
        ("latitude", "Vĩ độ", "degree", "Scorecard/IPEDS", "geography"),
        ("longitude", "Kinh độ", "degree", "Scorecard/IPEDS", "geography"),
        ("control", "Loại hình quản lý", "category", "IPEDS", "factor"),
        ("locale_group", "Đô thị/ngoại ô/thị trấn/nông thôn", "category", "IPEDS", "factor"),
        ("distance_only", "Cơ sở chỉ đào tạo từ xa", "category", "IPEDS", "factor"),
        ("undergrad_enrollment", "Quy mô sinh viên đại học", "students", "IPEDS", "factor"),
        ("pell_share", "Tỷ lệ sinh viên nhận Pell Grant", "0-1", "IPEDS", "factor"),
        ("federal_loan_share", "Tỷ lệ nhận khoản vay liên bang", "0-1", "IPEDS", "factor"),
        ("student_faculty_ratio", "Số sinh viên trên một giảng viên", "ratio", "IPEDS", "factor"),
        ("net_price", "Chi phí ròng trung bình sau hỗ trợ", "USD", "IPEDS", "factor"),
        ("tuition_in_state", "Học phí trong bang", "USD", "IPEDS", "factor"),
        ("retention_rate", "Tỷ lệ duy trì sau năm đầu", "0-1", "IPEDS", "early_indicator"),
        ("completion_rate", "Tỷ lệ hoàn thành trong 150% thời gian chuẩn", "0-1", "IPEDS", "outcome"),
        ("withdrawal_3yr_rate", "Tỷ lệ rút khỏi cơ sở sau ba năm", "0-1", "NSLDS", "outcome"),
        ("low_completion", "1 nếu completion_rate < 40%", "binary", "derived", "target"),
        ("cip_code", "Mã ngành CIP bốn chữ số", "code", "IPEDS", "key"),
        ("field_name", "Tên nhóm ngành", "text", "IPEDS", "dimension"),
        ("credential_level", "Mã bậc văn bằng", "code", "IPEDS/NSLDS", "dimension"),
        ("credentials_awarded", "Số văn bằng năm gần nhất IPEDSCOUNT2", "awards", "IPEDS", "outcome_supplement"),
    ]
    dictionary = pd.DataFrame(
        rows, columns=["variable", "meaning_vi", "unit", "source", "role"]
    )
    dictionary.to_csv(PROCESSED_DIR / "data_dictionary.csv", index=False, encoding="utf-8-sig")


def build_all() -> dict[str, Path]:
    ensure_runtime_directories()
    project = load_yaml("project.yaml")
    threshold = float(project["model"]["completion_threshold"])

    institution_path = _first_csv(RAW_DIR / "scorecard" / "institution")
    field_path = _first_csv(RAW_DIR / "scorecard" / "field_of_study")
    institution_raw = read_selected_csv(institution_path, INSTITUTION_COLUMNS)
    field_raw = read_selected_csv(field_path, FIELD_COLUMNS)

    institutions = prepare_institutions(
        institution_raw, completion_threshold=threshold
    )
    equity = build_equity_long(institutions)
    state_summary = build_state_summary(institutions)
    field_summary, field_state = prepare_fields(field_raw, institutions)
    ipeds_inventory = build_ipeds_inventory(institutions)
    institution_history = build_institution_history(completion_threshold=threshold)

    outputs = {
        "institutions": PROCESSED_DIR / "institutions.csv",
        "state_summary": PROCESSED_DIR / "state_summary.csv",
        "equity": PROCESSED_DIR / "equity_long.csv",
        "field_summary": PROCESSED_DIR / "field_summary.csv",
        "field_state": PROCESSED_DIR / "field_state_summary.csv",
        "ipeds_inventory": PROCESSED_DIR / "ipeds_inventory.csv",
        "institution_history": PROCESSED_DIR / "institution_history.csv",
        "quality_audit": OUTPUT_DIR / "eda" / "data_quality_audit.json",
    }
    institutions.to_csv(outputs["institutions"], index=False, encoding="utf-8-sig")
    state_summary.to_csv(outputs["state_summary"], index=False, encoding="utf-8-sig")
    equity.to_csv(outputs["equity"], index=False, encoding="utf-8-sig")
    field_summary.to_csv(outputs["field_summary"], index=False, encoding="utf-8-sig")
    field_state.to_csv(outputs["field_state"], index=False, encoding="utf-8-sig")
    ipeds_inventory.to_csv(outputs["ipeds_inventory"], index=False, encoding="utf-8-sig")
    if not institution_history.empty:
        institution_history.to_csv(
            outputs["institution_history"], index=False, encoding="utf-8-sig"
        )

    audit = quality_audit(
        institutions,
        field_summary,
        equity,
        {
            "scorecard_institution": len(institution_raw),
            "scorecard_field_of_study": len(field_raw),
        },
    )
    with outputs["quality_audit"].open("w", encoding="utf-8") as handle:
        audit["processed_rows"]["institution_history"] = len(institution_history)
        audit["history_years"] = (
            sorted(institution_history["academic_year"].dropna().astype(int).unique().tolist())
            if not institution_history.empty
            else []
        )
        json.dump(audit, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    write_data_dictionary()
    return outputs


def parse_args() -> argparse.Namespace:
    return argparse.ArgumentParser(description="Build analysis-ready datasets").parse_args()


def main() -> None:
    parse_args()
    outputs = build_all()
    for key, path in outputs.items():
        print(f"{key}: {path}")


if __name__ == "__main__":
    main()

