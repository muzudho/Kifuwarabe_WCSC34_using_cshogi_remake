class DebugPlan():
    """デバッグ計画"""

    _create_k_and_p_legal_moves = False
    _select_fo_move_u_and_policy_dictionary_no1 = False
    _select_fo_move_u_and_policy_dictionary_no2 = False
    _select_fo_move_u_and_policy_dictionary_no3 = True
    _select_fo_move_u_and_policy_dictionary_no4 = False
    _select_fo_move_u_and_policy_dictionary_no5 = False
    _select_fo_move_u_and_policy_dictionary = False
    _select_good_f_move_u_set_power = False


    @classmethod
    def create_k_and_p_legal_moves(clazz):
        return clazz._create_k_and_p_legal_moves


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no1(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no1


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no2(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no2


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no3(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no3


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no4(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no4


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no5(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no5


    @classmethod
    def select_fo_move_u_and_policy_dictionary(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary


    @classmethod
    def select_good_f_move_u_set_power(clazz):
        return clazz._select_good_f_move_u_set_power
