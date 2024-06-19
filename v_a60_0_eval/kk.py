import os
import datetime

from v_a60_0_eval.lib import EvaluationLib
from v_a60_0_eval.k import EvaluationKMove
from v_a60_0_misc.lib import FileName, Turn, Move, EvalutionMmTable
from v_a60_0_misc.usi import Usi


class EvaluationKkTable():
    """ＫＫ評価値テーブル"""


    #get_index_of_kk_table
    @staticmethod
    def get_black_k_black_l_index(
            # TODO ここは strict ではなく、 black にしてほしい
            k_move_obj,
            l_move_obj,
            shall_k_white_to_black,
            shall_l_white_to_black):
        """ＫＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        k_move_obj : Move
            自玉の着手
        l_move_obj : Move
            敵玉の応手
        shall_k_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_l_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        """

        # assert
        if Usi.is_drop_by_srcloc(k_move_obj.srcloc):
            raise ValueError(f"[evaluation kk table > get index of kk move > k] 玉の指し手で打なのはおかしい。 k_move_obj.srcloc_u:{Usi.srcloc_to_code(k_move_obj.srcloc)}  k_move_obj:{k_move_obj.dump()}")

        # assert
        if Usi.is_drop_by_srcloc(l_move_obj.srcloc):
            raise ValueError(f"[evaluation kk table > get index of kk move > l] 玉の指し手で打なのはおかしい。 l_move_obj.srcloc_u:{Usi.srcloc_to_code(l_move_obj.srcloc)}  l_move_obj:{l_move_obj.dump()}")

        # 0 ～ 296_479 =                                                                       0 ～ 543 *                                      544 +                                                                     0 ～ 543
        kk_index       = EvaluationKMove.get_black_index_by_k_move(k_move_obj, shall_k_white_to_black) * EvaluationKMove.get_serial_number_size() + EvaluationKMove.get_black_index_by_k_move(l_move_obj, shall_l_white_to_black)

        # assert
        if EvaluationKMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size() <= kk_index:
            raise ValueError(f"kk_index:{kk_index} out of range {EvaluationKMove.get_serial_number_size() * EvaluationKMove.get_serial_number_size()}")

        return kk_index


    #destructure_kl_index
    #build_k_l_moves_by_kl_index
    @staticmethod
    def build_black_k_black_l_moves_by_black_k_black_l_index(
            black_k_black_l_index):
        """ＫＬインデックス分解

        Parameter
        ---------
        black_k_black_l_index : int
            自玉と敵玉の関係の通しインデックス

        Returns
        -------
        - black_k_move_obj : Move
            自玉の着手
        - black_l_move_obj : Move
            敵玉の応手
        """

        king_serial_number_size = EvaluationKMove.get_serial_number_size()

        black_l_index = black_k_black_l_index % king_serial_number_size
        black_k_index = black_k_black_l_index // king_serial_number_size

        # assert
        if EvaluationKMove.get_serial_number_size() <= black_l_index:
            raise ValueError(f"black_l_index:{black_l_index} out of range {EvaluationKMove.get_serial_number_size()}")

        # assert
        if EvaluationKMove.get_serial_number_size() <= black_k_index:
            raise ValueError(f"black_k_index:{black_k_index} out of range {EvaluationKMove.get_serial_number_size()}")

        # Ｌ
        (l_srcsq,
         l_dstsq) = EvaluationKMove.destructure_srcsq_dstsq_by_k_index(
                k_index=black_l_index)
        black_l_move_obj = Move.from_src_dst_pro(
                srcloc=l_srcsq,
                dstsq=l_dstsq,
                # 玉に成りはありません
                promoted=False,
                # 先手のインデックスが渡されるので、回転して先手にする必要はありません
                is_rotate=False)

        # Ｋ
        (k_srcsq,
         k_dstsq) = EvaluationKMove.destructure_srcsq_dstsq_by_k_index(
                k_index=black_k_index)
        black_k_move_obj = Move.from_src_dst_pro(
                srcloc=k_srcsq,
                dstsq=k_dstsq,
                # 玉に成りはありません
                promoted=False,
                # 先手のインデックスが渡されるので、回転して先手にする必要はありません
                is_rotate=False)

        return (black_k_move_obj, black_l_move_obj)


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
        """ＫＫ評価値テーブル読込

        Parameters
        ----------
        turn : int
            手番
        """
        file_name_obj = FileName(
                file_stem=f'data[{self._engine_version_str}]_n1_eval_kk_{Turn.to_string(turn)}',
                file_extension='.bin'
        )

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
                    b_move_size=EvaluationKMove.get_serial_number_size())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name_obj=file_name_obj,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_kk_evaluation_table_file(
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


    def get_relation_exists_by_index(
            self,
            black_k_black_l_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        kl_index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=black_k_black_l_index)


    #set_relation_exsits_by_kl_moves
    def set_relation_exsits_by_black_k_black_l_moves(
            self,
            black_k_move_obj,
            black_l_move_obj,
            bit):
        """自玉の着手と敵玉の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        black_k_move_obj : Move
            自玉の指し手
        black_l_move_obj : Move
            敵玉の指し手
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        result_comment : str
            変更できなかった場合の説明
        """

        # assert
        if Usi.is_drop_by_srcloc(black_k_move_obj.srcloc):
            raise ValueError(f"[evaluation kk table > set relation exists by kl moves > k] 玉の指し手で打なのはおかしい。 black_k_move_obj.srcloc_u:{Usi.srcloc_to_code(black_k_move_obj.srcloc)}  black_k_move_obj:{black_k_move_obj.dump()}")

        # assert
        if Usi.is_drop_by_srcloc(black_l_move_obj.srcloc):
            raise ValueError(f"[evaluation kk table > set relation exists by kl moves > l] 玉の指し手で打なのはおかしい。 black_l_move_obj.srcloc_u:{Usi.srcloc_to_code(black_l_move_obj.srcloc)}  black_l_move_obj:{black_l_move_obj.dump()}")

        (is_changed, result_comment) = self._mm_table_obj.set_bit_by_index(
                black_f_black_o_index=EvaluationKkTable.get_black_k_black_l_index(
                        k_move_obj=black_k_move_obj,
                        l_move_obj=black_l_move_obj,
                        # 両方先手のインデックスなので、これ以上変更しません
                        shall_k_white_to_black=False,
                        shall_l_white_to_black=False),
                bit=bit)

        return (is_changed, result_comment)


    #create_relation_exists_dictionary_by_k_move_and_l_moves
    #select_kl_index_and_relation_exists
    def select_black_k_black_l_index_and_relation_exists(
            self,
            # ここは strict ではなく black にしてほしい
            k_strict_move_obj,
            l_strict_move_u_set,
            shall_k_white_to_black,
            shall_l_white_to_black):
        """自玉の指し手と、敵玉の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＫＫ評価値テーブル用

        Parameters
        ----------
        k_strict_move_obj : Move
            自玉の着手
        l_strict_move_u_set : List<str>
            敵玉の応手のリスト
        shall_k_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_l_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＫＫ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for l_strict_move_u in l_strict_move_u_set:
            black_k_black_l_index = EvaluationKkTable.get_black_k_black_l_index(
                    k_move_obj=k_strict_move_obj,
                    l_move_obj=Move.from_usi(l_strict_move_u),
                    shall_k_white_to_black=shall_k_white_to_black,
                    shall_l_white_to_black=shall_l_white_to_black)

            relation_bit = self.get_relation_exists_by_index(
                    black_k_black_l_index=black_k_black_l_index)

            relations[black_k_black_l_index] = relation_bit

        return relations
