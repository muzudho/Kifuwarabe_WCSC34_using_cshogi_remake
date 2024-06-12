import random

#              python v_a54_0.py
from                  v_a54_0_eval.facade import EvaluationFacade


class ChoiceBestMove():
    """最善の着手を選ぶ"""


    @staticmethod
    def do_it(
            legal_moves,
            board,
            kifuwarabe,
            is_debug=False):
        """最善の着手を選ぶ

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている
        is_debug : bool
            デバッグモードか？
        """

        # ランク付けされた指し手一覧
        (good_move_u_set,
         bad_move_u_set) = EvaluationFacade.select_ranked_f_move_u_set_facade(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        # 候補手の中からランダムに選ぶ。USIの指し手の記法で返却
        if 0 < len(good_move_u_set):
            return random.choice(list(good_move_u_set))

        # 何も指さないよりは、悪手を指した方がマシ
        else:
            return random.choice(list(bad_move_u_set))
