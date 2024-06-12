import cshogi
import datetime
import random

#              python v_a54_0.py
from                  v_a54_0_debug_plan import DebugPlan
from                  v_a54_0_eval.facade import EvaluationFacade
from                  v_a54_0_misc.lib import Move


class ChoiceBestMove():
    """最善の着手を選ぶ"""


    @staticmethod
    def select_ranked_f_move_u_set_facade(
            legal_moves,
            board,
            kifuwarabe,
            is_debug=False):
        """ランク付けされた指し手一覧（好手、悪手）を作成

        Parameters
        ----------
        legal_moves :
            合法手
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグか？

        Returns
        -------
         (good_move_u_set,
          bad_move_u_set)
        """

        # 好手の集合
        good_move_u_set = set()

        # 悪手の集合
        bad_move_u_set = set()

        for move_id in legal_moves:
            move_u = cshogi.move_to_usi(move_id)

            # 着手オブジェクト
            move_obj = Move.from_usi(move_u)

            # 自駒と敵玉に対する関係の辞書
            (fl_index_to_relation_exists_dictionary,
            # 自駒と敵兵に対する関係の辞書
            fq_index_to_relation_exists_dictionary,
            # 玉の指し手か？
            is_king_move,
            # 関係が陽性の総数
            positive_of_relation,
            # 関係の総数
            total_of_relation) = EvaluationFacade.get_summary(
                    move_obj=move_obj,
                    board=board,
                    kifuwarabe=kifuwarabe,
                    is_debug=is_debug)

            # ポリシー値（千分率）
            if 0 < total_of_relation:
                policy = EvaluationFacade.round_half_up(positive_of_relation * 1000 / total_of_relation)
            else:
                policy = 0

            if 500 <= policy:
                good_move_u_set.add(move_u)

            else:
                bad_move_u_set.add(move_u)


        # デバッグ表示
        if is_debug and DebugPlan.select_ranked_f_move_u_set_facade:

            print(f"[{datetime.datetime.now()}] [select ranked f move u set facade] ランク付けされた指し手一覧（好手）")

            for good_move_u in good_move_u_set:
                print(f"[{datetime.datetime.now()}] [select ranked f move u set facade]    good:{good_move_u:5}")

            print(f"[{datetime.datetime.now()}] [select ranked f move u set facade] ランク付けされた指し手一覧（悪手）")

            for bad_move_u in bad_move_u_set:
                print(f"[{datetime.datetime.now()}] [select ranked f move u set facade]    bad :{bad_move_u:5}")


        return (good_move_u_set,
                bad_move_u_set)


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
         bad_move_u_set) = ChoiceBestMove.select_ranked_f_move_u_set_facade(
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
