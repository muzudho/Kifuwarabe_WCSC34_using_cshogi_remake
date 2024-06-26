import cshogi
import os
import datetime

from v_a54_0_eval.lib import EvaluationLib
from v_a54_0_eval.p import EvaluationPMove
from v_a54_0_misc.lib import FileName, Turn, Move, EvalutionMmTable


class EvaluationPpTable():
    """ＰＰ評価値テーブル"""


    @staticmethod
    def get_index_of_pp_table(
            p1_move_obj,
            p2_move_obj,
            p1_turn):
        """ＰＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        p1_move_obj : Move
            兵１の着手
        p2_move_obj : Move
            兵２の応手
        p1_turn : int
            着手側の手番
        """

        # 評価値テーブルは先手用の形なので、後手番は１８０°回転させる必要がある
        if p1_turn == cshogi.BLACK:
            p1_rotate = False
            p2_rotate = True
        else:
            p1_rotate = True
            p2_rotate = False

        # 0 ～ 14_542_781 =                                                   0 ～ 3812 *                                     3813 +                                                  0 ～ 3812
        pp_index         = EvaluationPMove.get_index_by_p_move(p1_move_obj, p1_rotate) * EvaluationPMove.get_serial_number_size() + EvaluationPMove.get_index_by_p_move(p2_move_obj, p2_rotate)

        # assert
        if EvaluationPMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size() <= pp_index:
            raise ValueError(f"pp_index:{pp_index} out of range {EvaluationPMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size()}")

        return pp_index


    @staticmethod
    def destructure_pp_index(
            pp_index,
            p1_turn):
        """ＰＰインデックス分解

        Parameter
        ---------
        pp_index : int
            兵１と兵２の関係の通しインデックス
        p1_turn : int
            着手側の手番

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


        # 評価値テーブルは先手用の形なので、後手番は１８０°回転させる必要がある
        if p1_turn == cshogi.BLACK:
            p1_rotate = False
            p2_rotate = True
        else:
            p1_rotate = True
            p2_rotate = False

        p2_move_obj = EvaluationPMove.destructure_p_index(
                p_index=p2_index,
                is_rotate=p2_rotate)
        p1_move_obj = EvaluationPMove.destructure_p_index(
                p_index=p1_index,
                is_rotate=p1_rotate)

        return (p1_move_obj, p2_move_obj)


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
        file_name_obj = FileName(
                file_stem=f'data[{self._engine_version_str}]_n1_eval_pp_{Turn.to_string(turn)}',
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
                    b_move_size=EvaluationPMove.get_serial_number_size())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name_obj=file_name_obj,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_pp_evaluation_table_file(
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


    def set_relation_esixts_by_pp_moves(
            self,
            p1_move_obj,
            p2_move_obj,
            p1_turn,
            bit):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        p1_move_obj : Move
            兵１の着手
        p2_move_obj : Move
            兵２の応手
        p1_turn : int
            着手側の手番
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
                    p1_turn=p1_turn),
                bit=bit)

        return is_changed


    def select_pp_index_and_relation_exists(
            self,
            p1_move_obj,
            p2_move_u_set,
            p1_turn):
        """兵１の指し手と、兵２の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＰＰ評価値テーブル用

        Parameters
        ----------
        p1_move_obj : Move
            兵１の着手
        p2_move_u_set : List<str>
            兵２の応手のリスト
        p1_turn : int
            着手側の手番

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
                p1_turn=p1_turn)

            relation_bit = self.get_relation_esixts_by_index(
                    pp_index=pp_index)

            relations[pp_index] = relation_bit

        return relations
