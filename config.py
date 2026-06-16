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
        "対外直接投資チャート": {
            "chart_type": "outward_direct_investment",
            "codes": [
                "BPBP6H",  # 対外直接投資/地域別合計/ネット
                "BPBP6HCN",  # 対外直接投資/中華人民共和国/ネット
                "BPBP6HHK",  # 対外直接投資/香港/ネット
                "BPBP6HTW",  # 対外直接投資/台湾/ネット
                "BPBP6HKR",  # 対外直接投資/大韓民国/ネット
                "BPBP6HSG",  # 対外直接投資/シンガポール/ネット
                "BPBP6HTH",  # 対外直接投資/タイ/ネット
                "BPBP6HID",  # 対外直接投資/インドネシア/ネット
                "BPBP6HMY",  # 対外直接投資/マレーシア/ネット
                "BPBP6HPH",  # 対外直接投資/フィリピン/ネット
                "BPBP6HVN",  # 対外直接投資/ベトナム/ネット
                "BPBP6HIN",  # 対外直接投資/インド/ネット
                "BPBP6HUS",  # 対外直接投資/アメリカ合衆国/ネット
                "BPBP6HCA",  # 対外直接投資/カナダ/ネット
                "BPBP6HMX",  # 対外直接投資/メキシコ/ネット
                "BPBP6HBR",  # 対外直接投資/ブラジル/ネット
                "BPBP6HCI",  # 対外直接投資/ケイマン諸島/ネット
                "BPBP6HAU",  # 対外直接投資/オーストラリア/ネット
                "BPBP6HNZ",  # 対外直接投資/ニュージーランド/ネット
                "BPBP6HDE",  # 対外直接投資/ドイツ/ネット
                "BPBP6HGB",  # 対外直接投資/英国/ネット
                "BPBP6HFR",  # 対外直接投資/フランス/ネット
                "BPBP6HNL",  # 対外直接投資/オランダ/ネット
                "BPBP6HIT",  # 対外直接投資/イタリア/ネット
                "BPBP6HBE",  # 対外直接投資/ベルギー/ネット
                "BPBP6HLX",  # 対外直接投資/ルクセンブルク/ネット
                "BPBP6HCH",  # 対外直接投資/スイス/ネット
                "BPBP6HSE",  # 対外直接投資/スウェーデン/ネット
                "BPBP6HES",  # 対外直接投資/スペイン/ネット
                "BPBP6HSU",  # 対外直接投資/ロシア/ネット
                "BPBP6HSA",  # 対外直接投資/サウジアラビア/ネット
                "BPBP6HAE",  # 対外直接投資/アラブ首長国連邦/ネット
                "BPBP6HIR",  # 対外直接投資/イラン/ネット
                "BPBP6HZA",  # 対外直接投資/南アフリカ共和国/ネット
            ],
            "fields": {
                "total": "BPBP6H",
                "components": [
                    "BPBP6HCN",
                    "BPBP6HHK",
                    "BPBP6HTW",
                    "BPBP6HKR",
                    "BPBP6HSG",
                    "BPBP6HTH",
                    "BPBP6HID",
                    "BPBP6HMY",
                    "BPBP6HPH",
                    "BPBP6HVN",
                    "BPBP6HIN",
                    "BPBP6HUS",
                    "BPBP6HCA",
                    "BPBP6HMX",
                    "BPBP6HBR",
                    "BPBP6HCI",
                    "BPBP6HAU",
                    "BPBP6HNZ",
                    "BPBP6HDE",
                    "BPBP6HGB",
                    "BPBP6HFR",
                    "BPBP6HNL",
                    "BPBP6HIT",
                    "BPBP6HBE",
                    "BPBP6HLX",
                    "BPBP6HCH",
                    "BPBP6HSE",
                    "BPBP6HES",
                    "BPBP6HSU",
                    "BPBP6HSA",
                    "BPBP6HAE",
                    "BPBP6HIR",
                    "BPBP6HZA",
                ],
                "labels": {
                    "total": "対外直接投資",
                    "BPBP6H": "対外直接投資／地域別合計／ネット",
                    "BPBP6HCN": "中国",
                    "BPBP6HHK": "香港",
                    "BPBP6HTW": "台湾",
                    "BPBP6HKR": "韓国",
                    "BPBP6HSG": "シンガポール",
                    "BPBP6HTH": "タイ",
                    "BPBP6HID": "インドネシア",
                    "BPBP6HMY": "マレーシア",
                    "BPBP6HPH": "フィリピン",
                    "BPBP6HVN": "ベトナム",
                    "BPBP6HIN": "インド",
                    "BPBP6HUS": "米国",
                    "BPBP6HCA": "カナダ",
                    "BPBP6HMX": "メキシコ",
                    "BPBP6HBR": "ブラジル",
                    "BPBP6HCI": "ケイマン諸島",
                    "BPBP6HAU": "オーストラリア",
                    "BPBP6HNZ": "ニュージーランド",
                    "BPBP6HDE": "ドイツ",
                    "BPBP6HGB": "英国",
                    "BPBP6HFR": "フランス",
                    "BPBP6HNL": "オランダ",
                    "BPBP6HIT": "イタリア",
                    "BPBP6HBE": "ベルギー",
                    "BPBP6HLX": "ルクセンブルク",
                    "BPBP6HCH": "スイス",
                    "BPBP6HSE": "スウェーデン",
                    "BPBP6HES": "スペイン",
                    "BPBP6HSU": "ロシア",
                    "BPBP6HSA": "サウジアラビア",
                    "BPBP6HAE": "アラブ首長国連邦",
                    "BPBP6HIR": "イラン",
                    "BPBP6HZA": "南アフリカ共和国",
                },
            },
        },
        "対内直接投資チャート": {
            "chart_type": "inward_direct_investment",
            "codes": [
                "BPBP6I",  # 対内直接投資/地域別合計/ネット
                "BPBP6ICN",  # 対内直接投資/中華人民共和国/ネット
                "BPBP6IHK",  # 対内直接投資/香港/ネット
                "BPBP6ITW",  # 対内直接投資/台湾/ネット
                "BPBP6IKR",  # 対内直接投資/大韓民国/ネット
                "BPBP6ISG",  # 対内直接投資/シンガポール/ネット
                "BPBP6ITH",  # 対内直接投資/タイ/ネット
                "BPBP6IID",  # 対内直接投資/インドネシア/ネット
                "BPBP6IMY",  # 対内直接投資/マレーシア/ネット
                "BPBP6IPH",  # 対内直接投資/フィリピン/ネット
                "BPBP6IVN",  # 対内直接投資/ベトナム/ネット
                "BPBP6IIN",  # 対内直接投資/インド/ネット
                "BPBP6IUS",  # 対内直接投資/アメリカ合衆国/ネット
                "BPBP6ICA",  # 対内直接投資/カナダ/ネット
                "BPBP6IMX",  # 対内直接投資/メキシコ/ネット
                "BPBP6IBR",  # 対内直接投資/ブラジル/ネット
                "BPBP6ICI",  # 対内直接投資/ケイマン諸島/ネット
                "BPBP6IAU",  # 対内直接投資/オーストラリア/ネット
                "BPBP6INZ",  # 対内直接投資/ニュージーランド/ネット
                "BPBP6IDE",  # 対内直接投資/ドイツ/ネット
                "BPBP6IGB",  # 対内直接投資/英国/ネット
                "BPBP6IFR",  # 対内直接投資/フランス/ネット
                "BPBP6INL",  # 対内直接投資/オランダ/ネット
                "BPBP6IIT",  # 対内直接投資/イタリア/ネット
                "BPBP6IBE",  # 対内直接投資/ベルギー/ネット
                "BPBP6ILX",  # 対内直接投資/ルクセンブルク/ネット
                "BPBP6ICH",  # 対内直接投資/スイス/ネット
                "BPBP6ISE",  # 対内直接投資/スウェーデン/ネット
                "BPBP6IES",  # 対内直接投資/スペイン/ネット
                "BPBP6ISU",  # 対内直接投資/ロシア/ネット
                "BPBP6ISA",  # 対内直接投資/サウジアラビア/ネット
                "BPBP6IAE",  # 対内直接投資/アラブ首長国連邦/ネット
                "BPBP6IIR",  # 対内直接投資/イラン/ネット
                "BPBP6IZA",  # 対内直接投資/南アフリカ共和国/ネット
            ],
            "fields": {
                "total": "BPBP6I",
                "components": [
                    "BPBP6ICN",
                    "BPBP6IHK",
                    "BPBP6ITW",
                    "BPBP6IKR",
                    "BPBP6ISG",
                    "BPBP6ITH",
                    "BPBP6IID",
                    "BPBP6IMY",
                    "BPBP6IPH",
                    "BPBP6IVN",
                    "BPBP6IIN",
                    "BPBP6IUS",
                    "BPBP6ICA",
                    "BPBP6IMX",
                    "BPBP6IBR",
                    "BPBP6ICI",
                    "BPBP6IAU",
                    "BPBP6INZ",
                    "BPBP6IDE",
                    "BPBP6IGB",
                    "BPBP6IFR",
                    "BPBP6INL",
                    "BPBP6IIT",
                    "BPBP6IBE",
                    "BPBP6ILX",
                    "BPBP6ICH",
                    "BPBP6ISE",
                    "BPBP6IES",
                    "BPBP6ISU",
                    "BPBP6ISA",
                    "BPBP6IAE",
                    "BPBP6IIR",
                    "BPBP6IZA",
                ],
                "labels": {
                    "total": "対内直接投資",
                    "BPBP6I": "対内直接投資／地域別合計／ネット",
                    "BPBP6ICN": "中国",
                    "BPBP6IHK": "香港",
                    "BPBP6ITW": "台湾",
                    "BPBP6IKR": "韓国",
                    "BPBP6ISG": "シンガポール",
                    "BPBP6ITH": "タイ",
                    "BPBP6IID": "インドネシア",
                    "BPBP6IMY": "マレーシア",
                    "BPBP6IPH": "フィリピン",
                    "BPBP6IVN": "ベトナム",
                    "BPBP6IIN": "インド",
                    "BPBP6IUS": "米国",
                    "BPBP6ICA": "カナダ",
                    "BPBP6IMX": "メキシコ",
                    "BPBP6IBR": "ブラジル",
                    "BPBP6ICI": "ケイマン諸島",
                    "BPBP6IAU": "オーストラリア",
                    "BPBP6INZ": "ニュージーランド",
                    "BPBP6IDE": "ドイツ",
                    "BPBP6IGB": "英国",
                    "BPBP6IFR": "フランス",
                    "BPBP6INL": "オランダ",
                    "BPBP6IIT": "イタリア",
                    "BPBP6IBE": "ベルギー",
                    "BPBP6ILX": "ルクセンブルク",
                    "BPBP6ICH": "スイス",
                    "BPBP6ISE": "スウェーデン",
                    "BPBP6IES": "スペイン",
                    "BPBP6ISU": "ロシア",
                    "BPBP6ISA": "サウジアラビア",
                    "BPBP6IAE": "アラブ首長国連邦",
                    "BPBP6IIR": "イラン",
                    "BPBP6IZA": "南アフリカ共和国",
                },
            },
        },
    },
}
