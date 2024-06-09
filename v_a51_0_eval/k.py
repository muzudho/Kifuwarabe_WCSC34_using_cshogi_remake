from v_a51_0_misc.lib import Move, BoardHelper


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

    _src_to_dst_index_dictionary = None
    """元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書"""

    _index_to_src_dst_dictionary = None
    """マスの通し番号を渡すと、元マスと移動先マスを返す入れ子の辞書"""


    @classmethod
    def get_src_sq_to_dst_sq_index_dictionary_tuple(clazz):
        """元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します。
        初回アクセス時はテーブル生成に時間がかかります"""

        # 未生成なら生成（重い処理は１回だけ）
        if clazz._src_to_dst_index_dictionary == None:
            # 右
            right_file = - 1
            # 左
            left_file = 1
            # 上
            top_rank = - 1
            # 下
            bottom_rank = 1

            clazz._src_to_dst_index_dictionary = dict()
            clazz._index_to_src_dst_dictionary = dict()

            effect_serial_index = 0

            #
            # 利きのマスの集合を作成
            #
            for src_sq in range(0,81):

                dst_to_index_dictionary = dict()
                clazz._src_to_dst_index_dictionary[src_sq] = dst_to_index_dictionary

                # 利きのマスの集合
                dst_sq_set = set()

                # 元マスの座標
                (src_file,
                src_rank) = BoardHelper.get_file_rank_by_sq(src_sq)

                #
                # 絶対マス番号を作成
                #

                # 右上
                dst_file = src_file + right_file
                dst_rank = src_rank + top_rank
                if 0 <= dst_file and 0 <= dst_rank:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 右
                dst_file = src_file + right_file
                dst_rank = src_rank
                if 0 <= dst_file:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 右下
                dst_file = src_file + right_file
                dst_rank = src_rank + bottom_rank
                if 0 <= dst_file and dst_rank < 9:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 上
                dst_file = src_file
                dst_rank = src_rank + top_rank
                if 0 <= dst_rank:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 下
                dst_file = src_file
                dst_rank = src_rank + bottom_rank
                if dst_rank < 9:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 左上
                dst_file = src_file + left_file
                dst_rank = src_rank + top_rank
                if dst_file < 9 and 0 <= dst_rank:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 左
                dst_file = src_file + left_file
                dst_rank = src_rank
                if dst_file < 9:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                # 左下
                dst_file = src_file + left_file
                dst_rank = src_rank + bottom_rank
                if dst_file < 9 and dst_rank < 9:
                    dst_sq_set.add(BoardHelper.get_sq_by_file_rank(
                            file=dst_file,
                            rank=dst_rank))

                #
                # マス番号を昇順に並べ替える
                #
                dst_sq_list = sorted(list(dst_sq_set))

                #
                # 左表の利きのマスに、通し番号を振っていく
                #
                for dst_sq in dst_sq_list:
                    #print(f"[昇順] dst_sq={dst_sq}")

                    dst_to_index_dictionary[dst_sq] = effect_serial_index
                    clazz._index_to_src_dst_dictionary[effect_serial_index] = (src_sq, dst_sq)

                    effect_serial_index += 1


        return (clazz._src_to_dst_index_dictionary, clazz._index_to_src_dst_dictionary)


    def get_serial_number_size():
        """玉の指し手の数

        Returns
        -------
        - int
        """
        return 544


    #get_index_of_k_move
    @staticmethod
    def get_index_by_k_move(
            k_move_obj,
            is_rotate):
        """玉の指し手を指定すると、玉の指し手のインデックスを返す。

        Parameters
        ----------
        k_move_obj : Move
            玉の指し手
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
            - 玉の指し手のインデックス
        """

        if is_rotate:
            k_src_sq_or_none = k_move_obj.rot_src_sq_or_none
            k_dst_sq = k_move_obj.rot_dst_sq
        else:
            k_src_sq_or_none = k_move_obj.src_sq_or_none
            k_dst_sq = k_move_obj.dst_sq

        # 玉は成らない

        # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
        (src_to_dst_index_dictionary, _) = EvaluationKMove.get_src_sq_to_dst_sq_index_dictionary_tuple()

        try:
            # 移動元マス番号
            #
            #   - TODO 評価値テーブルに打は作ってるか？ k_src_sq_or_none は None になってるから k_src_drop_or_none がほしい？
            #
            dst_to_index_dictionary = src_to_dst_index_dictionary[k_src_sq_or_none]

        except KeyError as ex:
            print(f"k_move_obj.as_usi:{k_move_obj.as_usi}  rotated:{is_rotate}  k_src_sq:{k_src_sq_or_none}  src_masu:{BoardHelper.sq_to_jsa(k_src_sq_or_none)}  ex:{ex}")
            raise

        try:
            # 移動元マス番号
            #
            #   - 打はありません。したがって None にはなりません
            #
            k_index = dst_to_index_dictionary[k_dst_sq]

        except KeyError as ex:
            # k_move_obj.as_usi:5a5b  src_sq:36  dst_sq:37
            # k_move_obj.as_usi:5a4b  is_rotate:True  src_sq:44  dst_sq:52  src_masu:59  dst_masu:68  ex:28
            print(f"k_move_obj.as_usi:{k_move_obj.as_usi}  rotated:{is_rotate}  k_src_sq:{k_src_sq_or_none}  k_dst_sq:{k_dst_sq}  src_masu:{BoardHelper.sq_to_jsa(k_src_sq_or_none)}  dst_masu:{BoardHelper.sq_to_jsa(k_dst_sq)}  ex:{ex}")
            raise

        # assert
        if EvaluationKMove.get_serial_number_size() <= k_index:
            raise ValueError(f"k_index:{k_index} out of range {EvaluationKMove.get_serial_number_size()}")

        return k_index


    @staticmethod
    def destructure_k_index(
            k_index,
            is_rotate):
        """Ｋインデックス分解

        Parameter
        ---------
        k_index : int
            玉の指し手のインデックス
        is_rotate : bool
            後手なら真。指し手を１８０°回転させます

        Returns
        -------
        - k_move_obj : Move
            玉の指し手
        """

        # マスの通し番号を渡すと、元マスと移動先マスを返す入れ子の辞書を返します
        (_, index_to_src_dst_dictionary) = EvaluationKMove.get_src_sq_to_dst_sq_index_dictionary_tuple()

        (src_sq, dst_sq) = index_to_src_dst_dictionary[k_index]

        k_move_obj = Move.from_src_dst_pro(
                src_sq=src_sq,
                dst_sq=dst_sq,
                # 玉に成りはありません
                promoted=False)

        if is_rotate:
            k_move_obj = Move.from_src_dst_pro(
                    src_sq=k_move_obj.rot_src_sq_or_none,
                    dst_sq=k_move_obj.rot_dst_sq,
                    # 玉に成りはありません
                    promoted=False)

        return k_move_obj
