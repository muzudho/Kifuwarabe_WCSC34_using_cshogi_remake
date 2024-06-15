import cshogi
import datetime
import random

# python v_a56_0.py
from     v_a56_0_debug_plan import DebugPlan
from     v_a56_0_eval.kk import EvaluationKkTable
from     v_a56_0_eval.kp import EvaluationKpTable
from     v_a56_0_eval.pk import EvaluationPkTable
from     v_a56_0_eval.pp import EvaluationPpTable
from     v_a56_0_eval.facade import EvaluationFacade
from     v_a56_0_misc.lib import Turn, MoveHelper, BoardHelper, Move


class ChoiceBestMove():
    """最善の着手を選ぶ"""


    #select_fo_index_to_relation_exists
    @staticmethod
    def select_black_f_black_o_index_to_relation_exists(
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
        black_k_black_l_index_to_relation_exists_dic
            自玉の着手と、敵玉の応手の関係の有無を格納した辞書
        black_black_k_black_q_index_to_relation_exists_dic
            自玉の着手と、敵兵の応手の関係の有無を格納した辞書
        black_p_black_l_index_to_relation_exists_dic
            自兵の着手と、敵玉の応手の関係の有無を格納した辞書
        black_p_black_q_index_to_relation_exists_dic
            自兵の着手と、敵兵の応手の関係の有無を格納した辞書
        """

        # assert
        # 着手は後手か？
        is_white = board.turn == cshogi.WHITE
        move_rot_obj = move_obj.rotate()

        # 応手の一覧を作成
        l_move_u_set, q_move_u_set = BoardHelper.create_counter_move_u_set(
                board=board,
                move_obj=move_obj)

        if is_king_move:

            #
            # ＫＬ
            #

            # 自玉の着手と、敵玉の応手の一覧から、ＫＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            black_k_black_l_index_to_relation_exists_dic = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(board.turn)].select_black_k_black_l_index_and_relation_exists(
                    k_move_obj=move_obj,
                    l_move_u_set=l_move_u_set,
                    # 先手の指し手になるよう調整します
                    shall_k_white_to_black=board.turn==cshogi.WHITE,
                    shall_l_white_to_black=board.turn==cshogi.BLACK)

            # assert
            for black_k_black_l_index, relation_exists in black_k_black_l_index_to_relation_exists_dic.items():
                assert_black_k_move_obj, assert_black_l_move_obj = EvaluationKkTable.build_black_k_black_l_moves_by_black_k_black_l_index(
                        black_k_black_l_index=black_k_black_l_index,
                        # black_k_black_l_index は先手なので、１８０°回転させてはいけません
                        shall_k_white_to_black=False,
                        shall_l_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if assert_black_k_move_obj.as_usi != move_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_black_k_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_k_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kl] 指し手を先手の向きに変えて復元できなかったエラー
is_white  :{is_white}
move_u    :{move_obj.as_usi    :5} black_p_move_u:{assert_black_k_move_obj.as_usi:5}
move_rot_u:{move_rot_obj.as_usi:5}
           {''                 :5} black_l_move_u:{assert_black_l_move_obj.as_usi:5}
""")

            #
            # ＫＱ
            #

            # 自玉の着手と、敵兵の応手の一覧から、ＫＱテーブルのインデックスと、関係の有無を格納した辞書を作成
            black_k_black_q_index_to_relation_exists_dic = kifuwarabe.evaluation_kq_table_obj_array[Turn.to_index(board.turn)].select_black_k_black_p_index_and_relation_exists(
                    k_move_obj=move_obj,
                    p_move_u_set=q_move_u_set,
                    # 先手の指し手になるよう調整します
                    shall_k_white_to_black=board.turn==cshogi.WHITE,
                    shall_p_white_to_black=board.turn==cshogi.BLACK)

            # assert
            for black_k_black_q_index, relation_exists in black_k_black_q_index_to_relation_exists_dic.items():
                assert_black_k_move_obj, assert_black_q_move_obj = EvaluationKpTable.build_black_k_black_p_moves_by_black_k_black_p_index(
                        kp_index=black_k_black_q_index,
                        # black_k_black_q_index は先手なので、１８０°回転させてはいけません
                        shall_k_white_to_black=False,
                        shall_p_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if assert_black_k_move_obj.as_usi != move_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_black_k_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_k_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > kq] 指し手を先手の向きに変えて復元できなかったエラー
is_white  :{is_white}
move_u    :{move_obj.as_usi    :5} black_p_move_u:{assert_black_k_move_obj.as_usi:5}
move_rot_u:{move_rot_obj.as_usi:5}
           {''                 :5} black_l_move_u:{assert_black_q_move_obj.as_usi:5}
""")

            return (black_k_black_l_index_to_relation_exists_dic,
                    black_k_black_q_index_to_relation_exists_dic,
                    None,
                    None)

        else:

            #
            # ＰＬ
            #

            # 自兵の着手と、敵玉の応手の一覧から、ＰＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            black_p_black_l_index_to_relation_exists_dic = kifuwarabe.evaluation_pl_table_obj_array[Turn.to_index(board.turn)].select_black_p_black_k_index_and_relation_exists(
                    p_move_obj=move_obj,
                    k_move_u_set=l_move_u_set,
                    # 先手の指し手になるよう調整します
                    p_turn=board.turn)

            # assert
            for black_p_black_l_index, relation_exists in black_p_black_l_index_to_relation_exists_dic.items():
                assert_black_p_move_obj, assert_black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                        pk_index=black_p_black_l_index,
                        # black_p_black_l_index は先手なので、１８０°回転させてはいけません
                        shall_p_white_to_black=False,
                        shall_k_white_to_black=False)

                check_black_p_black_l_index = EvaluationPkTable.get_black_p_black_k_index(
                        p_move_obj=assert_black_p_move_obj,
                        k_move_obj=assert_black_l_move_obj,
                        # assert_black_p_move_obj, assert_black_l_move_obj は先手なので、１８０°回転させてはいけません
                        shall_p_white_to_black=False,
                        shall_k_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if black_p_black_l_index != check_black_p_black_l_index:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pl] インデックスから指し手を復元し、さらにインデックスに圧縮すると、元のインデックスに復元しなかったエラー
                   black_p_black_l_index:{        black_p_black_l_index:10}
check_black_p_black_l_index:{check_black_p_black_l_index  :10}
                   p_move_u:{assert_black_p_move_obj.as_usi:5}
                   l_move_u:{assert_black_l_move_obj.as_usi:5}
""")
                    else:
#                        print(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pl] インデックスから指し手を復元し、さらにインデックスに圧縮すると、元のインデックスに復元できた。Ok
#                   black_p_black_l_index:{        black_p_black_l_index:10}
#check_black_p_black_l_index:{check_black_p_black_l_index  :10}
#                   p_move_u:{assert_black_p_move_obj.as_usi:5}
#                   l_move_u:{assert_black_l_move_obj.as_usi:5}
#""")
                        pass

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:

                    if assert_black_p_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pl] 指し手を先手の向きに変えて復元できなかったエラー
is_white  :{is_white}
move_u    :{move_obj.as_usi    :5} black_p_move_u:{assert_black_p_move_obj.as_usi:5}
move_rot_u:{move_rot_obj.as_usi:5}
           {''                 :5} black_l_move_u:{assert_black_l_move_obj.as_usi:5}
""")

            #
            # ＰＱ
            #

            # 自兵の着手と、敵兵の応手の一覧から、ＰＱテーブルのインデックスと、関係の有無を格納した辞書を作成
            black_p_black_q_index_to_relation_exists_dic = kifuwarabe.evaluation_pq_table_obj_array[Turn.to_index(board.turn)].select_black_p_black_p_index_and_relation_exists(
                    p1_move_obj=move_obj,
                    p2_move_u_set=q_move_u_set,
                    # 先手の指し手になるよう調整します
                    p1_turn=board.turn)

            # assert
            for black_p_black_q_index, relation_exists in black_p_black_q_index_to_relation_exists_dic.items():
                assert_black_p_move_obj, assert_black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                        pp_index=black_p_black_q_index,
                        # black_p_black_q_index は両方先手のインデックスなので、これ以上変更しません
                        shall_p1_white_to_black=False,
                        shall_p2_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if not is_white:
                    if assert_black_p_move_obj.as_usi != move_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pq] 着手が変わっているエラー
is_white  :{is_white}
                                           手番（Ｐ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｐ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_p_move_obj.as_usi != move_rot_obj.as_usi:
                        print(board)
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > select fo index to relation exests > pq] 指し手を先手の向きに変えて復元できなかったエラー
is_white  :{is_white}
move_u    :{move_obj.as_usi    :5} black_p_move_u:{assert_black_p_move_obj.as_usi:5}
move_rot_u:{move_rot_obj.as_usi:5}
           {''                 :5} black_l_move_u:{assert_black_q_move_obj.as_usi:5}
""")

            return (None,
                    None,
                    black_p_black_l_index_to_relation_exists_dic,
                    black_p_black_q_index_to_relation_exists_dic)


    @staticmethod
    def get_number_of_connection_for_kl_kq(
            black_k_black_l_index_to_relation_exists_dictionary,
            black_k_black_q_index_to_relation_exists_dictionary,
            board,
            is_debug=False):
        """ＫＬとＫＱの関係が有りのものの数

        Parameters
        ----------
        black_k_black_l_index_to_relation_exists_dictionary : dict
            ＫＬ
        black_k_black_q_index_to_relation_exists_dictionary
            ＫＱ
        board : cshogi.Board
            現局面
        is_debug : bool
            デバッグモードか？
        """
        number_of_connection = 0

        # ＫＬ
        for black_k_black_l_index, relation_exists in black_k_black_l_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # ＫＱ
        for black_k_black_q_index, relation_exists in black_k_black_q_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # デバッグ表示
        if is_debug:
            # ＫＬ
            for black_k_black_l_index, relation_exists in black_k_black_l_index_to_relation_exists_dictionary.items():
                if DebugPlan.get_number_of_connection_for_kl_kq:
                    black_k_move_obj, black_l_move_obj = EvaluationKkTable.build_black_k_black_l_moves_by_black_k_black_l_index(
                            black_k_black_l_index=black_k_black_l_index,
                            shall_k_white_to_black=board.turn==cshogi.WHITE,
                            shall_l_white_to_black=board.turn==cshogi.BLACK)
                    print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kl]  black_k_black_l_index:{black_k_black_l_index:7}  K:{black_k_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＫＱ
            for black_k_black_q_index, relation_exists in black_k_black_q_index_to_relation_exists_dictionary.items():
                if DebugPlan.get_number_of_connection_for_kl_kq:
                    black_k_move_obj, black_q_move_obj = EvaluationKpTable.build_black_k_black_p_moves_by_black_k_black_p_index(
                            kp_index=black_k_black_q_index,
                            shall_k_white_to_black=board.turn==cshogi.WHITE,
                            shall_p_white_to_black=board.turn==cshogi.BLACK)
                    print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kq]  black_k_black_q_index:{black_k_black_q_index:7}  K:{black_k_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        return number_of_connection


    @staticmethod
    def get_number_of_connection_for_pl_pq(
            black_p_black_l_index_to_relation_exists_dictionary,
            black_p_black_q_index_to_relation_exists_dictionary,
            board,
            is_debug):
        """ＰＬとＰＱの関係が有りのものの数

        Parameters
        ----------
        black_p_black_l_index_to_relation_exists_dictionary : dict
            ＫＬ
        black_p_black_q_index_to_relation_exists_dictionary
            ＫＱ
        board : cshogi.Board
            現局面
        is_debug : bool
            デバッグモードか？
        """
        number_of_connection = 0

        # ＰＬ
        for black_p_black_l_index, relation_exists in black_p_black_l_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # ＰＱ
        for black_p_black_q_index, relation_exists in black_p_black_q_index_to_relation_exists_dictionary.items():
            if relation_exists == 1:
                number_of_connection += 1

        # デバッグ表示
        if is_debug:
            # ＰＬ
            for black_p_black_l_index, relation_exists in black_p_black_l_index_to_relation_exists_dictionary.items():
                if is_debug and DebugPlan.get_number_of_connection_for_pl_pq:
                    black_p_move_obj, black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                            pk_index=black_p_black_l_index,
                            shall_p_white_to_black=board.turn==cshogi.WHITE,
                            shall_k_white_to_black=board.turn==cshogi.BLACK)
                    print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pl]  black_p_black_l_index:{black_p_black_l_index:7}  P:{black_p_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＰＱ
            for black_p_black_q_index, relation_exists in black_p_black_q_index_to_relation_exists_dictionary.items():
                if is_debug and DebugPlan.get_number_of_connection_for_pl_pq:
                    black_p_move_obj, black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                            pp_index=black_p_black_q_index,
                            # black_p_black_q_index は両方先手のインデックスなので、これ以上変更しません
                            shall_p1_white_to_black=False,
                            shall_p2_white_to_black=False)
                    print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pq]  black_p_black_q_index:{black_p_black_q_index:7}  P:{black_p_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

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
        - black_f_black_l_index_to_relation_exists_dictionary
        - black_f_black_q_index_to_relation_exists_dictionary
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
            (black_k_black_l_index_to_relation_exists_dictionary,
             black_k_black_q_index_to_relation_exists_dictionary,
             _,
             _) = ChoiceBestMove.select_black_f_black_o_index_to_relation_exists(
                    move_obj=move_obj,
                    is_king_move=is_king_move,
                    board=board,
                    kifuwarabe=kifuwarabe)

            # assert
            for black_k_black_l_index, relation_exists in black_k_black_l_index_to_relation_exists_dictionary.items():
                assert_black_k_move_obj, assert_black_l_move_obj = EvaluationKkTable.build_black_k_black_l_moves_by_black_k_black_l_index(
                        black_k_black_l_index=black_k_black_l_index,
                        # black_k_black_l_index は両方先手のインデックスなので、これ以上変更しません
                        shall_k_white_to_black=False,
                        shall_l_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if kifuwarabe.board.turn==cshogi.BLACK:
                    if assert_black_k_move_obj.as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_black_k_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_k_move_obj.rotate().as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kl] 指し手を先手の向きに変えて復元できなかったエラー
                                      元の指し手（Ｋ）:{move_obj.as_usi:5}
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_black_k_move_obj.rotate().as_usi:5}
""")


            # assert
            for black_k_black_q_index, relation_exists in black_k_black_q_index_to_relation_exists_dictionary.items():
                assert_black_k_move_obj, assert_black_q_move_obj = EvaluationKpTable.build_black_k_black_p_moves_by_black_k_black_p_index(
                        kp_index=black_k_black_q_index,
                        # black_k_black_q_index は両方先手のインデックスなので、これ以上変更しません
                        shall_k_white_to_black=False,
                        shall_p_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if kifuwarabe.board.turn==cshogi.BLACK:
                    if assert_black_k_move_obj.as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_black_k_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_k_move_obj.rotate().as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > kq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｋ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｋ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{assert_black_k_move_obj.rotate().as_usi:5}
""")

            # ＫＬとＫＱの関係数
            total_of_relation = len(black_k_black_l_index_to_relation_exists_dictionary) + len(black_k_black_q_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > kl and kq]   total_of_relation:{total_of_relation}  =  len(black_k_black_l_index_to_relation_exists_dictionary):{len(black_k_black_l_index_to_relation_exists_dictionary)}  +  len(black_k_black_q_index_to_relation_exists_dictionary):{len(black_k_black_q_index_to_relation_exists_dictionary)}")

            # ＫＬとＫＱの関係が有りのものの数
            positive_of_relation = ChoiceBestMove.get_number_of_connection_for_kl_kq(
                    black_k_black_l_index_to_relation_exists_dictionary,
                    black_k_black_q_index_to_relation_exists_dictionary,
                    board=board,
                    is_debug=is_debug)

            return (black_k_black_l_index_to_relation_exists_dictionary,
                    black_k_black_q_index_to_relation_exists_dictionary,
                    is_king_move,
                    positive_of_relation,
                    total_of_relation)

        else:

            # １つの着手には、０～複数の着手がある木構造をしています。
            # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
            (_,
             _,
             black_p_black_l_index_to_relation_exists_dictionary,
             black_p_black_q_index_to_relation_exists_dictionary) = ChoiceBestMove.select_black_f_black_o_index_to_relation_exists(
                    move_obj=move_obj,
                    is_king_move=is_king_move,
                    board=board,
                    kifuwarabe=kifuwarabe)

            # assert
            for black_p_black_l_index, relation_exists in black_p_black_l_index_to_relation_exists_dictionary.items():
                assert_black_p_move_obj, assert_black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                        pk_index=black_p_black_l_index,
                        # black_p_black_l_index は両方先手のインデックスなので、これ以上変更しません
                        shall_p_white_to_black=False,
                        shall_k_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if board.turn==cshogi.BLACK:
                    if assert_black_p_move_obj.as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｐ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_p_move_obj.rotate().as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pl] 指し手を先手の向きに変えて復元できなかったエラー
                                      元の指し手（Ｐ）:{move_obj.as_usi:5}
                                           手番（Ｐ）:{Turn.to_string(board.turn)}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.rotate().as_usi:5}
""")

            # assert
            for black_p_black_q_index, relation_exists in black_p_black_q_index_to_relation_exists_dictionary.items():
                assert_black_p_move_obj, assert_black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                        pp_index=black_p_black_q_index,
                        # black_p_black_q_index は両方先手のインデックスなので、これ以上変更しません
                        shall_p1_white_to_black=False,
                        shall_p2_white_to_black=False)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if board.turn==cshogi.BLACK:
                    if assert_black_p_move_obj.as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(board.turn)}
                                      元の指し手（Ｐ）:{move_obj.as_usi:5}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.as_usi:5}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if assert_black_p_move_obj.rotate().as_usi != move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [choice best move > pq] 指し手を先手の向きに変えて復元できなかったエラー
                                      元の指し手（Ｐ）:{move_obj.as_usi:5}
                                           手番（Ｐ）:{Turn.to_string(board.turn)}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.rotate().as_usi:5}
""")


            # ＰＬとＰＱの関係数
            total_of_relation = len(black_p_black_l_index_to_relation_exists_dictionary) + len(black_p_black_q_index_to_relation_exists_dictionary)
            #print(f"[{datetime.datetime.now()}] [get summary > pl and pq]  total_of_relation:{total_of_relation}  =  len(black_p_black_l_index_to_relation_exists_dictionary):{len(black_p_black_l_index_to_relation_exists_dictionary)}  +  len(black_p_black_q_index_to_relation_exists_dictionary):{len(black_p_black_q_index_to_relation_exists_dictionary)}")

            # ＰＬとＰＱの関係が有りのものの数
            positive_of_relation = ChoiceBestMove.get_number_of_connection_for_pl_pq(
                    black_p_black_l_index_to_relation_exists_dictionary,
                    black_p_black_q_index_to_relation_exists_dictionary,
                    board=board,
                    is_debug=is_debug)

            return (black_p_black_l_index_to_relation_exists_dictionary,
                    black_p_black_q_index_to_relation_exists_dictionary,
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
            # 好手悪手のランキング算出
            #
            (ranking_th, policy_rate) = EvaluationFacade.get_ranking_th(
                    positive_of_relation=positive_of_relation,
                    total_of_relation=total_of_relation,
                    ranking_resolution=kifuwarabe.ranking_resolution)


            # 1 から始まる数を、0 から始まる数に変換して配列のインデックスに使用
            target_set = ranked_move_u_set_list[ranking_th - 1]
            target_set.add(move_u)

            # デバッグ表示
            if is_debug and DebugPlan.select_ranked_f_move_u_set_facade:
                print(f"[choice best move]  move_u:{move_u}  policy_rate:{policy_rate}  ranking_th:{ranking_th}  positive_of_relation:{positive_of_relation}  total_of_relation:{total_of_relation}")


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
