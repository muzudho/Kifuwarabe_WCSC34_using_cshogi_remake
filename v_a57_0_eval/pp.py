import os
import datetime

from v_a57_0_eval.lib import EvaluationLib
from v_a57_0_eval.p import EvaluationPMove
from v_a57_0_misc.lib import FileName, Turn, Move, EvalutionMmTable


class EvaluationPpTable():
    """ＰＰ評価値テーブル"""

    #get_index_of_pp_table
    @staticmethod
    def get_black_p1_black_p2_index(
            p1_move_obj,
            p2_move_obj,
            shall_p1_white_to_black,
            shall_p2_white_to_black):
        """ＰＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        p1_move_obj : Move
            兵１の着手
        p2_move_obj : Move
            兵２の応手
        shall_p1_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_p2_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        """

        try:
            # 0 ～ 14_542_781 =                                                                       0 ～ 3812 *                                     3813 +                                                                      0 ～ 3812
            pp_index         = EvaluationPMove.get_black_index_by_p_move(p1_move_obj, shall_p1_white_to_black) * EvaluationPMove.get_serial_number_size() + EvaluationPMove.get_black_index_by_p_move(p2_move_obj, shall_p2_white_to_black)

        except KeyError:
            print(f"""[evaluation pp table > get index of pp table] エラー
p1_move_obj:{p1_move_obj.as_usi:5}  shall_p1_white_to_black:{shall_p1_white_to_black}
p2_move_obj:{p2_move_obj.as_usi:5}
""")
            raise

        # assert
        if EvaluationPMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size() <= pp_index:
            raise ValueError(f"pp_index:{pp_index} out of range {EvaluationPMove.get_serial_number_size() * EvaluationPMove.get_serial_number_size()}")

        return pp_index


    #destructure_pp_index
    #build_p_p_moves_by_pp_index
    @staticmethod
    def build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
            black_p1_black_p2_index):
        """ＰＰインデックス分解

        Parameter
        ---------
        pp_index : int
            兵１と兵２の関係の通しインデックス

        Returns
        -------
        - black_p1_move_obj : Move
            兵１の着手
        - black_p2_move_obj : Move
            兵２の応手
        """

        rest = black_p1_black_p2_index

        p2_index = rest % EvaluationPMove.get_serial_number_size()
        rest //= EvaluationPMove.get_serial_number_size()

        p1_index = rest % EvaluationPMove.get_serial_number_size()

        # assert
        if EvaluationPMove.get_serial_number_size() <= p2_index:
            raise ValueError(f"p2_index:{p2_index} out of range {EvaluationPMove.get_serial_number_size()}")

        # assert
        if EvaluationPMove.get_serial_number_size() <= p1_index:
            raise ValueError(f"p1_index:{p1_index} out of range {EvaluationPMove.get_serial_number_size()}")


        # Ｐ２
        (p2_srcloc,
         p2_dstsq,
         p2_promote) = EvaluationPMove.destructure_srcloc_dstsq_promoted_by_p_index(
                p_index=p2_index)
        black_p2_move_obj = Move.from_src_dst_pro(
                srcloc=p2_srcloc,
                dstsq=p2_dstsq,
                promoted=p2_promote,
                # 先手のインデックスが渡されるので、先手に揃えるために指し手を回転させる必要はありません
                is_rotate=False)

        # Ｐ１
        (p1_srcloc,
         p1_dstsq,
         p1_promote) = EvaluationPMove.destructure_srcloc_dstsq_promoted_by_p_index(
                p_index=p1_index)
        black_p1_move_obj = Move.from_src_dst_pro(
                srcloc=p1_srcloc,
                dstsq=p1_dstsq,
                promoted=p1_promote,
                # 先手のインデックスが渡されるので、先手に揃えるために指し手を回転させる必要はありません
                is_rotate=False)

        return (black_p1_move_obj, black_p2_move_obj)


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
    def get_relation_exists_by_pp_moves(
            self,
            p1_move_obj,
            p2_move_obj,
            shall_p1_white_to_black,
            shall_p2_white_to_black):
        """兵と兵の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        p1_move_obj : Move
            兵１の指し手
        p2_move_obj : Move
            兵２の指し手
        shall_p1_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_p2_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？

        Returns
        -------
        bit : int
            0 or 1
        """
        return self.get_relation_exists_by_index(
                black_k_black_p_index=EvaluationPpTable.get_black_p1_black_p2_index(
                    p1_move_obj=p1_move_obj,
                    p2_move_obj=p2_move_obj,
                    shall_p1_white_to_black=shall_p1_white_to_black,
                    shall_p2_white_to_black=shall_p2_white_to_black))


    def get_relation_exists_by_index(
            self,
            black_p1_black_p2_index):
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
                index=black_p1_black_p2_index)


    #set_relation_exists_by_pp_moves
    def set_relation_exists_by_black_p_black_p_moves(
            self,
            black_p1_move_obj,
            black_p2_move_obj,
            bit):
        """玉の着手と兵の応手を受け取って、関係の有無を設定します

        Parameters
        ----------
        black_p1_move_obj : Move
            兵１の着手（先手の符号）
        black_p2_move_obj : Move
            兵２の応手（先手の符号）
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """
        is_changed = self._mm_table_obj.set_bit_by_index(
                black_f_black_o_index=EvaluationPpTable.get_black_p1_black_p2_index(
                        p1_move_obj=black_p1_move_obj,
                        p2_move_obj=black_p2_move_obj,
                        # 両方先手のインデックスなので、これ以上変更しません
                        shall_p1_white_to_black=False,
                        shall_p2_white_to_black=False),
                bit=bit)

        return is_changed


    #select_pp_index_and_relation_exists
    def select_black_p_black_p_index_and_relation_exists(
            self,
            p1_move_obj,
            p2_move_u_set,
            shall_p1_white_to_black,
            shall_p2_white_to_black):
        """兵１の指し手と、兵２の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＰＰ評価値テーブル用

        Parameters
        ----------
        p1_move_obj : Move
            兵１の着手
        p2_move_u_set : List<str>
            兵２の応手のリスト
        shall_p1_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        shall_p2_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＰＰ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for p2_move_u in p2_move_u_set:
            black_p1_black_p2_index = EvaluationPpTable.get_black_p1_black_p2_index(
                p1_move_obj=p1_move_obj,
                p2_move_obj=Move.from_usi(p2_move_u),
                shall_p1_white_to_black=shall_p1_white_to_black,
                shall_p2_white_to_black=shall_p2_white_to_black)

            relation_bit = self.get_relation_exists_by_index(
                    black_p1_black_p2_index=black_p1_black_p2_index)

            relations[black_p1_black_p2_index] = relation_bit

        return relations
