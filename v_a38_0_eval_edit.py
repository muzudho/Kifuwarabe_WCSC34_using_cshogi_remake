import cshogi
import datetime
from decimal import Decimal, ROUND_HALF_UP
from v_a38_0_eval import EvaluationFacade
from v_a38_0_eval_kk import EvaluationKkTable
from v_a38_0_eval_kp import EvaluationKpTable
from v_a38_0_eval_pk import EvaluationPkTable
from v_a38_0_eval_pp import EvaluationPpTable
from v_a38_0_lib import Turn, Move, MoveHelper, BoardHelper


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
            cmd_tail,
            is_debug=False):
        """評価値テーブルの調整。
        指定の着手のポリシー値が 0.5 未満になるよう価値値テーブルを調整する。
        code: weaken 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外

        Returns
        -------
        result_str : str
            'failed', 'changed', 'keep'
        """
        is_changed = False

        if cmd_tail.strip() == '':
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken] weaken command must be 1 move.  ex:`weaken 5i5h`  cmd_tail:`{cmd_tail}`")
            return 'failed'

        ## 投了局面時
        #if self._board.is_game_over():
        #    if is_debug:
        #        print(f'# failed to weaken (game over)', flush=True)
        #    return

        ## 入玉宣言局面時
        #if self._board.is_nyugyoku():
        #    if is_debug:
        #        print(f'# failed to weaken (nyugyoku win)', flush=True)
        #    return

        ## １手詰めを詰める
        ##
        ##   自玉に王手がかかっていない時で
        ##
        #if not self._board.is_check():
        #
        #    # １手詰めの指し手があれば、それを取得
        #    if (matemove := self._board.mate_move_in_1ply()):
        #
        #        best_move = cshogi.move_to_usi(matemove)
        #        if is_debug:
        #            print(f'# failed to weaken (mate {best_move})', flush=True)
        #        return


        move_u = cmd_tail

        move_obj = Move.from_usi(move_u)

        # １つの着手には、０～複数の着手がある木構造をしています。
        # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
        (kl_index_to_relation_exists_dictionary,
         kq_index_to_relation_exists_dictionary,
         pl_index_to_relation_exists_dictionary,
         pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                move_obj=move_obj,
                board=self._board,
                kifuwarabe=self._kifuwarabe)

        k_sq = BoardHelper.get_king_square(self._board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            # ＫＬとＫＱの関係数
            kl_kq_total = len(kl_index_to_relation_exists_dictionary) + len(kq_index_to_relation_exists_dictionary)
            print(f"[{datetime.datetime.now()}] [weaken > kl and kq]   kl_kq_total:{kl_kq_total}  =  len(kl_index_to_relation_exists_dictionary):{len(kl_index_to_relation_exists_dictionary)}  +  len(kq_index_to_relation_exists_dictionary):{len(kq_index_to_relation_exists_dictionary)}")

            def get_number_of_connection_for_kl_kq():
                """ＫＬとＫＱの関係が有りのものの数"""
                number_of_connection = 0

                # ＫＬ
                for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():

                    k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                            kl_index=kl_index,
                            k_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [weaken > kl]  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                # ＫＱ
                for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():

                    k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                            kp_index=kq_index,
                            k_turn=self._board.turn)

                    # 表示
                    if is_debug:
                        print(f"[{datetime.datetime.now()}] [weaken > kq]  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                return number_of_connection

            # ＫＬとＫＱの関係が有りのものの数
            number_of_connection_kl_kq = get_number_of_connection_for_kl_kq()

            # ＫＬとＫＱの関係の有りのものの数が５割未満の内、最大の整数
            #
            #   総数が０なら、答えは０
            #   総数が１なら、答えは０
            #   総数が２なら、答えは０
            #   総数が３なら、答えは１
            #   総数が４なら、答えは１
            #   総数が５なら、答えは２
            #
            # (1)   単純に kl_kq_total // 2 - 1 とすると、 kl_kq_total が３のときに答えが０になってしまう。
            #       そこで総数の半分は四捨五入しておく
            # (2)   総数が０のとき、答えはー１になってしまうので、最低の値は０にしておく
            #
            # (1)
            max_number_of_less_than_50_percent = Decimal(str(kl_kq_total / 2)).quantize(Decimal('0'), rounding=ROUND_HALF_UP) - 1
            # (2)
            if max_number_of_less_than_50_percent < 0:
                max_number_of_less_than_50_percent = 0

            # この着手に対する応手の関係を減らしたい
            #
            #   差を埋めればよい
            #
            difference = number_of_connection_kl_kq - max_number_of_less_than_50_percent

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken > kl and kq]  K:{move_obj.as_usi:5}  O:*****  有:{number_of_connection_kl_kq} / 総:{kl_kq_total}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

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

            print(f"[{datetime.datetime.now()}] [weaken > kl]  rest:{rest}  len(kl_indexes):{len(kl_index_to_relation_exists_dictionary)}")

            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():

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

            print(f"[{datetime.datetime.now()}] [weaken > kq]  rest:{rest}  len(kq_indexes):{len(kq_index_to_relation_exists_dictionary)}")

            for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():

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

            # ＰＬとＰＱの関係数
            pl_pq_total = len(pl_index_to_relation_exists_dictionary) + len(pq_index_to_relation_exists_dictionary)
            print(f"[{datetime.datetime.now()}] [weaken > pl and pq]  pl_pq_total:{pl_pq_total}  =  len(pl_index_to_relation_exists_dictionary):{len(pl_index_to_relation_exists_dictionary)}  +  len(pq_index_to_relation_exists_dictionary):{len(pq_index_to_relation_exists_dictionary)}")

            def get_number_of_connection_for_pl_pq():
                """ＰＬとＰＱの関係が有りのものの数"""
                number_of_connection = 0

                # ＰＬ
                for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():

                    p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                            pk_index=pl_index,
                            p_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [weaken > pl]  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                # ＰＱ
                for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():

                    p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                            pp_index=pq_index,
                            p1_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [weaken > pq]  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                return number_of_connection

            # ＰＬとＰＱの関係が有りのものの数
            number_of_connection_pl_pq = get_number_of_connection_for_pl_pq()

            max_number_of_less_than_50_percent = Decimal(str(pl_pq_total / 2)).quantize(Decimal('0'), rounding=ROUND_HALF_UP) - 1

            if max_number_of_less_than_50_percent < 0:
                max_number_of_less_than_50_percent = 0

            # この着手に対する応手の関係を減らしたい
            #
            #   差を埋めればよい
            #
            difference = number_of_connection_pl_pq - max_number_of_less_than_50_percent

            if is_debug:
                # デバッグ表示
                print(f"[{datetime.datetime.now()}] [weaken > pl and pq]  P:{move_obj.as_usi:5}  O:*****  有:{number_of_connection_pl_pq} / 総:{pl_pq_total}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

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

            print(f"[{datetime.datetime.now()}] [weaken > pl]  rest:{rest}  len(pl_indexes):{len(pl_index_to_relation_exists_dictionary)}")

            for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():

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

            print(f"[{datetime.datetime.now()}] [weaken > pq]  rest:{rest}  len(pq_indexes):{len(pq_index_to_relation_exists_dictionary)}")

            for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():

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
            cmd_tail,
            is_debug=False):
        """評価値テーブルの調整。
        指定の着手のポリシー値が 0.5 以上になるよう評価値テーブルを調整する。
        code: strengthen 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外

        Returns
        -------
        result_str : str
            'failed', 'changed', 'keep'
        """

        is_changed = False

        if cmd_tail.strip() == '':
            if is_debug:
                print(f"[{datetime.datetime.now()}] [strengthen] strengthen command must be 1 move.  ex:`strengthen 5i5h`  cmd_tail:`{cmd_tail}`")
            return 'failed'

        ## 投了局面時
        #if self._board.is_game_over():
        #    if is_debug:
        #        print(f'# failed to strengthen (game over)', flush=True)
        #    return

        ## 入玉宣言局面時
        #if self._board.is_nyugyoku():
        #    if is_debug:
        #        print(f'# failed to strengthen (nyugyoku win)', flush=True)
        #    return

        ## １手詰めを詰める
        ##
        ##   自玉に王手がかかっていない時で
        ##
        #if not self._board.is_check():
        #
        #    # １手詰めの指し手があれば、それを取得
        #    if (matemove := self._board.mate_move_in_1ply()):
        #
        #        best_move = cshogi.move_to_usi(matemove)
        #        if is_debug:
        #            print(f'# failed to strengthen (mate {best_move})', flush=True)
        #        return


        move_u = cmd_tail

        move_obj = Move.from_usi(move_u)

        # １つの着手には、０～複数の着手がある木構造をしています。
        # その木構造のパスをキーとし、そのパスが持つ有無のビット値を値とする辞書を作成します
        (kl_index_to_relation_exists_dictionary,
         kq_index_to_relation_exists_dictionary,
         pl_index_to_relation_exists_dictionary,
         pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                move_obj=move_obj,
                board=self._board,
                kifuwarabe=self._kifuwarabe)

        k_sq = BoardHelper.get_king_square(self._board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            # ＫＬとＫＱの関係数
            kl_kq_total = len(kl_index_to_relation_exists_dictionary) + len(kq_index_to_relation_exists_dictionary)

            def get_number_of_connection():
                """ＫＬとＫＱの関係が有りのものの数"""
                number_of_connection = 0

                # ＫＬ
                for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():

                    k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                            kl_index=kl_index,
                            k_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [strengthen > kl]  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                # ＫＱ
                for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():

                    k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                            kp_index=kq_index,
                            k_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [strengthen > kq]  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                return number_of_connection

            # ＫＬとＫＱの関係が有りのものの数
            number_of_connection_kl_kq = get_number_of_connection()

            # ＫＬの関係の有りのものの数が５割以上の内、最小の整数
            #
            #   総数が０なら、答えは０
            #   総数が１なら、答えは１
            #   総数が２なら、答えは１
            #   総数が３なら、答えは２
            #   総数が４なら、答えは２
            #   総数が５なら、答えは３
            #
            # (1)   単純に kl_kq_total // 2 とすると、 kl_kq_total が３のときに答えが１になってしまう。
            #       そこで総数の半分は四捨五入しておく
            #
            # (1)
            max_number_of_less_than_50_percent = Decimal(str(kl_kq_total / 2)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

            # この着手に対する応手の関係を増やしたい
            #
            #   差を埋めればよい
            #
            difference = max_number_of_less_than_50_percent - number_of_connection_kl_kq

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [strengthen > kl and kq]  K:{move_obj.as_usi:5}  O:*****  有:{number_of_connection_kl_kq} / 総:{kl_kq_total}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

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

            print(f"[{datetime.datetime.now()}] [strengthen > kl]  rest:{rest}  len(kl_indexes):{len(kl_index_to_relation_exists_dictionary)}")

            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():

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

            print(f"[{datetime.datetime.now()}] [strengthen > kq]  rest:{rest}  len(kq_indexes):{len(kq_index_to_relation_exists_dictionary)}")

            for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():

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

            # ＰＬとＰＱの関係数
            pl_pq_total = len(pl_index_to_relation_exists_dictionary) + len(pq_index_to_relation_exists_dictionary)

            def get_number_of_connection():
                """ＰＬとＰＱの関係が有りのものの数"""
                number_of_connection = 0

                # ＰＬ
                for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():

                    p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                            pk_index=pl_index,
                            p_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [strengthen > pl]  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                # ＰＱ
                for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():

                    p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                            pp_index=pq_index,
                            p1_turn=self._board.turn)

                    if is_debug:
                        # 表示
                        print(f"[{datetime.datetime.now()}] [strengthen > pq]  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                    if relation_exists == 1:
                        number_of_connection += 1

                return number_of_connection

            # ＰＬとＰＱの関係が有りのものの数
            number_of_connection_pl_pq = get_number_of_connection()

            max_number_of_less_than_50_percent = Decimal(str(pl_pq_total / 2)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)

            # この着手に対する応手の関係を増やしたい
            #
            #   差を埋めればよい
            #
            difference = max_number_of_less_than_50_percent - number_of_connection_pl_pq

            # デバッグ表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [strengthen > pl and pq]  P:{move_obj.as_usi:5}  O:*****  有:{number_of_connection_pl_pq} / 総:{pl_pq_total}  閾値:{max_number_of_less_than_50_percent}  difference:{difference}")

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

            print(f"[{datetime.datetime.now()}] [strengthen > pl]  rest:{rest}  len(pl_indexes):{len(pl_index_to_relation_exists_dictionary)}")

            for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():

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

            print(f"[{datetime.datetime.now()}] [strengthen > pq]  rest:{rest}  len(pq_indexes):{len(pq_index_to_relation_exists_dictionary)}")

            for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():

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
