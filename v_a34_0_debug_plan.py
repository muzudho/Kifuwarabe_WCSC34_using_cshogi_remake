class DebugPlan():
    """デバッグ計画"""

    _create_k_and_p_legal_moves = False
    _select_fo_move_u_and_policy_dictionary_no1 = True
    _select_fo_move_u_and_policy_dictionary = False


    @classmethod
    def create_k_and_p_legal_moves(clazz):
        return clazz._create_k_and_p_legal_moves


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no1(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no1


    @classmethod
    def select_fo_move_u_and_policy_dictionary(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary
