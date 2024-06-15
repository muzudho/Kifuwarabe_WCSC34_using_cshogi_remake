class DebugPlan():
    """デバッグ計画"""

    #####
    # C #
    #####
    _create_k_and_p_legal_moves = False

    #####
    # E #
    #####
    evaluation_edit_weaken = False
    evaluation_edit_strengthen = False

    #####
    # G #
    #####
    get_number_of_connection_for_kl_kq = False
    get_number_of_connection_for_pl_pq = False

    #####
    # L #
    #####

    # 学習の進捗を表示するものだから、表示したい
    _learn_at_odd_log_progress = True

    # 学習の進捗を表示するものだから、表示したい
    _learn_at_even_log_progress = True

    #####
    # S #
    #####
    select_ranked_f_move_u_set_facade = False

    _select_fo_move_u_and_policy_dictionary_no1 = False

    _select_fo_move_u_and_policy_dictionary_no2_kl = False
    _select_fo_move_u_and_policy_dictionary_no2_kq = False
    _select_fo_move_u_and_policy_dictionary_no2_pl = False
    _select_fo_move_u_and_policy_dictionary_no2_pq = False

    _select_fo_move_u_and_policy_dictionary_no3_kl = False
    _select_fo_move_u_and_policy_dictionary_no3_kq = False
    _select_fo_move_u_and_policy_dictionary_no3_pl = False
    _select_fo_move_u_and_policy_dictionary_no3_pq = False

    _select_fo_move_u_and_policy_dictionary_no4 = False
    _select_fo_move_u_and_policy_dictionary_no5 = False


    @classmethod
    def create_k_and_p_legal_moves(clazz):
        return clazz._create_k_and_p_legal_moves


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no1(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no1


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no2_kl(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no2_kl


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no2_kq(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no2_kq


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no2_pl(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no2_pl


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no2_pq(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no2_pq


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no3_kl(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no3_kl


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no3_kq(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no3_kq


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no3_pl(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no3_pl


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no3_pq(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no3_pq


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no4(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no4


    @classmethod
    def select_fo_move_u_and_policy_dictionary_no5(clazz):
        return clazz._select_fo_move_u_and_policy_dictionary_no5


    @classmethod
    def learn_at_odd_log_progress(clazz):
        return clazz._learn_at_odd_log_progress


    @classmethod
    def learn_at_even_log_progress(clazz):
        return clazz._learn_at_even_log_progress
