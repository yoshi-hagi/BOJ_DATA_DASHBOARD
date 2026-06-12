import pandas as pd

ACTUAL_FLAG = "0"
FORECAST_FLAG = "1"

ACTUAL_SUFFIX = "実績"
FORECAST_SUFFIX = "予測"


def get_code_forecast_flag(series_code: str) -> str | None:
    """
    CO系列コードから実績/予測フラグを取得する。

    ルール:
        右から5桁目が "0" -> 実績
        右から5桁目が "1" -> 予測

    Returns:
        "actual" / "forecast" / None
    """

    code = str(series_code)

    if len(code) < 5:
        return None

    flag = code[-5]

    if flag == ACTUAL_FLAG:
        return "actual"

    if flag == FORECAST_FLAG:
        return "forecast"

    return None


def make_tankan_pair_key(series_code: str) -> str | None:
    """
    実績/予測を同一系列として扱うためのキーを作る。

    例:
        右から5桁目だけが 0/1 で異なる場合、
        その位置を "*" に置換して同じキーにする。
    """

    code = str(series_code)

    if len(code) < 5:
        return None

    flag = code[-5]

    if flag not in {ACTUAL_FLAG, FORECAST_FLAG}:
        return None

    chars = list(code)
    chars[-5] = "*"

    return "".join(chars)


def get_name_forecast_flag(name: str) -> str | None:
    """
    系列名称から実績/予測を判定する。

    ルール:
        NAME_OF_TIME_SERIES_J の右から2文字が 実績/予測
    """

    value = str(name)

    if value.endswith(ACTUAL_SUFFIX):
        return "actual"

    if value.endswith(FORECAST_SUFFIX):
        return "forecast"

    return None


def make_tankan_base_name(name: str) -> str:
    """
    系列名称から末尾の「実績」「予測」を除いた表示名を作る。
    """

    value = str(name)

    if value.endswith(ACTUAL_SUFFIX):
        return value[: -len(ACTUAL_SUFFIX)]

    if value.endswith(FORECAST_SUFFIX):
        return value[: -len(FORECAST_SUFFIX)]

    return value


def add_tankan_actual_forecast_columns(series_df: pd.DataFrame) -> pd.DataFrame:
    """
    CO系列マスターに、実績/予測分類用の補助列を追加する。
    """

    required_cols = ["SERIES_CODE", "NAME_OF_TIME_SERIES_J"]

    missing_cols = [col for col in required_cols if col not in series_df.columns]
    if missing_cols:
        raise ValueError(f"必要な列がありません: {missing_cols}")

    df = series_df.copy()
    df.columns = df.columns.map(str)

    df["SERIES_CODE"] = df["SERIES_CODE"].astype(str)
    df["NAME_OF_TIME_SERIES_J"] = df["NAME_OF_TIME_SERIES_J"].astype(str)

    df["TANKAN_CODE_CLASS"] = df["SERIES_CODE"].map(get_code_forecast_flag)
    df["TANKAN_NAME_CLASS"] = df["NAME_OF_TIME_SERIES_J"].map(get_name_forecast_flag)

    # 系列コードと系列名の判定が一致するものだけ採用する
    df["TANKAN_CLASS"] = df["TANKAN_CODE_CLASS"].where(
        df["TANKAN_CODE_CLASS"] == df["TANKAN_NAME_CLASS"]
    )

    df["TANKAN_PAIR_KEY"] = df["SERIES_CODE"].map(make_tankan_pair_key)
    df["TANKAN_BASE_NAME"] = df["NAME_OF_TIME_SERIES_J"].map(make_tankan_base_name)

    return df


def build_tankan_actual_forecast_presets(
    series_df: pd.DataFrame,
) -> dict[str, dict]:
    """
    CO系列マスターから、実績・予測ペアのプリセットを動的に作る。

    抽出条件:
        - 系列コードの右から5桁目が 0/1
        - NAME_OF_TIME_SERIES_J の末尾が 実績/予測
        - 実績・予測の期種が一致
        - UNIT_J が "%ポイント"
    """

    df = add_tankan_actual_forecast_columns(series_df)

    # UNIT_J が %ポイント の系列だけに絞る
    if "UNIT_J" not in df.columns:
        raise ValueError("必要な列がありません: ['UNIT_J']")

    df["UNIT_J"] = df["UNIT_J"].astype(str).str.strip()
    df = df[df["UNIT_J"] == "%ポイント"]

    # 実績/予測として正しく判定できた行だけ対象
    df = df.dropna(
        subset=[
            "TANKAN_CLASS",
            "TANKAN_PAIR_KEY",
            "TANKAN_BASE_NAME",
            "FREQUENCY",
            "UNIT_J",
        ]
    )

    presets: dict[str, dict] = {}

    for pair_key, group_df in df.groupby("TANKAN_PAIR_KEY", dropna=True):
        actual_df = group_df[group_df["TANKAN_CLASS"] == "actual"]
        forecast_df = group_df[group_df["TANKAN_CLASS"] == "forecast"]

        if actual_df.empty or forecast_df.empty:
            continue

        # 同一ペア内で期種が混在する場合は、コードAPIでまとめて取れないため除外
        if group_df["FREQUENCY"].nunique(dropna=True) != 1:
            continue

        # 念のため、同一ペア内の単位が混在する場合も除外
        if group_df["UNIT_J"].nunique(dropna=True) != 1:
            continue

        actual_row = actual_df.iloc[0]
        forecast_row = forecast_df.iloc[0]

        actual_code = str(actual_row["SERIES_CODE"])
        forecast_code = str(forecast_row["SERIES_CODE"])

        base_name = str(actual_row["TANKAN_BASE_NAME"]).strip()
        frequency = str(actual_row["FREQUENCY"])
        unit = str(actual_row["UNIT_J"])

        preset_name = f"{base_name}｜実績・予測"

        presets[preset_name] = {
            "chart_type": "tankan_actual_forecast",
            "codes": [
                actual_code,
                forecast_code,
            ],
            "fields": {
                "actual": actual_code,
                "forecast": forecast_code,
                "labels": {
                    "actual": "実績",
                    "forecast": "予測",
                    "base": base_name,
                },
                "frequency": frequency,
                "unit": unit,
                "pair_key": pair_key,
            },
        }

    return presets
