# python v_a46_0_main_learn.py
import datetime
from v_a46_0 import Kifuwarabe, max_move_number
from v_a46_0_misc.learn import Learn
from v_a46_0_misc.lib import BoardHelper


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

        # トレーニングデータの用意
        print(f"[{datetime.datetime.now()}] [main learn > learn it > get training data] start...")

        # トレーニングデータが無いからプレイアウトする
        result_str = kifuwarabe.playout(
                is_debug=is_debug)

        position_command = BoardHelper.get_position_command(
                board=board)

        print(f"""[{datetime.datetime.now()}] [main learn > learn it > get training data] finished
{board}
    # playout result:`{result_str}`
    # move_number:{board.move_number} / max_move_number:{max_move_number}
    # {position_command}
""", flush=True)

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
