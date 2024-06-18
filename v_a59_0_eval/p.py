from v_a59_0_misc.usi import Usi


class EvaluationPMove():
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

    _srcsq_to_dstsq_to_index_for_npsi_dictionary = None
    """先手成らず（no promote）　通しインデックス（serial index）"""

    _srcsq_to_dstsq_to_index_for_psi_dictionary = None
    """先手成り（promote）　通しインデックス（serial index）"""

    _srcdrop_to_dstsq_index = None
    """先手持ち駒 to （移動先 to 通し番号）"""

    _index_to_srcloc_dstsq_promotion_dictionary = None
    """通しインデックスを渡すと、移動元、移動先、成りか、を返す辞書"""


    @classmethod
    def get_src_lists_to_dstsq_index_dictionary_tuple(clazz):

        # 未生成なら生成（重い処理は１回だけ）
        if clazz._srcsq_to_dstsq_to_index_for_npsi_dictionary == None:
            # 先手成らず（no promote）　通しインデックス（serial index）
            clazz._srcsq_to_dstsq_to_index_for_npsi_dictionary = dict()

            # 先手成り（promote）　通しインデックス（serial index）
            clazz._srcsq_to_dstsq_to_index_for_psi_dictionary = dict()

            # 持ち駒 to （移動先 to 通し番号）
            clazz._srcdrop_to_dstsq_index = dict()

            # 通しインデックスを渡すと、移動元、移動先、成りか、を返す辞書
            clazz._index_to_srcloc_dstsq_promotion_dictionary = dict()

            # 通しのインデックス
            effect_index = 0

            # 範囲外チェックを行いたいので、ループカウンタ―は sq ではなく file と rank の２重ループにする
            for src_file in range(0,9):
                for src_rank in range(0,9):
                    srcsq = Usi.file_rank_to_sq(
                            file=src_file,
                            rank=src_rank)

                    dstsq_to_index_for_npsi_dictionary = dict()
                    dstsq_to_index_for_b_dictionary = dict()

                    clazz._srcsq_to_dstsq_to_index_for_npsi_dictionary[srcsq] = dstsq_to_index_for_npsi_dictionary
                    clazz._srcsq_to_dstsq_to_index_for_psi_dictionary[srcsq] = dstsq_to_index_for_b_dictionary

                    # 成らないことができる移動先
                    no_pro_dstsq_set = set()

                    # 成ることができる移動先
                    pro_dstsq_set = set()

                    #
                    # 飛車の動き
                    #

                    # 垂直
                    for delta_rank in range(1,9):
                        # 上
                        next_rank = src_rank-delta_rank
                        if 0 <= next_rank:
                            dstsq = Usi.file_rank_to_sq(
                                    file=src_file,
                                    rank=next_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                            if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                                pro_dstsq_set.add(dstsq)

                        # 下
                        next_rank = src_rank+delta_rank
                        if next_rank < 9:
                            dstsq = Usi.file_rank_to_sq(
                                    file=src_file,
                                    rank=next_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                            if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                                pro_dstsq_set.add(dstsq)

                    # 水平
                    for delta_file in range(1,9):
                        # 右
                        next_file = src_file-delta_file
                        if 0 <= next_file:
                            dstsq = Usi.file_rank_to_sq(
                                    file=next_file,
                                    rank=src_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # １段目～３段目の水平の動きなら、成ることができる
                            if 0 <= src_rank and src_rank < 3:
                                pro_dstsq_set.add(dstsq)

                        # 左
                        next_file = src_file+delta_file
                        if next_file < 9:
                            dstsq = Usi.file_rank_to_sq(
                                    file=next_file,
                                    rank=src_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # １段目～３段目の水平の動きなら、成ることができる
                            if 0 <= src_rank and src_rank < 3:
                                pro_dstsq_set.add(dstsq)

                    #
                    # 角の動き
                    #
                    for delta in range(1,9):
                        # 右上
                        next_file = src_file-delta
                        next_rank = src_rank-delta
                        if 0 <= next_file and 0 <= next_rank:
                            dstsq = Usi.file_rank_to_sq(
                                    file=next_file,
                                    rank=next_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                            if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                                pro_dstsq_set.add(dstsq)

                        # 右下
                        next_file = src_file-delta
                        next_rank = src_rank+delta
                        if 0 <= next_file and next_rank < 9:
                            dstsq = Usi.file_rank_to_sq(
                                    file=next_file,
                                    rank=next_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                            if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                                pro_dstsq_set.add(dstsq)

                        # 左上
                        next_file = src_file+delta
                        next_rank = src_rank-delta
                        if next_file < 9 and 0 <= next_rank:
                            dstsq = Usi.file_rank_to_sq(
                                    file=next_file,
                                    rank=next_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                            if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                                pro_dstsq_set.add(dstsq)

                        # 左下
                        next_file = src_file+delta
                        next_rank = src_rank+delta
                        if next_file < 9 and next_rank < 9:
                            dstsq = Usi.file_rank_to_sq(
                                    file=next_file,
                                    rank=next_rank)
                            no_pro_dstsq_set.add(dstsq)

                            # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                            if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                                pro_dstsq_set.add(dstsq)

                    #
                    # 桂馬の動き
                    #

                    # 先手右上
                    next_file = src_file-1
                    next_rank = src_rank-2
                    if 0 <= next_file and 0 <= next_rank:
                        dstsq = Usi.file_rank_to_sq(
                                file=next_file,
                                rank=next_rank)
                        no_pro_dstsq_set.add(dstsq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dstsq_set.add(dstsq)

                    # 先手左上
                    next_file = src_file+1
                    next_rank = src_rank-2
                    if next_file < 9 and 0 <= next_rank:
                        dstsq = Usi.file_rank_to_sq(
                                file=next_file,
                                rank=next_rank)
                        no_pro_dstsq_set.add(dstsq)

                        # 移動元が１段目～３段目か、移動先が１段目～３段目なら、成ることができる
                        if (0 <= src_rank and src_rank < 3) or (0 <= next_rank and next_rank < 3):
                            pro_dstsq_set.add(dstsq)

                    #
                    # マス番号を昇順に並べ替える
                    #
                    no_pro_dstsq_list = sorted(list(no_pro_dstsq_set))
                    pro_dstsq_list = sorted(list(pro_dstsq_set))

                    for dstsq in no_pro_dstsq_list:
                        dstsq_to_index_for_npsi_dictionary[dstsq] = effect_index
                        clazz._index_to_srcloc_dstsq_promotion_dictionary[effect_index] = (srcsq, dstsq, False)
                        effect_index += 1

                    for dstsq in pro_dstsq_list:
                        dstsq_to_index_for_b_dictionary[dstsq] = effect_index
                        clazz._index_to_srcloc_dstsq_promotion_dictionary[effect_index] = (srcsq, dstsq, True)
                        effect_index += 1


            for drop_str in ['R*', 'B*', 'G*', 'S*', 'N*', 'L*', 'P*']:

                #
                # 移動先 to 通し番号
                #
                dstsq_to_index = dict()

                clazz._srcdrop_to_dstsq_index[Usi.code_to_srcloc(drop_str)] = dstsq_to_index

                if drop_str == 'N*':
                    min_rank = 2

                elif drop_str in ['L*', 'P*']:
                    min_rank = 1

                else:
                    min_rank = 0


                for dst_file in range(0,9):
                    for dst_rank in range(min_rank,9):
                        dstsq = Usi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank)

                        # 格納
                        dstsq_to_index[dstsq] = effect_index
                        clazz._index_to_srcloc_dstsq_promotion_dictionary[effect_index] = (Usi.code_to_srcloc(drop_str), dstsq, False)
                        effect_index += 1

        return (clazz._srcsq_to_dstsq_to_index_for_npsi_dictionary,
                clazz._srcsq_to_dstsq_to_index_for_psi_dictionary,
                clazz._srcdrop_to_dstsq_index,
                clazz._index_to_srcloc_dstsq_promotion_dictionary)


    def get_serial_number_size():
        """兵の指し手の数

        Returns
        -------
        - int
        """
        return 3813


    #get_index_by_p_move
    @staticmethod
    def get_black_index_by_p_move(
            p_move_obj,
            shall_p_white_to_black,
            ignore_error=False):
        """兵の指し手を指定すると、兵の指し手のインデックスを返す。

        Parameters
        ----------
        p_move_obj : Move
            兵の指し手
        shall_p_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        ignore_error : bool
            エラーが起きたら例外を投げ上げずに、 -1 を返します

        Returns
        -------
            - 兵の指し手のインデックス
        """

        if shall_p_white_to_black:
            p_srcloc = Usi.rotate_srcloc(p_move_obj.srcloc)
            p_dstsq = Usi.rotate_srcloc(p_move_obj.dstsq)
        else:
            p_srcloc = p_move_obj.srcloc
            p_dstsq = p_move_obj.dstsq

        # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
        (srcsq_to_dstsq_to_index_for_npsi_dictionary,
         srcsq_to_dstsq_to_index_for_psi_dictionary,
         srcdrop_to_dstsq_index,
         index_to_srcloc_dstsq_promotion_dictionary) = EvaluationPMove.get_src_lists_to_dstsq_index_dictionary_tuple()


        # 打つ手
        if Usi.is_drop_by_srcloc(p_srcloc):
            try:
                dstsq_to_index_dictionary = srcdrop_to_dstsq_index[p_srcloc]

            except KeyError as ex:
                print(f"[evaluation p move > get index by p move > 打つ手] p_move_obj.as_usi:{p_move_obj.as_usi}  P srcloc_u:{Usi.srcloc_to_code(p_srcloc)}  shall_p_white_to_black:{shall_p_white_to_black}  p_src_masu:{Usi.srcloc_to_jsa(p_srcloc)}  成:{p_move_obj.promoted}  ex:{ex}")

                if ignore_error:
                    return -1
                
                raise

            try:
                p_index = dstsq_to_index_dictionary[p_dstsq]

            except KeyError as ex:
                print(f"[evaluation p move > get index by p move > 打つ手] p_move_obj.as_usi:{p_move_obj.as_usi}  P srcloc_u:{Usi.srcloc_to_code(p_srcloc)}  shall_p_white_to_black:{shall_p_white_to_black}  p_src_masu:{Usi.srcloc_to_jsa(p_srcloc)}  成:{p_move_obj.promoted}  p_dst_masu:{Usi.sq_to_jsa(p_dstsq)}  ex:{ex}")

                if ignore_error:
                    return -1
                
                raise

        # 成る手
        elif p_move_obj.promoted:
            p_srcsq = p_srcloc

            try:
                dstsq_to_index_dictionary = srcsq_to_dstsq_to_index_for_psi_dictionary[p_srcsq]

            except KeyError as ex:
                print(f"[evaluation p move > get index by p move > 成る手1] p_move_obj.as_usi:{p_move_obj.as_usi}  P srcloc_u:{Usi.srcloc_to_code(p_srcloc)}  shall_p_white_to_black:{shall_p_white_to_black}  p_src_masu:{Usi.srcloc_to_jsa(p_srcsq)}  成:{p_move_obj.promoted}  ex:{ex}")

                if ignore_error:
                    return -1

                raise

            try:
                p_index = dstsq_to_index_dictionary[p_dstsq]

            except KeyError as ex:

                # 9f9g+ とか、そんな操作で成ることはできない
                """
[evaluation p move > get index by p move > 成る手2]
（後手は、盤を１８０°回転する必要があるか？：False）
兵の指し手 `9f9g+` を調べていたところ、移動元マス `96` から、移動先マス `97` へ指す動作が、配列の要素に含まれていませんでした  ex:78

    p_srcmasu:96
    p_dstmasu:41  p_index: 3183
    p_dstmasu:52  p_index: 3184
    p_dstmasu:63  p_index: 3185
    p_dstmasu:91  p_index: 3186
    p_dstmasu:92  p_index: 3187
    p_dstmasu:93  p_index: 3188
                """

                # 配列Ｂのインデックス `6` （符号で言うと `7a`）は存在しない要素を指定しています。この配列Ｂは、配列Ａの 15 （符号で言うと `7b`）要素に入っていたものです。この探索は、兵の指し手 `3h3i+` を調べているところでした   ex:6
                print(f"""[evaluation p move > get index by p move > 成る手2]
（後手は、盤を１８０°回転する必要があるか？：{shall_p_white_to_black}）
兵の指し手 `{p_move_obj.as_usi}` を調べていたところ、移動元マス `{Usi.sq_to_jsa(p_srcsq)}` から、移動先マス `{Usi.sq_to_jsa(p_dstsq)}` へ指す動作が、配列の要素に含まれていませんでした  ex:{ex}
""")

                # debug
                print(f"    p_srcmasu:{Usi.sq_to_jsa(p_srcsq):2}")
                for p_dstsq, p_index in dstsq_to_index_dictionary.items():
                    print(f"    p_dstmasu:{Usi.sq_to_jsa(p_dstsq):2}  p_index:{p_index:5}")

                if ignore_error:
                    return -1

                raise

        # 成らない手
        else:
            p_srcsq = p_srcloc

            try:
                dstsq_to_index_dictionary = srcsq_to_dstsq_to_index_for_npsi_dictionary[p_srcsq]

            except KeyError as ex:
                print(f"[evaluation p move > get index by p move > 成らない手] p_move_obj.as_usi:{p_move_obj.as_usi}  P srcloc_u:{Usi.srcloc_to_code(p_srcloc)}  shall_p_white_to_black:{shall_p_white_to_black}  p_src_masu:{Usi.srcloc_to_jsa(p_srcsq)}  成:{p_move_obj.promoted}  ex:{ex}")

                if ignore_error:
                    return -1

                raise

            try:
                p_index = dstsq_to_index_dictionary[p_dstsq]

            except KeyError as ex:
                # FIXME 先手の桂馬の動きを、なぜかひっくり返して後手の桂馬の動きにしていることがある
                # FIXME 後手の桂馬の動きをしようとしている。評価値テーブルには後手の動きは入っていないので、回転させる必要がある
                # 配列Ｂのインデックス `26` （符号で言うと `9c`）は存在しない要素を指定しています。この配列Ｂは、配列Ａの 7 （符号で言うと `8a`）要素に入っていたものです。この探索は、兵の指し手 `2i1g` を調べているところでした  ex:26
                # 配列Ｂのインデックス `59` （符号で言うと `7f`）は存在しない要素を指定しています。この配列Ｂは、配列Ａの 66 （符号で言うと `8d`）要素に入っていたものです。この探索は、兵の指し手 `8d7f` を調べているところでした  shall_p_white_to_black:False  ex:59
                print(f"""[evaluation p move > get index by p move > 成らない手]
（後手は、盤を１８０°回転する必要があるか？：{shall_p_white_to_black}）
兵の指し手 `{p_move_obj.as_usi}` を調べていたところ、移動元マス `{Usi.sq_to_jsa(p_srcsq)}` から、移動先マス `{Usi.sq_to_jsa(p_dstsq)}` ）へ指す動作が、配列の要素に含まれていませんでした  ex:{ex}""")

                # debug
                print(f"    p_srcmasu:{Usi.sq_to_jsa(p_srcsq):2}")
                for p_dstsq, p_index in dstsq_to_index_dictionary.items():
                    print(f"    p_dstmasu:{Usi.sq_to_jsa(p_dstsq):2}  p_index:{p_index:5}")

                if ignore_error:
                    return -1

                raise

        # assert
        if EvaluationPMove.get_serial_number_size() <= p_index:
            raise ValueError(f"p_index:{p_index} out of range {EvaluationPMove.get_serial_number_size()}")

        return p_index


    @staticmethod
    def destructure_srcloc_dstsq_promoted_by_p_index(
            p_index):
        """Ｐインデックス分解

        Parameter
        ---------
        p_index : int
            兵の指し手のインデックス

        Returns
        -------
        - srcloc : int
            移動元マス番号、または打つ駒種類の番号
        - dstsq : int
            移動先マス番号
        - promoted : bool
            成る手か？
        """
        # マスの通し番号を渡すと、元マスと移動先マスを返す入れ子の辞書を返します
        (srcsq_to_dstsq_to_index_for_npsi_dictionary,
         srcsq_to_dstsq_to_index_for_psi_dictionary,
         srcdrop_to_dstsq_index,
         index_to_srcloc_dstsq_promotion_dictionary) = EvaluationPMove.get_src_lists_to_dstsq_index_dictionary_tuple()

        (srcloc,
         dstsq,
         promoted) = index_to_srcloc_dstsq_promotion_dictionary[p_index]

        # assert: srcloc は数だ
        temp = srcloc + 1

        return (srcloc,
                dstsq,
                promoted)
