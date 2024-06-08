import datetime
import random
from v_a49_0_debug_plan import DebugPlan
from v_a49_0_eval.facade import EvaluationFacade
from v_a49_0_eval.kk import EvaluationKkTable
from v_a49_0_eval.kp import EvaluationKpTable
from v_a49_0_eval.pk import EvaluationPkTable
from v_a49_0_eval.pp import EvaluationPpTable
from v_a49_0_misc.lib import Turn, Move


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

            # TODO どの関係を無効にするか、計画できないか？
            # TODO ＦＬから何個、ＦＱから何個と配分できないか？

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
                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=target_fl_index,
                        k_turn=self._board.turn)

                # assert
                if k_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > kl] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > kl] turn:{Turn.to_string(self._board.turn)}  kl_index:{target_fl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
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
            for target_fq_index in target_fq_index_list:
                k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=target_fq_index,
                        k_turn=self._board.turn)

                # assert
                if k_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > kl] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > kq] turn:{Turn.to_string(self._board.turn)}  kq_index:{target_fq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                        k_move_obj=k_move_obj,
                        p_move_obj=q_move_obj,
                        k_turn=self._board.turn,
                        bit=0)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            ##
            ## ＫＬ
            ##
            #for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
            #
            #    # デバッグ表示
            #    if is_debug and DebugPlan.evaluation_edit_weaken:
            #        print(f"[{datetime.datetime.now()}] [weaken > kl]  rest:{rest} / {len(fl_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
            #            kl_index=kl_index,
            #            k_turn=self._board.turn)
            #
            #    if k_move_obj.as_usi == move_u:
            #        if relation_exists == 1:
            #
            #            # デバッグ表示
            #            if is_debug and DebugPlan.evaluation_edit_weaken:
            #                print(f"[{datetime.datetime.now()}] [weaken > kl]  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
            #                    k_move_obj=k_move_obj,
            #                    l_move_obj=l_move_obj,
            #                    k_turn=self._board.turn,
            #                    bit=0)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1

            ##
            ## ＫＱ
            ##
            #for kq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
            #
            #    # デバッグ表示
            #    if is_debug and DebugPlan.evaluation_edit_weaken:
            #        print(f"[{datetime.datetime.now()}] [weaken > kq]  rest:{rest} / {len(fq_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
            #            kp_index=kq_index,
            #            k_turn=self._board.turn)
            #
            #    if k_move_obj.as_usi == move_u:
            #        if relation_exists == 1:
            #
            #            # デバッグ表示
            #            if is_debug and DebugPlan.evaluation_edit_weaken:
            #                print(f"[{datetime.datetime.now()}] [weaken > kq]  turn:{Turn.to_string(self._board.turn)}  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
            #                    k_move_obj=k_move_obj,
            #                    p_move_obj=q_move_obj,
            #                    k_turn=self._board.turn,
            #                    bit=0)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1

        else:

            # この着手に対する応手の関係を減らしたい
            #
            #   差を埋めればよい
            #
            difference = positive_of_relation - max_number_of_less_than_50_percent

            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_weaken:
                print(f"[{datetime.datetime.now()}] [weaken > pl and pq]  P:{move_obj.as_usi:5}  O:*****  policy:{policy}‰  陽性:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に悪手評価なので、弱化は不要です
            if difference < 1:
                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pl and pg]  既に悪手評価なので、弱化は不要です")

                return 'unnecessary'

            # 関係を difference 個削除
            rest = difference

            # TODO どの関係を無効にするか、計画できないか？
            # TODO ＰＬから何個、ＰＱから何個と配分できないか？

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
                p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                        pk_index=target_fl_index,
                        p_turn=self._board.turn)

                # assert
                if p_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > pl] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pl] turn:{Turn.to_string(self._board.turn)}  pl_index:{target_fl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
                        k_move_obj=p_move_obj,
                        l_move_obj=l_move_obj,
                        k_turn=self._board.turn,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            #
            # ＰＱ
            #
            for target_fq_index in target_fq_index_list:
                p_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=target_fq_index,
                        k_turn=self._board.turn)

                # assert
                if k_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [weaken > pq] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_weaken:
                    print(f"[{datetime.datetime.now()}] [weaken > pq] turn:{Turn.to_string(self._board.turn)}  pq_index:{target_fq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pp_moves(
                        p1_move_obj=p_move_obj,
                        p2_move_obj=q_move_obj,
                        p1_turn=self._board.turn,
                        bit=0)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            ##
            ## ＰＬ
            ##
            #for pl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
            #
            #    # デバッグ表示
            #    if is_debug and DebugPlan.evaluation_edit_weaken:
            #        print(f"[{datetime.datetime.now()}] [weaken > pl]  rest:{rest} / {len(fl_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
            #            pk_index=pl_index,
            #            p_turn=self._board.turn)
            #
            #    if p_move_obj.as_usi == move_u:
            #        if relation_exists == 1:
            #
            #            # デバッグ表示
            #            if is_debug and DebugPlan.evaluation_edit_weaken:
            #                print(f"[{datetime.datetime.now()}] [weaken > pl]  turn:{Turn.to_string(self._board.turn)}  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_pl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pk_moves(
            #                    p_move_obj=p_move_obj,
            #                    k_move_obj=l_move_obj,
            #                    p_turn=self._board.turn,
            #                    bit=0)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1
            #
            ##
            ## ＰＱ
            ##
            #for pq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
            #
            #    # デバッグ表示
            #    if is_debug and DebugPlan.evaluation_edit_weaken:
            #        print(f"[{datetime.datetime.now()}] [weaken > pq]  rest:{rest} / {len(fq_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
            #            pp_index=pq_index,
            #            p1_turn=self._board.turn)
            #
            #    if p_move_obj.as_usi == move_u:
            #        if relation_exists == 1:
            #
            #            # デバッグ表示
            #            if is_debug and DebugPlan.evaluation_edit_weaken:
            #                print(f"[{datetime.datetime.now()}] [weaken > pq]  turn:{Turn.to_string(self._board.turn)}  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pp_moves(
            #                    p1_move_obj=p_move_obj,
            #                    p2_move_obj=q_move_obj,
            #                    p1_turn=self._board.turn,
            #                    bit=0)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1


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
            if is_debug and DebugPlan.evaluation_edit_strengthen:
                print(f"[{datetime.datetime.now()}] [strengthen > kl and kq]  K:{move_obj.as_usi:5}  O:*****  policy:{policy}  有:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に好手評価なので、強化は不要です
            if difference < 1:
                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kl and kq]  既に好手評価なので、強化は不要です")

                return 'unnecessary'

            # 関係を difference 個追加
            rest = difference

            # TODO どの関係を有効にするか、計画できないか？
            # TODO ＫＬから何個、ＫＱから何個と配分できないか？

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
                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=target_fl_index,
                        k_turn=self._board.turn)

                # assert
                if k_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > kl] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kl] turn:{Turn.to_string(self._board.turn)}  kl_index:{target_fl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
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
            for target_fq_index in target_fq_index_list:
                k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=target_fq_index,
                        k_turn=self._board.turn)

                # assert
                if k_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > kl] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > kq] turn:{Turn.to_string(self._board.turn)}  kq_index:{target_fq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
                        k_move_obj=k_move_obj,
                        p_move_obj=q_move_obj,
                        k_turn=self._board.turn,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            ##
            ## ＫＬ
            ##
            #for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
            #
            #    if is_debug and DebugPlan.evaluation_edit_strengthen:
            #        print(f"[{datetime.datetime.now()}] [strengthen > kl]  rest:{rest} / {len(fl_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
            #            kl_index=kl_index,
            #            k_turn=self._board.turn)
            #
            #    if k_move_obj.as_usi == move_u:
            #        if relation_exists == 0:
            #
            #            if is_debug and DebugPlan.evaluation_edit_strengthen:
            #                print(f"[{datetime.datetime.now()}] [strengthen > kl]  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
            #                    k_move_obj=k_move_obj,
            #                    l_move_obj=l_move_obj,
            #                    k_turn=self._board.turn,
            #                    bit=1)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1
            #
            ##
            ## ＫＱ
            ##
            #for kq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
            #
            #    if is_debug and DebugPlan.evaluation_edit_strengthen:
            #        print(f"[{datetime.datetime.now()}] [strengthen > kq]  rest:{rest} / {len(fq_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
            #            kp_index=kq_index,
            #            k_turn=self._board.turn)
            #
            #    if k_move_obj.as_usi == move_u:
            #        if relation_exists == 0:
            #
            #            if is_debug and DebugPlan.evaluation_edit_strengthen:
            #                print(f"[{datetime.datetime.now()}] [strengthen > kq]  turn:{Turn.to_string(self._board.turn)}  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_kq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kp_moves(
            #                    k_move_obj=k_move_obj,
            #                    p_move_obj=q_move_obj,
            #                    k_turn=self._board.turn,
            #                    bit=1)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1

        else:

            # この着手に対する応手の関係を増やしたい
            #
            #   差を埋めればよい
            #
            difference = max_number_of_less_than_50_percent - positive_of_relation

            # デバッグ表示
            if is_debug and DebugPlan.evaluation_edit_strengthen:
                print(f"[{datetime.datetime.now()}] [strengthen > pl and pq]  P:{move_obj.as_usi:5}  O:*****  policy:{policy}‰  有:{positive_of_relation}  /  総:{total_of_relation}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

            # 既に好手評価なので、強化は不要です
            if difference < 1:
                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pl and pq]  既に好手評価なので、強化は不要です")

                return 'unnecessary'

            # 関係を difference 個追加
            rest = difference

            # TODO どの関係を有効にするか、計画できないか？
            # TODO ＰＬから何個、ＰＱから何個と配分できないか？

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
                p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                        pk_index=target_fl_index,
                        p_turn=self._board.turn)

                # assert
                if p_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > pl] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pl] turn:{Turn.to_string(self._board.turn)}  pl_index:{target_fl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
                        k_move_obj=p_move_obj,
                        l_move_obj=l_move_obj,
                        k_turn=self._board.turn,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            #
            # ＰＱ
            #
            for target_fq_index in target_fq_index_list:
                p_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=target_fq_index,
                        k_turn=self._board.turn)

                # assert
                if k_move_obj.as_usi != move_u:
                    raise ValueError(f"[{datetime.datetime.now()}] [strengthen > pq] 着手が変わっているエラー")

                # デバッグ表示
                if is_debug and DebugPlan.evaluation_edit_strengthen:
                    print(f"[{datetime.datetime.now()}] [strengthen > pq] turn:{Turn.to_string(self._board.turn)}  pq_index:{target_fq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  remove relation")

                is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pp_moves(
                        p1_move_obj=p_move_obj,
                        p2_move_obj=q_move_obj,
                        p1_turn=self._board.turn,
                        bit=1)

                if is_changed_temp:
                    is_changed = True
                    rest -= 1

            ##
            ## ＰＬ
            ##
            #for pl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
            #
            #    if is_debug and DebugPlan.evaluation_edit_strengthen:
            #        print(f"[{datetime.datetime.now()}] [strengthen > pl]  rest:{rest} / {len(fl_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
            #            pk_index=pl_index,
            #            p_turn=self._board.turn)
            #
            #    if p_move_obj.as_usi == move_u:
            #        if relation_exists == 0:
            #
            #            if is_debug and DebugPlan.evaluation_edit_strengthen:
            #                print(f"[{datetime.datetime.now()}] [strengthen > pl]  turn:{Turn.to_string(self._board.turn)}  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_pl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pk_moves(
            #                    p_move_obj=p_move_obj,
            #                    k_move_obj=l_move_obj,
            #                    p_turn=self._board.turn,
            #                    bit=1)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1
            #
            ##
            ## ＰＱ
            ##
            #for pq_index, relation_exists in fq_index_to_relation_exists_dictionary.items():
            #
            #    if is_debug and DebugPlan.evaluation_edit_strengthen:
            #        print(f"[{datetime.datetime.now()}] [strengthen > pq]  rest:{rest} / {len(fq_index_to_relation_exists_dictionary)}")
            #
            #    if rest < 1:
            #        break
            #
            #    p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
            #            pp_index=pq_index,
            #            p1_turn=self._board.turn)
            #
            #    if p_move_obj.as_usi == move_u:
            #        if relation_exists == 0:
            #
            #            if is_debug and DebugPlan.evaluation_edit_strengthen:
            #                print(f"[{datetime.datetime.now()}] [strengthen > pq]  turn:{Turn.to_string(self._board.turn)}  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")
            #
            #            is_changed_temp = self._kifuwarabe._evaluation_pq_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_pp_moves(
            #                    p1_move_obj=p_move_obj,
            #                    p2_move_obj=q_move_obj,
            #                    p1_turn=self._board.turn,
            #                    bit=1)
            #
            #            if is_changed_temp:
            #                is_changed = True
            #                rest -= 1


        # 正常終了
        if is_changed:
            return 'changed'

        else:
            return 'keep'
