# python v_a23_0_eval_p.py
from v_a23_0_lib import Move

class EvaluationKMove():
    """自兵の指し手

    兵は玉以外の駒。

    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |   |   |
    +---+---+---+---+---+---+---+---+---+
              将棋盤のテンプレート

    👇下図：　兵の指し手は、現在地 yo と、移動先で表せる。例えば１一にある兵

    +---+---+---+---+---+---+---+---+---+
    | 22| 20| 18| 16| 14| 12| 10|  8|you|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   |   |  9|  0|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   |   | 11|   |  1|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   |   | 13|   |   |  2|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |   | 15|   |   |   |  3|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   | 17|   |   |   |   |  4|
    +---+---+---+---+---+---+---+---+---+
    |   |   | 19|   |   |   |   |   |  5|
    +---+---+---+---+---+---+---+---+---+
    |   | 21|   |   |   |   |   |   |  6|
    +---+---+---+---+---+---+---+---+---+
    | 23|   |   |   |   |   |   |   |  7|
    +---+---+---+---+---+---+---+---+---+

    👆　例えば　1a2b　なら、移動先は 9 が該当する

    飛車の利き、角の利き、桂の利きだけを考慮すればいい。金、銀、香、歩はその中に包摂される。

    +---+---+---+---+---+---+---+---+---+
    | 31|   |   |   | 13|   |   |   |  0|
    +---+---+---+---+---+---+---+---+---+
    |   | 28|   |   | 14|   |   |  3|   |
    +---+---+---+---+---+---+---+---+---+
    |   |   | 25| 21| 15|  9|  6|   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   | 22| 16| 10|   |   |   |
    +---+---+---+---+---+---+---+---+---+
    | 32| 29| 26| 23| yo| 11|  7|  4|  1|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   | 24| 17| 12|   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   | 27|   | 18|   |  8|   |   |
    +---+---+---+---+---+---+---+---+---+
    |   | 30|   |   | 19|   |   |  5|   |
    +---+---+---+---+---+---+---+---+---+
    | 33|   |   |   | 20|   |   |   |  2|
    +---+---+---+---+---+---+---+---+---+
                 ５五のケース

    👇　移動先は、移動元との相対SQを使うことでマス番号を取得できる

    +---+---+---+---+---+---+---+---+---+
    | 32|   |   |   | -4|   |   |   |-40|
    +---+---+---+---+---+---+---+---+---+
    |   | 24|   |   | -3|   |   |-30|   |
    +---+---+---+---+---+---+---+---+---+
    |   |   | 16|  7| -2|-11|-20|   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   |   |  8| -1|-10|   |   |   |
    +---+---+---+---+---+---+---+---+---+
    | 36| 27| 18|  9|you| -9|-18|-27|-36|
    +---+---+---+---+---+---+---+---+---+
    |   |   |   | 10|  1| -8|   |   |   |
    +---+---+---+---+---+---+---+---+---+
    |   |   | 20|   |  2|   |-16|   |   |
    +---+---+---+---+---+---+---+---+---+
    |   | 30|   |   |  3|   |   |-24|   |
    +---+---+---+---+---+---+---+---+---+
    | 40|   |   |   |  4|   |   |   |-32|
    +---+---+---+---+---+---+---+---+---+
                先手５五のケース

    👆　このマッピングは８１マス分あり、要素数も１種類ではない
    """


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    def get_sq_by_x_y(file, rank):
        return file * 9 + rank

    # 範囲外チェックを行いたいので、ループカウンタ―は sq ではなく file と rank の２重ループにする
    for file in range(0,9):
        for rank in range(0,9):
            src_sq = get_sq_by_x_y(
                    file=file,
                    rank=rank)
            dst_sq_set = set()

            # 飛車の動き
            for delta_rank in range(0,8):
                # 上
                next_rank = rank-delta_rank
                if 0 <= next_rank:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=file,
                            rank=next_rank))

                # 下
                next_rank = rank+delta_rank
                if next_rank < 9:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=file,
                            rank=next_rank))

            for delta_file in range(0,8):
                # 右
                next_file = file-delta_file
                if 0 <= next_file:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=next_file,
                            rank=rank))

                # 下
                next_file = file+delta_file
                if next_file < 9:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=next_file,
                            rank=rank))


            # 角の動き
            for delta in range(0,8):
                # 右上
                next_file = file-delta
                next_rank = rank-delta
                if 0 <= next_file and 0 <= next_rank:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=next_file,
                            rank=next_rank))

                # 右下
                next_file = file-delta
                next_rank = rank+delta
                if 0 <= next_file and next_rank < 9:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=next_file,
                            rank=next_rank))

                # 左上
                next_file = file+delta
                next_rank = rank-delta
                if next_file < 9 and 0 <= next_rank:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=next_file,
                            rank=next_rank))

                # 左下
                next_file = file+delta
                next_rank = rank+delta
                if next_file < 9 and next_rank < 9:
                    dst_sq_set.add(get_sq_by_x_y(
                            file=next_file,
                            rank=next_rank))

            # 桂馬の動き
            # 先手右上
            next_file = file-1
            next_rank = rank-2
            if 0 <= next_file and 0 <= next_rank:
                dst_sq_set.add(get_sq_by_x_y(
                        file=next_file,
                        rank=next_rank))

            # 先手左上
            next_file = file+1
            next_rank = rank-2
            if next_file < 9 and 0 <= next_rank:
                dst_sq_set.add(get_sq_by_x_y(
                        file=next_file,
                        rank=next_rank))

            #block_str = EvaluationKMove.get_block_by_sq(sq)
            print(f"src_sq:{src_sq}  len:{len(dst_sq_set)}")
            for dst_sq in sorted(list(dst_sq_set)):
                print(f"  dst_sq:{dst_sq}")

