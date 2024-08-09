from v_a65_0_misc.sub_usi import SubUsi


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


    def get_serial_number_size():
        """玉の指し手の数

        Returns
        -------
        - int
            盤面全体使用の場合 544。
            右辺のみ使用の場合 305。
        """
        #return 544
        return 305


    @classmethod
    def get_srcsq_to_dstsq_blackright_index_dictionary_tuple(clazz):
        """元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します。
        初回アクセス時はテーブル生成に時間がかかります

        玉に打は無いので、 srcsq です。 srcloc ではありません

        Returns
        -------
        (clazz._src_to_dst_index_dictionary,
         clazz._index_to_src_dst_dictionary)
        """

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

            # 順方向
            clazz._src_to_dst_index_dictionary = dict()
            # 逆方向
            clazz._index_to_src_dst_dictionary = dict()

            effect_serial_index = 0

            #
            # 元マス・先マスを渡して、インデックスを返す関数
            #
            #   （先手視点、右辺のみ使用）
            #
            for src_file in range(0,5):
                for src_rank in range(0,9):
                    # 移動元マス番号
                    srcsq = SubUsi.file_rank_to_sq(
                            file=src_file,
                            rank=src_rank)

                    dstsq_to_index_dictionary = dict()
                    clazz._src_to_dst_index_dictionary[srcsq] = dstsq_to_index_dictionary

                    # 利きのマスの集合
                    dstsq_set = set()

                    #
                    # 絶対マス番号を作成
                    #

                    # 右上
                    dst_file = src_file + right_file
                    dst_rank = src_rank + top_rank
                    if 0 <= dst_file and 0 <= dst_rank:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 右
                    dst_file = src_file + right_file
                    dst_rank = src_rank
                    if 0 <= dst_file:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 右下
                    dst_file = src_file + right_file
                    dst_rank = src_rank + bottom_rank
                    if 0 <= dst_file and dst_rank < 9:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 上
                    dst_file = src_file
                    dst_rank = src_rank + top_rank
                    if 0 <= dst_rank:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 下
                    dst_file = src_file
                    dst_rank = src_rank + bottom_rank
                    if dst_rank < 9:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 左上
                    dst_file = src_file + left_file
                    dst_rank = src_rank + top_rank
                    if dst_file < 9 and 0 <= dst_rank:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 左
                    dst_file = src_file + left_file
                    dst_rank = src_rank
                    if dst_file < 9:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    # 左下
                    dst_file = src_file + left_file
                    dst_rank = src_rank + bottom_rank
                    if dst_file < 9 and dst_rank < 9:
                        dstsq_set.add(SubUsi.file_rank_to_sq(
                                file=dst_file,
                                rank=dst_rank))

                    #
                    # マス番号を昇順に並べ替える
                    #
                    dstsq_list = sorted(list(dstsq_set))

                    #
                    # インデックスに対して、元位置・先位置を振っていく
                    #
                    for dstsq in dstsq_list:
                        #                        print(f"""[evaluation k move > get srcsq to dstsq index dictionary tuple]
                        #    [元マス・先マスの関係に対して、インデックスを振っていく]  srcsq:{srcsq}  dstsq:{dstsq}  effect_serial_index:{effect_serial_index}
                        #    [インデックスに対して、元マス・先マスを振っていく     ]  effect_serial_index:{effect_serial_index}  srcsq:{srcsq}  dstsq:{dstsq}
                        #""")

                        dstsq_to_index_dictionary[dstsq] = effect_serial_index
                        clazz._index_to_src_dst_dictionary[effect_serial_index] = (srcsq, dstsq)

                        effect_serial_index += 1


        return (clazz._src_to_dst_index_dictionary, clazz._index_to_src_dst_dictionary)


    #get_index_of_k_move
    #get_index_by_k_move
    @staticmethod
    def get_blackright_index_by_k_move(
            k_blackright_move_obj):
        """玉の指し手を指定すると、玉の指し手のインデックスを返す。

        Parameters
        ----------
        k_blackright_move_obj : Move
            玉の指し手（先手視点、右辺使用）

        Returns
        -------
            - 玉の指し手のインデックス
        """

        # assert
        if SubUsi.is_drop_by_srcloc(k_blackright_move_obj.srcloc):
            raise ValueError(f"[evaluation k move > get index by k move] 玉の指し手で打なのはおかしい。 k_blackright_move_obj.srcloc_u:{SubUsi.srcloc_to_code(k_blackright_move_obj.srcloc)}  k_blackright_move_obj:{k_blackright_move_obj.dump()}")

        k_srcsq = SubUsi.srcloc_to_sq(k_blackright_move_obj.srcloc)
        k_dstsq = k_blackright_move_obj.dstsq

        # 玉は成らない

        # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
        (srcsq_to_dstsq_index_dictionary, _) = EvaluationKMove.get_srcsq_to_dstsq_blackright_index_dictionary_tuple()

        #
        # unwrap
        #
        try:
            # 移動元マス番号を渡して、辞書を取得
            dstsq_to_index_dictionary = srcsq_to_dstsq_index_dictionary[k_srcsq]

        except KeyError as ex:
            # k_srcsq error. k_blackright_move_obj.as_usi:S*3b  rotated:False  k_srcsq:None  src_masu:None  ex:None
            print(f"[evaluation k move > get index by k move]  k_srcsq error. k_blackright_move_obj.as_usi:{k_blackright_move_obj.as_usi}  k_srcsq:{k_srcsq}  src_masu:{SubUsi.sq_to_jsa(k_srcsq)}  k_blackright_move_obj:{k_blackright_move_obj.dump()}  k_dstsq:{k_dstsq}  ex:{ex}")
            raise

        #
        # unwrap
        #
        try:
            # 移動先マス番号を渡して、玉の着手のインデックスを取得
            # FIXME Rotate してるとき、配列に無ければエラーになる
            k_index = dstsq_to_index_dictionary[k_dstsq]

        except KeyError as ex:
            # k_blackright_move_obj.as_usi:5a5b  k_srcsq:36  dstsq:37
            # k_blackright_move_obj.as_usi:5a4b  is_rotate:True  k_srcsq:44  dstsq:52  src_masu:59  dst_masu:68  ex:28
            # k_blackright_move_obj.as_usi:6g4e  rotated:True  k_srcsq:29  k_dstsq:49  src_masu:43  dst_masu:65  ex:49
            # k_blackright_move_obj.as_usi:8i6g  rotated:True  len(dstsq_to_index_dictionary):5  k_src_masu:21  k_dst_masu:43  k_srcsq:9  k_dstsq:29  ex:29
            # [evaluation k move > get index by k move]  k_dstsq error. k_blackright_move_obj.as_usi:2h6h  rotated:True  len(dstsq_to_index_dictionary):8  k_src_masu:82  k_dst_masu:42  k_srcsq:64  k_dstsq:28  ex:28
            print(f"[evaluation k move > get index by k move]  k_dstsq error. k_blackright_move_obj.as_usi:{k_blackright_move_obj.as_usi}  len(dstsq_to_index_dictionary):{len(dstsq_to_index_dictionary)}  k_src_masu:{SubUsi.sq_to_jsa(k_srcsq)}  k_dst_masu:{SubUsi.sq_to_jsa(k_dstsq)}  k_srcsq:{k_srcsq}  k_dstsq:{k_dstsq}  ex:{ex}")

            # ダンプ
            i = 0
            for k_dstsq, k_index in dstsq_to_index_dictionary.items():
                print(f"[evaluation k move > get index by k move]  ({i:2})  k_dstsq:{k_dstsq}  k_dst_masu:{SubUsi.sq_to_jsa(k_dstsq)}  k_index:{k_index}")
                i += 1

            raise

        # assert
        if EvaluationKMove.get_serial_number_size() <= k_index:
            raise ValueError(f"k_index:{k_index} out of range {EvaluationKMove.get_serial_number_size()}")

        return k_index


    @staticmethod
    def destructure_srcsq_dstsq_by_k_index(
            k_index):
        """Ｋインデックス分解

        Parameter
        ---------
        k_index : int
            玉の指し手のインデックス

        Returns
        -------
        - srcsq : int
            移動元マスの番号
        - dstsq : int
            移動先マスの番号
        """
        # マスの通し番号を渡すと、元マスと移動先マスを返す入れ子の辞書を返します
        (_, index_to_srcsq_dstsq_dictionary) = EvaluationKMove.get_srcsq_to_dstsq_blackright_index_dictionary_tuple()

        (srcsq, dstsq) = index_to_srcsq_dstsq_dictionary[k_index]

        return (srcsq, dstsq)
