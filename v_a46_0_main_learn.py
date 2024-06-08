# python v_a46_0_main_learn.py
import datetime
from v_a46_0 import Kifuwarabe, max_move_number
from v_a46_0_misc.learn import Learn
from v_a46_0_misc.lib import BoardHelper


class LearningFramework():
    """学習フレームワーク"""


    def __init__(self):
        pass


    def learn_about_one_game(
            self,
            board,
            kifuwarabe,
            is_debug):
        """対局１つについて学習する

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグモードか？
        """

        # トレーニングデータの用意
        print(f"[{datetime.datetime.now()}] [learning framework > learn about one game > get training data] start...")

        # トレーニングデータが無いからプレイアウトする
        result_str = kifuwarabe.playout(
                is_debug=is_debug)

        position_command = BoardHelper.get_position_command(
                board=board)

        print(f"""[{datetime.datetime.now()}] [learning framework > learn about one game > get training data] finished
{board}
    # playout result:`{result_str}`
    # move_number:{board.move_number} / max_move_number:{max_move_number}
    # {position_command}
""", flush=True)

        print(f"[{datetime.datetime.now()}] [learning framework > learn about one game] start...")

        # 学習する
        Learn(
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug).learn_it()

        print(f"[{datetime.datetime.now()}] [learning framework > learn about one game] finished")


    def start_it(
            self,
            board,
            kifuwarabe,
            is_debug):
        """学習フレームワークを始める

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

        # とりあえず 2000対局について学習するか
        max_game = 2000
        for game_number in range(0,max_game):

            print(f"[{datetime.datetime.now()}] [learning framework > start it] ({game_number + 1:4}/{max_game}) start...")

            self.learn_about_one_game(
                    board=board,
                    kifuwarabe=kifuwarabe,
                    is_debug=is_debug)

            print(f"[{datetime.datetime.now()}] [learning framework > start it] ({game_number + 1:4}/{max_game}) finished")


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    #print(f"cshogi.BLACK:{cshogi.BLACK}  cshogi.WHITE:{cshogi.WHITE}")

    try:
        kifuwarabe = Kifuwarabe()
        print(kifuwarabe.board)

        learning_framework = LearningFramework()
        learning_framework.start_it(
                board=kifuwarabe.board,
                kifuwarabe=kifuwarabe,
                is_debug=False)

    except Exception as err:
        print(f"[{datetime.datetime.now()}] [learning framework > unexpected error] {err=}, {type(err)=}")
        raise
