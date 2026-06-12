DB_OPTIONS = {
    "FM01": "無担保コールO/N物レート",
    "FM08": "外国為替市況",
    "FM09": "実効為替レート",
    "MD01": "マネタリーベース",
    "MD02": "マネーストック",
    "MD10": "預金者別預金",
    "CO": "短観",
    "PR01": "企業物価指数",
    "PR02": "企業向けサービス価格指数",
    "BP01": "国際収支統計",
    "FF": "資金循環",
}

BOJ_CREDIT = (
    "このサービスは、日本銀行時系列統計データ検索サイトの API 機能を使用しています。"
    "サービスの内容は日本銀行によって保証されたものではありません。"
)


SERIES_GROUPS = {
    "FM01": {
        "コールレートチャート": {
            "chart_type": "call_rate",
            "codes": [
                "STRDCLUCON",  # 平均値
                "STRDCLUCONH",  # 最高値
                "STRDCLUCONL",  # 最低値
                "STRDCLUCV",  # 出来高
            ],
            "fields": {
                "average": "STRDCLUCON",
                "high": "STRDCLUCONH",
                "low": "STRDCLUCONL",
                "volume": "STRDCLUCV",
                "labels": {
                    "average": "平均値",
                    "high": "最高値",
                    "low": "最低値",
                    "volume": "出来高",
                    "range": "最高値・最低値レンジ",
                },
            },
        },
    },
    "FM08": {
        "ドル円市況": {
            "chart_type": "exchange_market",
            "codes": [
                "FXERD01",
                "FXERD02",
                "FXERD03",
                "FXERD04",
                "FXERD05",
                "FXERD06",
                "FXERD07",
            ],
            "fields": {
                "open": "FXERD01",
                "high": "FXERD02",
                "low": "FXERD03",
                "close": "FXERD04",
                "line": "FXERD05",
                "line_label": "中心相場",
                "bars": ["FXERD06", "FXERD07"],
                "bar_labels": {
                    "FXERD06": "スポット出来高",
                    "FXERD07": "スワップ出来高",
                },
            },
        },
        "ユーロドル市況": {
            "chart_type": "exchange_market",
            "codes": [
                "FXERD31",
                "FXERD32",
                "FXERD33",
                "FXERD34",
                "FXERD35",
                "FXERD36",
            ],
            "fields": {
                "open": "FXERD31",
                "high": "FXERD32",
                "low": "FXERD33",
                "close": "FXERD34",
                "line": None,
                "line_label": None,
                "bars": ["FXERD35", "FXERD36"],
                "bar_labels": {
                    "FXERD35": "スポット出来高",
                    "FXERD36": "スワップ出来高",
                },
            },
        },
    },
    "MD01": {
        "マネタリーベースチャート": {
            "chart_type": "monetary_base",
            "codes": [
                "MABS1AN11",  # マネタリーベース平均残高
                "MABS2AN116",  # うち 日本銀行券発行高
                "MABS2AN117",  # うち 貨幣流通高
                "MABS1AN113",  # うち 日銀当座預金
            ],
            "fields": {
                "total": "MABS1AN11",
                "components": [
                    "MABS2AN116",
                    "MABS2AN117",
                    "MABS1AN113",
                ],
                "labels": {
                    "total": "マネタリーベース平均残高",
                    "MABS2AN116": "日本銀行券発行高",
                    "MABS2AN117": "貨幣流通高",
                    "MABS1AN113": "日銀当座預金",
                },
            },
        },
    },
}
