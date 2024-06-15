import cshogi
import os
import datetime

from v_a56_0_eval.k import EvaluationKMove
from v_a56_0_eval.lib import EvaluationLib
from v_a56_0_eval.p import EvaluationPMove
from v_a56_0_misc.lib import FileName, Turn, Move, EvalutionMmTable
from v_a56_0_misc.usi import Usi


class EvaluationPkTable():
    """ＰＫ評価値テーブル"""


    #get_index_of_pk_table
    @staticmethod
    def get_black_p_black_k_index(
            p_move_obj,
            k_move_obj,
            shall_p_white_to_black,
            shall_k_white_to_black):
        """ＰＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        p_move_obj : Move
            兵の着手
        k_move_obj : Move
            玉の応手
        shall_p_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_k_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        """

        # assert
        if Usi.is_drop_by_srcloc(k_move_obj.srcloc):
            raise ValueError(f"[evaluation pk table > get index of pk move > k] 玉の指し手で打なのはおかしい。 k_move_obj.srcloc_u:{Usi.srcloc_to_code(k_move_obj.srcloc)}  k_move_obj:{k_move_obj.dump()}")

        # 0 ～ 2_074_815      =                                                                      0 ～ 3812 *                                      544 +                                                                     0 ～ 543
        black_p_black_k_index = EvaluationPMove.get_black_index_by_p_move(p_move_obj, shall_p_white_to_black) * EvaluationKMove.get_serial_number_size() + EvaluationKMove.get_black_index_by_k_move(k_move_obj, shall_k_white_to_black)

        # assert
        if EvaluationPMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size() <= black_p_black_k_index:
            raise ValueError(f"black_p_black_k_index:{black_p_black_k_index} out of range {EvaluationPMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size()}")

        return black_p_black_k_index


    @staticmethod
    def destructure_p_k_index_by_pk_index(
            pk_index):
        """ＰＫインデックスを渡すと、ＰインデックスとＫインデックスに分解して返します

        Parameter
        ---------
        pk_index : int
            兵と玉の関係の通しインデックス

        Returns
        -------
        - p_index : int
            兵の着手のインデックス
        - k_index : int
            玉の応手のインデックス
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

        return (p_index, k_index)


    # destructure_pk_index
    # build_p_k_moves_by_pk_index
    # build_black_p_k_moves_by_pk_index
    @staticmethod
    def build_black_p_black_k_moves_by_black_p_black_k_index(
            black_p_black_k_index):
        """ＰＫインデックス分解

        Parameter
        ---------
        black_p_black_k_index : int
            兵と玉の関係の通しインデックス

        Returns
        -------
        - p_move_obj : Move
            兵の着手
        - k_move_obj : Move
            玉の応手
        """
        (p_index,
         k_index) = EvaluationPkTable.destructure_p_k_index_by_pk_index(
                pk_index=black_p_black_k_index)

        # Ｋ
        (k_srcsq,
         k_dstsq) = EvaluationKMove.destructure_srcsq_dstsq_by_k_index(
                k_index=k_index)

        # Ｐ
        (p_srcloc,
         p_dstsq,
         p_promote) = EvaluationPMove.destructure_srcloc_dstsq_promoted_by_p_index(
                p_index=p_index)

        # Ｋ
        black_k_move_obj = Move.from_src_dst_pro(
                srcloc=k_srcsq,
                dstsq=k_dstsq,
                # 玉に成りはありません
                promoted=False,
                # 先手のインデックスを渡されるので、回転して先手に合わせる必要はありません
                is_rotate=False)

        # Ｐ
        black_p_move_obj = Move.from_src_dst_pro(
                srcloc=p_srcloc,
                dstsq=p_dstsq,
                promoted=p_promote,
                # 先手のインデックスを渡されるので、回転して先手に合わせる必要はありません
                is_rotate=False)

        return (black_p_move_obj, black_k_move_obj)


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
    def get_relation_exists_by_pk_moves(
            self,
            p_move_obj,
            k_move_obj,
            shall_p_white_to_black,
            shall_k_white_to_black):
        """玉と兵の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        p_move_obj : Move
            兵の指し手
        k_move_obj : Move
            玉の指し手
        shall_p_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_k_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？

        Returns
        -------
        bit : int
            0 or 1
        """

        # assert
        if Usi.is_drop_by_srcloc(k_move_obj.srcloc):
            raise ValueError(f"[evaluation pk table > get relation exists by pk moves > k] 玉の指し手で打なのはおかしい。 k_move_obj.srcloc_u:{Usi.srcloc_to_code(k_move_obj.srcloc)}  k_move_obj:{k_move_obj.dump()}")

        return self.get_relation_exists_by_index(
                black_k_black_p_index=EvaluationPkTable.get_black_p_black_k_index(
                    p_move_obj=p_move_obj,
                    k_move_obj=k_move_obj,
                    shall_p_white_to_black=shall_p_white_to_black,
                    shall_k_white_to_black=shall_k_white_to_black))


    def get_relation_exists_by_index(
            self,
            black_p_black_k_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        black_p_black_k_index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=black_p_black_k_index)


    def set_relation_exists_by_pk_moves(
            self,
            p_move_obj,
            k_move_obj,
            shall_p_white_to_black,
            shall_k_white_to_black,
            bit):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        p_move_obj : Move
            兵の着手
        k_move_obj : Move
            玉の応手
        shall_p_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_k_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """
        is_changed = self._mm_table_obj.set_bit_by_index(
                index=EvaluationPkTable.get_black_p_black_k_index(
                        p_move_obj=p_move_obj,
                        k_move_obj=k_move_obj,
                    shall_p_white_to_black=shall_p_white_to_black,
                    shall_k_white_to_black=shall_k_white_to_black),
                bit=bit)

        return is_changed


    #select_pk_index_and_relation_exists
    def select_black_p_black_k_index_and_relation_exists(
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
            black_p_black_k_index = EvaluationPkTable.get_black_p_black_k_index(
                p_move_obj=p_move_obj,
                k_move_obj=Move.from_usi(k_move_u),
                shall_p_white_to_black=p_turn==cshogi.WHITE,
                shall_k_white_to_black=p_turn==cshogi.BLACK)

            relation_bit = self.get_relation_exists_by_index(
                    black_p_black_k_index=black_p_black_k_index)

            relations[black_p_black_k_index] = relation_bit

        return relations
