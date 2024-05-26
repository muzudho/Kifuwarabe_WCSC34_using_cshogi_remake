class EvaluationKMove():
    """自玉の指し手"""

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


    @classmethod
    def get_k_index_by_relative_sq(clazz):
        """玉の指し手の相対SQを、インデックスへ変換するテーブルを取得"""
        return clazz._k_index_by_relative_sq


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
