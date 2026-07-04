# CLI家計簿アプリ - 最小版（データはメモリ上のみ。終了すると消える）

# 支出を貯めておくリスト。1件の支出は {"item": 品名, "amount": 金額} という辞書で表す。
# 「品名と金額はセットで1つのモノ」なので、バラバラの変数ではなく辞書でまとめる。
expenses = []


def add_expense():
    """支出を1件追加する"""
    item = input("何に使った？ > ")
    # input()の戻り値は必ず文字列なので、計算に使えるようint（整数）に変換する
    amount = int(input("いくら？（円） > "))
    expenses.append({"item": item, "amount": amount})
    print(f"記録しました：{item} {amount}円")


def show_expenses():
    """支出の一覧と合計を表示する"""
    if not expenses:  # リストが空のときはTrueになる、Pythonらしい書き方
        print("まだ記録がありません")
        return

    print("---- 支出一覧 ----")
    total = 0
    for e in expenses:
        print(f"{e['item']}: {e['amount']}円")
        total += e["amount"]
    print(f"合計: {total}円")


def main():
    """メニューを表示し続けるメインループ"""
    # while True = 無限ループ。「終了」が選ばれるまでメニューを出し続ける
    while True:
        print("\n[1] 支出を追加  [2] 一覧を見る  [3] 終了")
        choice = input("番号を選んでください > ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            print("お疲れさまでした！")
            break  # ループを抜ける＝プログラム終了
        else:
            print("1〜3の番号を入力してください")


# このファイルが直接実行されたときだけmain()を動かす、Pythonの定型文
if __name__ == "__main__":
    main()
