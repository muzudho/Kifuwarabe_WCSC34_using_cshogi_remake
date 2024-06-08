# python v_a46_0_main_learn.py
import datetime
from v_a46_0 import Kifuwarabe
from v_a46_0_misc.learn import Learn


class MainLearn():
    """学習部"""


    def __init__(self):
        pass


    def learn_it(
            self,
            board,
            kifuwarabe,
            is_debug):
        """学習する

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグモードか？
        """

        # 評価値テーブルの読込
        kifuwarabe.load_eval_all_tables()

        print(f"[{datetime.datetime.now()}] [main learn > learn it] start...")

        # 学習する
        Learn(
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug).learn_it()

        print(f"[{datetime.datetime.now()}] [main learn > learn it] finished")


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    #print(f"cshogi.BLACK:{cshogi.BLACK}  cshogi.WHITE:{cshogi.WHITE}")

    try:
        kifuwarabe = Kifuwarabe()
        print(kifuwarabe.board)

        main_learn = MainLearn()
        main_learn.learn_it(
                board=kifuwarabe.board,
                kifuwarabe=kifuwarabe,
                is_debug=False)

    except Exception as err:
        print(f"[{datetime.datetime.now()}] [main learn > unexpected error] {err=}, {type(err)=}")
        raise
