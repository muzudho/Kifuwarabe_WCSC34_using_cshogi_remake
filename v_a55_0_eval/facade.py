from decimal import Decimal, ROUND_HALF_UP


class EvaluationFacade():
    """評価値のファサード"""


    @staticmethod
    def round_half_up(real):
        """小数点以下第１位を四捨五入します

        real : number
            実数
        """
        return Decimal(str(real)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)


    @staticmethod
    def get_max_number_of_less_than_50_percent(
            total):
        """ＫＬとＫＱ（または、ＰＬとＰＱ）の関係の有りのものの数が５割未満の内、最大の整数

        総数が０なら、答えは０
        総数が１なら、答えは０
        総数が２なら、答えは０
        総数が３なら、答えは１
        総数が４なら、答えは１
        総数が５なら、答えは２

        (1)   単純に kl_kq_total // 2 - 1 とすると、 kl_kq_total が３のときに答えが０になってしまう。
              そこで総数の半分は四捨五入しておく
        (2)   総数が０のとき、答えはー１になってしまうので、最低の値は０にしておく

        Parameters
        ----------
        total : int
            総数
        """

        # (1)
        max_number_of_less_than_50_percent = EvaluationFacade.round_half_up(total / 2) - 1

        # (2)
        if max_number_of_less_than_50_percent < 0:
            max_number_of_less_than_50_percent = 0

        return max_number_of_less_than_50_percent
