# python v_a24_0_eval_p.py
from v_a24_0_lib import BoardHelper
from v_a24_0_debug import DebugHelper


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

    👇 兵の指し手は、次の２種類に大別できる

    1. 先手
    2. 後手

    👇 さらに細かく、以下の３つに分類できる

    1. 成らずの手
    2. 成りの手
    3. 打

    👇 下図：　兵の指し手は、現在地 yo と、移動先で表せる。例えば１一にある兵

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

    with open("test_eval_p.log", 'w', encoding="utf-8") as f:

        subtotal_effect = [0] * 81

        src_sq_to_dst_sq_to_index_for_a_dictionary = dict()
        src_sq_to_dst_sq_to_index_for_b_dictionary = dict()
        src_sq_to_dst_sq_for_c_dictionary = dict()
        src_sq_to_dst_sq_for_d_dictionary = dict()

        # 通しのインデックス
        effect_index = 0

        # 範囲外チェックを行いたいので、ループカウンタ―は sq ではなく file と rank の２重ループにする
        for src_file in range(0,9):
            for src_rank in range(0,9):
                src_sq = BoardHelper.get_sq_by_file_rank(
                        file=src_file,
                        rank=src_rank)

                dst_sq_to_index_for_a_dictionary = dict()
                dst_sq_to_index_for_b_dictionary = dict()
                dst_sq_for_c_set = set()
                dst_sq_for_d_set = set()

                src_sq_to_dst_sq_to_index_for_a_dictionary[src_sq] = dst_sq_to_index_for_a_dictionary
                src_sq_to_dst_sq_to_index_for_b_dictionary[src_sq] = dst_sq_to_index_for_b_dictionary
                src_sq_to_dst_sq_for_c_dictionary[src_sq] = dst_sq_for_c_set
                src_sq_to_dst_sq_for_d_dictionary[src_sq] = dst_sq_for_d_set

                # 成らないことができる移動先
                no_pro_dst_sq_set = set()

                # 成ることができる移動先
                pro_dst_sq_set = set()

                #
                # 飛車の動き
                #

                # 垂直
                for delta_rank in range(1,9):
                    # 上
                    next_rank = src_rank-delta_rank
                    if 0 <= next_rank:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=src_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                    # 下
                    next_rank = src_rank+delta_rank
                    if next_rank < 9:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=src_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                # 水平
                for delta_file in range(1,9):
                    # 右
                    next_file = src_file-delta_file
                    if 0 <= next_file:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=next_file,
                                rank=src_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # １段目～３段目の水平の動きなら、成ることができる
                        if 0 <= src_rank and src_rank < 3:
                            pro_dst_sq_set.add(dst_sq)

                    # 左
                    next_file = src_file+delta_file
                    if next_file < 9:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=next_file,
                                rank=src_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # １段目～３段目の水平の動きなら、成ることができる
                        if 0 <= src_rank and src_rank < 3:
                            pro_dst_sq_set.add(dst_sq)

                #
                # 角の動き
                #
                for delta in range(1,9):
                    # 右上
                    next_file = src_file-delta
                    next_rank = src_rank-delta
                    if 0 <= next_file and 0 <= next_rank:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=next_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                    # 右下
                    next_file = src_file-delta
                    next_rank = src_rank+delta
                    if 0 <= next_file and next_rank < 9:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=next_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                    # 左上
                    next_file = src_file+delta
                    next_rank = src_rank-delta
                    if next_file < 9 and 0 <= next_rank:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=next_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                    # 左下
                    next_file = src_file+delta
                    next_rank = src_rank+delta
                    if next_file < 9 and next_rank < 9:
                        dst_sq = BoardHelper.get_sq_by_file_rank(
                                file=next_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                #
                # 桂馬の動き
                #

                # 先手右上
                next_file = src_file-1
                next_rank = src_rank-2
                if 0 <= next_file and 0 <= next_rank:
                    dst_sq = BoardHelper.get_sq_by_file_rank(
                            file=next_file,
                            rank=next_rank)
                    no_pro_dst_sq_set.add(dst_sq)

                    # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                    if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                        pro_dst_sq_set.add(dst_sq)

                # 先手左上
                next_file = src_file+1
                next_rank = src_rank-2
                if next_file < 9 and 0 <= next_rank:
                    dst_sq = BoardHelper.get_sq_by_file_rank(
                            file=next_file,
                            rank=next_rank)
                    no_pro_dst_sq_set.add(dst_sq)

                    # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                    if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                        pro_dst_sq_set.add(dst_sq)

                no_pro_len = len(no_pro_dst_sq_set)
                pro_len = len(pro_dst_sq_set)
                subtotal_len = no_pro_len + pro_len

                subtotal_effect[src_sq] = subtotal_len

                #
                # 表示
                #

                for dst_sq in no_pro_dst_sq_set:
                    dst_sq_to_index_for_a_dictionary[dst_sq] = effect_index
                    effect_index += 1
                    dst_sq_for_c_set.add(dst_sq)

                for dst_sq in pro_dst_sq_set:
                    dst_sq_to_index_for_b_dictionary[dst_sq] = effect_index
                    effect_index += 1
                    dst_sq_for_d_set.add(dst_sq)

        #
        # 持ち駒 to （移動先 to 通し番号）
        #
        drop_to_dst_sq_index = dict()

        for drop in ['R', 'B', 'G', 'S', 'N', 'L', 'P']:

            #
            # 移動先 to 通し番号
            #
            dst_sq_to_index = dict()

            drop_to_dst_sq_index[drop] = dst_sq_to_index

            if drop == 'N':
                min_rank = 2

            elif drop in ['L', 'P']:
                min_rank = 1

            else:
                min_rank = 0


            for dst_file in range(0,9):
                for dst_rank in range(min_rank,9):
                    dst_sq = BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank)

                    # 格納
                    dst_sq_to_index[dst_sq] = effect_index
                    effect_index += 1


        #
        # 表示
        #
        for src_sq in range(0,81):
            dst_sq_to_index_for_a_dictionary = src_sq_to_dst_sq_to_index_for_a_dictionary[src_sq]
            dst_sq_to_index_for_b_dictionary = src_sq_to_dst_sq_to_index_for_b_dictionary[src_sq]
            dst_sq_for_c_set = src_sq_to_dst_sq_for_c_dictionary[src_sq]
            dst_sq_for_d_set = src_sq_to_dst_sq_for_d_dictionary[src_sq]

            # 成らない指し手の各マス　値：通しインデックス
            label_table_for_a = ["    "] * 81

            # 成る指し手の各マス　値：通しインデックス
            label_table_for_b = ["    "] * 81

            # 成らない指し手の各マス　値：相対ます番号
            label_table_for_c = ["    "] * 81

            # 成る指し手の各マス　値：相対ます番号
            label_table_for_d = ["    "] * 81

            label_table_for_a[src_sq] = " you"
            label_table_for_b[src_sq] = " you"
            label_table_for_c[src_sq] = " you"
            label_table_for_d[src_sq] = " you"

            for dst_sq, effect_index in dst_sq_to_index_for_a_dictionary.items():
                label_table_for_a[dst_sq] = f"{effect_index:4}"

            for dst_sq, effect_index in dst_sq_to_index_for_b_dictionary.items():
                label_table_for_b[dst_sq] = f"{effect_index:4}"

            for dst_sq in dst_sq_for_c_set:
                label_table_for_c[dst_sq] = f"{dst_sq:4}"

            for dst_sq in dst_sq_for_d_set:
                label_table_for_d[dst_sq] = f"{dst_sq:4}"

            f.write(f"""src_sq:{src_sq}  effect:{subtotal_len} = no pro:{no_pro_len} + pro:{pro_len}
通しインデックス  先手成らず                          通しインデックス  先手成り                           絶対マス  先手成らず                                 絶対マス  先手成り
{DebugHelper.stringify_quadruple_4characters_board(label_table_for_a, label_table_for_b, label_table_for_c, label_table_for_d)}

""")

        # 打
        #
        #   - 打は SFEN では駒種類毎に分かれている。 R, B, G, S, N, L, P
        #
        for drop in ['R', 'B', 'G', 'S', 'N', 'L', 'P']:
            dst_sq_to_index_dictionary = drop_to_dst_sq_index[drop]

            label_table_for_drop = ['    '] * 81

            for dst_sq, effect_index in dst_sq_to_index_dictionary.items():
                label_table_for_drop[dst_sq] = f"{effect_index:4}"

            f.write(f"""
drop:{drop}
{DebugHelper.stringify_4characters_board(label_table_for_drop)}

""")

        f.write(f"""
total_effect:{effect_index + 1}

no pro + pro
{DebugHelper.stringify_3characters_board(subtotal_effect)}

""")

# TODO 後手
