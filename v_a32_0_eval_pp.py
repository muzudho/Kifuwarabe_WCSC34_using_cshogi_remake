import os
import datetime
from v_a32_0_lib import Turn, Move, EvalutionMmTable
from v_a32_0_eval_lib import EvaluationLib
from v_a32_0_eval_k import EvaluationKMove
from v_a32_0_eval_p import EvaluationPMove


class EvaluationPpTable():
    """ＰＰ評価値テーブル"""


    @staticmethod
    def get_index_of_pp_table(
            p1_move_obj,
            p2_move_obj,
            is_rotate):
        """ＰＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        p1_move_obj : Move
            兵１の指し手
        p2_move_obj : Move
            兵２の指し手
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます
        """

        # 0 ～ 14_542_781 =                                                   0 ～ 3812 *                                     3813 +                                                  0 ～ 3812
        pp_index         = EvaluationPMove.get_index_by_p_move(p1_move_obj, is_rotate) * EvaluationPMove.get_serial_number_size() + EvaluationPMove.get_index_by_p_move(p2_move_obj, is_rotate)

        # assert
        if EvaluationPMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size() <= pp_index:
            raise ValueError(f"pk_index:{pp_index} out of range {EvaluationPMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size()}")

        return pp_index


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
        """ＰＰ評価値テーブル読込

        Parameters
        ----------
        turn : int
            手番
        """
        file_name=f'n1_eval_pk_{Turn.to_string(turn)}_{self._engine_version_str}.bin'

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
                    a_move_size=EvaluationPMove.get_serial_number_size(),
                    b_move_size=EvaluationPMove.get_serial_number_size())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name=file_name,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_pp_evaluation_table_file(
            self):
        """ファイルへの保存

        保存するかどうかは先に判定しておくこと
        """
        EvaluationLib.save_evaluation_table_file(
                file_name=self.mm_table_obj.file_name,
                table_as_array=self.mm_table_obj.table_as_array)


    # 使ってない？
    def get_relation_esixts_by_pp_moves(
            self,
            p1_move_obj,
            p2_move_obj,
            is_rotate):
        """兵と兵の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        p1_move_obj : Move
            兵１の指し手
        p2_move_obj : Move
            兵２の指し手
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        bit : int
            0 or 1
        """
        return self.get_relation_esixts_by_index(
                kp_index=EvaluationPpTable.get_index_of_pp_table(
                    p1_move_obj=p1_move_obj,
                    p2_move_obj=p2_move_obj,
                    is_rotate=is_rotate))


    def get_relation_esixts_by_index(
            self,
            pp_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        pp_index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=pp_index)


    # 使ってない？
    def set_relation_esixts_by_pp_moves(
            self,
            p1_move_obj,
            p2_move_obj,
            bit,
            is_rotate):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        p1_move_obj : Move
            兵１の指し手
        p2_move_obj : Move
            兵２の指し手
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
                index=EvaluationPpTable.get_index_of_pp_table(
                    p1_move_obj=p1_move_obj,
                    p2_move_obj=p2_move_obj,
                    is_rotate=is_rotate),
                bit=bit)

        return is_changed


    def select_pp_index_and_relation_exists(
            self,
            p1_move_obj,
            p2_move_u_set,
            is_rotate):
        """兵１の指し手と、兵２の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＰＰ評価値テーブル用

        Parameters
        ----------
        p1_move_obj : Move
            兵１の着手
        p2_move_u_set : List<str>
            兵２の応手のリスト
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＰＰ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for p2_move_u in p2_move_u_set:
            pp_index = EvaluationPpTable.get_index_of_pp_table(
                p1_move_obj=p1_move_obj,
                p2_move_obj=Move.from_usi(p2_move_u),
                is_rotate=is_rotate)

            relation_bit = self.get_relation_esixts_by_index(
                    pp_index=pp_index)

            relations[pp_index] = relation_bit

        return relations


    @staticmethod
    def destructure_pp_index(
            pp_index):
        """ＰＰインデックス分解

        Parameter
        ---------
        pp_index : int
            兵１と兵２の関係の通しインデックス

        Returns
        -------
        - p1_move_obj : Move
            兵１の着手
        - p2_move_obj : Move
            兵２の応手
        """

        rest = pp_index

        p2_index = rest % EvaluationPMove.get_serial_number_size()
        rest //= EvaluationPMove.get_serial_number_size()

        p1_index = rest % EvaluationPMove.get_serial_number_size()

        # assert
        if EvaluationPMove.get_serial_number_size() <= p2_index:
            raise ValueError(f"p2_index:{p2_index} out of range {EvaluationPMove.get_serial_number_size()}")

        # assert
        if EvaluationPMove.get_serial_number_size() <= p1_index:
            raise ValueError(f"p1_index:{p1_index} out of range {EvaluationPMove.get_serial_number_size()}")


        p2_move_obj = EvaluationPMove.destructure_p_index(
                p_index=p2_index)
        p1_move_obj = EvaluationPMove.destructure_p_index(
                p_index=p1_index)

        return (p1_move_obj, p2_move_obj)
