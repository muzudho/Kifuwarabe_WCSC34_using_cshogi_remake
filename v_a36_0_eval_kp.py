import cshogi
import os
import datetime
from v_a36_0_lib import Turn, Move, EvalutionMmTable
from v_a36_0_eval_lib import EvaluationLib
from v_a36_0_eval_k import EvaluationKMove
from v_a36_0_eval_p import EvaluationPMove


class EvaluationKpTable():
    """ＫＰ評価値テーブル"""


    @staticmethod
    def get_index_of_kp_table(
            k_move_obj,
            p_move_obj,
            k_turn):
        """ＫＰ評価値テーブルのインデックスを算出

        Parameters
        ----------
        k_move_obj : Move
            玉の着手
        p_move_obj : Move
            兵の応手
        k_turn : int
            着手側の手番
        """

        # 評価値テーブルは先手用の形なので、後手番は１８０°回転させる必要がある
        if k_turn == cshogi.BLACK:
            k_rotate = False
            l_rotate = True
        else:
            k_rotate = True
            l_rotate = False

        # 0 ～ 2_078_084 =                                                   0 ～ 543 *                                     3813 +                                                0 ～ 3812
        kp_index         = EvaluationKMove.get_index_by_k_move(k_move_obj, k_rotate) * EvaluationPMove.get_serial_number_size() + EvaluationPMove.get_index_by_p_move(p_move_obj, l_rotate)

        # assert
        if EvaluationKMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size() <= kp_index:
            raise ValueError(f"kp_index:{kp_index} out of range {EvaluationKMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size()}")

        return kp_index


    @staticmethod
    def destructure_kp_index(
            kp_index,
            k_turn):
        """ＫＰインデックス分解

        Parameter
        ---------
        kp_index : int
            玉と兵の関係の通しインデックス
        k_turn : int
            着手側の手番

        Returns
        -------
        - k_move_obj : Move
            玉の着手
        - p_move_obj : Move
            兵の応手
        """

        rest = kp_index

        p_index = rest % EvaluationPMove.get_serial_number_size()
        rest //= EvaluationPMove.get_serial_number_size()

        k_index = rest % EvaluationKMove.get_serial_number_size()

        # assert
        if EvaluationPMove.get_serial_number_size() <= p_index:
            raise ValueError(f"p_index:{p_index} out of range {EvaluationPMove.get_serial_number_size()}")

        # assert
        if EvaluationKMove.get_serial_number_size() <= k_index:
            raise ValueError(f"k_index:{k_index} out of range {EvaluationKMove.get_serial_number_size()}")


        # 評価値テーブルは先手用の形なので、後手番は１８０°回転させる必要がある
        if k_turn == cshogi.BLACK:
            k_rotate = False
            l_rotate = True
        else:
            k_rotate = True
            l_rotate = False

        p_move_obj = EvaluationPMove.destructure_p_index(
                p_index=p_index,
                is_rotate=l_rotate)
        k_move_obj = EvaluationKMove.destructure_k_index(
                k_index=k_index,
                is_rotate=k_rotate)

        return (k_move_obj, p_move_obj)


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
        file_name=f'n1_eval_kp_{Turn.to_string(turn)}_{self._engine_version_str}.bin'

        print(f"[{datetime.datetime.now()}] {file_name} file exists check ...", flush=True)
        is_file_exists = os.path.isfile(file_name)

        if is_file_exists:
            # 読込
            table_as_array = EvaluationLib.read_evaluation_table_as_array_from_file(
                    file_name=file_name)
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
                file_name=file_name,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_kp_evaluation_table_file(
            self):
        """ファイルへの保存

        保存するかどうかは先に判定しておくこと
        """
        EvaluationLib.save_evaluation_table_file(
                file_name=self.mm_table_obj.file_name,
                table_as_array=self.mm_table_obj.table_as_array)


    # 使ってない？
    def get_relation_esixts_by_kp_moves(
            self,
            k_move_obj,
            p_move_obj,
            is_rotate):
        """玉と兵の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        k_move_obj : Move
            玉の指し手
        p_move_obj : Move
            兵の指し手
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        bit : int
            0 or 1
        """
        return self.get_relation_esixts_by_index(
                kp_index=EvaluationKpTable.get_index_of_kp_table(
                    k_move_obj=k_move_obj,
                    p_move_obj=p_move_obj,
                    is_rotate=is_rotate))


    def get_relation_esixts_by_index(
            self,
            kp_index):
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
                index=kp_index)


    def set_relation_esixts_by_kp_moves(
            self,
            k_move_obj,
            p_move_obj,
            bit,
            is_rotate):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        k_move_obj : Move
            玉の指し手
        p_move_obj : Move
            兵の指し手
        bit : int
            0 か 1
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """
        is_changed = self._mm_table_obj.set_bit_by_index(
                index=EvaluationKpTable.get_index_of_kp_table(
                    k_move_obj=k_move_obj,
                    p_move_obj=p_move_obj,
                    is_rotate=is_rotate),
                bit=bit)

        return is_changed


    # 使ってない？
    def select_kp_index_and_relation_exists(
            self,
            k_move_obj,
            p_move_u_set,
            k_turn):
        """玉の指し手と、兵の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＫＰ評価値テーブル用

        Parameters
        ----------
        k_move_obj : Move
            玉の着手
        p_move_u_set : List<str>
            兵の応手のリスト
        k_turn : int
            着手側の手番

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＫＰ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for p_move_u in p_move_u_set:
            kp_index = EvaluationKpTable.get_index_of_kp_table(
                k_move_obj=k_move_obj,
                p_move_obj=Move.from_usi(p_move_u),
                k_turn=k_turn)

            relation_bit = self.get_relation_esixts_by_index(
                    kp_index=kp_index)

            relations[kp_index] = relation_bit

        return relations
