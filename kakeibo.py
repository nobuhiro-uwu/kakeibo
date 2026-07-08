# CLI家計簿アプリ - ファイル保存対応版
import json
import os
from datetime import date  # 今日の日付を取るために使う

# 保存先ファイル名。あちこちに直書きせず1か所にまとめておくと、後で変えたくなっても1行で済む
FILE_NAME = "kakeibo.json"

# カテゴリは自由入力にせず固定リストから選ばせる。
# 表記ゆれ（食費/食料/ごはん…）を防いで、あとでカテゴリごとの集計を可能にするため
CATEGORIES = ["食費", "日用品", "交通費", "娯楽", "その他"]


def load_expenses():
    """ファイルから支出データを読み込む（起動時に1回だけ呼ぶ）"""
    # ファイルがまだ無い＝初回起動。空のリストから始める
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)  # JSONテキスト → Pythonのリスト・辞書に変換


def save_expenses():
    """支出データをファイルに書き出す（追加のたびに呼ぶ）"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        # ensure_ascii=False で日本語をそのまま保存（指定しないと読めない文字コードになる）
        # indent=2 は人間が読みやすいよう改行と字下げを入れる指定
        json.dump(expenses, f, ensure_ascii=False, indent=2)


# 支出を貯めておくリスト。1件の支出は {"item": 品名, "amount": 金額} という辞書で表す。
# 起動時にファイルから復元するのがポイント（前回のデータがここで蘇る）
expenses = load_expenses()


def choose_category():
    """カテゴリ一覧を見せて1つ選んでもらう。無効な入力ならNoneを返す"""
    for i, name in enumerate(CATEGORIES, start=1):
        print(f"[{i}] {name}", end="  ")  # end="  " で改行せず横に並べる
    print()  # 最後に1回だけ改行
    try:
        number = int(input("カテゴリ番号 > "))
    except ValueError:
        return None
    if number < 1 or number > len(CATEGORIES):
        return None
    return CATEGORIES[number - 1]  # 人間の1番目はリストの[0]。削除機能と同じ -1


def add_expense():
    """支出を1件追加する"""
    item = input("何に使った？ > ")
    # input()の戻り値は必ず文字列なので、計算に使えるようint（整数）に変換する。
    # ただし "abc" などは変換できずValueErrorで落ちるので、try/exceptで受け止める
    try:
        amount = int(input("いくら？（円） > "))
    except ValueError:
        print("金額は半角の数字で入力してください（例: 500）")
        return  # 記録せずにメニューへ戻る
    category = choose_category()
    if category is None:
        print(f"カテゴリは1〜{len(CATEGORIES)}の番号で入力してください")
        return
    # str(date.today()) は "2026-07-08" のようなISO形式の文字列になる。
    # 文字列にして保存するのは、JSONが日付型を直接は扱えないため
    today = str(date.today())
    expenses.append({"item": item, "amount": amount, "date": today, "category": category})
    save_expenses()  # 追加したら即ファイルへ。これで終了してもデータが残る
    print(f"記録しました：{today} [{category}] {item} {amount}円")


def show_expenses():
    """支出の一覧と合計を表示する"""
    if not expenses:  # リストが空のときはTrueになる、Pythonらしい書き方
        print("まだ記録がありません")
        return

    print("---- 支出一覧 ----")
    total = 0
    # enumerate(リスト, start=1) = 「1から番号を振りながらループする」書き方。
    # この番号は削除機能で「何番を消す？」の指定にも使う
    for i, e in enumerate(expenses, start=1):
        # e["date"] だと日付を保存していなかった頃のデータでエラーになる。
        # .get() なら無いときに "日付なし" を返してくれるので、古いデータも表示できる
        print(f"{i}. {e.get('date', '日付なし')}[{e.get('category','未分類')}] {e['item']}: {e['amount']}円")
        total += e["amount"]
    print(f"合計: {total}円")


def calc_monthly_total(expense_list, month):
    """指定した月（"2026-07" 形式）の支出合計を計算して返す。

    printせず数値をreturnするだけ・グローバル変数に触らず引数だけを見る、
    という作りにしてあるのは、テストコードから答え合わせできるようにするため
    """
    total = 0
    for e in expense_list:
        # 日付の先頭7文字が指定月と一致するものだけ足す。日付なしの古いデータは対象外
        if e.get("date", "")[:7] == month:
            total += e["amount"]
    return total


def calc_category_total(expense_list, month, category):
    total = 0                                                           # ← 4スペース
    for e in expense_list:                                              # ← 4スペース
        if e.get("date", "")[:7] == month and e.get("category", "") == category:   # ← 8スペース
            total += e["amount"]                                        # ← 12スペース
    return total                                                        # ← 4スペース

def calc_totals_by_month(expense_list):
    """月ごとの合計を辞書で返す。例: {"2026-06": 3200, "2026-07": 4800}

    どの月が存在するかは事前に分からないので、支出を1件ずつ見ながら
    「初めて出会った月は席を作り、2回目からは足し込む」方式で表を育てる
    """
    totals = {}  # 空の辞書からスタート。キー＝月、値＝その月の合計
    for e in expense_list:
        month = e.get("date", "")[:7]
        if month != "":  # 日付なしの古いデータは月別集計に含めない
            if month not in totals:  # in = 「このキーは辞書にもう居る？」の確認
                totals[month] = 0  # 初登場の月は、まず0円で席を作る
            totals[month] += e["amount"]
    return totals


def delete_expense(expense_list, number):
    """number番目（1始まり）の支出を削除し、削除した1件を返す。無効な番号ならNoneを返す。

    calc_monthly_totalと同じく、input/printをせず引数と戻り値だけで完結させて
    テストできる形にしてある
    """
    if number < 1 or number > len(expense_list):
        return None
    # 人間の「1番目」はリストでは[0]。この -1 を忘れるのが定番のオフバイワンエラー
    return expense_list.pop(number - 1)


def delete_expense_menu():
    """一覧を見せて番号を聞き、支出を1件削除する（対話部分の担当）"""
    if not expenses:
        print("まだ記録がありません")
        return
    show_expenses()
    try:
        number = int(input("削除する番号 > "))
    except ValueError:
        print("番号は半角の数字で入力してください")
        return
    deleted = delete_expense(expenses, number)
    if deleted is None:
        print(f"1〜{len(expenses)} の番号を入力してください")
        return
    save_expenses()  # 消した結果もファイルに反映しないと、再起動で復活してしまう
    print(f"削除しました：{deleted['item']} {deleted['amount']}円")


def show_monthly_total():
    """今月の支出合計を表示する（計算はcalc_monthly_totalに任せる）"""
    this_month = str(date.today())[:7]  # "2026-07-08" → "2026-07"（先頭7文字）
    total = calc_monthly_total(expenses, this_month)
    print(f"{this_month} の合計: {total}円")

def show_category_totals():
    """今月の支出をカテゴリごとに集計して表示する"""
    this_month = str(date.today())[:7]
    print(f"---- {this_month} カテゴリ別集計")
    for name in CATEGORIES:
        total = calc_category_total(expenses, this_month, name)
        print(f"{name}: {total}円")

def show_totals_by_month():
    """月毎の合計を一覧表示する"""   
    totals = calc_totals_by_month(expenses)
    print("---- 月別集計 ----")
    for month in sorted(totals):
        print(f"{month}: {totals[month]}円")
        
def main():
    """メニューを表示し続けるメインループ"""
    # while True = 無限ループ。「終了」が選ばれるまでメニューを出し続ける
    while True:
        print("\n[1] 支出を追加  [2] 一覧を見る  [3] 今月の合計  [4] 削除  [5] カテゴリ別集計 [6] 終了")
        choice = input("番号を選んでください > ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            show_monthly_total()
        elif choice == "4":
            delete_expense_menu()
        elif choice == "5":
            show_category_totals()
        elif choice == "6":
            print("お疲れさまでした！")
            break  # ループを抜ける＝プログラム終了
        else:
            print("1〜6の番号を入力してください")


# このファイルが直接実行されたときだけmain()を動かす、Pythonの定型文
if __name__ == "__main__":
    main()
