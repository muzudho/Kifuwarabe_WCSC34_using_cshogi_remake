from decimal import Decimal, ROUND_HALF_UP

from v_a63_0_debug_plan import DebugPlan


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


    def get_tier_th(
            positive_of_relation,
            total_of_relation,
            tier_resolution,
            is_debug=False):
        """好手悪手の階位を求めます。
        最高が 1位、最低が tier_resolution 位

        positive_of_relation : int
            挙手数
        total_of_relation : int
            議席数
        tier_resolution : int
            階位の階数
        is_debug : bool
            デバッグモードか？
        """

        # ポリシー率
        #
        #   例えば　挙手数　０、議席数１０なら、ポリシー率は 0.0
        #   例えば　挙手数　１、議席数１０なら、ポリシー率は 0.1
        #   例えば　挙手数１０、議席数１０なら、ポリシー率は 1.0
        #
        if 0 < total_of_relation:
            policy_rate = positive_of_relation / total_of_relation
        else:
            policy_rate = 1.0

        # 補ポリシー率
        #
        #   例えば　ポリシー率が 0.0 なら、補ポリシー率は 1.0
        #   例えば　ポリシー率が 0.1 なら、補ポリシー率は 0.9
        #   例えば　ポリシー率が 1.0 なら、補ポリシー率は 0.0
        #
        policy_rate_rev = 1 - policy_rate

        # 解像度
        #
        #   例えば tier_resolution が 10 なら、解像度は 0.1
        #
        ranking_resolution_threshold = 1 / tier_resolution

        # 階位
        #
        #
        #   例えば　補ポリシー率が 1.0、解像度が 0.1 なら、階位は 10
        #   例えば　補ポリシー率が 0.9、解像度が 0.1 なら、階位は  9
        #   例えば　補ポリシー率が 0.1、解像度が 0.1 なら、階位は  1
        #
        ranking_th = int(policy_rate_rev // ranking_resolution_threshold)

        # デバッグ表示
        if is_debug and DebugPlan.select_ranked_f_strict_move_u_set_facade:
            #move_u:{move_u}
            print(f"[choice best move]  ranking_th:{ranking_th}  positive_of_relation:{positive_of_relation}  total_of_relation:{total_of_relation}  policy_rate:{policy_rate}  policy_rate_rev:{policy_rate_rev}  ranking_resolution_threshold:{ranking_resolution_threshold}")

        return (ranking_th, policy_rate)
