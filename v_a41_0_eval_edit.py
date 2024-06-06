import cshogi
import datetime
from v_a41_0_eval import EvaluationFacade
from v_a41_0_eval_kk import EvaluationKkTable
from v_a41_0_eval_kp import EvaluationKpTable
from v_a41_0_eval_pk import EvaluationPkTable
from v_a41_0_eval_pp import EvaluationPpTable
from v_a41_0_lib import Turn, Move


class EvaluationEdit():
    """評価値テーブルを編集します"""


    def __init__(
            self,
            board,
            kifuwarabe):
        """初期化

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        """
        self._board=board
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
         total_of_relation) = EvaluationFacade.get_summary(
                move_obj=move_obj,
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=is_debug)

        # ポリシー値（千分率）
        if 0 < total_of_relation:
            policy = EvaluationFacade.round_half_up(positive_of_relation * 1000 / total_of_relation)
        else:
            policy = 0

        # 関係の数の半分未満のうち、最大の数
        max_number_of_less_than_50_percent = EvaluationFacade.get_max_number_of_less_than_50_percent(
                total=total_of_relation)

        is_changed = False

        if is_king_move:

            # この着手に対する応手の関係を減らしたい
            #
            #   差を埋めればよい
            #
            difference = positive_of_relation - max_number_of_less_than_50_percent

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken > kl and kq]  K:{move_obj.as_usi:5}  O:*****  policy:{policy}‰  =  陽性:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に悪手評価なので、弱化は不要です
            if difference < 1:
                # デバッグ表示
                if is_debug:
                    print(f"[{datetime.datetime.now()}] [weaken > kl and kq]  既に悪手評価なので、弱化は不要です")

                return 'unnecessary'

            # 関係を difference 個削除
            rest = difference

            #
            # ＫＬ
            #

            print(f"[{datetime.datetime.now()}] [weaken > kl]  rest:{rest}  len(kl_indexes):{len(fl_index_to_relation_exists_dictionary)}")

            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [weaken > kl]  rest:{rest}  break")

                    break

                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index,
                        k_turn=self._board.turn)

                if k_move_obj.as_usi == move_u:
                    if relation_exists == 1:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [weaken > kl]  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")

                        is_changed_temp = self._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
                                k_move_obj=k_move_obj,
                                l_move_obj=l_move_obj,
                                k_turn=self._board.turn,
                                bit=0)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1

            #
            # ＫＱ
            #

            print(f"[{datetime.datetime.now()}] [weaken > kq]  rest:{rest}  len(kq_indexes):{len(fq_index_to_relation_exists_dictionary)}")

            for kq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [weaken > kq]  rest:{rest}  break")

                    break

                k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=kq_index,
                        k_turn=self._board.turn)

                if k_move_obj.as_usi == move_u:
                    if relation_exists == 1:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [weaken > kq]  turn:{Turn.to_string(self._board.turn)}  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")

                        is_changed_temp = self._evaluation_kq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                                k_move_obj=k_move_obj,
                                p_move_obj=q_move_obj,
                                k_turn=self._board.turn,
                                bit=0)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1

        else:

            # この着手に対する応手の関係を減らしたい
            #
            #   差を埋めればよい
            #
            difference = positive_of_relation - max_number_of_less_than_50_percent

            if is_debug:
                # デバッグ表示
                print(f"[{datetime.datetime.now()}] [weaken > pl and pq]  P:{move_obj.as_usi:5}  O:*****  policy:{policy}‰  陽性:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に悪手評価なので、弱化は不要です
            if difference < 1:
                if is_debug:
                    # デバッグ表示
                    print(f"[{datetime.datetime.now()}] [weaken > po]  既に悪手評価なので、弱化は不要です")

                return 'unnecessary'

            # 関係を difference 個削除
            rest = difference

            #
            # ＰＬ
            #

            print(f"[{datetime.datetime.now()}] [weaken > pl]  rest:{rest}  len(fl_indexes):{len(fl_index_to_relation_exists_dictionary)}")

            for pl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [weaken > pl]  rest:{rest}  break")
                    break

                p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                        pk_index=pl_index,
                        p_turn=self._board.turn)

                if p_move_obj.as_usi == move_u:
                    if relation_exists == 1:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [weaken > pl]  turn:{Turn.to_string(self._board.turn)}  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")

                        is_changed_temp = self._evaluation_pl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                                p_move_obj=p_move_obj,
                                k_move_obj=l_move_obj,
                                p_turn=self._board.turn,
                                bit=0)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1

            #
            # ＰＱ
            #

            print(f"[{datetime.datetime.now()}] [weaken > pq]  rest:{rest}  len(fq_indexes):{len(fq_index_to_relation_exists_dictionary)}")

            for pq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [weaken > pq]  rest:{rest}  break")
                    break

                p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                        pp_index=pq_index,
                        p1_turn=self._board.turn)

                if p_move_obj.as_usi == move_u:
                    if relation_exists == 1:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [weaken > pq]  turn:{Turn.to_string(self._board.turn)}  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")

                        is_changed_temp = self._evaluation_pq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pp_moves(
                                p1_move_obj=p_move_obj,
                                p2_move_obj=q_move_obj,
                                p1_turn=self._board.turn,
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
         total_of_relation) = EvaluationFacade.get_summary(
                move_obj=move_obj,
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=is_debug)

        # ポリシー値（千分率）
        if 0 < total_of_relation:
            policy = EvaluationFacade.round_half_up(positive_of_relation * 1000 / total_of_relation)
        else:
            policy = 0

        # 関係の数の半分未満のうち、最大の数
        max_number_of_less_than_50_percent = EvaluationFacade.get_max_number_of_less_than_50_percent(
                total=total_of_relation)

        is_changed = False

        if is_king_move:

            # この着手に対する応手の関係を増やしたい
            #
            #   差を埋めればよい
            #
            difference = max_number_of_less_than_50_percent - positive_of_relation

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [strengthen > kl and kq]  K:{move_obj.as_usi:5}  O:*****  policy:{policy}  有:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に好手評価なので、強化は不要です
            if difference < 1:
                # デバッグ表示
                if is_debug:
                    print(f"[{datetime.datetime.now()}] [strengthen > kl and kq]  既に好手評価なので、強化は不要です")

                return 'unnecessary'

            # 関係を difference 個追加
            rest = difference

            #
            # ＫＬ
            #

            print(f"[{datetime.datetime.now()}] [strengthen > kl]  rest:{rest}  len(kl_indexes):{len(fl_index_to_relation_exists_dictionary)}")

            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [strengthen > kl]  rest:{rest}  break")

                    break

                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index,
                        k_turn=self._board.turn)

                if k_move_obj.as_usi == move_u:
                    if relation_exists == 0:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [strengthen > kl]  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")

                        is_changed_temp = self._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
                                k_move_obj=k_move_obj,
                                l_move_obj=l_move_obj,
                                k_turn=self._board.turn,
                                bit=1)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1

            #
            # ＫＱ
            #

            print(f"[{datetime.datetime.now()}] [strengthen > kq]  rest:{rest}  len(kq_indexes):{len(fq_index_to_relation_exists_dictionary)}")

            for kq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [strengthen > kq]  rest:{rest}  break")

                    break

                k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=kq_index,
                        k_turn=self._board.turn)

                if k_move_obj.as_usi == move_u:
                    if relation_exists == 0:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [strengthen > kq]  turn:{Turn.to_string(self._board.turn)}  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")

                        is_changed_temp = self._evaluation_kq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                                k_move_obj=k_move_obj,
                                p_move_obj=q_move_obj,
                                bit=1,
                                is_rotate=self._board.turn==cshogi.WHITE)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1

        else:

            # この着手に対する応手の関係を増やしたい
            #
            #   差を埋めればよい
            #
            difference = max_number_of_less_than_50_percent - positive_of_relation

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [strengthen > pl and pq]  P:{move_obj.as_usi:5}  O:*****  policy:{policy}‰  有:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に好手評価なので、強化は不要です
            if difference < 1:
                # デバッグ表示
                if is_debug:
                    print(f"[{datetime.datetime.now()}] [strengthen > pl and pq]  既に好手評価なので、強化は不要です")

                return 'unnecessary'

            # 関係を difference 個追加
            rest = difference

            #
            # ＰＬ
            #

            print(f"[{datetime.datetime.now()}] [strengthen > pl]  rest:{rest}  len(pl_indexes):{len(fl_index_to_relation_exists_dictionary)}")

            for pl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [strengthen > pl]  rest:{rest}  break")

                    break

                p_move_obj, l_move_obj = EvaluationPkTable.destructure_pl_index(
                        pl_index=pl_index,
                        p_turn=self._board.turn)

                if p_move_obj.as_usi == move_u:
                    if relation_exists == 0:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [strengthen > pl]  turn:{Turn.to_string(self._board.turn)}  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")

                        is_changed_temp = self._evaluation_pl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                                p_move_obj=p_move_obj,
                                k_move_obj=l_move_obj,
                                bit=1,
                                is_rotate=self._board.turn==cshogi.WHITE)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1

            #
            # ＰＱ
            #

            print(f"[{datetime.datetime.now()}] [strengthen > pq]  rest:{rest}  len(pq_indexes):{len(fq_index_to_relation_exists_dictionary)}")

            for pq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():

                if rest < 1:
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [strengthen > pq]  rest:{rest}  break")

                    break

                p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                        pp_index=pq_index,
                        p1_turn=self._board.turn)

                if p_move_obj.as_usi == move_u:
                    if relation_exists == 0:

                        if is_debug:
                            print(f"[{datetime.datetime.now()}] [strengthen > pq]  turn:{Turn.to_string(self._board.turn)}  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")

                        is_changed_temp = self._evaluation_pq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                                p1_move_obj=p_move_obj,
                                p2_move_obj=q_move_obj,
                                bit=1,
                                is_rotate=self._board.turn==cshogi.WHITE)

                        if is_changed_temp:
                            is_changed = True
                            rest -= 1


        # 正常終了
        if is_changed:
            return 'changed'

        else:
            return 'keep'
