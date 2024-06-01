# python v_a23_0_eval_p.py
from v_a23_0_lib import Move
from v_a23_0_debug import DebugHelper


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

        def get_sq_by_x_y(file, rank):
            return file * 9 + rank

        subtotal_effect = [0] * 81

        # 通しのインデックス
        effect_index = 0

        # 範囲外チェックを行いたいので、ループカウンタ―は sq ではなく file と rank の２重ループにする
        for src_file in range(0,9):
            for src_rank in range(0,9):
                src_sq = get_sq_by_x_y(
                        file=src_file,
                        rank=src_rank)

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
                        dst_sq = get_sq_by_x_y(
                                file=src_file,
                                rank=next_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dst_sq_set.add(dst_sq)

                    # 下
                    next_rank = src_rank+delta_rank
                    if next_rank < 9:
                        dst_sq = get_sq_by_x_y(
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
                        dst_sq = get_sq_by_x_y(
                                file=next_file,
                                rank=src_rank)
                        no_pro_dst_sq_set.add(dst_sq)

                        # １段目～３段目の水平の動きなら、成ることができる
                        if 0 <= src_rank and src_rank < 3:
                            pro_dst_sq_set.add(dst_sq)

                    # 左
                    next_file = src_file+delta_file
                    if next_file < 9:
                        dst_sq = get_sq_by_x_y(
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
                        dst_sq = get_sq_by_x_y(
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
                        dst_sq = get_sq_by_x_y(
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
                        dst_sq = get_sq_by_x_y(
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
                        dst_sq = get_sq_by_x_y(
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
                    dst_sq = get_sq_by_x_y(
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
                    dst_sq = get_sq_by_x_y(
                            file=next_file,
                            rank=next_rank)
                    no_pro_dst_sq_set.add(dst_sq)

                    # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                    if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                        pro_dst_sq_set.add(dst_sq)

                #block_str = EvaluationKMove.get_block_by_sq(sq)
                no_pro_len = len(no_pro_dst_sq_set)
                pro_len = len(pro_dst_sq_set)
                subtotal_len = no_pro_len + pro_len

                subtotal_effect[src_sq] = subtotal_len

                #
                # デバッグ表示
                #

                # 成らない指し手の各マス　値：通しインデックス
                a = ["    "] * 81

                # 成る指し手の各マス　値：通しインデックス
                m = ["    "] * 81

                # 成らない指し手の各マス　値：相対ます番号
                b = ["    "] * 81

                # 成る指し手の各マス　値：相対ます番号
                c = ["    "] * 81

                a[src_sq] = " you"
                m[src_sq] = " you"
                b[src_sq] = " you"
                c[src_sq] = " you"

                for dst_sq in no_pro_dst_sq_set:
                    a[dst_sq] = f"{effect_index:4}"
                    effect_index += 1
                    b[dst_sq] = f"{dst_sq-src_sq:4}"

                for dst_sq in pro_dst_sq_set:
                    m[dst_sq] = f"{effect_index:4}"
                    effect_index += 1
                    c[dst_sq] = f"{dst_sq-src_sq:4}"

                f.write(f"""src_sq:{src_sq}  effect:{subtotal_len} = no pro:{no_pro_len} + pro:{pro_len}
先手成らず                                         先手成り
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
│{a[72]}|{a[63]}|{a[54]}|{a[45]}|{a[36]}|{a[27]}|{a[18]}|{a[9]}|{a[0]}|    |{m[72]}|{m[63]}|{m[54]}|{m[45]}|{m[36]}|{m[27]}|{m[18]}|{m[9]}|{m[0]}|    |{b[72]}|{b[63]}|{b[54]}|{b[45]}|{b[36]}|{b[27]}|{b[18]}|{b[9]}|{b[0]}|    |{c[72]}|{c[63]}|{c[54]}|{c[45]}|{c[36]}|{c[27]}|{c[18]}|{c[9]}|{c[0]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[73]}|{a[64]}|{a[55]}|{a[46]}|{a[37]}|{a[28]}|{a[19]}|{a[10]}|{a[1]}|    |{m[73]}|{m[64]}|{m[55]}|{m[46]}|{m[37]}|{m[28]}|{m[19]}|{m[10]}|{m[1]}|    |{b[73]}|{b[64]}|{b[55]}|{b[46]}|{b[37]}|{b[28]}|{b[19]}|{b[10]}|{b[1]}|    |{c[73]}|{c[64]}|{c[55]}|{c[46]}|{c[37]}|{c[28]}|{c[19]}|{c[10]}|{c[1]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[74]}|{a[65]}|{a[56]}|{a[47]}|{a[38]}|{a[29]}|{a[20]}|{a[11]}|{a[2]}|    |{m[74]}|{m[65]}|{m[56]}|{m[47]}|{m[38]}|{m[29]}|{m[20]}|{m[11]}|{m[2]}|    |{b[74]}|{b[65]}|{b[56]}|{b[47]}|{b[38]}|{b[29]}|{b[20]}|{b[11]}|{b[2]}|    |{c[74]}|{c[65]}|{c[56]}|{c[47]}|{c[38]}|{c[29]}|{c[20]}|{c[11]}|{c[2]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[75]}|{a[66]}|{a[57]}|{a[48]}|{a[39]}|{a[30]}|{a[21]}|{a[12]}|{a[3]}|    |{m[75]}|{m[66]}|{m[57]}|{m[48]}|{m[39]}|{m[30]}|{m[21]}|{m[12]}|{m[3]}|    |{b[75]}|{b[66]}|{b[57]}|{b[48]}|{b[39]}|{b[30]}|{b[21]}|{b[12]}|{b[3]}|    |{c[75]}|{c[66]}|{c[57]}|{c[48]}|{c[39]}|{c[30]}|{c[21]}|{c[12]}|{c[3]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[76]}|{a[67]}|{a[58]}|{a[49]}|{a[40]}|{a[31]}|{a[22]}|{a[13]}|{a[4]}|    |{m[76]}|{m[67]}|{m[58]}|{m[49]}|{m[40]}|{m[31]}|{m[22]}|{m[13]}|{m[4]}|    |{b[76]}|{b[67]}|{b[58]}|{b[49]}|{b[40]}|{b[31]}|{b[22]}|{b[13]}|{b[4]}|    |{c[76]}|{c[67]}|{c[58]}|{c[49]}|{c[40]}|{c[31]}|{c[22]}|{c[13]}|{c[4]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[77]}|{a[68]}|{a[59]}|{a[50]}|{a[41]}|{a[32]}|{a[23]}|{a[14]}|{a[5]}|    |{m[77]}|{m[68]}|{m[59]}|{m[50]}|{m[41]}|{m[32]}|{m[23]}|{m[14]}|{m[5]}|    |{b[77]}|{b[68]}|{b[59]}|{b[50]}|{b[41]}|{b[32]}|{b[23]}|{b[14]}|{b[5]}|    |{c[77]}|{c[68]}|{c[59]}|{c[50]}|{c[41]}|{c[32]}|{c[23]}|{c[14]}|{c[5]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[78]}|{a[69]}|{a[60]}|{a[51]}|{a[42]}|{a[33]}|{a[24]}|{a[15]}|{a[6]}|    |{m[78]}|{m[69]}|{m[60]}|{m[51]}|{m[42]}|{m[33]}|{m[24]}|{m[15]}|{m[6]}|    |{b[78]}|{b[69]}|{b[60]}|{b[51]}|{b[42]}|{b[33]}|{b[24]}|{b[15]}|{b[6]}|    |{c[78]}|{c[69]}|{c[60]}|{c[51]}|{c[42]}|{c[33]}|{c[24]}|{c[15]}|{c[6]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[79]}|{a[70]}|{a[61]}|{a[52]}|{a[43]}|{a[34]}|{a[25]}|{a[16]}|{a[7]}|    |{m[79]}|{m[70]}|{m[61]}|{m[52]}|{m[43]}|{m[34]}|{m[25]}|{m[16]}|{m[7]}|    |{b[79]}|{b[70]}|{b[61]}|{b[52]}|{b[43]}|{b[34]}|{b[25]}|{b[16]}|{b[7]}|    |{c[79]}|{c[70]}|{c[61]}|{c[52]}|{c[43]}|{c[34]}|{c[25]}|{c[16]}|{c[7]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{a[80]}|{a[71]}|{a[62]}|{a[53]}|{a[44]}|{a[35]}|{a[26]}|{a[17]}|{a[8]}|    |{m[80]}|{m[71]}|{m[62]}|{m[53]}|{m[44]}|{m[35]}|{m[26]}|{m[17]}|{m[8]}|    |{b[80]}|{b[71]}|{b[62]}|{b[53]}|{b[44]}|{b[35]}|{b[26]}|{b[17]}|{b[8]}|    |{c[80]}|{c[71]}|{c[62]}|{c[53]}|{c[44]}|{c[35]}|{c[26]}|{c[17]}|{c[8]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+

""")

            #for dst_sq in sorted(list(dst_sq_set)):
            #    #print(f"  dst_sq:{dst_sq}")
            #    pass

        #
        # TODO 打
        #
        #   - 打は SFEN では駒種類毎に分かれている。 R, B, G, S, N, L, P
        #
        r = ['    '] * 81
        b = ['    '] * 81
        g = ['    '] * 81
        s = ['    '] * 81
        n = ['    '] * 81
        l = ['    '] * 81
        p = ['    '] * 81
        for drop in ['R', 'B', 'G', 'S', 'N', 'L', 'P']:

            if drop == 'R':
                arr = r

            elif drop == 'B':
                arr = b

            elif drop == 'G':
                arr = g

            elif drop == 'S':
                arr = s

            elif drop == 'N':
                arr = n

            elif drop == 'L':
                arr = l

            elif drop == 'P':
                arr = p

            else:
                raise ValueError(f'drop:{drop}')

            if drop == 'N':
                min_rank = 2

            elif drop in ['L', 'P']:
                min_rank = 1

            else:
                min_rank = 0

            for dst_file in range(0,9):
                for dst_rank in range(min_rank,9):
                    dst_sq = get_sq_by_x_y(
                            file=dst_file,
                            rank=dst_rank)

                    arr[dst_sq] = f"{effect_index:4}"
                    effect_index += 1

            f.write(f"""
drop:{drop}
{DebugHelper.stringify_4characters_board(arr)}

""")




        f.write(f"""
total_effect:{effect_index}

no pro + pro
+---+---+---+---+---+---+---+---+---+
│{subtotal_effect[72]:3}|{subtotal_effect[63]:3}|{subtotal_effect[54]:3}|{subtotal_effect[45]:3}|{subtotal_effect[36]:3}|{subtotal_effect[27]:3}|{subtotal_effect[18]:3}|{subtotal_effect[9]:3}|{subtotal_effect[0]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[73]:3}|{subtotal_effect[64]:3}|{subtotal_effect[55]:3}|{subtotal_effect[46]:3}|{subtotal_effect[37]:3}|{subtotal_effect[28]:3}|{subtotal_effect[19]:3}|{subtotal_effect[10]:3}|{subtotal_effect[1]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[74]:3}|{subtotal_effect[65]:3}|{subtotal_effect[56]:3}|{subtotal_effect[47]:3}|{subtotal_effect[38]:3}|{subtotal_effect[29]:3}|{subtotal_effect[20]:3}|{subtotal_effect[11]:3}|{subtotal_effect[2]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[75]:3}|{subtotal_effect[66]:3}|{subtotal_effect[57]:3}|{subtotal_effect[48]:3}|{subtotal_effect[39]:3}|{subtotal_effect[30]:3}|{subtotal_effect[21]:3}|{subtotal_effect[12]:3}|{subtotal_effect[3]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[76]:3}|{subtotal_effect[67]:3}|{subtotal_effect[58]:3}|{subtotal_effect[49]:3}|{subtotal_effect[40]:3}|{subtotal_effect[31]:3}|{subtotal_effect[22]:3}|{subtotal_effect[13]:3}|{subtotal_effect[4]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[77]:3}|{subtotal_effect[68]:3}|{subtotal_effect[59]:3}|{subtotal_effect[50]:3}|{subtotal_effect[41]:3}|{subtotal_effect[32]:3}|{subtotal_effect[23]:3}|{subtotal_effect[14]:3}|{subtotal_effect[5]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[78]:3}|{subtotal_effect[69]:3}|{subtotal_effect[60]:3}|{subtotal_effect[51]:3}|{subtotal_effect[42]:3}|{subtotal_effect[33]:3}|{subtotal_effect[24]:3}|{subtotal_effect[15]:3}|{subtotal_effect[6]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[79]:3}|{subtotal_effect[70]:3}|{subtotal_effect[61]:3}|{subtotal_effect[52]:3}|{subtotal_effect[43]:3}|{subtotal_effect[34]:3}|{subtotal_effect[25]:3}|{subtotal_effect[16]:3}|{subtotal_effect[7]:3}|
+---+---+---+---+---+---+---+---+---+
|{subtotal_effect[80]:3}|{subtotal_effect[71]:3}|{subtotal_effect[62]:3}|{subtotal_effect[53]:3}|{subtotal_effect[44]:3}|{subtotal_effect[35]:3}|{subtotal_effect[26]:3}|{subtotal_effect[17]:3}|{subtotal_effect[8]:3}|
+---+---+---+---+---+---+---+---+---+

""")

# TODO 後手
