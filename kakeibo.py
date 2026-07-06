# CLI家計簿アプリ - ファイル保存対応版
import json
import os
from datetime import date  # 今日の日付を取るために使う

# 保存先ファイル名。あちこちに直書きせず1か所にまとめておくと、後で変えたくなっても1行で済む
FILE_NAME = "kakeibo.json"


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
    # str(date.today()) は "2026-07-08" のようなISO形式の文字列になる。
    # 文字列にして保存するのは、JSONが日付型を直接は扱えないため
    today = str(date.today())
    expenses.append({"item": item, "amount": amount, "date": today})
    save_expenses()  # 追加したら即ファイルへ。これで終了してもデータが残る
    print(f"記録しました：{today} {item} {amount}円")


def show_expenses():
    """支出の一覧と合計を表示する"""
    if not expenses:  # リストが空のときはTrueになる、Pythonらしい書き方
        print("まだ記録がありません")
        return

    print("---- 支出一覧 ----")
    total = 0
    for e in expenses:
        # e["date"] だと日付を保存していなかった頃のデータでエラーになる。
        # .get() なら無いときに "日付なし" を返してくれるので、古いデータも表示できる
        print(f"{e.get('date', '日付なし')} {e['item']}: {e['amount']}円")
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


def show_monthly_total():
    """今月の支出合計を表示する（計算はcalc_monthly_totalに任せる）"""
    this_month = str(date.today())[:7]  # "2026-07-08" → "2026-07"（先頭7文字）
    total = calc_monthly_total(expenses, this_month)
    print(f"{this_month} の合計: {total}円")


def main():
    """メニューを表示し続けるメインループ"""
    # while True = 無限ループ。「終了」が選ばれるまでメニューを出し続ける
    while True:
        print("\n[1] 支出を追加  [2] 一覧を見る  [3] 今月の合計  [4] 終了")
        choice = input("番号を選んでください > ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            show_monthly_total()
        elif choice == "4":
            print("お疲れさまでした！")
            break  # ループを抜ける＝プログラム終了
        else:
            print("1〜4の番号を入力してください")


# このファイルが直接実行されたときだけmain()を動かす、Pythonの定型文
if __name__ == "__main__":
    main()
