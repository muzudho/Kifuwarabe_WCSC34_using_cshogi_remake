import os
import datetime

from v_a61_0_eval.lib import EvaluationLib
from v_a61_0_eval.k import EvaluationKMove
from v_a61_0_eval.p import EvaluationPMove
from v_a61_0_misc.lib import FileName, Turn, Move, EvalutionMmTable
from v_a61_0_misc.usi import Usi


class EvaluationKpTable():
    """ＫＰ評価値テーブル"""


    #get_index_of_kp_table
    @staticmethod
    def get_blackright_k_blackright_p_index(
            k_blackright_move_obj,
            p_blackright_move_obj):
        """ＫＰ評価値テーブルのインデックスを算出

        Parameters
        ----------
        k_blackright_move_obj : Move
            玉の着手（先手視点、右辺使用）
        p_blackright_move_obj : Move
            兵の応手（先手視点、右辺使用）
        """

        # assert
        if Usi.is_drop_by_srcloc(k_blackright_move_obj.srcloc):
            raise ValueError(f"[evaluation kp table > get index of kp move > k] 玉の指し手で打なのはおかしい。 k_blackright_move_obj.srcloc_u:{Usi.srcloc_to_code(k_blackright_move_obj.srcloc)}  k_blackright_move_obj:{k_blackright_move_obj.dump()}")

        # 0 ～ 2_078_084                =                                                               0 ～ 543 *                                     3813 +                                                            0 ～ 3812
        blackright_k_blackright_p_index = EvaluationKMove.get_blackright_index_by_k_move(k_blackright_move_obj) * EvaluationPMove.get_serial_number_size() + EvaluationPMove.get_blackright_index_by_p_move(p_blackright_move_obj)

        # assert
        if EvaluationKMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size() <= blackright_k_blackright_p_index:
            raise ValueError(f"blackright_k_blackright_p_index:{blackright_k_blackright_p_index} out of range {EvaluationKMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size()}")

        return blackright_k_blackright_p_index


    #destructure_kp_index
    #build_k_p_moves_by_kp_index
    @staticmethod
    def build_k_blackright_p_blackright_moves_by_kp_index(
            k_blackright_p_blackright_index):
        """ＫＰインデックス分解

        Parameter
        ---------
        blackright_k_blackright_p_index : int
            玉と兵の関係の通しインデックス（先手視点、右辺使用）

        Returns
        -------
        - k_blackright_move_obj : Move
            玉の着手
        - p_blackright_move_obj : Move
            兵の応手
        """

        rest = k_blackright_p_blackright_index

        p_index = rest % EvaluationPMove.get_serial_number_size()
        rest //= EvaluationPMove.get_serial_number_size()

        k_index = rest % EvaluationKMove.get_serial_number_size()

        # assert
        if EvaluationPMove.get_serial_number_size() <= p_index:
            raise ValueError(f"p_index:{p_index} out of range {EvaluationPMove.get_serial_number_size()}")

        # assert
        if EvaluationKMove.get_serial_number_size() <= k_index:
            raise ValueError(f"k_index:{k_index} out of range {EvaluationKMove.get_serial_number_size()}")

        # Ｐ
        ((p_srcloc,
         p_dstsq,
         p_promote)) = EvaluationPMove.destructure_srcloc_dstsq_promoted_by_p_index(
                p_index=p_index)
        p_blackright_move_obj = Move.from_src_dst_pro(
                srcloc=p_srcloc,
                dstsq=p_dstsq,
                promoted=p_promote,
                # 先手のインデックスが渡されるので、先手に揃えるように回転させる必要はありません
                is_rotate=False)

        # Ｋ
        (k_srcsq,
         k_dstsq) = EvaluationKMove.destructure_srcsq_dstsq_by_k_index(
                k_index=k_index)
        k_blackright_move_obj = Move.from_src_dst_pro(
                srcloc=k_srcsq,
                dstsq=k_dstsq,
                # 玉に成りはありません
                promoted=False,
                # 先手のインデックスが渡されるので、先手に揃えるように回転させる必要はありません
                is_rotate=False)

        return (k_blackright_move_obj, p_blackright_move_obj)


    def __init__(
            self,
            engine_version_str):
        """初期化

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        self._engine_version_str = engine_version_str
        self._mm_table_obj = None


    @property
    def mm_table_obj(self):
        """評価値テーブル"""
        return self._mm_table_obj


    def load_on_usinewgame(
            self,
            turn):
        """ＫＰ評価値テーブル読込

        Parameters
        ----------
        turn : int
            手番
        """
        file_name_obj = FileName(
            file_stem=f'data[{self._engine_version_str}]_n1_eval_kp_{Turn.to_string(turn)}',
            file_extension=f'.bin')

        print(f"[{datetime.datetime.now()}] check  `{file_name_obj.base_name}` file exists...", flush=True)
        is_file_exists = os.path.isfile(file_name_obj.base_name)

        if is_file_exists:
            # 読込
            table_as_array = EvaluationLib.read_evaluation_table_as_array_from_file(
                    file_name_obj=file_name_obj)
        else:
            table_as_array = None


        # ファイルが存在しないとき
        if table_as_array is None:
            table_as_array = EvaluationLib.create_random_evaluation_table_as_array(
                    a_move_size=EvaluationKMove.get_serial_number_size(),
                    b_move_size=EvaluationPMove.get_serial_number_size())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name_obj=file_name_obj,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_kp_evaluation_table_file(
            self,
            is_debug=False):
        """ファイルへの保存

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？

        保存するかどうかは先に判定しておくこと
        """
        EvaluationLib.save_evaluation_table_file(
                file_name_obj=self.mm_table_obj.file_name_obj,
                table_as_array=self.mm_table_obj.table_as_array,
                is_debug=is_debug)


    # 使ってない？
    def get_relation_exists_by_kp_moves(
            self,
            k_black_move_obj,
            p_black_move_obj):
        """玉と兵の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        k_black_move_obj : Move
            玉の指し手
        p_black_move_obj : Move
            兵の指し手

        Returns
        -------
        bit : int
            0 or 1
        """

        # assert
        if Usi.is_drop_by_srcloc(k_black_move_obj.srcloc):
            raise ValueError(f"[evaluation kp table > get relation exists by kp moves > k] 玉の指し手で打なのはおかしい。 k_black_move_obj.srcloc_u:{Usi.srcloc_to_code(k_black_move_obj.srcloc)}  k_black_move_obj:{k_black_move_obj.dump()}")

        return self.get_relation_exists_by_index(
                black_k_black_p_index=EvaluationKpTable.get_blackright_k_blackright_p_index(
                        k_blackright_move_obj=k_black_move_obj,
                        p_blackright_move_obj=p_black_move_obj))


    def get_relation_exists_by_index(
            self,
            black_k_black_p_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        kp_index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=black_k_black_p_index)


    def set_relation_exists_by_black_k_black_p_moves(
            self,
            black_k_move_obj,
            black_p_move_obj,
            bit):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        black_k_move_obj : Move
            玉の着手（符号は先手番方向）
        black_p_move_obj : Move
            兵の応手（符号は先手番方向）
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """
        (is_changed, result_comment) = self._mm_table_obj.set_bit_by_index(
                black_f_black_o_index=EvaluationKpTable.get_blackright_k_blackright_p_index(
                        k_blackright_move_obj=black_k_move_obj,
                        p_blackright_move_obj=black_p_move_obj),
                bit=bit)

        return is_changed


    #select_kp_index_and_relation_exists
    def select_blackright_k_blackright_p_index_and_relation_exists(
            self,
            k_blackright_move_obj,
            p_blackright_move_u_set):
        """玉の指し手と、兵の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＫＰ評価値テーブル用

        Parameters
        ----------
        k_blackright_move_obj : Move
            玉の着手（先手視点、右辺使用）
        p_blackright_move_u_set : List<str>
            兵の応手のリスト（先手視点、右辺使用）

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＫＰ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for p_blackright_move_u in p_blackright_move_u_set:
            black_k_black_p_index = EvaluationKpTable.get_blackright_k_blackright_p_index(
                k_blackright_move_obj=k_blackright_move_obj,
                p_blackright_move_obj=Move.from_usi(p_blackright_move_u))

            relation_bit = self.get_relation_exists_by_index(
                    black_k_black_p_index=black_k_black_p_index)

            relations[black_k_black_p_index] = relation_bit

        return relations
