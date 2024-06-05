import datetime
from decimal import Decimal, ROUND_HALF_UP
from v_a39_0_debug_plan import DebugPlan
from v_a39_0_eval_kk import EvaluationKkTable
from v_a39_0_eval_kp import EvaluationKpTable
from v_a39_0_eval_pk import EvaluationPkTable
from v_a39_0_eval_pp import EvaluationPpTable
from v_a39_0_lib import Turn, Move, MoveHelper, BoardHelper, MoveListHelper, PolicyHelper


class MoveAndPolicyHelper():
    """評価値付きの指し手のリストのヘルパー"""


    #get_moves
    @staticmethod
    def get_best_moves(
            weakest0_strongest1,
            board,
            kifuwarabe,
            is_debug=False):
        """最強手または最弱手の取得

        Parameters
        ----------
        weakest0_strongest1 : int
            0なら最弱手、1なら最強手を取得
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグか？
        """
        #
        # USIプロトコルでの符号表記と、ポリシー値の辞書に変換
        # --------------------------------------------
        #
        #   自玉の指し手と、自玉を除く自軍の指し手を分けて取得
        #   ポリシー値は千分率の４桁の整数
        #
        (k_move_u_for_l_and_policy_dictionary,
         k_move_u_for_q_and_policy_dictionary,
         p_move_u_for_l_and_policy_dictionary,
         p_move_u_for_q_and_policy_dictionary) = EvaluationFacade.select_fo_move_u_and_policy_dictionary(
                legal_moves=list(board.legal_moves),
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        if weakest0_strongest1 == 1:
            best_kl_policy = -1000
            best_kq_policy = -1000
            best_pl_policy = -1000
            best_pq_policy = -1000

        else:
            best_kl_policy = 1000
            best_kq_policy = 1000
            best_pl_policy = 1000
            best_pq_policy = 1000

        best_kl_move_dictionary = {}
        best_kq_move_dictionary = {}
        best_pl_move_dictionary = {}
        best_pq_move_dictionary = {}

        #
        # ＫＬ
        # ----
        #

        for move_u, policy in k_move_u_for_l_and_policy_dictionary.items():

            # tie
            if best_kl_policy == policy:
                best_kl_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_kl_policy < policy) or (weakest0_strongest1 == 0 and policy < best_kl_policy):
                best_kl_policy = policy
                best_kl_move_dictionary = {move_u:policy}

        #
        # ＫＱ
        # ----
        #

        for move_u, policy in k_move_u_for_q_and_policy_dictionary.items():

            # tie
            if best_kq_policy == policy:
                best_kq_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_kq_policy < policy) or (weakest0_strongest1 == 0 and policy < best_kq_policy):
                best_kq_policy = policy
                best_kq_move_dictionary = {move_u:policy}

        #
        # ＰＬ
        # ----
        #

        for move_u, policy in p_move_u_for_l_and_policy_dictionary.items():

            # tie
            if best_pl_policy == policy:
                best_pl_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_pl_policy < policy) or (weakest0_strongest1 == 0 and policy < best_pl_policy):
                best_pl_policy = policy
                best_pl_move_dictionary = {move_u:policy}

        #
        # ＰＱ
        # ----
        #

        for move_u, policy in p_move_u_for_q_and_policy_dictionary.items():

            # tie
            if best_pq_policy == policy:
                best_pq_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_pq_policy < policy) or (weakest0_strongest1 == 0 and policy < best_pq_policy):
                best_pq_policy = policy
                best_pq_move_dictionary = {move_u:policy}

        #
        # ベスト
        # ------
        #

        return (best_kl_move_dictionary,
                best_kq_move_dictionary,
                best_pl_move_dictionary,
                best_pq_move_dictionary)


    @staticmethod
    def seleft_f_move_u_add_l_and_q(
            k_move_u_for_l_and_policy_dictionary,
            k_move_u_for_q_and_policy_dictionary,
            p_move_u_for_l_and_policy_dictionary,
            p_move_u_for_q_and_policy_dictionary,
            is_debug=False):
        """ＫＬとＫＱをマージしてＫにし、ＰＬとＰＱをマージしてＰにする

        Parameters
        ----------
        k_move_u_for_l_and_policy_dictionary :
            ＫＬ
        k_move_u_for_q_and_policy_dictionary :
            ＫＱ
        p_move_u_for_l_and_policy_dictionary :
            ＰＬ
        p_move_u_for_q_and_policy_dictionary :
            ＰＱ
        is_debug : bool
            デバッグか？
        """

        k_move_u_to_policy_dictionary = {}
        p_move_u_to_policy_dictionary = {}

        #
        # Ｋ
        #

        for move_u, policy in k_move_u_for_l_and_policy_dictionary.items():
            k_move_u_to_policy_dictionary[move_u] = policy

        for move_u, policy in k_move_u_for_q_and_policy_dictionary.items():
            if move_u in k_move_u_to_policy_dictionary.keys():
                k_move_u_to_policy_dictionary[move_u] = (k_move_u_to_policy_dictionary[move_u] + policy) // 2
            else:
                k_move_u_to_policy_dictionary[move_u] = policy

        #
        # Ｐ
        #

        for move_u, policy in p_move_u_for_l_and_policy_dictionary.items():
            p_move_u_to_policy_dictionary[move_u] = policy

        for move_u, policy in p_move_u_for_q_and_policy_dictionary.items():
            if move_u in p_move_u_to_policy_dictionary.keys():
                p_move_u_to_policy_dictionary[move_u] = (p_move_u_to_policy_dictionary[move_u] + policy) // 2
            else:
                p_move_u_to_policy_dictionary[move_u] = policy

        return (k_move_u_to_policy_dictionary,
                p_move_u_to_policy_dictionary)


    #select_good_f_move_u_set
    @staticmethod
    def select_good_f_move_u_set_pipe(
            k_move_u_to_policy_dictionary,
            p_move_u_to_policy_dictionary,
            turn,
            is_debug=False):
        """ポリシー値が 0.5 以上の着手と、それ以外の着手の２つのリストを返します

        Parameters
        ----------
        k_move_u_to_policy_dictionary : Dictionary<str, int>
            自玉の着手と、そのポリシー値を格納した辞書
        p_move_u_to_policy_dictionary : Dictionary<str, int>
            自兵の着手と、そのポリシー値を格納した辞書
        turn : int
            手番
        is_debug : bool
            デバッグか？
        """

        number = 1

        # ポリシー値が 0.5 以上の指し手
        good_move_u_set = set()

        # ポリシー値が 0.5 未満の指し手
        bad_move_u_set = set()

        #
        # Ｋ
        #

        if is_debug:
            print('  自玉の着手のポリシー値一覧（Ｋ）：')

        for move_u, policy in k_move_u_to_policy_dictionary.items():
            if is_debug:
                print(f'    ({number:3})  turn:{Turn.to_string(turn)}  K:{move_u:5}  L:*****  policy:{policy:4}‰')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        #
        # Ｐ
        #

        if is_debug:
            print('  自兵の着手のポリシー値一覧（Ｐ）：')

        for move_u, policy in p_move_u_to_policy_dictionary.items():
            if is_debug:
                print(f'    ({number:3})  turn:{Turn.to_string(turn)}  P:{move_u:5}  L:*****  policy:{policy:4}‰')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        return (good_move_u_set, bad_move_u_set)


    @staticmethod
    def select_good_f_move_u_set_power(
            legal_moves,
            board,
            kifuwarabe,
            is_debug=False):
        """好手と悪手の一覧を作成

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
        """

        #print(f"[{datetime.datetime.now()}] [select good f move u set power no1] start...")

        # 合法手を、着手と応手に紐づくポリシー値を格納した辞書に変換します
        #
        #   ポリシー値は千分率の４桁の整数
        #
        (k_move_u_for_l_and_policy_dictionary,
         k_move_u_for_q_and_policy_dictionary,
         p_move_u_for_l_and_policy_dictionary,
         p_move_u_for_q_and_policy_dictionary) = EvaluationFacade.select_fo_move_u_and_policy_dictionary(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)


        if is_debug and DebugPlan.select_good_f_move_u_set_power():
            for k_move_u, policy in k_move_u_for_l_and_policy_dictionary.items():
                print(f"[select good f move u set power] k_move_u:{k_move_u:5} for l  policy:{policy}‰")

            for k_move_u, policy in k_move_u_for_q_and_policy_dictionary.items():
                print(f"[select good f move u set power] k_move_u:{k_move_u:5} for q  policy:{policy}‰")

            for p_move_u, policy in p_move_u_for_l_and_policy_dictionary.items():
                print(f"[select good f move u set power] p_move_u:{p_move_u:5} for l  policy:{policy}‰")

            for p_move_u, policy in p_move_u_for_q_and_policy_dictionary.items():
                print(f"[select good f move u set power] p_move_u:{p_move_u:5} for q  policy:{policy}‰")


        #print(f"[{datetime.datetime.now()}] [select good f move u set power no2] start...")


        (k_move_u_to_policy_dictionary,
         p_move_u_to_policy_dictionary) = MoveAndPolicyHelper.seleft_f_move_u_add_l_and_q(
                k_move_u_for_l_and_policy_dictionary=k_move_u_for_l_and_policy_dictionary,
                k_move_u_for_q_and_policy_dictionary=k_move_u_for_q_and_policy_dictionary,
                p_move_u_for_l_and_policy_dictionary=p_move_u_for_l_and_policy_dictionary,
                p_move_u_for_q_and_policy_dictionary=p_move_u_for_q_and_policy_dictionary,
                is_debug=is_debug)


        if is_debug and DebugPlan.select_good_f_move_u_set_power():
            for k_move_u, policy in k_move_u_to_policy_dictionary.items():
                print(f"[select good f move u set power] k_move_u:{k_move_u:5}  policy:{policy}‰")

            for p_move_u, policy in p_move_u_to_policy_dictionary.items():
                print(f"[select good f move u set power] p_move_u:{p_move_u:5}  policy:{policy}‰")


        #print(f"[{datetime.datetime.now()}] [select good f move u set power no3] start...")


        # ポリシー値は　分母の異なる集団の　投票数なので、
        # 絶対値に意味はなく、
        # 賛同か否定か（0.5 より高いか、低いか）ぐらいの判断にしか使えないと思うので、
        # そのようにします

        #
        # 好手、悪手一覧
        # ------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set_pipe(
                k_move_u_to_policy_dictionary=k_move_u_to_policy_dictionary,
                p_move_u_to_policy_dictionary=p_move_u_to_policy_dictionary,
                turn=board.turn,
                is_debug=is_debug)


        #print(f"[{datetime.datetime.now()}] [select good f move u set power] end")


        return (good_move_u_set,
                bad_move_u_set)


class EvaluationFacade():
    """評価値のファサード"""


    #query_mm_move_u_and_relation_bit
    #select_mm_index_and_relation_bit
    @staticmethod
    def select_fo_index_and_relation_bit(
            k_moves_u,
            l_move_u_for_k_set,
            q_move_u_for_k_set,
            p_moves_u,
            l_move_u_for_p_set,
            q_move_u_for_p_set,
            turn,
            kifuwarabe,
            is_debug=False):
        """着手と応手の関係を４つの辞書として取得

        第１階層の根と、第２階層の着手の葉と、第３階層の応手の葉から成る、ツリー構造になっているだろうから、
        それを、以下の４つの辞書に分ける

        （１）第２階層が自玉の着手、第３階層が敵玉の応手
        （２）第２階層が自玉の着手、第３階層が敵兵の応手
        （３）第２階層が自兵の着手、第３階層が敵玉の応手
        （４）第２階層が自兵の着手、第３階層が敵兵の応手

        ここで、第２階層の着手と、第３階層の着手の２つを合わせて１つのインデックスを作り、それをキーとする。
        値は、関係の有無を無いとき 0、有るときを 1 としたリレーション・ビットとする


        Parameters
        ----------
        k_moves_u : iterable
            自玉の着手の収集
        l_move_u_for_k_set : iterable
            自玉の着手に対する、敵玉の応手の収集
        q_move_u_for_k_set : iterable
            自玉の着手に対する、敵兵の応手の収集
        p_moves_u : iterable
            自兵の着手の収集
        l_move_u_for_p_set : iterable
            自兵の着手に対する、敵玉の応手の収集
        q_move_u_for_p_set : iterable
            自兵の着手に対する、敵兵の応手の収集
        turn : int
            手番
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている
        is_debug : bool
            デバッグか？

        Returns
        -------
        kl_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵玉の応手の数
        kq_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵兵の応手の数
        pl_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵玉の応手の数
        pq_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵兵の応手の数
        """

        def select_fo_index_and_relation_bit_local(
                kind,
                f_move_obj,
                o_move_u_for_f_set):
            """指定の着手と、指定の応手のセットに対して、

            Parameters
            ----------
            kind : str
                'KL', 'KQ', 'PL', 'PQ' のいずれか
            f_move_obj : Move
                指定の着手
            o_move_u_for_f_set : set<str>
                指定の応手のセット
            """
            fo_index_and_relation_bit_dictionary = {}

            for o_move_u in o_move_u_for_f_set:
                o_move_obj = Move.from_usi(o_move_u)

                #
                # キー。fo_index
                #

                # ＫＬ
                if kind == 'KL':
                    fo_index = EvaluationKkTable.get_index_of_kk_table(
                            k_move_obj=f_move_obj,
                            l_move_obj=o_move_obj,
                            k_turn=turn)

                # ＫＱ
                elif kind == 'KQ':
                    fo_index = EvaluationKpTable.get_index_of_kp_table(
                            k_move_obj=f_move_obj,
                            p_move_obj=o_move_obj,
                            k_turn=turn)

                # ＰＬ
                elif kind == 'PL':
                    fo_index = EvaluationPkTable.get_index_of_pk_table(
                            p_move_obj=f_move_obj,
                            k_move_obj=o_move_obj,
                            p_turn=turn)

                # ＰＱ
                elif kind == 'PQ':
                    fo_index = EvaluationPpTable.get_index_of_pp_table(
                            p1_move_obj=f_move_obj,
                            p2_move_obj=o_move_obj,
                            p1_turn=turn)

                else:
                    raise ValueError(f"unexpected kind:{kind}")

                #
                # 値。relation bit
                #

                # ＫＬ
                if kind == 'KL':
                    relation_bit = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(turn)].get_relation_esixts_by_index(
                            kl_index=fo_index)

                # ＫＱ
                elif kind == 'KQ':
                    relation_bit = kifuwarabe.evaluation_kq_table_obj_array[Turn.to_index(turn)].get_relation_esixts_by_index(
                            kp_index=fo_index)

                # ＰＬ
                elif kind == 'PL':
                    relation_bit = kifuwarabe.evaluation_pl_table_obj_array[Turn.to_index(turn)].get_relation_esixts_by_index(
                            pk_index=fo_index)

                # ＰＱ
                elif kind == 'PQ':
                    relation_bit = kifuwarabe.evaluation_pq_table_obj_array[Turn.to_index(turn)].get_relation_esixts_by_index(
                            pp_index=fo_index)

                else:
                    raise ValueError(f"unexpected kind:{kind}")

                fo_index_and_relation_bit_dictionary[fo_index] = relation_bit

            return fo_index_and_relation_bit_dictionary

        # 指し手と、ビット値を紐づける
        kl_index_and_relation_bit_dictionary = {}
        kq_index_and_relation_bit_dictionary = {}
        pl_index_and_relation_bit_dictionary = {}
        pq_index_and_relation_bit_dictionary = {}

        # ポリシー値を累計していく
        for k_move_u in k_moves_u:
            k_move_obj = Move.from_usi(k_move_u)

            # ＫＬ
            temp_dictionary = select_fo_index_and_relation_bit_local(
                    kind='KL',
                    f_move_obj=k_move_obj,
                    o_move_u_for_f_set=l_move_u_for_k_set)

            # 和集合
            kl_index_and_relation_bit_dictionary = kl_index_and_relation_bit_dictionary | temp_dictionary

            # ＫＱ
            temp_dictionary = select_fo_index_and_relation_bit_local(
                    kind='KQ',
                    f_move_obj=k_move_obj,
                    o_move_u_for_f_set=q_move_u_for_k_set)

            kq_index_and_relation_bit_dictionary = kq_index_and_relation_bit_dictionary | temp_dictionary

        for p_move_u in p_moves_u:
            p_move_obj = Move.from_usi(p_move_u)

            # ＰＬ
            temp_dictionary = select_fo_index_and_relation_bit_local(
                    kind='PL',
                    f_move_obj=p_move_obj,
                    o_move_u_for_f_set=l_move_u_for_p_set)

            pl_index_and_relation_bit_dictionary = pl_index_and_relation_bit_dictionary | temp_dictionary

            # ＰＱ
            temp_dictionary = select_fo_index_and_relation_bit_local(
                    kind='PQ',
                    f_move_obj=p_move_obj,
                    o_move_u_for_f_set=q_move_u_for_p_set)

            pq_index_and_relation_bit_dictionary = pq_index_and_relation_bit_dictionary | temp_dictionary

        return (kl_index_and_relation_bit_dictionary,
                kq_index_and_relation_bit_dictionary,
                pl_index_and_relation_bit_dictionary,
                pq_index_and_relation_bit_dictionary)


    #put_policy_permille_to_move_u
    #merge_policy_permille
    #map_relation_bit_to_policy_permille
    @staticmethod
    def select_move_u_and_policy_permille_group_by_move_u(
            k_move_u_and_l_to_relation_number_dictionary,
            k_move_u_and_q_to_relation_number_dictionary,
            p_move_u_and_l_to_relation_number_dictionary,
            p_move_u_and_q_to_relation_number_dictionary,
            is_debug=False):
        """ＭＮ関係を、Ｍ毎にまとめ直して、関係の有無は件数に変換し、スケールを千分率に揃える

        Parameters
        ----------
        k_move_u_and_l_to_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵玉の応手の数
        k_move_u_and_q_to_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵兵の応手の数
        p_move_u_and_l_to_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵玉の応手の数
        p_move_u_and_q_to_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵兵の応手の数

        Returns
        -------
        k_move_u_and_l_and_policy_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵玉の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        k_move_u_and_q_and_policy_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵兵の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        p_move_u_and_l_and_policy_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵玉の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        p_move_u_and_q_and_policy_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵兵の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        """

        def select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary,
                label_f,
                label_o
        ):
            f_move_u_and_o_to_policy_dictionary = {}
            counter_move_size = len(f_move_u_and_o_to_relation_number_dictionary)

            # デバッグ表示
            if is_debug:
                for move_u, relation_number in f_move_u_and_o_to_relation_number_dictionary.items():
                    print(f"{label_f}:{move_u:5}  {label_o}:*****  relation_number:{relation_number:3}  /  size:{counter_move_size}")

            for move_u, relation_number in f_move_u_and_o_to_relation_number_dictionary.items():
                f_move_u_and_o_to_policy_dictionary[move_u] = PolicyHelper.get_permille_from_relation_number(
                        relation_number=relation_number,
                        counter_move_size=counter_move_size)

                if is_debug:
                    print(f"{label_f}:{move_u:5}  {label_o}:*****  sum(f policy):{f_move_u_and_o_to_policy_dictionary[move_u]:4}‰")

            return f_move_u_and_o_to_policy_dictionary

        # ＫＬ
        k_move_u_and_l_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=k_move_u_and_l_to_relation_number_dictionary,
                label_f='K',
                label_o='L')

        # ＫＱ
        k_move_u_and_q_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=k_move_u_and_q_to_relation_number_dictionary,
                label_f='K',
                label_o='Q')

        # ＰＬ
        p_move_u_and_l_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=p_move_u_and_l_to_relation_number_dictionary,
                label_f='P',
                label_o='L')

        # ＰＱ
        p_move_u_and_q_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=p_move_u_and_q_to_relation_number_dictionary,
                label_f='P',
                label_o='Q')

        return (k_move_u_and_l_to_policy_dictionary,
                k_move_u_and_q_to_policy_dictionary,
                p_move_u_and_l_to_policy_dictionary,
                p_move_u_and_q_to_policy_dictionary)


    @staticmethod
    def select_move_u_and_relation_number_group_by_move_u(
            kl_index_and_relation_bit_dictionary,
            kq_index_and_relation_bit_dictionary,
            pl_index_and_relation_bit_dictionary,
            pq_index_and_relation_bit_dictionary,
            turn,
            is_debug=False):
        """ＭＮ関係を、Ｍ毎にまとめ直して、関係の有無は件数に変換します

        Parameters
        ----------
        kl_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵玉の応手の数
        kq_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵兵の応手の数
        pl_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵玉の応手の数
        pq_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵兵の応手の数
        turn : int
            手番
        is_debug : bool
            デバッグモードか？

        Returns
        -------
        k_move_u_and_l_and_relation_number_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵玉の応手の数
        k_move_u_and_q_and_relation_number_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵兵の応手の数
        p_move_u_and_l_and_relation_number_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵玉の応手の数
        p_move_u_and_q_and_relation_number_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵兵の応手の数
        """

        def select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary,
                label_f,
                label_o):

            f_move_u_and_o_and_relation_number_dictionary = {}

            kind = f"{label_f}{label_o}"

            for fo_index, relation_bit in fo_index_and_relation_bit_dictionary.items():

                if kind == 'KL':
                    f_move_obj, o_move_obj = EvaluationKkTable.destructure_kl_index(
                            kl_index=fo_index,
                            k_turn=turn)

                # ＫＱ
                elif kind == 'KQ':
                    f_move_obj, o_move_obj = EvaluationKpTable.destructure_kp_index(
                            kp_index=fo_index,
                            k_turn=turn)

                # ＰＬ
                elif kind == 'PL':
                    f_move_obj, o_move_obj = EvaluationPkTable.destructure_pk_index(
                            pk_index=fo_index,
                            p_turn=turn)

                # ＰＱ
                elif kind == 'PQ':
                    f_move_obj, o_move_obj = EvaluationPpTable.destructure_pp_index(
                            pp_index=fo_index,
                            p1_turn=turn)

                else:
                    raise ValueError(f"unexpected kind:{kind}")

                if f_move_obj.as_usi in f_move_u_and_o_and_relation_number_dictionary.keys():
                    f_move_u_and_o_and_relation_number_dictionary[f_move_obj.as_usi] += relation_bit

                else:
                    f_move_u_and_o_and_relation_number_dictionary[f_move_obj.as_usi] = relation_bit

                if is_debug:
                    print(f"{label_f.lower()}{label_o.lower()}_index:{fo_index}  {label_f}:{f_move_obj.as_usi:5}  {label_o}:{o_move_obj.as_usi:5}  relation_bit:{relation_bit}  sum(f relation):{f_move_u_and_o_and_relation_number_dictionary[f_move_obj.as_usi]}")

            return f_move_u_and_o_and_relation_number_dictionary

        # ＫＬ
        k_move_u_and_l_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=kl_index_and_relation_bit_dictionary,
                label_f='K',
                label_o='L')

        # ＫＱ
        k_move_u_and_q_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=kq_index_and_relation_bit_dictionary,
                label_f='K',
                label_o='Q')

        # ＰＬ
        p_move_u_and_l_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=pl_index_and_relation_bit_dictionary,
                label_f='P',
                label_o='L')

        # ＰＱ
        p_move_u_and_q_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=pq_index_and_relation_bit_dictionary,
                label_f='P',
                label_o='Q')

        return (k_move_u_and_l_and_relation_number_dictionary,
                k_move_u_and_q_and_relation_number_dictionary,
                p_move_u_and_l_and_relation_number_dictionary,
                p_move_u_and_q_and_relation_number_dictionary)


    #create_list_of_friend_move_u_and_policy_dictionary
    @staticmethod
    def select_fo_move_u_and_policy_dictionary(
            legal_moves,
            board,
            kifuwarabe,
            is_debug=False):
        """自玉の着手の一覧が渡されるので、
        各着手についてポリシー値が紐づいた辞書を作成する

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている

        Returns
        -------
        - k_move_u_for_l_and_policy_dictionary : Dictionary<str, int>
            自玉の着手と、敵玉の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        - k_move_u_for_q_and_policy_dictionary,
            自玉の着手と、敵兵の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        - p_move_u_for_l_and_policy_dictionary,
            自兵の着手と、敵玉の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        - p_move_u_for_q_and_policy_dictionary
            自兵の着手と、敵兵の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        """

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no1] start...")

        # 自軍の着手の集合を、自玉の着手の集合と、自兵の着手の集合に分ける
        k_moves_u, p_moves_u = MoveListHelper.create_k_and_p_legal_moves(
                legal_moves,
                board,
                is_debug=is_debug)

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no1():
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no1]   自玉の着手の一覧：")
            for move_u in k_moves_u:
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no1]    turn:{Turn.to_string(board.turn)}  K:{move_u:5}  O:*****")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no1]  自兵の着手の一覧：")
            for move_u in p_moves_u:
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no1]    turn:{Turn.to_string(board.turn)}  P:{move_u:5}  O:*****")


        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no1] end")


        #
        # 相手が指せる手の集合
        # -----------------
        #
        #   ヌルムーブをしたいが、 `board.push_pass()` が機能しなかったので、合法手を全部指してみることにする
        #

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2] start...")

        # 自玉の着手に対する、敵玉（Lord）の応手の集合
        l_move_u_for_k_set = set()
        # 自玉の着手に対する、敵軍の玉以外の応手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_move_u_for_k_set = set()
        # 自軍の玉以外の着手に対する、敵玉（Lord）の応手の集合
        l_move_u_for_p_set = set()
        # 自軍の玉以外の着手に対する、敵軍の玉以外の応手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_move_u_for_p_set = set()

        # 自玉に対する、敵玉の応手の一覧と、敵兵の応手の一覧を作成
        for move_u in k_moves_u:
            move_obj = Move.from_usi(move_u)

            (temp_l_move_u_for_k_set,
             temp_q_move_u_for_k_set) = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

            # 和集合を作成
            l_move_u_for_k_set = l_move_u_for_k_set.union(temp_l_move_u_for_k_set)
            q_move_u_for_k_set = q_move_u_for_k_set.union(temp_q_move_u_for_k_set)

        # 自兵に対する、敵玉の応手の一覧と、敵兵の応手の一覧を作成
        for move_u in p_moves_u:
            move_obj = Move.from_usi(move_u)

            (temp_l_move_u_for_p_set,
             temp_q_move_u_for_p_set) = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

            # 和集合を作成
            l_move_u_for_p_set = l_move_u_for_p_set.union(temp_l_move_u_for_p_set)
            q_move_u_for_p_set = q_move_u_for_p_set.union(temp_q_move_u_for_p_set)


        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no2_kl():
            # ＫＬ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]  自玉に対する、敵玉の応手の一覧：")
            for l_move_u in l_move_u_for_k_set:
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]    [L for K]  turn:{Turn.to_string(board.turn)}  K:*****  L:{l_move_u}")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no2_kq():
            # ＫＱ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]  自玉に対する、敵兵の応手の一覧：")
            for q_move_u in q_move_u_for_k_set:
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]    [Q for K]  turn:{Turn.to_string(board.turn)}  K:*****  Q:{q_move_u}")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no2_pl():
            # ＰＬ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]  自兵に対する、敵玉の応手の一覧：")
            for l_move_u in l_move_u_for_p_set:
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]    [L for P]  turn:{Turn.to_string(board.turn)}  P:*****  L:{l_move_u}")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no2_pq():
            # ＰＱ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]  自兵に対する、敵兵の応手の一覧：")
            for q_move_u in q_move_u_for_p_set:
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2]    [Q for P]  turn:{Turn.to_string(board.turn)}  P:*****  Q:{q_move_u}")

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no2] end")

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3] start...")

        #
        # 着手と応手の関係を全部取得
        # -----------------------
        #
        #   辞書。
        #   キーは、着手と応手の２つの通しインデックス。値は　関係が無ければ０，あれば１
        #
        (kl_index_and_relation_bit_dictionary,
         kq_index_and_relation_bit_dictionary,
         pl_index_and_relation_bit_dictionary,
         pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_fo_index_and_relation_bit(
                k_moves_u=k_moves_u,
                l_move_u_for_k_set=l_move_u_for_k_set,
                q_move_u_for_k_set=q_move_u_for_k_set,
                p_moves_u=p_moves_u,
                l_move_u_for_p_set=l_move_u_for_p_set,
                q_move_u_for_p_set=q_move_u_for_p_set,
                turn=board.turn,
                kifuwarabe=kifuwarabe)

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3] end")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no3_kl():
            # ＫＬ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]  自玉の着手と、敵玉の応手の、関係の一覧（キー：ｆｏ＿ｉｎｄｅｘ，　値：関係ビット）：")
            for fo_index, relation_bit in kl_index_and_relation_bit_dictionary.items():

                (k_move_obj,
                l_move_obj) = EvaluationKkTable.destructure_kl_index(
                        kl_index=fo_index,
                        k_turn=board.turn)

                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]      [KL]  turn:{Turn.to_string(board.turn)}  kl_index:{fo_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_bit:{relation_bit}")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no3_kq():
            # ＫＱ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]    自玉の着手と、敵兵の応手の、関係の一覧：")
            for fo_index, relation_bit in kq_index_and_relation_bit_dictionary.items():

                (k_move_obj,
                q_move_obj) = EvaluationKpTable.destructure_kp_index(
                        kp_index=fo_index,
                        k_turn=board.turn)

                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]      [KQ]  turn:{Turn.to_string(board.turn)}  kq_index:{fo_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_bit:{relation_bit}")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no3_pl():
            # ＰＬ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]    自兵の着手と、敵玉の応手の、関係の一覧：")
            for fo_index, relation_bit in pl_index_and_relation_bit_dictionary.items():

                (p_move_obj,
                l_move_obj) = EvaluationPkTable.destructure_pk_index(
                        pk_index=fo_index,
                        p_turn=board.turn)

                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]      [PL]  turn:{Turn.to_string(board.turn)}  pl_index:{fo_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_bit:{relation_bit}")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no3_pq():
            # ＰＱ
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]    自兵の着手と、敵兵の応手の、関係の一覧：")
            for fo_index, relation_bit in pq_index_and_relation_bit_dictionary.items():

                (p_move_obj,
                q_move_obj) = EvaluationPpTable.destructure_pp_index(
                        pp_index=fo_index,
                        p1_turn=board.turn)

                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no3]      [PQ]  turn:{Turn.to_string(board.turn)}  pq_index:{fo_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_bit:{relation_bit}")

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4] start")

        # 関係のキーをインデックスから着手へ変換
        (k_move_u_and_l_to_relation_number_dictionary,
         k_move_u_and_q_to_relation_number_dictionary,
         p_move_u_and_l_to_relation_number_dictionary,
         p_move_u_and_q_to_relation_number_dictionary) = EvaluationFacade.select_move_u_and_relation_number_group_by_move_u(
                kl_index_and_relation_bit_dictionary,
                kq_index_and_relation_bit_dictionary,
                pl_index_and_relation_bit_dictionary,
                pq_index_and_relation_bit_dictionary,
                turn=board.turn)

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4] end")

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no4():
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]  自玉の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：関係数）：")
            for f_move_u, relation_number in k_move_u_and_l_to_relation_number_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]    [K for L]  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  L:*****  relation_number:{relation_number:3}")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]  自玉の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：関係数）：")
            for f_move_u, relation_number in k_move_u_and_q_to_relation_number_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]    [K for Q]  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  Q:*****  relation_number:{relation_number:3}")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]  自兵の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：関係数）：")
            for f_move_u, relation_number in p_move_u_and_l_to_relation_number_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]    [P for L]  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  L:*****  relation_number:{relation_number:3}")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]  自兵の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：関係数）：")
            for f_move_u, relation_number in p_move_u_and_q_to_relation_number_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no4]    [P for Q]  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  Q:*****  relation_number:{relation_number:3}")

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5] start...")

        #
        # 評価値テーブルを参照し、各指し手にポリシー値を付ける
        # ---------------------------------------------
        #
        #   ポリシー値は千分率の４桁の整数
        #
        (k_move_u_for_l_and_policy_dictionary,
         k_move_u_for_q_and_policy_dictionary,
         p_move_u_for_l_and_policy_dictionary,
         p_move_u_for_q_and_policy_dictionary) = EvaluationFacade.select_move_u_and_policy_permille_group_by_move_u(
                k_move_u_and_l_to_relation_number_dictionary=k_move_u_and_l_to_relation_number_dictionary,
                k_move_u_and_q_to_relation_number_dictionary=k_move_u_and_q_to_relation_number_dictionary,
                p_move_u_and_l_to_relation_number_dictionary=p_move_u_and_l_to_relation_number_dictionary,
                p_move_u_and_q_to_relation_number_dictionary=p_move_u_and_q_to_relation_number_dictionary)

        if is_debug and DebugPlan.select_fo_move_u_and_policy_dictionary_no5():
            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]  自玉の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
            for f_move_u, policy in k_move_u_for_l_and_policy_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]    [K for L]  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  L:*****  policy:{policy:3}")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]  自玉の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
            for f_move_u, policy in k_move_u_for_q_and_policy_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]    [K for Q]  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  Q:*****  policy:{policy:3}")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]  自兵の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
            for f_move_u, policy in p_move_u_for_l_and_policy_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]    [P for L]  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  L:*****  policy:{policy:3}")

            print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]  自兵の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
            for f_move_u, policy in p_move_u_for_q_and_policy_dictionary.items():
                print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5]    [P for Q]  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  Q:*****  policy:{policy:3}")

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary no5] end")

        # FIXME 同じ 5i4h でも、ＫＬとＫＱの２つあるといった状況になっているが、これでいいか？
        # TODO このあと、 good と bad に分けるときマージするか？

        #print(f"[{datetime.datetime.now()}] [select fo move u and policy dictionary] end")

        return (k_move_u_for_l_and_policy_dictionary,
                k_move_u_for_q_and_policy_dictionary,
                p_move_u_for_l_and_policy_dictionary,
                p_move_u_for_q_and_policy_dictionary)


    #select_fl_index_to_relation_exists
    def select_fo_index_to_relation_exists(
            move_obj,
            board,
            kifuwarabe):
        """１つの着手と全ての応手をキー、関係の有無を値とする辞書を作成します

        Parameters
        ----------
        move_obj : Move
            着手
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

        kl_index_to_relation_exists_dic = {}
        kq_index_to_relation_exists_dic = {}
        pl_index_to_relation_exists_dic = {}
        pq_index_to_relation_exists_dic = {}

        # 自玉のマス番号
        k_sq = BoardHelper.get_king_square(board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

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

        return (kl_index_to_relation_exists_dic,
                kq_index_to_relation_exists_dic,
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

            k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                    kl_index=kl_index,
                    k_turn=board.turn)

            if is_debug:
                # 表示
                print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kl]  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            if relation_exists == 1:
                number_of_connection += 1

        # ＫＱ
        for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():

            k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                    kp_index=kq_index,
                    k_turn=board.turn)

            # 表示
            if is_debug:
                print(f"[{datetime.datetime.now()}] [get number of connection for kl kq > kq]  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            if relation_exists == 1:
                number_of_connection += 1

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

            p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                    pk_index=pl_index,
                    p_turn=board.turn)

            if is_debug:
                # 表示
                print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pl]  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            if relation_exists == 1:
                number_of_connection += 1

        # ＰＱ
        for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():

            p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                    pp_index=pq_index,
                    p1_turn=board.turn)

            if is_debug:
                # 表示
                print(f"[{datetime.datetime.now()}] [get number of connection for pl pq > pq]  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            if relation_exists == 1:
                number_of_connection += 1

        return number_of_connection


    @staticmethod
    def get_max_number_of_less_than_50_percent(
            total):
        """ＫＬとＫＱ（または、ＰＬとＰＱ）の関係の有りのものの数が５割未満の内、最大の整数

        総数が０なら、答えは０
        総数が１なら、答えは０
        総数が２なら、答えは０
        総数が３なら、答えは１
        総数が４なら、答えは１
        総数が５なら、答えは２

        (1)   単純に kl_kq_total // 2 - 1 とすると、 kl_kq_total が３のときに答えが０になってしまう。
              そこで総数の半分は四捨五入しておく
        (2)   総数が０のとき、答えはー１になってしまうので、最低の値は０にしておく

        Parameters
        ----------
        total : int
            総数
        """

        # (1)
        max_number_of_less_than_50_percent = Decimal(str(total / 2)).quantize(Decimal('0'), rounding=ROUND_HALF_UP) - 1

        # (2)
        if max_number_of_less_than_50_percent < 0:
            max_number_of_less_than_50_percent = 0

        return max_number_of_less_than_50_percent
