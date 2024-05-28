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
    """スクリプト実行時

    +---+---+---+---+---+---+---+---+---+
    | 22| 24| 24| 24| 24| 24| 24| 24| 22|
    +---+---+---+---+---+---+---+---+---+
    | 24| 27| 27| 27| 27| 27| 27| 27| 24|
    +---+---+---+---+---+---+---+---+---+
    | 25| 29| 31| 31| 31| 31| 31| 29| 25|
    +---+---+---+---+---+---+---+---+---+
    | 25| 29| 31| 33| 33| 33| 31| 29| 25|
    +---+---+---+---+---+---+---+---+---+
    | 25| 29| 31| 33| 35| 33| 31| 29| 25|
    +---+---+---+---+---+---+---+---+---+
    | 25| 29| 31| 33| 33| 33| 31| 29| 25|
    +---+---+---+---+---+---+---+---+---+
    | 25| 29| 31| 31| 31| 31| 31| 29| 25|
    +---+---+---+---+---+---+---+---+---+
    | 25| 29| 29| 29| 29| 29| 29| 29| 25|
    +---+---+---+---+---+---+---+---+---+
    | 23| 26| 26| 26| 26| 26| 26| 26| 23|
    +---+---+---+---+---+---+---+---+---+
       マス毎の先手成らずのSFENのパターン数
    """

    with open("test.log", 'w', encoding="utf-8") as f:

        def get_sq_by_x_y(file, rank):
            return file * 9 + rank

        total_effect = 0

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

                total_effect += subtotal_len
                subtotal_effect[src_sq] = subtotal_len

                #
                # デバッグ表示
                #

                # 成らない指し手の各マス
                l = ["    "] * 81

                # 成る指し手の各マス
                m = ["    "] * 81

                l[src_sq] = " you"
                m[src_sq] = " you"

                for dst_sq in no_pro_dst_sq_set:
                    l[dst_sq] = f"{effect_index:4}"
                    effect_index += 1

                for dst_sq in pro_dst_sq_set:
                    m[dst_sq] = f"{effect_index:4}"
                    effect_index += 1

                f.write(f"""src_sq:{src_sq}  effect:{subtotal_len} = no pro:{no_pro_len} + pro:{pro_len}
先手成らず                                         先手成り
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
│{l[72]}|{l[63]}|{l[54]}|{l[45]}|{l[36]}|{l[27]}|{l[18]}|{l[9]}|{l[0]}|    |{m[72]}|{m[63]}|{m[54]}|{m[45]}|{m[36]}|{m[27]}|{m[18]}|{m[9]}|{m[0]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[73]}|{l[64]}|{l[55]}|{l[46]}|{l[37]}|{l[28]}|{l[19]}|{l[10]}|{l[1]}|    |{m[73]}|{m[64]}|{m[55]}|{m[46]}|{m[37]}|{m[28]}|{m[19]}|{m[10]}|{m[1]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[74]}|{l[65]}|{l[56]}|{l[47]}|{l[38]}|{l[29]}|{l[20]}|{l[11]}|{l[2]}|    |{m[74]}|{m[65]}|{m[56]}|{m[47]}|{m[38]}|{m[29]}|{m[20]}|{m[11]}|{m[2]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[75]}|{l[66]}|{l[57]}|{l[48]}|{l[39]}|{l[30]}|{l[21]}|{l[12]}|{l[3]}|    |{m[75]}|{m[66]}|{m[57]}|{m[48]}|{m[39]}|{m[30]}|{m[21]}|{m[12]}|{m[3]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[76]}|{l[67]}|{l[58]}|{l[49]}|{l[40]}|{l[31]}|{l[22]}|{l[13]}|{l[4]}|    |{m[76]}|{m[67]}|{m[58]}|{m[49]}|{m[40]}|{m[31]}|{m[22]}|{m[13]}|{m[4]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[77]}|{l[68]}|{l[59]}|{l[50]}|{l[41]}|{l[32]}|{l[23]}|{l[14]}|{l[5]}|    |{m[77]}|{m[68]}|{m[59]}|{m[50]}|{m[41]}|{m[32]}|{m[23]}|{m[14]}|{m[5]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[78]}|{l[69]}|{l[60]}|{l[51]}|{l[42]}|{l[33]}|{l[24]}|{l[15]}|{l[6]}|    |{m[78]}|{m[69]}|{m[60]}|{m[51]}|{m[42]}|{m[33]}|{m[24]}|{m[15]}|{m[6]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[79]}|{l[70]}|{l[61]}|{l[52]}|{l[43]}|{l[34]}|{l[25]}|{l[16]}|{l[7]}|    |{m[79]}|{m[70]}|{m[61]}|{m[52]}|{m[43]}|{m[34]}|{m[25]}|{m[16]}|{m[7]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+
|{l[80]}|{l[71]}|{l[62]}|{l[53]}|{l[44]}|{l[35]}|{l[26]}|{l[17]}|{l[8]}|    |{m[80]}|{m[71]}|{m[62]}|{m[53]}|{m[44]}|{m[35]}|{m[26]}|{m[17]}|{m[8]}|
+----+----+----+----+----+----+----+----+----+    +----+----+----+----+----+----+----+----+----+

""")

            #for dst_sq in sorted(list(dst_sq_set)):
            #    #print(f"  dst_sq:{dst_sq}")
            #    pass

        f.write(f"""
total_effect:{total_effect}
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

# TODO 打
# TODO 後手
