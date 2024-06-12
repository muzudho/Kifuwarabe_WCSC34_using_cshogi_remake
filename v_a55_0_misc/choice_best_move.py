import cshogi
import datetime
import random

# python v_a55_0.py
from     v_a55_0_debug_plan import DebugPlan
from     v_a55_0_eval.kk import EvaluationKkTable
from     v_a55_0_eval.kp import EvaluationKpTable
from     v_a55_0_eval.pk import EvaluationPkTable
from     v_a55_0_eval.pp import EvaluationPpTable
from     v_a55_0_misc.lib import Turn, MoveHelper, BoardHelper, Move


class ChoiceBestMove():
    """最善の着手を選ぶ"""


    def select_fo_index_to_relation_exists(
            move_obj,
            is_king_move,
            board,
            kifuwarabe):
        """１つの着手と全ての応手をキー、関係の有無を値とする辞書を作成します

        Parameters
        ----------
        move_obj : Move
            着手
        is_king_move : bool
            自玉の指し手か？
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            きふわらべ

        Returns
        -------
        kl_index_to_relation_exists_dic
            自玉の着手と、敵玉の応手の関係の有無を格納した辞書
        kq_index_to_relation_exists_dic
            自玉の着手と、敵兵の応手の関係の有無を格納した辞書
        pl_index_to_relation_exists_dic
            自兵の着手と、敵玉の応手の関係の有無を格納した辞書
        pq_index_to_relation_exists_dic
            自兵の着手と、敵兵の応手の関係の有無を格納した辞書
        """

        # 応手の一覧を作成
        l_move_u_set, q_move_u_set = BoardHelper.create_counter_move_u_set(
                board=board,
                move_obj=move_obj)

        if is_king_move:
            # 自玉の着手と、敵玉の応手の一覧から、ＫＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            kl_index_to_relation_exists_dic = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(board.turn)].select_kl_index_and_relation_exists(
                    k_move_obj=move_obj,
                    l_move_u_set=l_move_u_set,
                    k_turn=board.turn)

            # 自玉の着手と、敵兵の応手の一覧から、ＫＱテーブルのインデックスと、関係の有無を格納した辞書を作成
            kq_index_to_relation_exists_dic = kifuwarabe.evaluation_kq_table_obj_array[Turn.to_index(board.turn)].select_kp_index_and_relation_exists(
                    k_move_obj=move_obj,
                    p_move_u_set=q_move_u_set,
                    k_turn=board.turn)

            return (kl_index_to_relation_exists_dic,
                    kq_index_to_relation_exists_dic,
                    None,
                    None)

        else:
            # 自兵の着手と、敵玉の応手の一覧から、ＰＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            pl_index_to_relation_exists_dic = kifuwarabe.evaluation_pl_table_obj_array[Turn.to_index(board.turn)].select_pk_index_and_relation_exists(
                    p_move_obj=move_obj,
                    k_move_u_set=l_move_u_set,
                    p_turn=board.turn)

            # 自兵の着手と、敵兵の応手の一覧から、ＰＱテーブルのインデックスと、関係の有無を格納した辞書を作成
            pq_index_to_relation_exists_dic = kifuwarabe.evaluation_pq_table_obj_array[Turn.to_index(board.turn)].select_pp_index_and_relation_exists(
                    p1_move_obj=move_obj,
                    p2_move_u_set=q_move_u_set,
                    p1_turn=board.turn)

            return (None,
                    None,
                    pl_index_to_relation_exists_dic,
                    pq_index_to_relation_exists_dic)


    @staticmethod
    def get_number_of_connection_for_kl_kq(
            kl_index_to_relation_exists_dictionary,
            kq_index_to_relation_exists_dictionary,
            board,
            is_debug=False):
        """ＫＬとＫＱの関係が有りのものの数

        Parameters
        ----------
        kl_index_to_relation_exists_dictionary : dict
            ＫＬ
        kq_index_to_relation_exists_dictionary
            ＫＱ
        board : cshogi.Board
            現局面
        is_debug : bool
            デバッグモードか？
        """
        number_of_connection = 0

        # ＫＬ
        for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # ＫＱ
        for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # デバッグ表示
        if is_debug:
            # ＫＬ
            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
                if DebugPlan.get_number_of_connection_for_kl_kq:
                    k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                            kl_index=kl_index,
                            k_turn=board.turn)
                    print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kl]  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＫＱ
            for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():
                if DebugPlan.get_number_of_connection_for_kl_kq:
                    k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                            kp_index=kq_index,
                            k_turn=board.turn)
                    print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kq]  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        return number_of_connection


    @staticmethod
    def get_number_of_connection_for_pl_pq(
            pl_index_to_relation_exists_dictionary,
            pq_index_to_relation_exists_dictionary,
            board,
            is_debug):
        """ＰＬとＰＱの関係が有りのものの数

        Parameters
        ----------
        kl_index_to_relation_exists_dictionary : dict
            ＫＬ
        kq_index_to_relation_exists_dictionary
            ＫＱ
        board : cshogi.Board
            現局面
        is_debug : bool
            デバッグモードか？
        """
        number_of_connection = 0

        # ＰＬ
        for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # ＰＱ
        for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # デバッグ表示
        if is_debug:
            # ＰＬ
            for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():
                if is_debug and DebugPlan.get_number_of_connection_for_pl_pq:
                    p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                            pk_index=pl_index,
                            p_turn=board.turn)
                    print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pl]  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＰＱ
            for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():
                if is_debug and DebugPlan.get_number_of_connection_for_pl_pq:
                    p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                            pp_index=pq_index,
                            p1_turn=board.turn)
                    print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pq]  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        return number_of_connection


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
             _) = ChoiceBestMove.select_fo_index_to_relation_exists(
                    move_obj=move_obj,
                    is_king_move=is_king_move,
                    board=board,
                    kifuwarabe=kifuwarabe)

            # ＫＬとＫＱの関係数
            total_of_relation = len(kl_index_to_relation_exists_dictionary) + len(kq_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > kl and kq]   total_of_relation:{total_of_relation}  =  len(kl_index_to_relation_exists_dictionary):{len(kl_index_to_relation_exists_dictionary)}  +  len(kq_index_to_relation_exists_dictionary):{len(kq_index_to_relation_exists_dictionary)}")

            # ＫＬとＫＱの関係が有りのものの数
            positive_of_relation = ChoiceBestMove.get_number_of_connection_for_kl_kq(
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
             pq_index_to_relation_exists_dictionary) = ChoiceBestMove.select_fo_index_to_relation_exists(
                    move_obj=move_obj,
                    is_king_move=is_king_move,
                    board=board,
                    kifuwarabe=kifuwarabe)

            # ＰＬとＰＱの関係数
            total_of_relation = len(pl_index_to_relation_exists_dictionary) + len(pq_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > pl and pq]  total_of_relation:{total_of_relation}  =  len(pl_index_to_relation_exists_dictionary):{len(pl_index_to_relation_exists_dictionary)}  +  len(pq_index_to_relation_exists_dictionary):{len(pq_index_to_relation_exists_dictionary)}")

            # ＰＬとＰＱの関係が有りのものの数
            positive_of_relation = ChoiceBestMove.get_number_of_connection_for_pl_pq(
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

        ranked_move_u_set_list = []

        # もし好手と悪手の２パターンなら ranking_resolution は ２。
        # 配列のインデックスの小さい方がランクが上とする
        for i in range(0, kifuwarabe.ranking_resolution):
            ranked_move_u_set_list.append(set())

        # デバッグ表示
        if is_debug and DebugPlan.select_ranked_f_move_u_set_facade:
            print(f"[choice best move]  kifuwarabe.ranking_resolution:{kifuwarabe.ranking_resolution}")

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

            # ポリシー率
            if 0 < total_of_relation:
                policy_rate = positive_of_relation / total_of_relation
            else:
                policy_rate = 1.0


            ranking_resolution_threshold = 1 / kifuwarabe.ranking_resolution
            policy_rate_rev = 1 - policy_rate
            ranking = int(policy_rate_rev // ranking_resolution_threshold)

            target_set = ranked_move_u_set_list[ranking]
            target_set.add(move_u)

            # デバッグ表示
            if is_debug and DebugPlan.select_ranked_f_move_u_set_facade:
                print(f"[choice best move]  move_u:{move_u}  ranking:{ranking}  positive_of_relation:{positive_of_relation}  total_of_relation:{total_of_relation}  policy_rate:{policy_rate}  policy_rate_rev:{policy_rate_rev}  ranking_resolution_threshold:{ranking_resolution_threshold}")


        # デバッグ表示
        if is_debug and DebugPlan.select_ranked_f_move_u_set_facade:

            for ranking in range(0, kifuwarabe.ranking_resolution):

                print(f"[{datetime.datetime.now()}] [select ranked f move u set facade] ランク付けされた指し手一覧（ranking:{ranking}）")
                target_set = ranked_move_u_set_list[ranking]

                for ranked_move_u in target_set:
                    print(f"[{datetime.datetime.now()}] [select ranked f move u set facade]  ranking:{ranking}  move:{ranked_move_u:5}")


        return ranked_move_u_set_list


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
        ranked_move_u_set_list = ChoiceBestMove.select_ranked_f_move_u_set_facade(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        for ranked_move_set in ranked_move_u_set_list:

            # このランキングに候補手が無ければ、下のランキングへ
            if len(ranked_move_set) < 1:
                continue

            # 候補手の中からランダムに選ぶ。USIの指し手の記法で返却
            return random.choice(list(ranked_move_set))

        # ここにくることはないはず
        return "resign"
