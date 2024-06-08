import cshogi
import os
import datetime

# python v_a50_0_eval/pk.py
from     v_a50_0_eval.k import EvaluationKMove
from     v_a50_0_eval.lib import EvaluationLib
from     v_a50_0_eval.p import EvaluationPMove
from     v_a50_0_misc.lib import FileName, Turn, Move, EvalutionMmTable


class EvaluationPkTable():
    """ＰＫ評価値テーブル"""


    @staticmethod
    def get_index_of_pk_table(
            p_move_obj,
            k_move_obj,
            p_turn):
        """ＰＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        p_move_obj : Move
            兵の着手
        k_move_obj : Move
            玉の応手
        p_turn : int
            着手側の手番
        """

        # 評価値テーブルは先手用の形なので、後手番は１８０°回転させる必要がある
        if p_turn == cshogi.BLACK:
            p_rotate = False
            k_rotate = True
        else:
            p_rotate = True
            k_rotate = False

        # 0 ～ 2_074_815 =                                                  0 ～ 3812 *                                      544 +                                                 0 ～ 543
        pk_index         = EvaluationPMove.get_index_by_p_move(p_move_obj, p_rotate) * EvaluationKMove.get_serial_number_size() + EvaluationKMove.get_index_by_k_move(k_move_obj, k_rotate)

        # assert
        if EvaluationPMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size() <= pk_index:
            raise ValueError(f"pk_index:{pk_index} out of range {EvaluationPMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size()}")

        return pk_index


    @staticmethod
    def destructure_pk_index(
            pk_index,
            p_turn):
        """ＰＫインデックス分解

        Parameter
        ---------
        pk_index : int
            兵と玉の関係の通しインデックス
        p_turn : int
            着手側の手番

        Returns
        -------
        - p_move_obj : Move
            兵の着手
        - k_move_obj : Move
            玉の応手
        """

        rest = pk_index

        k_index = rest % EvaluationKMove.get_serial_number_size()
        rest //= EvaluationKMove.get_serial_number_size()

        p_index = rest % EvaluationPMove.get_serial_number_size()

        # assert
        if EvaluationKMove.get_serial_number_size() <= k_index:
            raise ValueError(f"k_index:{k_index} out of range {EvaluationKMove.get_serial_number_size()}")

        # assert
        if EvaluationPMove.get_serial_number_size() <= p_index:
            raise ValueError(f"p_index:{p_index} out of range {EvaluationPMove.get_serial_number_size()}")


        # 評価値テーブルは先手用の形なので、後手番は１８０°回転させる必要がある
        if p_turn == cshogi.BLACK:
            p_rotate = False
            k_rotate = True
        else:
            p_rotate = True
            k_rotate = False

        k_move_obj = EvaluationKMove.destructure_k_index(
                k_index=k_index,
                is_rotate=k_rotate)
        p_move_obj = EvaluationPMove.destructure_p_index(
                p_index=p_index,
                is_rotate=p_rotate)

        return (p_move_obj, k_move_obj)


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
        """ＰＫ評価値テーブル読込

        Parameters
        ----------
        turn : int
            手番
        """
        file_name_obj = FileName(
                file_stem=f'data[{self._engine_version_str}]_n1_eval_pk_{Turn.to_string(turn)}',
                file_extension='.bin')

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
                    a_move_size=EvaluationPMove.get_serial_number_size(),
                    b_move_size=EvaluationKMove.get_serial_number_size())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name_obj=file_name_obj,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_pk_evaluation_table_file(
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
    def get_relation_esixts_by_pk_moves(
            self,
            p_move_obj,
            k_move_obj,
            is_rotate):
        """玉と兵の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        p_move_obj : Move
            兵の指し手
        k_move_obj : Move
            玉の指し手
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        bit : int
            0 or 1
        """
        return self.get_relation_esixts_by_index(
                kp_index=EvaluationPkTable.get_index_of_pk_table(
                    p_move_obj=p_move_obj,
                    k_move_obj=k_move_obj,
                    is_rotate=is_rotate))


    def get_relation_esixts_by_index(
            self,
            pk_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        pk_index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=pk_index)


    # 使ってない？
    def set_relation_esixts_by_pk_moves(
            self,
            p_move_obj,
            k_move_obj,
            p_turn,
            bit):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        p_move_obj : Move
            兵の着手
        k_move_obj : Move
            玉の応手
        p_turn : int
            着手側の手番
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """
        is_changed = self._mm_table_obj.set_bit_by_index(
                index=EvaluationPkTable.get_index_of_pk_table(
                    p_move_obj=p_move_obj,
                    k_move_obj=k_move_obj,
                    p_turn=p_turn),
                bit=bit)

        return is_changed


    def select_pk_index_and_relation_exists(
            self,
            p_move_obj,
            k_move_u_set,
            p_turn):
        """兵の指し手と、玉の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＰＫ評価値テーブル用

        Parameters
        ----------
        p_move_obj : Move
            兵の着手
        k_move_u_set : List<str>
            玉の応手のリスト
        p_turn : int
            着手側の手番

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＰＫ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for k_move_u in k_move_u_set:
            pk_index = EvaluationPkTable.get_index_of_pk_table(
                p_move_obj=p_move_obj,
                k_move_obj=Move.from_usi(k_move_u),
                p_turn=p_turn)

            relation_bit = self.get_relation_esixts_by_index(
                    pk_index=pk_index)

            relations[pk_index] = relation_bit

        return relations


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    # 後手
    expected_p_move_u = '3h3i+'
    expected_p_move_obj = Move.from_usi(expected_p_move_u)

    # 先手
    expected_k_move_u = '5h5i'
    expected_k_move_obj = Move.from_usi(expected_k_move_u)

    pk_index = EvaluationPkTable.get_index_of_pk_table(
            p_move_obj=expected_p_move_obj,
            k_move_obj=expected_k_move_obj,
            p_turn=cshogi.WHITE)

    (actual_p_move_obj,
     actual_k_move_obj) = EvaluationPkTable.destructure_pk_index(
            pk_index=pk_index,
            p_turn=cshogi.WHITE)

    if expected_p_move_obj.as_usi != actual_p_move_obj.as_usi or expected_k_move_obj.as_usi != actual_k_move_obj.as_usi:
        raise ValueError(f'unexpected error. move_obj expected P:`{expected_p_move_obj.as_usi}`  K:`{expected_k_move_obj.as_usi}`  actual P:`{actual_p_move_obj.as_usi}`  K:`{actual_k_move_obj.as_usi}`')
