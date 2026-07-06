# kakeibo.py の計算ロジックを自動で確かめるテスト
# 実行方法: python3 test_kakeibo.py
from kakeibo import calc_monthly_total, delete_expense

# テスト専用の偽データ。本物のkakeibo.jsonに依存しないことが重要。
# （本物のデータでテストすると、支出を追加するたびに「正解」が変わってしまう）
test_data = [
    {"item": "昼食", "amount": 800, "date": "2026-07-01"},
    {"item": "本", "amount": 1500, "date": "2026-07-15"},
    {"item": "映画", "amount": 2000, "date": "2026-06-30"},  # 先月分
    {"item": "牛乳", "amount": 200},  # 日付なしの古い形式のデータ
]

# assert = 「これは真のはず。違ったらエラーで止まって教えて」という宣言

# テスト1: 基本の動き。7月分だけ足されるか（800 + 1500 = 2300）
assert calc_monthly_total(test_data, "2026-07") == 2300

# テスト2: 境界の確認。6/30は「先月」として7月に混ざらないか
assert calc_monthly_total(test_data, "2026-06") == 2000

# テスト3: 該当データが1件もない月は0円になるか
assert calc_monthly_total(test_data, "2025-01") == 0

# テスト4: データが空っぽでも落ちずに0を返すか
assert calc_monthly_total([], "2026-07") == 0

# ---- ここから削除機能のテスト ----
# 削除はリストを変化させるので、上のtest_dataを使い回さず専用のリストを作る。
# （テスト同士が影響し合うと、順番を変えただけで壊れる困ったテストになる）
delete_data = [
    {"item": "コーヒー", "amount": 300},
    {"item": "ノート", "amount": 150},
]

# テスト5: 「1番」を消すとリストの先頭（コーヒー）が消えるか ＝ オフバイワンの検問所
deleted = delete_expense(delete_data, 1)
assert deleted["item"] == "コーヒー"
assert len(delete_data) == 1  # 2件が1件に減った
assert delete_data[0]["item"] == "ノート"  # 残ったのはノートの方

# テスト6: 無効な番号（0、範囲外）は削除せずNoneが返るか
assert delete_expense(delete_data, 0) is None
assert delete_expense(delete_data, 99) is None
assert len(delete_data) == 1  # 失敗したときに勝手に消えていないことも大事

# テスト7: 空のリストから削除しようとしても落ちないか
assert delete_expense([], 1) is None

print("すべてのテストに合格しました！")
