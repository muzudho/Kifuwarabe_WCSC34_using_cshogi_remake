import cshogi
import datetime
import random

# python v_a54_0.py
from     v_a54_0_debug_plan import DebugPlan
from     v_a54_0_eval.facade import EvaluationFacade
from     v_a54_0_misc.lib import MoveHelper, BoardHelper, Move


class ChoiceBestMove():
    """最善の着手を選ぶ"""


    @staticmethod
    def get_summary(
            move_obj,
            board,
            kifuwarabe,
            is_debug=False):
        """集計を取得

        Parameters
        ----------
        move_obj : Move
            着手オブジェクト
        board : cshogi.Board
            現局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグモードか？

        Returns
        -------
        - fl_index_to_relation_exists_dictionary
        - fq_index_to_relation_exists_dictionary
        - is_king_move
        - positive_of_relation
        - total_of_relation
        """

        # 投了局面時、入玉宣言局面時、１手詰めは無視

        k_sq = BoardHelper.get_king_square(board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            # １つの着手には、０～複数の着手がある木構造をしています。
            # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
            (kl_index_to_relation_exists_dictionary,
             kq_index_to_relation_exists_dictionary,
             _,
             _) = EvaluationFacade.select_fo_index_to_relation_exists(
                    move_obj=move_obj,
                    is_king_move=is_king_move,
                    board=board,
                    kifuwarabe=kifuwarabe)

            # ＫＬとＫＱの関係数
            total_of_relation = len(kl_index_to_relation_exists_dictionary) + len(kq_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > kl and kq]   total_of_relation:{total_of_relation}  =  len(kl_index_to_relation_exists_dictionary):{len(kl_index_to_relation_exists_dictionary)}  +  len(kq_index_to_relation_exists_dictionary):{len(kq_index_to_relation_exists_dictionary)}")

            # ＫＬとＫＱの関係が有りのものの数
            positive_of_relation = EvaluationFacade.get_number_of_connection_for_kl_kq(
                    kl_index_to_relation_exists_dictionary,
                    kq_index_to_relation_exists_dictionary,
                    board=board,
                    is_debug=is_debug)

            return (kl_index_to_relation_exists_dictionary,
                    kq_index_to_relation_exists_dictionary,
                    is_king_move,
                    positive_of_relation,
                    total_of_relation)

        else:

            # １つの着手には、０～複数の着手がある木構造をしています。
            # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
            (_,
             _,
             pl_index_to_relation_exists_dictionary,
             pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                    move_obj=move_obj,
                    is_king_move=is_king_move,
                    board=board,
                    kifuwarabe=kifuwarabe)

            # ＰＬとＰＱの関係数
            total_of_relation = len(pl_index_to_relation_exists_dictionary) + len(pq_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > pl and pq]  total_of_relation:{total_of_relation}  =  len(pl_index_to_relation_exists_dictionary):{len(pl_index_to_relation_exists_dictionary)}  +  len(pq_index_to_relation_exists_dictionary):{len(pq_index_to_relation_exists_dictionary)}")

            # ＰＬとＰＱの関係が有りのものの数
            positive_of_relation = EvaluationFacade.get_number_of_connection_for_pl_pq(
                    pl_index_to_relation_exists_dictionary,
                    pq_index_to_relation_exists_dictionary,
                    board=board,
                    is_debug=is_debug)

            return (pl_index_to_relation_exists_dictionary,
                    pq_index_to_relation_exists_dictionary,
                    is_king_move,
                    positive_of_relation,
                    total_of_relation)


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
            total_of_relation) = ChoiceBestMove.get_summary(
                    move_obj=move_obj,
                    board=board,
                    kifuwarabe=kifuwarabe,
                    is_debug=is_debug)

            #
            # 分離機
            #

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
