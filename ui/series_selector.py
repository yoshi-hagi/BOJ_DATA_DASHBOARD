from datetime import date, datetime
from zoneinfo import ZoneInfo
import unicodedata

import pandas as pd
import streamlit as st

from config import SERIES_GROUPS

from ui.tankan_series_groups import build_tankan_actual_forecast_presets

DISPLAY_COLUMNS = [
    "SERIES_CODE",
    "NAME_OF_TIME_SERIES_J",
    "UNIT_J",
    "FREQUENCY",
    "CATEGORY_J",
    "START_OF_THE_TIME_SERIES",
    "END_OF_THE_TIME_SERIES",
    "LAST_UPDATE",
]


def get_current_fiscal_year(today: date | None = None) -> int:
    """
    当年度を返す。

    判定ルール:
        1月1日〜3月31日: 前年を当年度とする
        4月1日〜12月31日: その年を当年度とする

    例:
        2027-03-31 -> 2026
        2027-04-01 -> 2027
    """

    if today is None:
        today = datetime.now(ZoneInfo("Asia/Tokyo")).date()

    if today.month <= 3:
        return today.year - 1

    return today.year


def get_last_update_cutoff(today: date | None = None) -> int:
    """
    LAST_UPDATE の抽出基準日を YYYYMMDD の整数で返す。

    例:
        当年度が 2026 年の場合 -> 20260331
    """

    fiscal_year = get_current_fiscal_year(today)
    return int(f"{fiscal_year}0331")


def filter_co_by_last_update(
    series_df: pd.DataFrame,
    db: str,
) -> pd.DataFrame:
    """
    COの場合のみ、LAST_UPDATEが当年度+0331以降の系列に絞り込む。
    """

    if db != "CO":
        return series_df

    if "LAST_UPDATE" not in series_df.columns:
        return series_df

    filtered_df = series_df.copy()

    last_update = pd.to_numeric(
        filtered_df["LAST_UPDATE"],
        errors="coerce",
    )

    cutoff = get_last_update_cutoff()

    filtered_df = filtered_df[last_update >= cutoff]

    return filtered_df


def extract_base_year_from_unit(unit: object) -> float:
    """
    UNIT_J の先頭4文字を基準年として抽出する。

    例:
        "2020年基準=100" -> 2020
        "２０１５年基準=100" -> 2015

    数値化できない場合は NaN を返す。
    """

    if pd.isna(unit):
        return float("nan")

    normalized_unit = unicodedata.normalize("NFKC", str(unit))
    base_year_text = normalized_unit[:4]

    return pd.to_numeric(base_year_text, errors="coerce")


def filter_price_index_by_latest_base_year(
    series_df: pd.DataFrame,
    db: str,
) -> pd.DataFrame:
    """
    PR01・PR02の場合のみ、UNIT_Jの先頭4文字で表される基準年が
    最大の系列だけに絞り込む。
    """

    if db not in {"PR01", "PR02"}:
        return series_df

    if "UNIT_J" not in series_df.columns:
        return series_df

    filtered_df = series_df.copy()

    base_year = filtered_df["UNIT_J"].apply(extract_base_year_from_unit)

    max_base_year = base_year.max(skipna=True)

    if pd.isna(max_base_year):
        return filtered_df

    filtered_df = filtered_df[base_year == max_base_year]

    return filtered_df


def filter_series_df(
    series_df: pd.DataFrame,
    db: str,
    selected_frequency: str,
    keyword: str,
) -> pd.DataFrame:
    """
    期種とキーワードで系列マスターを絞り込む。

    DB別の共通フィルタは apply_db_specific_series_filters() 側で適用する。
    """

    filtered_df = series_df.copy()

    if selected_frequency != "すべて":
        filtered_df = filtered_df[filtered_df["FREQUENCY"] == selected_frequency]

    if keyword:
        mask = (
            filtered_df["SERIES_CODE"]
            .astype(str)
            .str.contains(keyword, case=False, na=False)
            | filtered_df["NAME_OF_TIME_SERIES_J"]
            .astype(str)
            .str.contains(keyword, case=False, na=False)
            | filtered_df["CATEGORY_J"]
            .astype(str)
            .str.contains(keyword, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    return filtered_df


def render_series_group_selector(
    db: str,
    series_df: pd.DataFrame,
) -> tuple[str | None, list[str] | None]:
    """
    DB別のプリセット系列グループを表示する。

    config.py の固定プリセットに加えて、
    PR01・PR02ではメタデータから動的プリセットを作成する。
    """

    fixed_group_options = SERIES_GROUPS.get(db, {})

    dynamic_group_options = make_price_index_preset_groups(
        series_df=series_df,
        db=db,
    )

    group_options = {
        **fixed_group_options,
        **dynamic_group_options,
    }

    if not group_options:
        return None, None

    st.subheader("1. 系列コードの選択")

    use_group = st.checkbox(
        "プリセット系列グループを使用する",
        value=True,
    )

    if not use_group:
        return None, None

    selected_group_name = st.selectbox(
        "系列グループを選択",
        options=list(group_options.keys()),
    )

    selected_group = group_options[selected_group_name]
    selected_codes = selected_group["codes"]

    description = selected_group.get("description")

    if description:
        st.info(f"「{selected_group_name}」として、{description}をまとめて取得します。")
    else:
        st.info(
            f"「{selected_group_name}」として、以下の系列コードをまとめて取得します。"
        )

    st.code(", ".join(selected_codes))

    st.caption(f"系列数: {len(selected_codes)}")

    group_options = get_series_group_options(
        db=db,
        series_df=series_df,
    )

    return selected_group_name, selected_codes


def apply_db_specific_series_filters(
    series_df: pd.DataFrame,
    db: str,
) -> pd.DataFrame:
    """
    DB別の共通系列フィルタを適用する。

    - CO: LAST_UPDATE で絞り込み
    - PR01・PR02:
        - PR01: CATEGORY_J に含まれる "/" が1つのみ
        - PR02: CATEGORY_J に "/" を含まない
        - UNIT_J の先頭4文字で表される最新基準年に絞り込み
    """

    filtered_df = series_df.copy()

    filtered_df = filter_co_by_last_update(
        series_df=filtered_df,
        db=db,
    )

    filtered_df = filter_price_index_by_category_slash_count(
        series_df=filtered_df,
        db=db,
    )

    filtered_df = filter_price_index_by_latest_base_year(
        series_df=filtered_df,
        db=db,
    )

    return filtered_df


def render_series_selector(
    db: str,
    series_df: pd.DataFrame,
) -> tuple[list[str] | None, str | None, dict | None]:
    """
    系列コード選択UIを表示し、選択された系列コード・グループ名・グループ設定を返す。

    Returns:
        tuple[list[str] | None, str | None, dict | None]:
            選択系列コード, 選択グループ名, 選択グループ設定
    """

    # プリセットにも通常選択にも、DB別フィルタを共通適用する
    base_filtered_df = apply_db_specific_series_filters(
        series_df=series_df,
        db=db,
    )

    selected_group_name, group_codes, selected_group_config = (
        render_series_group_selector(
            db=db,
            series_df=base_filtered_df,
        )
    )

    if group_codes:
        missing_codes = [
            code
            for code in group_codes
            if code not in base_filtered_df["SERIES_CODE"].astype(str).tolist()
        ]

        if missing_codes:
            st.warning(
                "メタデータ上で確認できない系列コードがあります。"
                "API取得時にエラーになる可能性があります。"
            )
            st.code(", ".join(missing_codes))

        return group_codes, selected_group_name, selected_group_config

    st.subheader("1. 系列コードの選択")

    col1, col2 = st.columns([1, 2])

    with col1:
        frequency_options = sorted(
            [x for x in base_filtered_df["FREQUENCY"].dropna().unique()]
        )

        selected_frequency = st.selectbox(
            "期種で絞り込み",
            options=["すべて"] + frequency_options,
        )

    with col2:
        keyword = st.text_input(
            "系列名・系列コードで検索",
            value="",
            placeholder="例：企業物価、サービス価格、大類別",
        )

    filtered_df = filter_series_df(
        series_df=base_filtered_df,
        db=db,
        selected_frequency=selected_frequency,
        keyword=keyword,
    )

    if db in PRICE_INDEX_DBS and "UNIT_J" in series_df.columns:
        base_year = series_df["UNIT_J"].apply(extract_base_year_from_unit)
        max_base_year = base_year.max(skipna=True)

        if pd.notna(max_base_year):
            st.caption(
                f"{db}は UNIT_J の先頭4文字で表される基準年が "
                f"{int(max_base_year)} の系列のみ表示しています。"
            )

    display_columns = [col for col in DISPLAY_COLUMNS if col in filtered_df.columns]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        height=300,
    )

    if filtered_df.empty:
        st.warning("条件に一致する系列がありません。")
        return None, None, None

    options = filtered_df["SERIES_CODE"].astype(str).tolist()

    code_label_map = {
        str(row["SERIES_CODE"]): (
            f'{row["SERIES_CODE"]}｜{row["NAME_OF_TIME_SERIES_J"]}'
        )
        for _, row in filtered_df.iterrows()
    }

    selected_codes = st.multiselect(
        "取得する系列を選択",
        options=options,
        format_func=lambda x: code_label_map.get(x, x),
        max_selections=10,
    )

    if not selected_codes:
        st.info("系列コードを1つ以上選択してください。")
        return None, None, None

    return selected_codes, None, None


def get_series_group_options(
    db: str,
    series_df: pd.DataFrame,
) -> dict[str, dict]:
    """
    DB別のプリセット系列グループを取得する。

    - config.py の静的プリセット
    - CO の実績・予測ペア動的プリセット
    - PR01・PR02 の大類別・類別動的プリセット

    を統合して返す。
    """

    db = str(db).strip().upper()

    group_options = dict(SERIES_GROUPS.get(db, {}))

    if db == "CO":
        tankan_groups = build_tankan_actual_forecast_presets(series_df)
        group_options.update(tankan_groups)

    if db in {"PR01", "PR02"}:
        price_index_groups = make_price_index_preset_groups(
            series_df=series_df,
            db=db,
        )
        group_options.update(price_index_groups)

    return group_options


def render_series_group_selector(
    db: str,
    series_df: pd.DataFrame,
) -> tuple[str | None, list[str] | None, dict | None]:
    """
    DB別のプリセット系列グループを表示する。

    Returns:
        tuple:
            selected_group_name,
            selected_codes,
            selected_group_config
    """

    group_options = get_series_group_options(
        db=db,
        series_df=series_df,
    )

    if not group_options:
        return None, None, None

    st.subheader("1. 系列コードの選択")

    use_group = st.checkbox(
        "プリセット系列グループを使用する",
        value=True,
    )

    if not use_group:
        return None, None, None

    selected_group_name = st.selectbox(
        "系列グループを選択",
        options=list(group_options.keys()),
    )

    selected_group_config = group_options[selected_group_name]
    selected_codes = selected_group_config["codes"]

    st.info(f"「{selected_group_name}」として、以下の系列コードをまとめて取得します。")

    st.code(", ".join(selected_codes))

    if (
        db == "CO"
        and selected_group_config.get("chart_type") == "tankan_actual_forecast"
    ):
        fields = selected_group_config.get("fields", {})
        labels = fields.get("labels", {})

        st.caption(
            f"実績: {fields.get('actual')} / "
            f"予測: {fields.get('forecast')} / "
            f"期種: {fields.get('frequency')}"
        )

        base_name = labels.get("base")
        if base_name:
            st.caption(f"系列名: {base_name}")

    return selected_group_name, selected_codes, selected_group_config


def validate_selected_frequency(
    series_df: pd.DataFrame,
    selected_codes: list[str],
) -> bool:
    """選択系列の期種が混在していないか確認する"""

    selected_meta = series_df[series_df["SERIES_CODE"].isin(selected_codes)]

    if selected_meta.empty:
        st.warning(
            "選択された系列コードがメタデータ上で確認できませんでした。"
            "そのままAPI取得を試行します。"
        )
        return True

    if selected_meta["FREQUENCY"].nunique(dropna=True) > 1:
        st.error(
            "選択された系列の期種が混在しています。"
            "コードAPIでは同じ期種の系列のみ複数指定できます。"
        )
        st.dataframe(
            selected_meta[["SERIES_CODE", "NAME_OF_TIME_SERIES_J", "FREQUENCY"]],
            use_container_width=True,
        )
        return False

    return True


# 以下、物価指数をの系列コードをプリセット化するための関数
PRICE_INDEX_DBS = {"PR01", "PR02"}


def normalize_text(value: object) -> str:
    """
    文字列を比較しやすい形に正規化する。
    全角・半角ゆれを吸収し、前後空白を除去する。
    """

    if pd.isna(value):
        return ""

    return unicodedata.normalize("NFKC", str(value)).strip()


def startswith_normalized(series: pd.Series, prefix: str) -> pd.Series:
    """
    Series内の文字列を正規化したうえで startswith 判定する。
    """

    normalized_prefix = normalize_text(prefix)

    return series.apply(lambda x: normalize_text(x).startswith(normalized_prefix))


def make_price_index_preset_groups(
    series_df: pd.DataFrame,
    db: str,
) -> dict[str, dict]:
    """
    PR01・PR02用の動的プリセットを作成する。

    NAME_OF_TIME_SERIES_J が以下で始まる系列をまとめる。
        - 大類別
        - 類別

    前提:
        series_df は、すでに最新基準年フィルタ適用後のDataFrame。
    """

    if db not in PRICE_INDEX_DBS:
        return {}

    required_cols = {"SERIES_CODE", "NAME_OF_TIME_SERIES_J"}

    if not required_cols.issubset(series_df.columns):
        return {}

    preset_definitions = {
        "大類別": "大類別",
        "類別": "類別",
    }

    groups: dict[str, dict] = {}

    for group_label, prefix in preset_definitions.items():
        mask = startswith_normalized(
            series_df["NAME_OF_TIME_SERIES_J"],
            prefix,
        )

        group_df = series_df.loc[mask].copy()

        if group_df.empty:
            continue

        codes = group_df["SERIES_CODE"].astype(str).dropna().drop_duplicates().tolist()

        groups[f"{db} {group_label}"] = {
            "chart_type": "line",
            "codes": codes,
            "source": "metadata",
            "description": f"NAME_OF_TIME_SERIES_J が「{prefix}」で始まる系列",
        }

    return groups


def filter_price_index_by_category_slash_count(
    series_df: pd.DataFrame,
    db: str,
) -> pd.DataFrame:
    """
    PR01・PR02の場合のみ、CATEGORY_J の "/" の個数で系列を絞り込む。

    条件:
        PR01: CATEGORY_J に含まれる "/" が1つのみ
        PR02: CATEGORY_J に "/" を含まない
    """

    db = str(db).strip().upper()

    if db not in {"PR01", "PR02"}:
        return series_df

    if "CATEGORY_J" not in series_df.columns:
        return series_df

    filtered_df = series_df.copy()

    category = filtered_df["CATEGORY_J"].astype(str)

    slash_count = category.str.count("/")

    if db == "PR01":
        filtered_df = filtered_df[category.str.endswith("/国内企業物価指数", na=False)]

    elif db == "PR02":
        filtered_df = filtered_df[slash_count == 0]

    return filtered_df
