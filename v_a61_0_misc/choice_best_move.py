import cshogi
import datetime
import random

# python v_a61_0.py
from     v_a61_0_debug_plan import DebugPlan
from     v_a61_0_eval.kk import EvaluationKkTable
from     v_a61_0_eval.kp import EvaluationKpTable
from     v_a61_0_eval.pk import EvaluationPkTable
from     v_a61_0_eval.pp import EvaluationPpTable
from     v_a61_0_eval.facade import EvaluationFacade
from     v_a61_0_misc.lib import Turn, MoveHelper, BoardHelper, Move


class ChoiceBestMove():
    """最善の着手を選ぶ"""


    #select_fo_index_to_relation_exists
    @staticmethod
    def select_f_blackright_o_blackright_index_to_relation_exists(
            strict_move_obj,
            is_king_move,
            board,
            kifuwarabe):
        """１つの着手と全ての応手をキー、関係の有無を値とする辞書を作成します

        Parameters
        ----------
        strict_move_obj : Move
            着手
        is_king_move : bool
            自玉の指し手か？
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            きふわらべ

        Returns
        -------
        blackright_k_blackright_l_index_to_relation_exists_dic
            自玉の着手と、敵玉の応手の関係の有無を格納した辞書
        blackright_k_blackright_q_index_to_relation_exists_dic
            自玉の着手と、敵兵の応手の関係の有無を格納した辞書
        blackright_p_blackright_l_index_to_relation_exists_dic
            自兵の着手と、敵玉の応手の関係の有無を格納した辞書
        blackright_p_blackright_q_index_to_relation_exists_dic
            自兵の着手と、敵兵の応手の関係の有無を格納した辞書
        """

        # assert
        # 着手は後手か？
        is_white = board.turn == cshogi.WHITE
        move_rot_obj = strict_move_obj.rotate()

        # 応手の一覧を作成
        l_strict_move_u_set, q_strict_move_u_set = BoardHelper.create_counter_move_u_set(
                board=board,
                strict_move_obj=strict_move_obj)

        # （先手視点，右辺使用）に変更
        blackright_move_obj = Move.from_move_obj(
                strict_move_obj=strict_move_obj,
                # 先手の指し手になるよう調整します
                shall_white_to_black=board.turn==cshogi.WHITE,
                # 指し手の元位置が、右辺を使うように左右反転します
                use_only_right_side=True)

        # （先手視点，右辺使用）に変更
        l_blackright_move_u_set = set()
        for l_strict_move_u in l_strict_move_u_set:
            l_blackright_move_u_set.add(Move.from_move_obj(
                    strict_move_obj=Move.from_usi(l_strict_move_u),
                    # 先手の指し手になるよう調整します
                    shall_white_to_black=board.turn==cshogi.WHITE,
                    use_only_right_side=True).as_usi)

        # （先手視点，右辺使用）に変更
        q_blackright_move_u_set = set()
        for q_strict_move_u in q_strict_move_u_set:
            q_blackright_move_u_set.add(Move.from_move_obj(
                    strict_move_obj=Move.from_usi(q_strict_move_u),
                    # 先手の指し手になるよう調整します
                    shall_white_to_black=board.turn==cshogi.BLACK,
                    use_only_right_side=True).as_usi)

        if is_king_move:

            #
            # ＫＬ
            #

            # 自玉の着手と、敵玉の応手の一覧から、ＫＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            blackright_k_blackright_l_index_to_relation_exists_dic = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(board.turn)].select_blackright_k_blackright_l_index_and_relation_exists(
                    k_blackright_move_obj=blackright_move_obj,
                    l_blackright_move_u_set=l_blackright_move_u_set)

            # assert
            for blackright_k_black_l_index, relation_exists in blackright_k_blackright_l_index_to_relation_exists_dic.items():
                assert_k_blackright_move_obj, assert_l_blackright_move_obj = EvaluationKkTable.build_blackright_k_blackright_l_moves_by_kl_index(
                        blackright_k_blackright_l_index=blackright_k_black_l_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if assert_k_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_k_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_k_blackright_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kl] 指し手を先手の向きに変えて復元できなかったエラー
is_white     :{is_white}
strict_move_u:{strict_move_obj.as_usi    :5} black_p_move_u:{assert_k_blackright_move_obj.as_usi:5}
move_rot_u   :{move_rot_obj.as_usi:5}
              {''                 :5} black_l_move_u:{assert_l_blackright_move_obj.as_usi:5}
""")

            #
            # ＫＱ
            #

            # 自玉の着手と、敵兵の応手の一覧から、ＫＱテーブルのインデックスと、関係の有無を格納した辞書を作成
            blackright_k_blackright_q_index_to_relation_exists_dic = kifuwarabe.evaluation_kq_table_obj_array[Turn.to_index(board.turn)].select_blackright_k_blackright_p_index_and_relation_exists(
                    k_black_move_obj=blackright_move_obj,
                    p_black_move_u_set=q_blackright_move_u_set)

            # assert
            for k_blackright_q_blackright_index, relation_exists in blackright_k_blackright_q_index_to_relation_exists_dic.items():
                assert_k_blackright_move_obj, assert_q_blackright_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                        k_blackright_p_blackright_index=k_blackright_q_blackright_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if assert_k_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_k_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_k_blackright_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kq] 指し手を先手の向きに変えて復元できなかったエラー
is_white     :{is_white}
strict_move_u:{strict_move_obj.as_usi    :5} black_p_move_u:{assert_k_blackright_move_obj.as_usi:5}
move_rot_u   :{move_rot_obj.as_usi       :5}
              {''                        :5} black_l_move_u:{assert_q_blackright_move_obj.as_usi:5}
""")

            return (blackright_k_blackright_l_index_to_relation_exists_dic,
                    blackright_k_blackright_q_index_to_relation_exists_dic,
                    None,
                    None)

        else:

            #
            # ＰＬ
            #

            # 自兵の着手と、敵玉の応手の一覧から、ＰＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            p_blackright_l_blackright_index_to_relation_exists_dic = kifuwarabe.evaluation_pl_table_obj_array[Turn.to_index(board.turn)].select_black_p_black_k_index_and_relation_exists(
                    p_black_move_obj=blackright_move_obj,
                    k_black_move_u_set=l_blackright_move_u_set)

            # assert
            for p_blackright_l_blackright_index, relation_exists in p_blackright_l_blackright_index_to_relation_exists_dic.items():
                assert_p_blackright_move_obj, assert_l_blackright_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                        p_blackright_k_blackright_index=p_blackright_l_blackright_index)

                check_black_p_black_l_index = EvaluationPkTable.get_black_p_black_k_index(
                        p_black_move_obj=assert_p_blackright_move_obj,
                        k_black_move_obj=assert_l_blackright_move_obj)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if p_blackright_l_blackright_index != check_black_p_black_l_index:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pl] インデックスから指し手を復元し、さらにインデックスに圧縮すると、元のインデックスに復元しなかったエラー
                   p_blackright_l_blackright_index:{        p_blackright_l_blackright_index:10}
check_black_p_black_l_index:{check_black_p_black_l_index  :10}
                   p_move_u:{assert_p_blackright_move_obj.as_usi:5}
                   l_move_u:{assert_l_blackright_move_obj.as_usi:5}
""")
                    else:
#                        print(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pl] インデックスから指し手を復元し、さらにインデックスに圧縮すると、元のインデックスに復元できた。Ok
#                   p_blackright_l_blackright_index:{        p_blackright_l_blackright_index:10}
#check_black_p_black_l_index:{check_black_p_black_l_index  :10}
#                   p_move_u:{assert_p_blackright_move_obj.as_usi:5}
#                   l_move_u:{assert_l_blackright_move_obj.as_usi:5}
#""")
                        pass

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:

                    if assert_p_blackright_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pl] 指し手を先手の向きに変えて復元できなかったエラー
is_white     :{is_white}
strict_move_u:{strict_move_obj.as_usi:5} black_p_move_u:{assert_p_blackright_move_obj.as_usi:5}
move_rot_u   :{move_rot_obj.as_usi   :5}
              {''                    :5} black_l_move_u:{assert_l_blackright_move_obj.as_usi:5}
""")

            #
            # ＰＱ
            #

            # 自兵の着手と、敵兵の応手の一覧から、ＰＱテーブルのインデックスと、関係の有無を格納した辞書を作成
            p_blackright_q_blackright_index_to_relation_exists_dic = kifuwarabe.evaluation_pq_table_obj_array[Turn.to_index(board.turn)].select_blackright_p_blackright_p_index_and_relation_exists(
                    p1_blackright_move_obj=blackright_move_obj,
                    p2_blackright_move_u_set=q_blackright_move_u_set)

            # assert
            for blackright_p_black_q_index, relation_exists in p_blackright_q_blackright_index_to_relation_exists_dic.items():
                assert_p_blackright_move_obj, assert_q_blackright_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                        p1_blackright_p2_blackright_index=blackright_p_black_q_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if assert_p_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pq] 着手が変わっているエラー
is_white  :{is_white}
                                           手番（Ｐ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｐ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_p_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_p_blackright_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pq] 指し手を先手の向きに変えて復元できなかったエラー
is_white     :{is_white}
strict_move_u:{strict_move_obj.as_usi:5} black_p_move_u:{assert_p_blackright_move_obj.as_usi:5}
move_rot_u   :{move_rot_obj.as_usi   :5}
              {''                    :5} black_l_move_u:{assert_q_blackright_move_obj.as_usi:5}
""")

            return (None,
                    None,
                    p_blackright_l_blackright_index_to_relation_exists_dic,
                    p_blackright_q_blackright_index_to_relation_exists_dic)


    @staticmethod
    def get_number_of_connection_for_kl_kq(
            k_blackright_l_blackright_index_to_relation_exists_dictionary,
            k_blackright_q_blackright_index_to_relation_exists_dictionary,
            is_debug=False):
        """ＫＬとＫＱの関係が有るものの数

        Parameters
        ----------
        k_blackright_l_blackright_index_to_relation_exists_dictionary : dict
            ＫＬ
        k_blackright_q_blackright_index_to_relation_exists_dictionary : dict
            ＫＱ
        is_debug : bool
            デバッグモードか？
        """
        number_of_connection = 0

        # ＫＬ
        for relation_exists in k_blackright_l_blackright_index_to_relation_exists_dictionary.values():
            if relation_exists == 1:
                number_of_connection += 1

        # ＫＱ
        for relation_exists in k_blackright_q_blackright_index_to_relation_exists_dictionary.values():
            if relation_exists == 1:
                number_of_connection += 1

        # デバッグ表示
        if is_debug:
            # ＫＬ
            for k_blackright_l_blackright_index, relation_exists in k_blackright_l_blackright_index_to_relation_exists_dictionary.items():
                if DebugPlan.get_number_of_connection_for_kl_kq:
                    black_k_move_obj, black_l_move_obj = EvaluationKkTable.build_blackright_k_blackright_l_moves_by_kl_index(
                            blackright_k_blackright_l_index=k_blackright_l_blackright_index)
                    print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kl]  k_blackright_l_blackright_index:{k_blackright_l_blackright_index:7}  K:{black_k_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＫＱ
            for k_blackright_q_blackright_index, relation_exists in k_blackright_q_blackright_index_to_relation_exists_dictionary.items():
                if DebugPlan.get_number_of_connection_for_kl_kq:
                    black_k_move_obj, black_q_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                            k_blackright_p_blackright_index=k_blackright_q_blackright_index)
                    print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kq]  k_blackright_q_blackright_index:{k_blackright_q_blackright_index:7}  K:{black_k_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        return number_of_connection


    @staticmethod
    def get_number_of_connection_for_pl_pq(
            p_blackright_l_blackright_index_to_relation_exists_dictionary,
            p_blackright_q_blackright_index_to_relation_exists_dictionary,
            is_debug):
        """ＰＬとＰＱの関係が有りのものの数

        Parameters
        ----------
        p_blackright_l_blackright_index_to_relation_exists_dictionary : dict
            ＫＬ
        p_blackright_q_blackright_index_to_relation_exists_dictionary
            ＫＱ
        is_debug : bool
            デバッグモードか？
        """
        number_of_connection = 0

        # ＰＬ
        for relation_exists in p_blackright_l_blackright_index_to_relation_exists_dictionary.values():
            if relation_exists == 1:
                number_of_connection += 1

        # ＰＱ
        for relation_exists in p_blackright_q_blackright_index_to_relation_exists_dictionary.values():
            if relation_exists == 1:
                number_of_connection += 1

        # デバッグ表示
        if is_debug:
            # ＰＬ
            for p_blackright_l_blackright_index, relation_exists in p_blackright_l_blackright_index_to_relation_exists_dictionary.items():
                if is_debug and DebugPlan.get_number_of_connection_for_pl_pq:
                    black_p_move_obj, black_l_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                            p_blackright_k_blackright_index=p_blackright_l_blackright_index)
                    print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pl]  p_blackright_l_blackright_index:{p_blackright_l_blackright_index:7}  P:{black_p_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＰＱ
            for p_blackright_q_blackright_index, relation_exists in p_blackright_q_blackright_index_to_relation_exists_dictionary.items():
                if is_debug and DebugPlan.get_number_of_connection_for_pl_pq:
                    black_p_move_obj, black_q_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                            p1_blackright_p2_blackright_index=p_blackright_q_blackright_index)
                    print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pq]  p_blackright_q_blackright_index:{p_blackright_q_blackright_index:7}  P:{black_p_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        return number_of_connection


    @staticmethod
    def get_summary(
            strict_move_obj,
            kifuwarabe,
            is_debug=False):
        """集計を取得

        Parameters
        ----------
        strict_move_obj : Move
            着手オブジェクト
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグモードか？

        Returns
        -------
        - p_blackright_l_blackright_index_to_relation_exists_dictionary
        - p_blackright_q_blackright_index_to_relation_exists_dictionary
        - is_king_move
        - positive_of_relation
        - total_of_relation
        """

        # 投了局面時、入玉宣言局面時、１手詰めは無視

        k_sq = BoardHelper.get_king_square(kifuwarabe.board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, strict_move_obj)

        if is_king_move:

            # １つの着手には、０～複数の着手がある木構造をしています。
            # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
            (k_blackright_l_blackright_index_to_relation_exists_dictionary,
             k_blackright_q_blackright_index_to_relation_exists_dictionary,
             _,
             _) = ChoiceBestMove.select_f_blackright_o_blackright_index_to_relation_exists(
                    strict_move_obj=strict_move_obj,
                    is_king_move=is_king_move,
                    board=kifuwarabe.board,
                    kifuwarabe=kifuwarabe)

            # assert
            for k_blackright_l_blackright_index, relation_exists in k_blackright_l_blackright_index_to_relation_exists_dictionary.items():
                assert_k_blackright_move_obj, assert_l_blackright_move_obj = EvaluationKkTable.build_blackright_k_blackright_l_moves_by_kl_index(
                        blackright_k_blackright_l_index=k_blackright_l_blackright_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if kifuwarabe.board.turn==cshogi.BLACK:
                    if assert_k_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_k_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_k_blackright_move_obj.rotate().as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kl] 指し手を先手の向きに変えて復元できなかったエラー
                                      元の指し手（Ｋ）:{strict_move_obj.as_usi:5}
                                           手番（Ｋ）:{Turn.to_string(kifuwarabe.board.turn)}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_k_blackright_move_obj.rotate().as_usi:5}
""")


            # assert
            for k_blackright_q_blackright_index, relation_exists in k_blackright_q_blackright_index_to_relation_exists_dictionary.items():
                assert_k_blackright_move_obj, assert_q_blackright_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                        k_blackright_p_blackright_index=k_blackright_q_blackright_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if kifuwarabe.board.turn==cshogi.BLACK:
                    if assert_k_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_k_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_k_blackright_move_obj.rotate().as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｋ）:{Turn.to_string(kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_k_blackright_move_obj.rotate().as_usi:5}
""")

            # ＫＬとＫＱの関係数
            total_of_relation = len(k_blackright_l_blackright_index_to_relation_exists_dictionary) + len(k_blackright_q_blackright_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > kl and kq]   total_of_relation:{total_of_relation}  =  len(k_blackright_l_blackright_index_to_relation_exists_dictionary):{len(k_blackright_l_blackright_index_to_relation_exists_dictionary)}  +  len(k_blackright_q_blackright_index_to_relation_exists_dictionary):{len(k_blackright_q_blackright_index_to_relation_exists_dictionary)}")

            # ＫＬとＫＱの関係が有りのものの数
            positive_of_relation = ChoiceBestMove.get_number_of_connection_for_kl_kq(
                    k_blackright_l_blackright_index_to_relation_exists_dictionary,
                    k_blackright_q_blackright_index_to_relation_exists_dictionary,
                    is_debug=is_debug)

            return (k_blackright_l_blackright_index_to_relation_exists_dictionary,
                    k_blackright_q_blackright_index_to_relation_exists_dictionary,
                    is_king_move,
                    positive_of_relation,
                    total_of_relation)

        else:

            # １つの着手には、０～複数の着手がある木構造をしています。
            # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
            (_,
             _,
             p_blackright_l_blackright_index_to_relation_exists_dictionary,
             p_blackright_q_blackright_index_to_relation_exists_dictionary) = ChoiceBestMove.select_f_blackright_o_blackright_index_to_relation_exists(
                    strict_move_obj=strict_move_obj,
                    is_king_move=is_king_move,
                    board=kifuwarabe.board,
                    kifuwarabe=kifuwarabe)

            # assert
            for p_blackright_l_blackright_index, relation_exists in p_blackright_l_blackright_index_to_relation_exists_dictionary.items():
                assert_p_blackright_move_obj, assert_l_blackright_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                        p_blackright_k_blackright_index=p_blackright_l_blackright_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if kifuwarabe.board.turn==cshogi.BLACK:
                    if assert_p_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_p_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_p_blackright_move_obj.rotate().as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pl] 指し手を先手の向きに変えて復元できなかったエラー
                                      元の指し手（Ｐ）:{strict_move_obj.as_usi:5}
                                           手番（Ｐ）:{Turn.to_string(kifuwarabe.board.turn)}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_p_blackright_move_obj.rotate().as_usi:5}
""")

            # assert
            for p_blackright_q_blackright_index, relation_exists in p_blackright_q_blackright_index_to_relation_exists_dictionary.items():
                assert_p_blackright_move_obj, assert_q_blackright_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                        p1_blackright_p2_blackright_index=p_blackright_q_blackright_index)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if kifuwarabe.board.turn==cshogi.BLACK:
                    if assert_p_blackright_move_obj.as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{strict_move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_p_blackright_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_p_blackright_move_obj.rotate().as_usi != strict_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pq] 指し手を先手の向きに変えて復元できなかったエラー
                                      元の指し手（Ｐ）:{strict_move_obj.as_usi:5}
                                           手番（Ｐ）:{Turn.to_string(kifuwarabe.board.turn)}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_p_blackright_move_obj.rotate().as_usi:5}
""")


            # ＰＬとＰＱの関係数
            total_of_relation = len(p_blackright_l_blackright_index_to_relation_exists_dictionary) + len(p_blackright_q_blackright_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > pl and pq]  total_of_relation:{total_of_relation}  =  len(p_blackright_l_blackright_index_to_relation_exists_dictionary):{len(p_blackright_l_blackright_index_to_relation_exists_dictionary)}  +  len(p_blackright_q_blackright_index_to_relation_exists_dictionary):{len(p_blackright_q_blackright_index_to_relation_exists_dictionarydictionary)}")

            # ＰＬとＰＱの関係が有りのものの数
            positive_of_relation = ChoiceBestMove.get_number_of_connection_for_pl_pq(
                    p_blackright_l_blackright_index_to_relation_exists_dictionary,
                    p_blackright_q_blackright_index_to_relation_exists_dictionary,
                    is_debug=is_debug)

            return (p_blackright_l_blackright_index_to_relation_exists_dictionary,
                    p_blackright_q_blackright_index_to_relation_exists_dictionary,
                    is_king_move,
                    positive_of_relation,
                    total_of_relation)


    @staticmethod
    def select_ranked_strict_f_move_u_set_facade(
            legal_moves,
            kifuwarabe,
            is_debug=False):
        """ランク付けされた指し手一覧（好手、悪手）を作成

        Parameters
        ----------
        legal_moves :
            合法手
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグか？

        Returns
        -------
        ranked_strict_move_u_set_list : list[set()]
        """

        ranked_strict_move_u_set_list = []

        # もし好手と悪手の２パターンなら tier_resolution は ２。
        # 配列のインデックスの小さい方がランクが上とする
        for i in range(0, kifuwarabe.tier_resolution):
            ranked_strict_move_u_set_list.append(set())

        # デバッグ表示
        if is_debug and DebugPlan.select_ranked_strict_f_move_u_set_facade:
            print(f"[choice best move]  kifuwarabe.tier_resolution:{kifuwarabe.tier_resolution}")

        for strict_move_id in legal_moves:
            strict_move_u = cshogi.move_to_usi(strict_move_id)

            # 着手オブジェクト
            strict_move_obj = Move.from_usi(strict_move_u)

            # 自駒と敵玉に対する関係の辞書
            (black_f_black_l_index_to_relation_exists_dictionary,
             # 自駒と敵兵に対する関係の辞書
             black_f_black_q_index_to_relation_exists_dictionary,
             # 玉の指し手か？
             is_king_move,
             # 関係が陽性の総数
             positive_of_relation,
             # 関係の総数
             total_of_relation) = ChoiceBestMove.get_summary(
                    strict_move_obj=strict_move_obj,
                    kifuwarabe=kifuwarabe,
                    is_debug=is_debug)

            #
            # 好手悪手の階位算出
            #
            (ranking_th, policy_rate) = EvaluationFacade.get_tier_th(
                    positive_of_relation=positive_of_relation,
                    total_of_relation=total_of_relation,
                    tier_resolution=kifuwarabe.tier_resolution)


            # 1 から始まる数を、0 から始まる数に変換して配列のインデックスに使用
            target_strict_move_u_set = ranked_strict_move_u_set_list[ranking_th - 1]
            target_strict_move_u_set.add(strict_move_u)

            # デバッグ表示
            if is_debug and DebugPlan.select_ranked_strict_f_move_u_set_facade:
                print(f"[choice best move]  strict_move_u:{strict_move_u}  policy_rate:{policy_rate}  ranking_th:{ranking_th}  positive_of_relation:{positive_of_relation}  total_of_relation:{total_of_relation}")


        # デバッグ表示
        if is_debug and DebugPlan.select_ranked_strict_f_move_u_set_facade:

            for tier_th in range(0, kifuwarabe.tier_resolution):

                print(f"[{datetime.datetime.now()}] [select ranked f move u set facade] ランク付けされた指し手一覧（{tier_th:2}位）")
                target_strict_move_u_set = ranked_strict_move_u_set_list[tier_th]

                for ranked_strict_move_u in target_strict_move_u_set:
                    print(f"[{datetime.datetime.now()}] [select ranked f move u set facade]  {tier_th}位  strict_move:{ranked_strict_move_u:5}")


        return ranked_strict_move_u_set_list


    @staticmethod
    def choice_best_move(
            legal_moves,
            kifuwarabe,
            is_debug=False):
        """最善の着手を選ぶ

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている
        is_debug : bool
            デバッグモードか？
        """

        # ランク付けされた指し手一覧
        ranked_strict_move_u_set_list = ChoiceBestMove.select_ranked_strict_f_move_u_set_facade(
                legal_moves=legal_moves,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        for ranked_strict_move_set in ranked_strict_move_u_set_list:

            # このランキングに候補手が無ければ、下のランキングへ
            if len(ranked_strict_move_set) < 1:
                continue

            # 候補手の中からランダムに選ぶ。USIの指し手の記法で返却
            return random.choice(list(ranked_strict_move_set))

        # ここにくることはないはず
        return "resign"
