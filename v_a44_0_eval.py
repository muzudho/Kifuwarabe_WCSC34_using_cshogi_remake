import cshogi
import datetime
from decimal import Decimal, ROUND_HALF_UP
from v_a44_0_debug_plan import DebugPlan
from v_a44_0_eval_kk import EvaluationKkTable
from v_a44_0_eval_kp import EvaluationKpTable
from v_a44_0_eval_pk import EvaluationPkTable
from v_a44_0_eval_pp import EvaluationPpTable
from v_a44_0_lib import Turn, Move, MoveHelper, BoardHelper


class EvaluationFacade():
    """評価値のファサード"""


    #select_fl_index_to_relation_exists
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
    def round_half_up(real):
        """小数点以下第１位を四捨五入します

        real : number
            実数
        """
        return Decimal(str(real)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)


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
        max_number_of_less_than_50_percent = EvaluationFacade.round_half_up(total / 2) - 1

        # (2)
        if max_number_of_less_than_50_percent < 0:
            max_number_of_less_than_50_percent = 0

        return max_number_of_less_than_50_percent


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
    def select_good_f_move_u_set_facade(
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
            total_of_relation) = EvaluationFacade.get_summary(
                    move_obj=move_obj,
                    board=board,
                    kifuwarabe=kifuwarabe,
                    is_debug=is_debug)

            # ポリシー値（千分率）
            if 0 < total_of_relation:
                policy = EvaluationFacade.round_half_up(positive_of_relation * 1000 / total_of_relation)
            else:
                policy = 0

            if 500 <= policy:
                good_move_u_set.add(move_u)

            else:
                bad_move_u_set.add(move_u)


        if is_debug and DebugPlan.select_good_f_move_u_set_facade:

            print(f"[{datetime.datetime.now()}] [select good f move u set facade] 好手一覧")

            for good_move_u in good_move_u_set:
                print(f"[{datetime.datetime.now()}] [select good f move u set facade]    good:{good_move_u:5}")

            print(f"[{datetime.datetime.now()}] [select good f move u set facade] 悪手一覧")

            for bad_move_u in bad_move_u_set:
                print(f"[{datetime.datetime.now()}] [select good f move u set facade]    bad :{bad_move_u:5}")


        return (good_move_u_set,
                bad_move_u_set)
