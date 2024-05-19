import os
import datetime
from v_a15_0_lib import Turn, Move, EvalutionMmTable
from v_a15_0_eval_lib import EvaluationLib


class EvaluationKkTable():
    """ＫＫ評価値テーブル

    下図：　玉の指し手は、現在地 you と、移動先の８方向で表せる

    +----+----+----+
    |  5 |  3 |  0 |
    |    |    |    |
    +----+----+----+
    |  6 | You|  1 |
    |    |    |    |
    +----+----+----+
    |  7 |  4 |  2 |
    |    |    |    |
    +----+----+----+

    👆　例えば　5g5f　なら、移動先は 3 が該当する

    👇　移動先は、移動元との相対SQを使うことでマス番号を取得できる

    +----+----+----+
    | +8 | -1 |-10 |
    |    |    |    |
    +----+----+----+
    | +9 | You| -9 |
    |    |    |    |
    +----+----+----+
    |+10 | +1 | -8 |
    |    |    |    |
    +----+----+----+

    しかし、盤の隅に玉があるとき、玉は３方向にしか移動できないので、８方向のテーブルには無駄ができる。
    切り詰めたいので　下図：９つのケース（Ａ～Ｉブロック）　に対応する９つのテーブルを用意する

      9     2～8  1
    +--+--------+--+
    | G|      D | A| 一
    +--+--------+--+
    |  |        |  | 二～八
    | H|      E | B|
    |  |        |  |
    +--+--------+--+
    | I|      F | C| 九
    +--+--------+--+

    +----+----+    +----+----+----+    +----+----+
    |  G |  0 |    |  3 |  D |  0 |    |  1 |  A |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+
    |  2 |  1 |    |  4 |  2 |  1 |    |  2 |  0 |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+

    +----+----+    +----+----+----+    +----+----+
    |  3 |  0 |    |  5 |  3 |  0 |    |  2 |  0 |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+
    |  H |  1 |    |  6 |  E |  1 |    |  3 |  B |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+
    |  4 |  2 |    |  7 |  4 |  2 |    |  4 |  1 |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+

    +----+----+    +----+----+----+    +----+----+
    |  2 |  0 |    |  3 |  2 |  0 |    |  1 |  0 |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+
    |  I |  1 |    |  4 |  F |  1 |    |  2 |  C |
    |    |    |    |    |    |    |    |    |    |
    +----+----+    +----+----+----+    +----+----+

    Ａは３マス、　１か所、計　　３マス
    Ｂは５マス、　７か所、計　３５マス
    Ｃは３マス、　１か所、計　　３マス
    Ｄは５マス、　７か所、計　３５マス
    Ｅは８マス、４９か所、計３９２マス
    Ｆは５マス、　７か所、計　３５マス
    Ｇは３マス、　１か所、計　　３マス
    Ｈは５マス、　７か所、計　３５マス
    Ｉは３マス、　１か所、計　　３マス
    合計　５４４マス

    圧縮しない場合　８マス×８１か所で６４８マスだったので
    ６４８ー５４４＝１０４マスの削減
    1 - 544 / 658 = 0.17... なので１７％の削減
    """


    _relative_sq_to_move_index = {
        'A':{
            1: 0,
            9: 1,
            10: 2,
        },
        'B':{
            -1: 0,
            1: 1,
            8: 2,
            9: 3,
            10: 4,
        },
        'C':{
            -1: 0,
            8: 1,
            9: 2,
        },
        'D':{
            -9: 0,
            -8: 1,
            1: 2,
            9: 3,
            10: 4,
        },
        'E':{
            -10: 0,
            -9: 1,
            -8: 2,
            -1: 3,
            1: 4,
            8: 5,
            9: 6,
            10: 7,
        },
        'F':{
            -10: 0,
            -9: 1,
            -1: 2,
            8: 3,
            9: 4,
        },
        'G':{
            -9: 0,
            -8: 1,
            1: 2,
        },
        'H':{
            -10: 0,
            -9: 1,
            -8: 2,
            -1: 3,
            1: 4,
        },
        'I':{
            -10: 0,
            -9: 1,
            -1: 2,
        },
    }
    """相対SQを、玉の指し手のインデックスへ変換"""

    _relative_index_to_relative_sq = {
        'A':{
            0:1,
            1:9,
            2:10,
        },
        'B':{
            0:-1,
            1:1,
            2:8,
            3:9,
            4:10,
        },
        'C':{
            0:-1,
            1:8,
            2:9,
        },
        'D':{
            0:-9,
            1:-8,
            2:1,
            3:9,
            4:10,
        },
        'E':{
            0: -10,
            1: -9,
            2: -8,
            3: -1,
            4: 1,
            5: 8,
            6: 9,
            7: 10,
        },
        'F':{
            0:-10,
            1:-9,
            2:-1,
            3:8,
            4:9,
        },
        'G':{
            0:-9,
            1:-8,
            2:1,
        },
        'H':{
            0:-10,
            1:-9,
            2:-8,
            3:-1,
            4:1,
        },
        'I':{
            0:-10,
            1:-9,
            2:-1,
        },
    }
    """玉の指し手のインデックスを相対SQへ変換"""


    @staticmethod
    def get_block_by_sq(sq):
        """マス番号をブロック番号へ変換"""
        if sq == 0:
            return 'A'
        elif sq == 8:
            return 'C'
        elif sq == 72:
            return 'G'
        elif sq == 80:
            return 'I'
        elif sq % 9 == 0: # and sq != 0 and sq != 72:
            return 'D'
        elif sq % 9 == 8: # and sq != 8 and sq != 80:
            return 'F'
        elif 1 <= sq and sq <= 7:
            return 'B'
        elif 73 <= sq and sq <= 79:
            return 'H'
        else:
            return 'E'


    @staticmethod
    def get_king_direction_max_number():
        """玉の移動方向の最大数

        Returns
        -------
        - int
        """
        return 8


    @staticmethod
    def get_king_move_number():
        """玉の指し手の数

        Returns
        -------
        - int
        """
        # move_number = sq_size * directions
        #         648 =      81 *          8
        return    648


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

        # 0 ～ 419_903 =                                          0 ～ 647 *                                      648 +                                          0 ～ 647
        return           EvaluationKkTable.get_index_of_k_move(k_move_obj) * EvaluationKkTable.get_king_move_number() + EvaluationKkTable.get_index_of_k_move(l_move_obj)


    @staticmethod
    def get_index_of_k_move(
            move_obj):
        """指し手を指定すると、指し手のインデックスを返す。
        ＫＫ評価値テーブル用

        Parameters
        ----------
        move_obj : Move
            指し手

        Returns
        -------
            - 指し手のインデックス
        """

        # 移動元マス番号
        #
        #   - 打はありません。したがって None にはなりません
        #
        src_sq = move_obj.src_sq_or_none

        # 玉は成らない

        # 相対SQ    =  移動先マス番号    - 移動元マス番号
        relative_sq = move_obj.dst_sq - src_sq

        try:
            relative_index = EvaluationKkTable._relative_sq_to_move_index['E'][relative_sq]

        except KeyError as ex:
            # move_obj.as_usi:5a5b / relative_sq:1 move_obj.dst_sq:37 src_sq:36
            print(f"move_obj.as_usi:{move_obj.as_usi} / relative_sq:{relative_sq} move_obj.dst_sq:{move_obj.dst_sq} src_sq:{src_sq}")
            raise


        # 0～647 =  0～80  *                                                 8 +           0～7
        return     src_sq * EvaluationKkTable.get_king_direction_max_number() + relative_index


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
                    a_move_size=EvaluationKkTable.get_king_move_number(),
                    b_move_size=EvaluationKkTable.get_king_move_number())
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
        """
        return self._mm_table_obj.set_bit_by_index(
                index=EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj),
                bit=bit)


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
    def destructure_k_index(
            k_index):
        """Ｋインデックス分解

        Parameter
        ---------
        k_index : int
            玉の指し手のインデックス

        Returns
        -------
        - move_obj : Move
            指し手
        """
        rest = k_index

        king_direction_max_number = EvaluationKkTable.get_king_direction_max_number()

        relative_index = rest % king_direction_max_number
        rest //= king_direction_max_number

        src_sq = rest

        # Ｅブロック
        relative_sq = EvaluationKkTable._relative_index_to_relative_sq['E'][relative_index]
        dst_sq = src_sq + relative_sq

        return Move.from_src_dst_pro(
                src_sq=src_sq,
                dst_sq=dst_sq,
                promoted=False)


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
        king_move_number = EvaluationKkTable.get_king_move_number()

        l_index = kl_index % king_move_number
        k_index = kl_index // king_move_number

        l_move_obj = EvaluationKkTable.destructure_k_index(
            k_index=l_index)
        k_move_obj = EvaluationKkTable.destructure_k_index(
            k_index=k_index)

        return (k_move_obj, l_move_obj)


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    for sq in range(0,81):
        block_str = EvaluationKkTable.get_block_by_sq(sq)
        print(f"sq:{sq}  block:{block_str}")
