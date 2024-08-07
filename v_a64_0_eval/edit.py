import cshogi
import datetime
import random

from v_a64_0_debug_plan import DebugPlan
from v_a64_0_eval.facade import EvaluationFacade
from v_a64_0_eval.kk import EvaluationKkTable
from v_a64_0_eval.kp import EvaluationKpTable
from v_a64_0_eval.pk import EvaluationPkTable
from v_a64_0_eval.pp import EvaluationPpTable
from v_a64_0_misc.choice_best_move import ChoiceBestMove
from v_a64_0_misc.lib import Turn, Move
from v_a64_0_misc.usi import Usi


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


    @staticmethod
    def let_change_amount(f_blackright_move_obj):
        """評価値テーブルの変更したセル数を算出

        Parameters
        ----------
        f_blackright_move_obj : Move
            着手点

        Returns
        -------
        change_amount
            変更量
        """
        # 盤の５筋以外の筋は、左右対称のとき、左辺と右辺の２か所に効くので、変化量は２倍
        (src_on_board, src_file_th, src_rank_th) = Usi.srcloc_to_file_th_rank_th(f_blackright_move_obj.srcloc)
        if src_on_board:
            if src_file_th == 5:
                change_amount = 1
            else:
                change_amount = 2

        # 打なら
        else:
            (dst_on_board, dst_file_th, dst_rank_th) = Usi.srcloc_to_file_th_rank_th(f_blackright_move_obj.dstsq)

            if dst_file_th == 5:
                change_amount = 1
            else:
                change_amount = 2

        return change_amount


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
        comment : str
            過程の説明
        """

        # 投了局面時、入玉宣言局面時、１手詰めは省略

        move_obj = Move.from_usi(move_u)

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
                f_strict_move_obj=move_obj,
                kifuwarabe=self._kifuwarabe,
                is_debug=is_debug)

        # assert: 与えた着手が変わってないか調べる
        if is_king_move:

            #
            # ＫＬ
            #
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                assert_k_blackright_move_obj, assert_l_blackright_move_obj = EvaluationKkTable.build_k_blackright_l_blackright_moves_by_kl_index(
                        k_blackright_l_blackright_index=black_f_black_l_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_k_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_k_blackright_move_obj.as_usi}")

            #
            # ＫＱ
            #
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                assert_k_blackright_move_obj, assert_p_blackright_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                        k_blackright_p_blackright_index=black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_k_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_k_blackright_move_obj.as_usi}")

        else:

            #
            # ＰＬ
            #
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                assert_p_blackright_move_obj, assert_l_blackright_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                        p_blackright_k_blackright_index=black_f_black_l_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_p_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_p_blackright_move_obj.as_usi}")

            #
            # ＰＱ
            #
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                assert_p1_blackright_move_obj, assert_p2_blackright_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                        p1_blackright_p2_blackright_index=black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_p1_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_p1_blackright_move_obj.as_usi}")


        # 減らすものがないので、弱化できなかった
        if positive_of_relation < 1:
            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken]  減らすものがないので、弱化できなかった")

            return ('already_empty', '減らすものがなかった')

        #
        # 好手悪手の階位算出
        #
        (ranking_th, policy_rate) = EvaluationFacade.get_tier_th(
                positive_of_relation=positive_of_relation,
                total_of_relation=total_of_relation,
                tier_resolution=self._kifuwarabe.tier_resolution)

        #
        # 弱める量
        #
        update_delta = int(total_of_relation // self._kifuwarabe.tier_resolution)
        if update_delta < 1:
            update_delta = 1

        if positive_of_relation < update_delta:
            update_delta = positive_of_relation

        is_changed = False

        # assert: 変更に挑戦した回数
        assert_challenge = 0
        assert_failed_to_change = 0

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
            target_black_f_black_l_index_list = list()
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                if relation_exists == 1:
                    target_black_f_black_l_index_list.append(black_f_black_l_index)

            target_black_f_black_q_index_list = list()
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                if relation_exists == 1:
                    target_black_f_black_q_index_list.append(black_f_black_q_index)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_black_f_black_l_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_black_f_black_q_index_list)

            if fl_size + fq_size < 1:
                return ("empty_moves", "変化量０だった")

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_black_f_black_l_index_list = random.choices(target_black_f_black_l_index_list, k=fl_target_size)
            target_black_f_black_q_index_list = random.choices(target_black_f_black_q_index_list, k=fq_target_size)

            #
            # ＫＬ
            #
            for target_black_f_black_l_index in target_black_f_black_l_index_list:
                k_blackright_move_obj, black_l_move_obj = EvaluationKkTable.build_k_blackright_l_blackright_moves_by_kl_index(
                        k_blackright_l_blackright_index=target_black_f_black_l_index)

                # assert
                if Usi.is_drop_by_srcloc(k_blackright_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > weaken > k] 玉の指し手で打なのはおかしい。 k_blackright_move_obj.srcloc_u:{Usi.srcloc_to_code(k_blackright_move_obj.srcloc)}  k_blackright_move_obj:{k_blackright_move_obj.dump()}")

                # assert
                if Usi.is_drop_by_srcloc(black_l_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > weaken > l] 玉の指し手で打なのはおかしい。 black_l_move_obj.srcloc_u:{Usi.srcloc_to_code(black_l_move_obj.srcloc)}  black_l_move_obj:{black_l_move_obj.dump()}")

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != k_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{k_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > kl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kl_index:{target_black_f_black_l_index:7}  K:{k_blackright_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ倒す
                (is_changed_temp, result_comment) = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exsits_by_black_k_black_l_moves(
                        k_blackright_move_obj=k_blackright_move_obj,
                        l_blackright_move_obj=black_l_move_obj,
                        bit=0)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(k_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

            #
            # ＫＱ
            #
            for target_black_f_black_q_index in target_black_f_black_q_index_list:
                k_blackright_move_obj, black_q_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                        k_blackright_p_blackright_index=target_black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != k_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                     元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{k_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > kq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kq_index:{target_black_f_black_q_index:7}  K:{k_blackright_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ倒す
                is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_black_k_black_p_moves(
                        k_blackright_move_obj=k_blackright_move_obj,
                        p_blackright_move_obj=black_q_move_obj,
                        bit=0)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(k_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

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
            target_black_f_black_l_index_list = list()
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_black_f_black_l_index_list.append(black_f_black_l_index)

            target_black_f_black_q_index_list = list()
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_black_f_black_q_index_list.append(black_f_black_q_index)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_black_f_black_l_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_black_f_black_q_index_list)

            if fl_size + fq_size < 1:
                return ("empty_moves", "変化量０だった")

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_black_f_black_l_index_list = random.choices(target_black_f_black_l_index_list, k=fl_target_size)
            target_black_f_black_q_index_list = random.choices(target_black_f_black_q_index_list, k=fq_target_size)

            #
            # ＰＬ
            #
            for target_black_f_black_l_index in target_black_f_black_l_index_list:
                p_blackright_move_obj, black_l_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                        p_blackright_k_blackright_index=target_black_f_black_l_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != p_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > pl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{p_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pl_index:{target_black_f_black_l_index:7}  P:{p_blackright_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ倒す
                is_changed_temp = self._kifuwarabe._evaluation_pl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_black_p_black_k_moves(
                        p_blackright_move_obj=p_blackright_move_obj,
                        k_blackright_move_obj=black_l_move_obj,
                        bit=0)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(p_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

            #
            # ＰＱ
            #
            for target_black_f_black_q_index in target_black_f_black_q_index_list:
                p_blackright_move_obj, black_q_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                        p1_blackright_p2_blackright_index=target_black_f_black_q_index)

                # assert
                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != p_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [weaken > pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{p_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pq_index:{target_black_f_black_q_index:7}  P:{p_blackright_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ倒す
                is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_black_p_black_p_moves(
                        p1_blackright_move_obj=p_blackright_move_obj,
                        p2_blackright_move_obj=black_q_move_obj,
                        bit=0)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(p_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

        # 正常終了
        if is_changed:
            return ('changed', '')

        else:
            return ('keep', f'減らせなかった  update_delta:{update_delta}  fl_target_size:{fl_target_size}  fq_target_size:{fq_target_size}  len(target_black_f_black_q_index_list):{len(target_black_f_black_q_index_list)}  challenge:{assert_challenge}  assert_failed_to_change:{assert_failed_to_change}')


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
            'failed', 'changed', 'keep', 'allready_empty', 'allready_full'
        comment : str
            過程の説明
        """

        # 投了局面時、入玉宣言局面時、１手詰めは省略

        move_obj = Move.from_usi(move_u)

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
                f_strict_move_obj=move_obj,
                kifuwarabe=self._kifuwarabe,
                is_debug=is_debug)

        # assert: 与えた着手が変わってないか調べる
        if is_king_move:

            #
            # ＫＬ
            #
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                assert_k_blackright_move_obj, assert_l_blackright_move_obj = EvaluationKkTable.build_k_blackright_l_blackright_moves_by_kl_index(
                        k_blackright_l_blackright_index=black_f_black_l_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_k_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_k_blackright_move_obj.as_usi}")

            #
            # ＫＱ
            #
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                assert_k_blackright_move_obj, assert_p_blackright_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                        k_blackright_p_blackright_index=black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_k_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_k_blackright_move_obj.as_usi}")

        else:

            #
            # ＰＬ
            #
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                assert_p_blackright_move_obj, assert_l_blackright_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                        p_blackright_k_blackright_index=black_f_black_l_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_p_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_p_blackright_move_obj.as_usi}")

            #
            # ＰＱ
            #
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                assert_p1_blackright_move_obj, assert_p2_blackright_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                        p1_blackright_p2_blackright_index=black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != assert_p1_blackright_move_obj.as_usi:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > fl] 着手が変わっているエラー  元の着手:{move_u}  作った着手:{assert_p1_blackright_move_obj.as_usi}")


        # 既に全ての議席が挙手しているので、強化は不要です
        if total_of_relation <= positive_of_relation:
            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_strengthen:
                print(f"[{datetime.datetime.now()}] [strengthen]  既に全ての議席が挙手しているので、強化は不要です")

            return ('already_full', '既に評価は最大だった')


        #
        # 好手悪手の階位算出
        #
        (ranking_th, policy_rate) = EvaluationFacade.get_tier_th(
                positive_of_relation=positive_of_relation,
                total_of_relation=total_of_relation,
                tier_resolution=self._kifuwarabe.tier_resolution)
        #
        # 強める量
        #
        #       全然好手は見つからないから、見つけたら一気に全議席取得するようにします
        #
        update_delta = total_of_relation
        #update_delta = int(total_of_relation // self._kifuwarabe.tier_resolution)
        if update_delta < 1:
            update_delta = 1

        if total_of_relation < positive_of_relation + update_delta:
            update_delta = total_of_relation - positive_of_relation

        is_changed = False

        # assert: 変更に挑戦した回数
        assert_challenge = 0
        assert_failed_to_change = 0

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
            target_black_f_black_l_index_list = list()
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_black_f_black_l_index_list.append(black_f_black_l_index)

            target_black_f_black_q_index_list = list()
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_black_f_black_q_index_list.append(black_f_black_q_index)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_black_f_black_l_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_black_f_black_q_index_list)

            if fl_size + fq_size < 1:
                return ("empty_moves", "変化量０だった")

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_black_f_black_l_index_list = random.choices(target_black_f_black_l_index_list, k=fl_target_size)
            target_black_f_black_q_index_list = random.choices(target_black_f_black_q_index_list, k=fq_target_size)

            #
            # ＫＬ
            #
            for target_black_f_black_l_index in target_black_f_black_l_index_list:
                k_blackright_move_obj, black_l_move_obj = EvaluationKkTable.build_k_blackright_l_blackright_moves_by_kl_index(
                        k_blackright_l_blackright_index=target_black_f_black_l_index)

                # assert
                if Usi.is_drop_by_srcloc(k_blackright_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > strengthen > k] 玉の指し手で打なのはおかしい。 k_blackright_move_obj.srcloc_u:{Usi.srcloc_to_code(k_blackright_move_obj.srcloc)}  k_blackright_move_obj:{k_blackright_move_obj.dump()}")

                # assert
                if Usi.is_drop_by_srcloc(black_l_move_obj.srcloc):
                    raise ValueError(f"[evaluation edit > strengthen > l] 玉の指し手で打なのはおかしい。 black_l_move_obj.srcloc_u:{Usi.srcloc_to_code(black_l_move_obj.srcloc)}  black_l_move_obj:{black_l_move_obj.dump()}")

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != k_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > kl] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{k_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kl_index:{target_black_f_black_l_index:7}  K:{k_blackright_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ立てる
                (is_changed_temp, result_comment) = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exsits_by_black_k_black_l_moves(
                        k_blackright_move_obj=k_blackright_move_obj,
                        l_blackright_move_obj=black_l_move_obj,
                        bit=1)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(k_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

            #
            # ＫＱ
            #
            for target_black_f_black_q_index in target_black_f_black_q_index_list:
                k_blackright_move_obj, black_q_move_obj = EvaluationKpTable.build_k_blackright_p_blackright_moves_by_kp_index(
                        k_blackright_p_blackright_index=target_black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != k_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > kq] 着手が変わっているエラー
                                           手番（Ｋ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｋ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｋ）:{k_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  kq_index:{target_black_f_black_q_index:7}  K:{k_blackright_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ立てる
                is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_black_k_black_p_moves(
                        k_blackright_move_obj=k_blackright_move_obj,
                        p_blackright_move_obj=black_q_move_obj,
                        bit=1)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(k_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

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
            target_black_f_black_l_index_list = list()
            for black_f_black_l_index, relation_exists in black_f_black_l_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:

                    # assert
                    assert_p_blackright_move_obj, assert_l_blackright_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                            p_blackright_k_blackright_index=black_f_black_l_index)

                    f_blackright_move_obj = Move.from_move_obj(
                            f_strict_move_obj=move_obj,
                            shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                    if f_blackright_move_obj.as_usi != assert_p_blackright_move_obj.as_usi:
                        raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pl and pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{assert_p_blackright_move_obj.as_usi}
""")

                    target_black_f_black_l_index_list.append(black_f_black_l_index)

            target_black_f_black_q_index_list = list()
            for black_f_black_q_index, relation_exists in black_f_black_q_index_to_relation_exists_dictionary.items():
                if relation_exists == 0:
                    target_black_f_black_q_index_list.append(black_f_black_q_index)

            # 例えばＦＬが２個、ＦＱが３０個あり、削除したい関係が９個の場合の配分
            # 　　　　１／１６　＝　２／（２＋３０）　　……　ＦＬの割合は１／１６
            # 　　　　０．１２５　＝　２×（１／１６）　　……　ＦＬの割合は０．１２５
            #        １　＝　ｒｏｕｎｄ（９　×　０．１２５）　　……削除するＦＬの個数は１
            #      　８　＝　９　ー　１　　……　削除するＦＱの個数は８
            # 例：ＦＬの個数　２
            fl_size = len(target_black_f_black_l_index_list)
            # 例：ＦＱの個数　３０
            fq_size = len(target_black_f_black_q_index_list)

            if fl_size + fq_size < 1:
                return ("empty_moves", "変化量０だった")

            # 例：ＦＬの割合　０．１２５
            fl_weight = fl_size / (fl_size + fq_size)
            # 例：削除するＦＬの個数　１
            fl_target_size = int(round(float(rest) * fl_weight)) # この四捨五入には丸めが入っているが、めんどくさいんでとりあえずこれを使う
            # 例：削除するＦＱの個数　８
            fq_target_size = int(rest - fl_target_size)
            # TODO 辞書のキーから何個抽出するとかできないか？ random.choices(sequence, k)
            target_black_f_black_l_index_list = random.choices(target_black_f_black_l_index_list, k=fl_target_size)
            target_black_f_black_q_index_list = random.choices(target_black_f_black_q_index_list, k=fq_target_size)

            #
            # ＰＬ
            #
            for target_black_f_black_l_index in target_black_f_black_l_index_list:
                p_blackright_move_obj, black_l_move_obj = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                        p_blackright_k_blackright_index=target_black_f_black_l_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != p_blackright_move_obj.as_usi:
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pl] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{p_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pl] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pl_index:{target_black_f_black_l_index:7}  P:{p_blackright_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ立てる
                is_changed_temp = self._kifuwarabe._evaluation_pl_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_black_p_black_k_moves(
                        p_blackright_move_obj=p_blackright_move_obj,
                        k_blackright_move_obj=black_l_move_obj,
                        bit=1)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(p_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

            #
            # ＰＱ
            #
            for target_black_f_black_q_index in target_black_f_black_q_index_list:
                p_blackright_move_obj, black_q_move_obj = EvaluationPpTable.build_p1_blackright_p2_blackright_moves_by_p1p2_index(
                        p1_blackright_p2_blackright_index=target_black_f_black_q_index)

                f_blackright_move_obj = Move.from_move_obj(
                        f_strict_move_obj=move_obj,
                        shall_white_to_black=self._kifuwarabe.board.turn==cshogi.WHITE,
                        use_only_right_side=True)

                if f_blackright_move_obj.as_usi != p_blackright_move_obj.as_usi:
                    # p_move_obj.as_usi:9d8e  move_u:4a4b
                    raise ValueError(f"""[{datetime.datetime.now()}] [strengthen > pq] 着手が変わっているエラー
                                           手番（Ｐ）:{Turn.to_string(self._kifuwarabe.board.turn)}
                                      元の指し手（Ｐ）:{move_u}
１回インデックスに変換し、インデックスから指し手を復元（Ｐ）:{p_blackright_move_obj.as_usi}
""")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pq] turn:{Turn.to_string(self._kifuwarabe.board.turn)}  pq_index:{target_black_f_black_q_index:7}  P:{p_blackright_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  remove relation")

                # 評価値のフラグを１つ立てる
                is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._kifuwarabe.board.turn)].set_relation_exists_by_black_p_black_p_moves(
                        p1_blackright_move_obj=p_blackright_move_obj,
                        p2_blackright_move_obj=black_q_move_obj,
                        bit=1)

                assert_challenge += 1

                if is_changed_temp:
                    is_changed = True

                    # 評価値テーブルの変更したセル数
                    change_amount = EvaluationEdit.let_change_amount(p_blackright_move_obj)

                    rest -= change_amount

                else:
                    assert_failed_to_change += 1

        # 正常終了
        if is_changed:
            return ('changed', '')

        else:
            return ('keep', f'増やせなかった  update_delta:{update_delta}  fl_target_size:{fl_target_size}  fq_target_size:{fq_target_size}')
