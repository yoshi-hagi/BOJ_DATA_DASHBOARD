import requests
import pandas as pd
import time


def get_series_code(db: str):
    """：メタデータAPIより、系列コードを取得する関数
    Args:
        db (str): DB名

    Returns:
        _type_: 系列コードと系列コード名称のデータフレーム
    """
    boj_meta_url = "https://www.stat-search.boj.or.jp/api/v1/getMetadata"
    base_boj_meta_params = {
        "format": "json",
        "lang": "jp",
        "db": db,
    }

    boj_meta_res = requests.get(
        boj_meta_url,
        params=base_boj_meta_params,
        headers={"Accept-Encoding": "gzip"},
        timeout=120,
    )
    boj_meta_res.raise_for_status()
    boj_meta_json = boj_meta_res.json()
    status = boj_meta_json.get("STATUS")
    if status is not None and int(status) != 200:
        raise RuntimeError(
            f"API error: STATUS={status} "
            f"MESSAGEID={boj_meta_json.get('MESSAGEID')} "
            f"MESSAGE={boj_meta_json.get('MESSAGE')}"
        )

    series_code_df = pd.DataFrame(
        [
            {
                "SERIES_CODE": item.get("SERIES_CODE"),
                "NAME_OF_TIME_SERIES_J": item.get("NAME_OF_TIME_SERIES_J"),
                "UNIT_J": item.get("UNIT_J"),
                "FREQUENCY": item.get("FREQUENCY"),
                "CATEGORY_J": item.get("CATEGORY_J"),
                "START_OF_THE_TIME_SERIES": item.get("START_OF_THE_TIME_SERIES"),
                "END_OF_THE_TIME_SERIES": item.get("END_OF_THE_TIME_SERIES"),
                "LAST_UPDATE": item.get("LAST_UPDATE"),
            }
            for item in boj_meta_json["RESULTSET"]
            if item.get("SERIES_CODE")
        ]
    )

    # SERIES_CODE の重複を除去
    series_code_df = series_code_df.drop_duplicates(
        subset="SERIES_CODE",
    ).reset_index(drop=True)

    # NAME_OF_TIME_SERIES_J における更新停止などの系列を除外
    exclude_words = ["更新停止", "6版組替", "参考"]

    pattern = "|".join(exclude_words)
    series_code_df = series_code_df[
        ~series_code_df["NAME_OF_TIME_SERIES_J"]
        .fillna("")
        .str.contains(pattern, na=False)
    ].reset_index(drop=True)

    return series_code_df


def get_boj_data_per_page(
    db: str,
    codes: list[str],
    start_date: str,
    end_date: str,
    start_position: int | None = None,
    lang: str = "jp",
    timeout: int = 120,
) -> dict:
    """_summary_：コードAPIより、1ページ分のデータを取得
    Args:
        db (str): DB名
        codes (list[str]): 系列コード
        start_date (str): 開始期
        end_date (str): 終了期
        start_position (int | None, optional): 検索開始位置。デフォルトはNone
        lang (str, optional): 言語。デフォルトは日本語
        timeout (int, optional): タイムアウト。デフォルトは2分

    Returns:
        dict: コードAPIより取得した、1ページ分のJSON
    """
    BASE = "https://www.stat-search.boj.or.jp/api/v1"
    url = f"{BASE}/getDataCode"
    params = {
        "db": db,
        "code": ",".join(codes),  # 同一期種のみ複数指定可
        "startDate": start_date,
        "endDate": end_date,
        "format": "json",
        "lang": lang,
    }
    if start_position is not None:
        params["startPosition"] = str(start_position)

    r = requests.get(
        url,
        params=params,
        headers={"Accept-Encoding": "gzip"},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


def get_all_boj_data(
    db: str,
    codes: list[str],
    start_date: str,
    end_date: str,
    lang: str = "jp",
    sleep_sec: float = 1.0,
) -> dict:
    """_summary_：コードAPIより、複数ページのデータを取得し、結合して1つのJSONにして返す
    Args:
        db (str): DB名
        codes (list[str]): 系列コード
        start_date (str): 開始期
        end_date (str): 終了期
        lang (str, optional): 言語。デフォルトは日本語
        sleep_sec (float, optional): 連続リクエストをするときの待機時間

    Raises:
        RuntimeError: ランタイムエラー

    Returns:
        dict: 複数ページのデータを結合したJSON
    """
    all_resultset = []
    start_pos = None
    first_payload = None

    while True:
        payload = get_boj_data_per_page(
            db=db,
            codes=codes,
            start_date=start_date,
            end_date=end_date,
            start_position=start_pos,
            lang=lang,
        )
        if first_payload is None:
            first_payload = payload

        # APIステータスチェック（200以外はエラー扱い）
        status = payload.get("STATUS")
        if status is not None and int(status) != 200:
            raise RuntimeError(
                f"API error: STATUS={status} MESSAGEID={payload.get('MESSAGEID')} MESSAGE={payload.get('MESSAGE')}"
            )

        # 1ページ分を蓄積
        all_resultset.extend(payload.get("RESULTSET", []))

        # 続きがあるか？
        next_pos = payload.get("NEXTPOSITION")
        if not next_pos:
            break

        start_pos = int(next_pos)
        time.sleep(sleep_sec)

    # 最初のpayloadをベースに、RESULTSET を全件に差し替えて返す
    merged_boj_data = dict(first_payload) if first_payload else {}
    merged_boj_data["RESULTSET"] = all_resultset
    merged_boj_data["NEXTPOSITION"] = None
    return merged_boj_data


def resultset_to_df(payload: dict) -> pd.DataFrame:
    """
    payload["RESULTSET"] を横持ち DataFrame に変換する。
    - 1行 = 1系列
    - columns = SURVEY_DATES（例: 202504, 202505, ...）
    - values  = VALUES（欠損は None→NaN）
    - SERIES_CODE 等のメタ列も左側に保持
    """
    resultset = payload.get("RESULTSET", [])
    if not isinstance(resultset, list) or len(resultset) == 0:
        return pd.DataFrame()

    rows = []
    for s in resultset:
        v = s.get("VALUES") or {}
        dates = v.get("SURVEY_DATES") or []
        values = v.get("VALUES") or []

        # 時系列部分（SURVEY_DATES -> 値）
        row = dict(zip(dates, values))

        # RESULTSET のメタ情報（必要に応じて増減OK）
        row.update(
            {
                "SERIES_CODE": s.get("SERIES_CODE"),
                "NAME_OF_TIME_SERIES_J": s.get("NAME_OF_TIME_SERIES_J"),
                "UNIT_J": s.get("UNIT_J"),
                "FREQUENCY": s.get("FREQUENCY"),
                "CATEGORY_J": s.get("CATEGORY_J"),
                "LAST_UPDATE": s.get("LAST_UPDATE"),
            }
        )
        rows.append(row)

    df = pd.DataFrame(rows)

    # 列順：メタ列 → 日付列（昇順）
    meta_cols = [
        "SERIES_CODE",
        "NAME_OF_TIME_SERIES_J",
        "UNIT_J",
        "FREQUENCY",
        "CATEGORY_J",
        "LAST_UPDATE",
    ]
    date_cols = sorted([c for c in df.columns if isinstance(c, int)])

    # 日付が文字列で来るケースもあるなら、こちらに置換（保険）
    if not date_cols:
        date_cols = sorted([c for c in df.columns if str(c).isdigit()])

    keep_cols = [c for c in meta_cols if c in df.columns] + date_cols
    return df[keep_cols]


def resultset_to_long_df(payload: dict) -> pd.DataFrame:
    """
    グラフ表示しやすい縦持ちDataFrameに変換する。
    1行 = 1系列・1時点
    """

    wide_df = resultset_to_df(payload)

    if wide_df.empty:
        return wide_df

    meta_cols = [
        "SERIES_CODE",
        "NAME_OF_TIME_SERIES_J",
        "UNIT_J",
        "FREQUENCY",
        "CATEGORY_J",
        "LAST_UPDATE",
    ]

    existing_meta_cols = [c for c in meta_cols if c in wide_df.columns]
    value_cols = [c for c in wide_df.columns if c not in existing_meta_cols]

    long_df = wide_df.melt(
        id_vars=existing_meta_cols,
        value_vars=value_cols,
        var_name="SURVEY_DATE",
        value_name="VALUE",
    )

    long_df["SURVEY_DATE"] = long_df["SURVEY_DATE"].astype(str)
    long_df["SURVEY_DATE_LABEL"] = long_df["SURVEY_DATE"].apply(
        format_survey_date_yyyy_mm
    )
    long_df["VALUE"] = pd.to_numeric(long_df["VALUE"], errors="coerce")

    long_df = long_df.dropna(subset=["VALUE"]).reset_index(drop=True)

    return long_df


def format_survey_date_yyyy_mm(value: str) -> str:
    """
    SURVEY_DATEを YYYY-MM 表示に変換する。

    主な想定:
    - 202501   -> 2025-01
    - 20250101 -> 2025-01
    - 2025     -> 2025
    """

    s = str(value)

    # YYYYMM または YYYYQQ 形式
    if len(s) == 6 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}"

    # YYYYMMDD 形式
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}"

    # YYYY 形式などはそのまま返す
    return s
