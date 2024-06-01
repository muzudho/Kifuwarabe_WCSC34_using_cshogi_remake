import os
import datetime
from v_a23_0_lib import Turn, Move, EvalutionMmTable
from v_a23_0_eval_lib import EvaluationLib
from v_a23_0_eval_k import EvaluationKMove


class EvaluationKkTable():
    """ＫＫ評価値テーブル"""


    @staticmethod
    def get_index_of_kk_table(
            k_move_obj,
            l_move_obj):
        """ＫＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        k_move_obj : Move
            自玉の指し手
        l_move_obj : Move
            敵玉の指し手
        """

        # 0 ～ 353_159 =                                         0 ～ 647 *                                     544 +                                        0 ～ 647
        kk_index       = EvaluationKMove.get_index_by_k_move(k_move_obj) * EvaluationKMove.get_serial_number_size() + EvaluationKMove.get_index_by_k_move(l_move_obj)

        if EvaluationKMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size() <= kk_index:
            raise ValueError(f"kk_index:{kk_index} out of range {EvaluationKMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size()}")

        return kk_index


    def __init__(
            self,
            engine_version_str):
        """初期化

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        self._mm_table_obj = None
        self._engine_version_str = engine_version_str


    @property
    def mm_table_obj(self):
        return self._mm_table_obj


    def load_on_usinewgame(
            self,
            turn):
        """ＫＫ評価値テーブル読込

        Parameters
        ----------
        turn : int
            手番

        Returns
        -------
        - テーブル
        - バージョンアップしたので保存要求の有無
        """
        file_name=f'n1_eval_kk_{Turn.to_string(turn)}_{self._engine_version_str}.bin'

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
                    b_move_size=EvaluationKMove.get_serial_number_size())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name=file_name,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_kk_evaluation_table_file(
            self):
        """ファイルへの保存"""

        # 保存するかどうかは先に判定しておくこと
        EvaluationLib.save_evaluation_table_file(
                file_name=self.mm_table_obj.file_name,
                table_as_array=self.mm_table_obj.table_as_array)


    def get_relation_esixts_by_kl_moves(
            self,
            k_move_obj,
            l_move_obj):
        """自玉と敵玉の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        k_move_obj : Move
            自玉の指し手
        l_move_obj : Move
            敵玉の指し手

        Returns
        -------
        bit : int
            0 or 1
        """
        return self.get_relation_esixts_by_index(
                kl_index=EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj))


    def get_relation_esixts_by_index(
            self,
            kl_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=kl_index)


    def set_relation_esixts_by_kl_moves(
            self,
            k_move_obj,
            l_move_obj,
            bit):
        """自玉の着手と敵玉の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        k_move_obj : Move
            自玉の指し手
        l_move_obj : Move
            敵玉の指し手
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """
        is_changed = self._mm_table_obj.set_bit_by_index(
                index=EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj),
                bit=bit)

        return is_changed


    # create_relation_exists_dictionary_by_k_move_and_l_moves
    def select_kl_index_and_relation_exists(
            self,
            k_move_obj,
            l_move_u_set):
        """自玉の指し手と、敵玉の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＫＫ評価値テーブル用

        Parameters
        ----------
        k_move_obj : Move
            自玉の着手
        l_move_u_set : List<str>
            敵玉の応手のリスト

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＫＫ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for l_move_u in l_move_u_set:
            kl_index = EvaluationKkTable.get_index_of_kk_table(
                k_move_obj=k_move_obj,
                l_move_obj=Move.from_usi(l_move_u))

            relation_bit = self.get_relation_esixts_by_index(
                    kl_index=kl_index)

            relations[kl_index] = relation_bit

        return relations


    @staticmethod
    def destructure_kl_index(
            kl_index):
        """ＫＬインデックス分解

        Parameter
        ---------
        kl_index : int
            自玉と敵玉の関係の通しインデックス

        Returns
        -------
        - k_move_obj : Move
            自玉の着手
        - l_move_obj : Move
            敵玉の応手
        """
        if EvaluationKMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size() <= kl_index:
            raise ValueError(f"kl_index:{kl_index} out of range {EvaluationKMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size()}")

        king_serial_number_size = EvaluationKMove.get_serial_number_size()

        l_index = kl_index % king_serial_number_size
        k_index = kl_index // king_serial_number_size

        if EvaluationKMove.get_serial_number_size() <= l_index:
            raise ValueError(f"l_index:{l_index} out of range {EvaluationKMove.get_serial_number_size()}")

        if EvaluationKMove.get_serial_number_size() <= k_index:
            raise ValueError(f"k_index:{k_index} out of range {EvaluationKMove.get_serial_number_size()}")


        l_move_obj = EvaluationKMove.destructure_k_index(
            k_index=l_index)
        k_move_obj = EvaluationKMove.destructure_k_index(
            k_index=k_index)

        return (k_move_obj, l_move_obj)
