# python v_a23_0_eval_k.py
from v_a23_0_lib import Move
from v_a23_0_debug import DebugHelper


class EvaluationKMove():
    """自玉の指し手

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

    #_relative_sq_to_move_index
    _k_index_by_relative_sq = {
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
    """玉の指し手の相対SQを、インデックスへ変換"""


    #_relative_index_to_relative_sq
    _relative_sq_by_k_index = {
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
    """将棋盤を A ～ I の９ブロックに分け、玉の指し手のインデックスを相対SQへ変換"""


    @staticmethod
    def get_king_direction_max_number():
        """玉の移動方向の最大数

        Returns
        -------
        - int
        """
        return 8


    #get_king_move_number
    @staticmethod
    def get_pattern_number():
        """玉の指し手の数

        Returns
        -------
        - int
        """
        # move_number = sq_size * directions
        #         648 =      81 *          8
        return    648


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


    @classmethod
    def get_k_index_by_relative_sq(clazz):
        """玉の指し手の相対SQを、インデックスへ変換するテーブルを取得"""
        return clazz._k_index_by_relative_sq


    @classmethod
    def get_relative_sq_by_k_index(clazz):
        return clazz._relative_sq_by_k_index


    #get_index_of_k_move
    @staticmethod
    def get_index_by_k_move(
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
            k_index = EvaluationKMove.get_k_index_by_relative_sq()['E'][relative_sq]

        except KeyError as ex:
            # move_obj.as_usi:5a5b / relative_sq:1 move_obj.dst_sq:37 src_sq:36
            print(f"move_obj.as_usi:{move_obj.as_usi} / relative_sq:{relative_sq} move_obj.dst_sq:{move_obj.dst_sq} src_sq:{src_sq}")
            raise


        # 0～647 =  0～80  *                                              8 +    0～7
        return     src_sq * EvaluationKMove.get_king_direction_max_number() + k_index


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

        king_direction_max_number = EvaluationKMove.get_king_direction_max_number()

        relative_index = rest % king_direction_max_number
        rest //= king_direction_max_number

        src_sq = rest

        # Ｅブロック
        relative_sq = EvaluationKMove.get_relative_sq_by_k_index()['E'][relative_index]
        dst_sq = src_sq + relative_sq

        return Move.from_src_dst_pro(
                src_sq=src_sq,
                dst_sq=dst_sq,
                promoted=False)


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    # ３桁
    squares = ['   '] * 81

    with open("test_eval_k.log", 'w', encoding="utf-8") as f:

        for sq in range(0,81):
            block_str = EvaluationKMove.get_block_by_sq(sq)
            squares[sq] = f" {block_str} "
            #f.write(f"sq:{sq}  block:{block_str}\n")

        f.write(f"""\
block:
{DebugHelper.stringify_3characters_board(squares)}

""")
