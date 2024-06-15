import cshogi
import datetime
import random

from v_a56_0_debug_plan import DebugPlan
from v_a56_0_eval.facade import EvaluationFacade
from v_a56_0_eval.kk import EvaluationKkTable
from v_a56_0_eval.kp import EvaluationKpTable
from v_a56_0_eval.pk import EvaluationPkTable
from v_a56_0_eval.pp import EvaluationPpTable
from v_a56_0_misc.choice_best_move import ChoiceBestMove
from v_a56_0_misc.lib import Turn, Move
from v_a56_0_misc.usi import Usi


class EvaluationEdit():
    """評価値テーブルを編集します"""


    def __init__(
            self,
            kifuwarabe):
        """初期化

        Parameters
        ----------
        kifuwarabe : Kifuwarabe
            きふわらべ
        """
        self._kifuwarabe=kifuwarabe


    def weaken(
            self,
            move_u,
            is_debug=False):
        """評価値テーブルの調整。
        指定の着手のポリシー値が 0.5 未満になるよう価値値テーブルを調整する。
        code: weaken 5i5h

        Parameters
        ----------
        move_u : str
            着手
        is_debug : bool
            デバッグモードか？

        Returns
        -------
        result_str : str
            'failed', 'changed', 'keep'
        """

        # 投了局面時、入玉宣言局面時、１手詰めは省略

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
                board=self._kifuwarabe.board,
                kifuwarabe=self._kifuwarabe,
                is_debug=is_debug)

        # assert
        for fl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
            assert_black_p_move_obj, assert_black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                    pk_index=fl_index,
                    shall_p_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

            # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
            if self._kifuwarabe.board.turn==cshogi.BLACK:
                if assert_black_p_move_obj.as_usi != move_u:
                    # FIXME Rotate でも絡んでいる不具合か？
                    # [2024-06-14 00:23:32.615808] [weaken > fl] 着手が変わっているエラー  p_move_obj.as_usi:7f3c  move_u:4c3c
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > fl] 着手が変わっているエラー
                                           手番:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手:{move_u}
１回インデックスに変換し、インデックスから指し手を復元:{assert_black_p_move_obj.as_usi}
""")

            # 着手が後手なら、１８０°回転させるので、インデックスは変わる
            else:
                if assert_black_p_move_obj.rotate().as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > fl] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手:{move_u}
１回インデックスに変換し、インデックスから指し手を復元:{assert_black_p_move_obj.rotate().as_usi}
""")

        # assert
        for fq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
            assert_black_p_move_obj, assert_black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                    pp_index=fq_index,
                    shall_p1_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

            # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
            if self._kifuwarabe.board.turn==cshogi.BLACK:
                if assert_black_p_move_obj.as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > fq] 着手が変わっているエラー
                                           手番:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手:{move_u}
１回インデックスに変換し、インデックスから指し手を復元:{assert_black_p_move_obj.as_usi}
""")

            # 着手が後手なら、１８０°回転させるので、インデックスは変わる
            else:
                if assert_black_p_move_obj.rotate().as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > fq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手:{move_u}
１回インデックスに変換し、インデックスから指し手を復元:{assert_black_p_move_obj.rotate().as_usi}
""")


        # 減らすものがないので、弱化は不要です
        if positive_of_relation < 1:
            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken]  減らすものがないので、弱化は不要です")

            return 'unnecessary'

        #
        # 好手悪手のランキング算出
        #
        (ranking_th, policy_rate) = EvaluationFacade.get_ranking_th(
                positive_of_relation=positive_of_relation,
                total_of_relation=total_of_relation,
                ranking_resolution=self._kifuwarabe.ranking_resolution)

        #
        # 弱める量
        #
        update_delta = int(total_of_relation // self._kifuwarabe.ranking_resolution)
        if update_delta < 1:
            update_delta = 1

        if positive_of_relation < update_delta:
            update_delta = positive_of_relation

        is_changed = False

        if is_king_move:

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken > kl and kq]  K:{move_obj.as_usi:5}  O:*****  policy:{policy_rate}  =  陽性:{positive_of_relation}  /  総:{total_of_relation}  update_delta:{update_delta}")

            # 関係を update_delta 個削除
            rest = update_delta

            #
            # ＦＬから何個、ＦＱから何個と配分して弱化していく
            #

            # ビットが立っている項目だけ残します
            target_fl_index_list = list()
            for key, relation_exists in fl_index_to_relation_exists_dictionary.items():
                if relation_exists == 1:
                    target_fl_index_list.append(key)

            target_fq_index_list = list()
            for key, relation_exists in fq_index_to_relation_exists_dictionary.items():
                if relation_exists == 1:
                    target_fq_index_list.append(key)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_fl_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_fq_index_list)

            if fl_size + fq_size < 1:
                return "empty_moves"

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_fl_index_list = random.choices(target_fl_index_list, k=fl_target_size)
            target_fq_index_list = random.choices(target_fq_index_list, k=fq_target_size)

            #
            # ＫＬ
            #
            for target_fl_index in target_fl_index_list:
                black_k_move_obj, white_l_move_obj = EvaluationKkTable.build_k_l_moves_by_kl_index(
                        kl_index=target_fl_index,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # assert
                if Usi.is_drop_by_srcloc(black_k_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > weaken > k] 玉の指し手で打なのはおかしい。 black_k_move_obj.srcloc_u:{Usi.srcloc_to_code(black_k_move_obj.srcloc)}  black_k_move_obj:{black_k_move_obj.dump()}")

                # assert
                if Usi.is_drop_by_srcloc(white_l_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > weaken > l] 玉の指し手で打なのはおかしい。 white_l_move_obj.srcloc_u:{Usi.srcloc_to_code(white_l_move_obj.srcloc)}  white_l_move_obj:{white_l_move_obj.dump()}")

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_k_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_k_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > kl] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > kl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kl_index:{target_fl_index:7}  K:{black_k_move_obj.as_usi:5}  L:{white_l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exsits_by_kl_moves(
                        k_move_obj=black_k_move_obj,
                        l_move_obj=white_l_move_obj,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=0)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            #
            # ＫＱ
            #
            for target_fq_index in target_fq_index_list:
                black_k_move_obj, white_q_move_obj = EvaluationKpTable.build_k_p_moves_by_kp_index(
                        kp_index=target_fq_index,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_k_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                     元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_k_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > kq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                     元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > kq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kq_index:{target_fq_index:7}  K:{black_k_move_obj.as_usi:5}  Q:{white_q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_kp_moves(
                        k_move_obj=black_k_move_obj,
                        p_move_obj=white_q_move_obj,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=0)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

        else:

            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_weaken:
                print(f"[{datetime.datetime.now()}] [weaken > pl and pq]  P:{move_obj.as_usi:5}  O:*****  policy:{policy_rate}  陽性:{positive_of_relation}  /  総:{total_of_relation}  update_delta:{update_delta}")

            # 関係を update_delta 個削除
            rest = update_delta

            #
            # ＰＬから何個、ＰＱから何個と配分できないか？
            #

            # ビットが下りている項目だけ残します
            target_fl_index_list = list()
            for key, relation_exists in fl_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_fl_index_list.append(key)

            target_fq_index_list = list()
            for key, relation_exists in fq_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_fq_index_list.append(key)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_fl_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_fq_index_list)

            if fl_size + fq_size < 1:
                return "empty_moves"

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_fl_index_list = random.choices(target_fl_index_list, k=fl_target_size)
            target_fq_index_list = random.choices(target_fq_index_list, k=fq_target_size)

            #
            # ＰＬ
            #
            for target_fl_index in target_fl_index_list:
                black_p_move_obj, black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                        pk_index=target_fl_index,
                        shall_p_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_p_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > pl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_p_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > pl] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pl_index:{target_fl_index:7}  P:{black_p_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_pk_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exsits_by_pk_moves(
                        k_move_obj=black_p_move_obj,
                        l_move_obj=black_l_move_obj,
                        k_turn=self._kifuwarabe.board.turn,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            #
            # ＰＱ
            #
            for target_fq_index in target_fq_index_list:
                black_p_move_obj, black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                        pp_index=target_fq_index,
                        shall_p1_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_p_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_p_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [weaken > pq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pq_index:{target_fq_index:7}  P:{black_p_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_pp_moves(
                        p1_move_obj=black_p_move_obj,
                        p2_move_obj=black_q_move_obj,
                        shall_p1_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=0)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

        # 正常終了
        if is_changed:
            return 'changed'

        else:
            return 'keep'


    def strengthen(
            self,
            move_u,
            is_debug=False):
        """評価値テーブルの調整。
        指定の着手のポリシー値が 0.5 以上になるよう評価値テーブルを調整する。
        code: strengthen 5i5h

        Parameters
        ----------
        move_u : str
            着手

        Returns
        -------
        result_str : str
            'failed', 'changed', 'keep'
        """

        # 投了局面時、入玉宣言局面時、１手詰めは省略

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
                board=self._kifuwarabe.board,
                kifuwarabe=self._kifuwarabe,
                is_debug=is_debug)

        # assert
        for fl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
            assert_black_p_move_obj, assert_black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                    pk_index=fl_index,
                    shall_p_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)
            
            # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
            if self._kifuwarabe.board.turn==cshogi.BLACK:
                if assert_black_p_move_obj.as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > fl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.as_usi}
""")

            # 着手が後手なら、１８０°回転させるので、インデックスは変わる
            else:
                if assert_black_p_move_obj.rotate().as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > fl] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.rotate().as_usi}
""")

        # assert
        for fq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
            assert_black_p_move_obj, assert_black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                    pp_index=fq_index,
                    shall_p1_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)
            
            # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
            if self._kifuwarabe.board.turn==cshogi.BLACK:
                if assert_black_p_move_obj.as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > fq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.as_usi}
""")

            # 着手が後手なら、１８０°回転させるので、インデックスは変わる
            else:
                if assert_black_p_move_obj.rotate().as_usi != move_u:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > fq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.rotate().as_usi}
""")

        # 既に全ての議席が挙手しているので、強化は不要です
        if total_of_relation <= positive_of_relation:
            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_strengthen:
                print(f"[{datetime.datetime.now()}] [strengthen]  既に全ての議席が挙手しているので、強化は不要です")

            return 'unnecessary'


        #
        # 好手悪手のランキング算出
        #
        (ranking_th, policy_rate) = EvaluationFacade.get_ranking_th(
                positive_of_relation=positive_of_relation,
                total_of_relation=total_of_relation,
                ranking_resolution=self._kifuwarabe.ranking_resolution)
        #
        # 強める量
        #
        update_delta = int(total_of_relation // self._kifuwarabe.ranking_resolution)
        if update_delta < 1:
            update_delta = 1

        if total_of_relation < positive_of_relation + update_delta:
            update_delta = total_of_relation - positive_of_relation

        is_changed = False

        if is_king_move:

            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_strengthen:
                print(f"[{datetime.datetime.now()}] [strengthen > kl and kq]  K:{move_obj.as_usi:5}  O:*****  policy:{policy_rate}  有:{positive_of_relation}  /  総:{total_of_relation}  update_delta:{update_delta}")

            # 関係を update_delta 個追加
            rest = update_delta

            #
            # ＫＬから何個、ＫＱから何個と配分する
            #

            # ビットが下りている項目だけ残します
            target_fl_index_list = list()
            for fl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_fl_index_list.append(fl_index)

            target_fq_index_list = list()
            for fq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_fq_index_list.append(fq_index)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_fl_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_fq_index_list)

            if fl_size + fq_size < 1:
                return "empty_moves"

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_fl_index_list = random.choices(target_fl_index_list, k=fl_target_size)
            target_fq_index_list = random.choices(target_fq_index_list, k=fq_target_size)

            #
            # ＫＬ
            #
            for target_fl_index in target_fl_index_list:
                black_k_move_obj, white_l_move_obj = EvaluationKkTable.build_k_l_moves_by_kl_index(
                        kl_index=target_fl_index,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # assert
                if Usi.is_drop_by_srcloc(black_k_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > strengthen > k] 玉の指し手で打なのはおかしい。 black_k_move_obj.srcloc_u:{Usi.srcloc_to_code(black_k_move_obj.srcloc)}  black_k_move_obj:{black_k_move_obj.dump()}")

                # assert
                if Usi.is_drop_by_srcloc(white_l_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > strengthen > l] 玉の指し手で打なのはおかしい。 white_l_move_obj.srcloc_u:{Usi.srcloc_to_code(white_l_move_obj.srcloc)}  white_l_move_obj:{white_l_move_obj.dump()}")

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_k_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_k_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > kl] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.rotate().as_usi}
""")


                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kl_index:{target_fl_index:7}  K:{black_k_move_obj.as_usi:5}  L:{white_l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exsits_by_kl_moves(
                        k_move_obj=black_k_move_obj,
                        l_move_obj=white_l_move_obj,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            #
            # ＫＱ
            #
            for target_fq_index in target_fq_index_list:
                black_k_move_obj, white_q_move_obj = EvaluationKpTable.build_k_p_moves_by_kp_index(
                        kp_index=target_fq_index,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_k_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_k_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > kq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{black_k_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kq_index:{target_fq_index:7}  K:{black_k_move_obj.as_usi:5}  Q:{white_q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_kp_moves(
                        k_move_obj=black_k_move_obj,
                        p_move_obj=white_q_move_obj,
                        shall_k_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

        else:

            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_strengthen:
                print(f"[{datetime.datetime.now()}] [strengthen > pl and pq]  P:{move_obj.as_usi:5}  O:*****  policy:{policy_rate}  有:{positive_of_relation}  /  総:{total_of_relation}  update_delta:{update_delta}")

            # 関係を update_delta 個追加
            rest = update_delta

            #
            # ＰＬから何個、ＰＱから何個と配分する
            #

            # ビットが下りている項目だけ残します
            target_fl_index_list = list()
            for fl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:

                    # assert
                    assert_black_p_move_obj, assert_black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                            pk_index=fl_index,
                            shall_p_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                    # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                    if self._kifuwarabe.board.turn==cshogi.BLACK:
                        if assert_black_p_move_obj.as_usi != move_u:
                            raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pl and pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.as_usi}
""")

                    # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                    else:
                        if assert_black_p_move_obj.rotate().as_usi != move_u:
                            raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pl and pq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_black_p_move_obj.rotate().as_usi}
""")

                    target_fl_index_list.append(fl_index)

            target_fq_index_list = list()
            for fq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_fq_index_list.append(fq_index)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_fl_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_fq_index_list)

            if fl_size + fq_size < 1:
                return "empty_moves"

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_fl_index_list = random.choices(target_fl_index_list, k=fl_target_size)
            target_fq_index_list = random.choices(target_fq_index_list, k=fq_target_size)

            #
            # ＰＬ
            #
            for target_fl_index in target_fl_index_list:
                black_p_move_obj, black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                        pk_index=target_fl_index,
                        shall_p_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_p_move_obj.as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_p_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pl] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pl_index:{target_fl_index:7}  P:{black_p_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_pl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_pk_moves(
                        p_move_obj=black_p_move_obj,
                        k_move_obj=black_l_move_obj,
                        shall_p_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            #
            # ＰＱ
            #
            for target_fq_index in target_fq_index_list:
                black_p_move_obj, black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                        pp_index=target_fq_index,
                        shall_p1_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE)

                # 着手が先手なら、１８０°回転させないので、インデックスは変わらない
                if self._kifuwarabe.board.turn==cshogi.BLACK:
                    if black_p_move_obj.as_usi != move_u:
                        # p_move_obj.as_usi:9d8e  move_u:4a4b
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.as_usi}
""")

                # 着手が後手なら、１８０°回転させるので、インデックスは変わる
                else:
                    if black_p_move_obj.rotate().as_usi != move_u:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pq] 指し手を先手の向きに変えて復元できなかったエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{black_p_move_obj.rotate().as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pq_index:{target_fq_index:7}  P:{black_p_move_obj.as_usi:5}  Q:{white_q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_pp_moves(
                        p1_move_obj=black_p_move_obj,
                        p2_move_obj=white_q_move_obj,
                        shall_p1_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

        # 正常終了
        if is_changed:
            return 'changed'

        else:
            return 'keep'