from v_a54_0_misc.lib import MoveSourceLocation, MoveDestinationLocation, Move, BoardHelper
from v_a54_0_misc.usi import Usi


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

    _srcsq_to_dst_sq_to_index_for_npsi_dictionary = None
    """先手成らず（no promote）　通しインデックス（serial index）"""

    _srcsq_to_dst_sq_to_index_for_psi_dictionary = None
    """先手成り（promote）　通しインデックス（serial index）"""

    _srcdrop_to_dst_sq_index = None
    """先手持ち駒 to （移動先 to 通し番号）"""

    _index_to_srcloc_dst_sq_promotion_dictionary = None
    """通しインデックスを渡すと、移動元、移動先、成りか、を返す辞書"""


    @classmethod
    def get_src_lists_to_dst_sq_index_dictionary_tuple(clazz):

        # 未生成なら生成（重い処理は１回だけ）
        if clazz._srcsq_to_dst_sq_to_index_for_npsi_dictionary == None:
            # 先手成らず（no promote）　通しインデックス（serial index）
            clazz._srcsq_to_dst_sq_to_index_for_npsi_dictionary = dict()

            # 先手成り（promote）　通しインデックス（serial index）
            clazz._srcsq_to_dst_sq_to_index_for_psi_dictionary = dict()

            # 持ち駒 to （移動先 to 通し番号）
            clazz._srcdrop_to_dst_sq_index = dict()

            # 通しインデックスを渡すと、移動元、移動先、成りか、を返す辞書
            clazz._index_to_srcloc_dst_sq_promotion_dictionary = dict()

            # 通しのインデックス
            effect_index = 0

            # 範囲外チェックを行いたいので、ループカウンタ―は sq ではなく file と rank の２重ループにする
            for src_file in range(0,9):
                for src_rank in range(0,9):
                    srcsq = BoardHelper.get_sq_by_file_rank(
                            file=src_file,
                            rank=src_rank)

                    dst_sq_to_index_for_npsi_dictionary = dict()
                    dst_sq_to_index_for_b_dictionary = dict()

                    clazz._srcsq_to_dst_sq_to_index_for_npsi_dictionary[srcsq] = dst_sq_to_index_for_npsi_dictionary
                    clazz._srcsq_to_dst_sq_to_index_for_psi_dictionary[srcsq] = dst_sq_to_index_for_b_dictionary

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

                    #
                    # マス番号を昇順に並べ替える
                    #
                    no_pro_dst_sq_list = sorted(list(no_pro_dst_sq_set))
                    pro_dst_sq_list = sorted(list(pro_dst_sq_set))

                    for dst_sq in no_pro_dst_sq_list:
                        dst_sq_to_index_for_npsi_dictionary[dst_sq] = effect_index
                        clazz._index_to_srcloc_dst_sq_promotion_dictionary[effect_index] = (srcsq, dst_sq, False)
                        effect_index += 1

                    for dst_sq in pro_dst_sq_list:
                        dst_sq_to_index_for_b_dictionary[dst_sq] = effect_index
                        clazz._index_to_srcloc_dst_sq_promotion_dictionary[effect_index] = (srcsq, dst_sq, True)
                        effect_index += 1


            for drop in ['R*', 'B*', 'G*', 'S*', 'N*', 'L*', 'P*']:

                #
                # 移動先 to 通し番号
                #
                dst_sq_to_index = dict()

                clazz._srcdrop_to_dst_sq_index[Usi.code_to_srcloc(drop)] = dst_sq_to_index

                if drop == 'N*':
                    min_rank = 2

                elif drop in ['L*', 'P*']:
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
                        clazz._index_to_srcloc_dst_sq_promotion_dictionary[effect_index] = (drop, dst_sq, False)
                        effect_index += 1

        return (clazz._srcsq_to_dst_sq_to_index_for_npsi_dictionary,
                clazz._srcsq_to_dst_sq_to_index_for_psi_dictionary,
                clazz._srcdrop_to_dst_sq_index,
                clazz._index_to_srcloc_dst_sq_promotion_dictionary)


    def get_serial_number_size():
        """兵の指し手の数

        Returns
        -------
        - int
        """
        return 3813


    @staticmethod
    def get_index_by_p_move(
            p_move_obj,
            is_rotate):
        """兵の指し手を指定すると、兵の指し手のインデックスを返す。

        Parameters
        ----------
        p_move_obj : Move
            兵の指し手
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
            - 兵の指し手のインデックス
        """

        if is_rotate:
            p_srcsq_or_none = p_move_obj.src_location.rot_sq
            p_dst_sq = p_move_obj.dst_location.rot_sq
        else:
            p_srcsq_or_none = p_move_obj.src_location.sq
            p_dst_sq = p_move_obj.dst_location.sq

        # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
        (srcsq_to_dst_sq_to_index_for_npsi_dictionary,
         srcsq_to_dst_sq_to_index_for_psi_dictionary,
         srcdrop_to_dst_sq_index,
         index_to_srcloc_dst_sq_promotion_dictionary) = EvaluationPMove.get_src_lists_to_dst_sq_index_dictionary_tuple()


        # 打か。打に成りはありません。したがって None にはなりません
        if p_move_obj.src_location.rank_th is None:
            try:
                dst_sq_to_index_dictionary = srcdrop_to_dst_sq_index[p_move_obj.src_location.srcloc]

            except KeyError as ex:
                print(f"p_move_obj.as_usi:{p_move_obj.as_usi}  P src:{Usi.srcloc_to_code(p_move_obj.src_location.srcloc)}  rotated:{is_rotate}  p_src_masu:{BoardHelper.sq_to_jsa(p_srcsq_or_none)}  成:{p_move_obj.promoted}  ex:{ex}")
                raise

            try:
                p_index = dst_sq_to_index_dictionary[p_dst_sq]

            except KeyError as ex:
                print(f"p_move_obj.as_usi:{p_move_obj.as_usi}  P src:{Usi.srcloc_to_code(p_move_obj.src_location.srcloc)}  rotated:{is_rotate}  p_src_masu:{BoardHelper.sq_to_jsa(p_srcsq_or_none)}  成:{p_move_obj.promoted}  p_dst_masu:{BoardHelper.sq_to_jsa(p_dst_sq)}  ex:{ex}")
                raise

        # 成りか。成りに打は有りません
        elif p_move_obj.promoted:
            try:
                dst_sq_to_index_dictionary = srcsq_to_dst_sq_to_index_for_psi_dictionary[p_srcsq_or_none]

            except KeyError as ex:
                print(f"p_move_obj.as_usi:{p_move_obj.as_usi}  P src:{Usi.srcloc_to_code(p_move_obj.src_location.srcloc)}  rotated:{is_rotate}  p_src_masu:{BoardHelper.sq_to_jsa(p_srcsq_or_none)}  成:{p_move_obj.promoted}  ex:{ex}")
                raise

            try:
                p_index = dst_sq_to_index_dictionary[p_dst_sq]

            except KeyError as ex:
                print(f"p_move_obj.as_usi:{p_move_obj.as_usi}  P src:{Usi.srcloc_to_code(p_move_obj.src_location.srcloc)}  rotated:{is_rotate}  p_src_masu:{BoardHelper.sq_to_jsa(p_srcsq_or_none)}  成:{p_move_obj.promoted}  p_dst_masu:{BoardHelper.sq_to_jsa(p_dst_sq)}  ex:{ex}")
                raise

        # 成らずだ
        else:
            try:
                dst_sq_to_index_dictionary = srcsq_to_dst_sq_to_index_for_npsi_dictionary[p_srcsq_or_none]

            except KeyError as ex:
                print(f"p_move_obj.as_usi:{p_move_obj.as_usi}  P src:{Usi.srcloc_to_code(p_move_obj.src_location.srcloc)}  rotated:{is_rotate}  p_src_masu:{BoardHelper.sq_to_jsa(p_srcsq_or_none)}  成:{p_move_obj.promoted}  ex:{ex}")
                raise

            try:
                p_index = dst_sq_to_index_dictionary[p_dst_sq]

            except KeyError as ex:
                print(f"p_move_obj.as_usi:{p_move_obj.as_usi}  P src:{Usi.srcloc_to_code(p_move_obj.src_location.srcloc)}  rotated:{is_rotate}  p_src_masu:{BoardHelper.sq_to_jsa(p_srcsq_or_none)}  成:{p_move_obj.promoted}  p_dst_masu:{BoardHelper.sq_to_jsa(p_dst_sq)}  ex:{ex}")
                raise

        # assert
        if EvaluationPMove.get_serial_number_size() <= p_index:
            raise ValueError(f"p_index:{p_index} out of range {EvaluationPMove.get_serial_number_size()}")

        return p_index


    @staticmethod
    def destructure_p_index(
            p_index,
            is_rotate):
        """Ｐインデックス分解

        Parameter
        ---------
        p_index : int
            兵の指し手のインデックス
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        - p_move_obj : Move
            兵の指し手
        """

        # マスの通し番号を渡すと、元マスと移動先マスを返す入れ子の辞書を返します
        (srcsq_to_dst_sq_to_index_for_npsi_dictionary,
         srcsq_to_dst_sq_to_index_for_psi_dictionary,
         srcdrop_to_dst_sq_index,
         index_to_srcloc_dst_sq_promotion_dictionary) = EvaluationPMove.get_src_lists_to_dst_sq_index_dictionary_tuple()

        (srcloc,
         dst_sq,
         promoted) = index_to_srcloc_dst_sq_promotion_dictionary[p_index]

        p_move_obj = Move.from_src_dst_pro(
                src_location=MoveSourceLocation.from_srcloc(
                        srcloc=srcloc),
                dst_location=MoveDestinationLocation.from_sq(
                        sq=dst_sq),
                promoted=promoted)

        if is_rotate:
            # TODO ここでオブジェクトを生成しなくて済む方法はないか？
            p_move_obj = Move.from_src_dst_pro(
                    src_location=p_move_obj.src_location.rotate(),
                    dst_location=p_move_obj.dst_location.rotate(),
                    promoted=promoted)

        return p_move_obj
