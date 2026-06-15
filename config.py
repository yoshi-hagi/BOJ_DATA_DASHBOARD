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
    "MD10": {
        "一般法人預金": {
            "chart_type": "depositor_deposits",
            "codes": [
                # 上段: 積み上げ棒グラフ
                "DLDDLKY42111_DLDD3DB201",
                "DLDDLKY42211_DLDD3DB202",
                "DLDDLKY42311_DLDD3DB203",
                "DLDDLKY42411_DLDD3DB204",
                "DLDDLKY42511_DLDD3DB205",
                "DLDDLKY42611_DLDD3DB206",
                # 下段: 折れ線グラフ
                "DLDDLKY45011_DLDD3DB2TL",
            ],
            "fields": {
                "bars": [
                    "DLDDLKY42111_DLDD3DB201",
                    "DLDDLKY42211_DLDD3DB202",
                    "DLDDLKY42311_DLDD3DB203",
                    "DLDDLKY42411_DLDD3DB204",
                    "DLDDLKY42511_DLDD3DB205",
                    "DLDDLKY42611_DLDD3DB206",
                ],
                "line": "DLDDLKY45011_DLDD3DB2TL",
                "line_label": "一般法人預金 合計",
                "top_yaxis_title": "一般法人預金 内訳",
                "bottom_yaxis_title": "一般法人預金 合計",
            },
        },
        "個人預金": {
            "chart_type": "depositor_deposits",
            "codes": [
                # 上段: 積み上げ棒グラフ
                "DLDDLKY42112_DLDD3DB301",
                "DLDDLKY42212_DLDD3DB302",
                "DLDDLKY42312_DLDD3DB303",
                "DLDDLKY42412_DLDD3DB304",
                "DLDDLKY42512_DLDD3DB305",
                "DLDDLKY42612_DLDD3DB306",
                # 下段: 折れ線グラフ
                "DLDDLKY45012_DLDD3DB3TL",
            ],
            "fields": {
                "bars": [
                    "DLDDLKY42112_DLDD3DB301",
                    "DLDDLKY42212_DLDD3DB302",
                    "DLDDLKY42312_DLDD3DB303",
                    "DLDDLKY42412_DLDD3DB304",
                    "DLDDLKY42512_DLDD3DB305",
                    "DLDDLKY42612_DLDD3DB306",
                ],
                "line": "DLDDLKY45012_DLDD3DB3TL",
                "line_label": "個人預金 合計",
                "top_yaxis_title": "個人預金 内訳",
                "bottom_yaxis_title": "個人預金 合計",
            },
        },
    },
    "BP01": {
        "経常収支チャート": {
            "chart_type": "current_account",
            "codes": [
                "BPBP6JYNCB",  # 経常収支
                "BPBP6JYNTB",  # 貿易収支
                "BPBP6JYNSN",  # サービス収支
                "BPBP6JYNPIN",  # 第一次所得収支
                "BPBP6JYNSIN",  # 第二次所得収支
            ],
            "fields": {
                "total": "BPBP6JYNCB",
                "components": [
                    "BPBP6JYNTB",
                    "BPBP6JYNSN",
                    "BPBP6JYNPIN",
                    "BPBP6JYNSIN",
                ],
                "labels": {
                    "total": "経常収支",
                    "BPBP6JYNCB": "経常収支",
                    "BPBP6JYNTB": "貿易収支",
                    "BPBP6JYNSN": "サービス収支",
                    "BPBP6JYNPIN": "第一次所得収支",
                    "BPBP6JYNSIN": "第二次所得収支",
                },
            },
        },
        "貿易・サービス収支チャート": {
            "chart_type": "trade_services",
            "codes": [
                "BPBP6JYNTS",  # 貿易・サービス収支
                "BPBP6JYNTB1",  # 一般商品
                "BPBP6JYNTB2",  # 仲介貿易商品
                "BPBP6JYNTB3",  # 非貨幣金
                "BPBP6JYNSN1",  # サービス/輸送
                "BPBP6JYNSN2",  # サービス/旅行
                "BPBP6JYNSN9",  # サービス/その他サービス
            ],
            "fields": {
                "total": "BPBP6JYNTS",
                "components": [
                    "BPBP6JYNTB1",
                    "BPBP6JYNTB2",
                    "BPBP6JYNTB3",
                    "BPBP6JYNSN1",
                    "BPBP6JYNSN2",
                    "BPBP6JYNSN9",
                ],
                "labels": {
                    "total": "貿易・サービス収支",
                    "BPBP6JYNTS": "貿易・サービス収支",
                    "BPBP6JYNTB1": "一般商品",
                    "BPBP6JYNTB2": "仲介貿易商品",
                    "BPBP6JYNTB3": "非貨幣金",
                    "BPBP6JYNSN1": "サービス/輸送",
                    "BPBP6JYNSN2": "サービス/旅行",
                    "BPBP6JYNSN9": "サービス/その他サービス",
                },
            },
        },
        "第一次所得収支チャート": {
            "chart_type": "primary_income",
            "codes": [
                "BPBP6JYNPIN",  # 第一次所得収支
                "BPBP6JYNPIN1",  # 雇用者報酬
                "BPBP6JYNPIN211",  # 直接投資収益/出資所得
                "BPBP6JYNPIN212",  # 直接投資収益/利子所得
                "BPBP6JYNPIN221",  # 投資収益/証券投資収益/配当金
                "BPBP6JYNPIN222",  # 投資収益/証券投資収益/債券利子
                "BPBP6JYNPIN291",  # 投資収益/その他投資収益/出資所得
                "BPBP6JYNPIN292",  # 投資収益/その他投資収益/利子所得
                "BPBP6JYNPIN9",  # その他第一次所得
            ],
            "fields": {
                "total": "BPBP6JYNPIN",
                "components": [
                    "BPBP6JYNPIN1",
                    "BPBP6JYNPIN211",
                    "BPBP6JYNPIN212",
                    "BPBP6JYNPIN221",
                    "BPBP6JYNPIN222",
                    "BPBP6JYNPIN291",
                    "BPBP6JYNPIN292",
                    "BPBP6JYNPIN9",
                ],
                "labels": {
                    "total": "第一次所得収支",
                    "BPBP6JYNPIN": "第一次所得収支",
                    "BPBP6JYNPIN1": "雇用者報酬",
                    "BPBP6JYNPIN211": "直接投資収益／出資所得",
                    "BPBP6JYNPIN212": "直接投資収益／利子所得",
                    "BPBP6JYNPIN221": "証券投資収益／配当金",
                    "BPBP6JYNPIN222": "証券投資収益／債券利子",
                    "BPBP6JYNPIN291": "その他投資収益／出資所得",
                    "BPBP6JYNPIN292": "その他投資収益／利子所得",
                    "BPBP6JYNPIN9": "その他第一次所得",
                },
            },
        },
    },
}
