import cshogi
import datetime

# python v_a51_0_test.py
from     v_a51_0_eval.k import EvaluationKMove
from     v_a51_0_eval.kk import EvaluationKkTable
from     v_a51_0_eval.p import EvaluationPMove
from     v_a51_0_eval.pk import EvaluationPkTable
from     v_a51_0_misc.bit_ope import BitOpe
from     v_a51_0_misc.lib import Turn, MoveSourceLocation, MoveDestinationLocation, Move, BoardHelper
from     v_a51_0_misc.debug import DebugHelper


def test_k():
    # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
    (src_to_dst_index_dictionary, index_to_src_dst_dictionary) = EvaluationKMove.get_src_sq_to_dst_sq_index_dictionary_tuple()

    base_name = "test_eval_k.log"
    print(f"please read `{base_name}` file")

    with open(base_name, 'w', encoding="utf-8") as f:

        #
        #
        # １マスが３桁のテーブルを２つ並べる
        #
        #

        #
        # 元マス・先マス to インデックス
        #
        for src_sq in range(0,81):
            dst_to_index_dictionary = src_to_dst_index_dictionary[src_sq]

            #   - １マスが３桁の文字列の表
            #   - 元マス
            label_table_for_serial_index = ['   '] * 81
            label_table_for_src_dst = ['   '] * 81

            label_table_for_serial_index[src_sq] = 'you'
            label_table_for_src_dst[src_sq] = 'you'

            for dst_sq, serial_index in dst_to_index_dictionary.items():
                label_table_for_serial_index[dst_sq] = f'{serial_index:3}'
                label_table_for_src_dst[dst_sq] = f'{dst_sq:3}'

            # 表示
            f.write(f"""src_masu:{BoardHelper.sq_to_jsa(src_sq):2}
src と dst                              通しインデックス
{DebugHelper.stringify_double_3characters_boards(label_table_for_src_dst, label_table_for_serial_index)}
""")

        #
        # インデックス to 元マス・先マス
        #

        previous_src_sq = -1

        for serial_index in range(0, EvaluationKMove.get_serial_number_size()):
            (src_sq, dst_sq) = index_to_src_dst_dictionary[serial_index]

            print(f"(src_masu:{BoardHelper.sq_to_jsa(src_sq):2}, dst_masu:{BoardHelper.sq_to_jsa(dst_sq):2}) = dictionary[ serial_index:{serial_index:3} ]")

            if previous_src_sq != src_sq:

                if previous_src_sq != -1:
                    # 表示
                    f.write(f"""src_masu:{BoardHelper.sq_to_jsa(src_sq):2}
通しインデックス                           src と dst
{DebugHelper.stringify_double_3characters_boards(label_table_for_serial_index, label_table_for_src_dst)}
""")


                #   - １マスが３桁の文字列の表
                #   - 元マス
                label_table_for_src_dst = ['   '] * 81
                label_table_for_src_dst[src_sq] = 'you'

                label_table_for_serial_index = ['   '] * 81
                label_table_for_serial_index[src_sq] = 'you'

            label_table_for_src_dst[dst_sq] = f'{dst_sq:3}'
            label_table_for_serial_index[dst_sq] = f'{serial_index:3}'

            previous_src_sq = src_sq


def test_kk():
    k_move_obj_expected = Move.from_usi('5i5h')
    l_move_obj_expected = Move.from_usi('5a5b')
    k_turn = cshogi.BLACK

    kk_index = EvaluationKkTable.get_index_of_kk_table(
            k_move_obj=k_move_obj_expected,
            l_move_obj=l_move_obj_expected,
            k_turn=k_turn)

    (k_move_obj_actual,
     l_move_obj_actual) = EvaluationKkTable.destructure_kl_index(
            kl_index=kk_index,
            k_turn=k_turn)

    if k_move_obj_expected.as_usi != k_move_obj_actual.as_usi:
        raise ValueError(f"not match. k_turn:{Turn.to_string(k_turn)} K expected:`{k_move_obj_expected.as_usi}`  actual:`{k_move_obj_actual.as_usi}`")

    if l_move_obj_expected.as_usi != l_move_obj_actual.as_usi:
        raise ValueError(f"not match. k_turn:{Turn.to_string(k_turn)} L expected:`{l_move_obj_expected.as_usi}`  actual:`{l_move_obj_actual.as_usi}`")


def test_p():
    #
    # 後手の歩を９段目に突いて成る
    #
    expected_p_move_u = '3h3i+'
    expected_p_move_obj = Move.from_usi(expected_p_move_u)

    p_index = EvaluationPMove.get_index_by_p_move(
            p_move_obj=expected_p_move_obj,
            is_rotate=True)

    actual_p_move_obj = EvaluationPMove.destructure_p_index(
            p_index=p_index,
            is_rotate=True)

    if expected_p_move_obj.as_usi != actual_p_move_obj.as_usi:
        raise ValueError(f'unexpected error. move_obj expected P:`{expected_p_move_obj.as_usi}`  actual P:`{actual_p_move_obj.as_usi}`')



    #
    # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
    #
    (src_sq_to_dst_sq_to_index_for_npsi_dictionary,
     src_sq_to_dst_sq_to_index_for_psi_dictionary,
     drop_to_dst_sq_index,
     index_to_src_sq_dst_sq_promotion_dictionary) = EvaluationPMove.get_src_sq_to_dst_sq_index_dictionary_tuple()

    base_name = "test_eval_p.log"
    print(f"please read `{base_name}` file")

    with open(base_name, 'w', encoding="utf-8") as f:

        #
        #
        # １マスが４桁のテーブルを４つ並べる
        #
        #

        #
        # 元マス・先マス to インデックス
        #
        for src_sq in range(0,81):
            dst_sq_to_index_for_npsi_dictionary = src_sq_to_dst_sq_to_index_for_npsi_dictionary[src_sq]
            dst_sq_to_index_for_b_dictionary = src_sq_to_dst_sq_to_index_for_psi_dictionary[src_sq]

            # 成らない指し手（no promote）の各マス　値：通しインデックス（serial index）
            label_table_for_npsi = ["    "] * 81

            # 成る指し手（promote）の各マス　値：通しインデックス
            label_table_for_psi = ["    "] * 81

            # 成らない指し手の各マス　値：絶対マス番号（sq）
            label_table_for_npsq = ["    "] * 81

            # 成る指し手の各マス　値：絶対マス番号
            label_table_for_psq = ["    "] * 81

            label_table_for_npsi[src_sq] = " you"
            label_table_for_psi[src_sq] = " you"
            label_table_for_npsq[src_sq] = " you"
            label_table_for_psq[src_sq] = " you"

            for dst_sq, effect_index in dst_sq_to_index_for_npsi_dictionary.items():
                label_table_for_npsi[dst_sq] = f"{effect_index:4}"
                label_table_for_npsq[dst_sq] = f"{dst_sq:4}"

            for dst_sq, effect_index in dst_sq_to_index_for_b_dictionary.items():
                label_table_for_psi[dst_sq] = f"{effect_index:4}"
                label_table_for_psq[dst_sq] = f"{dst_sq:4}"


            f.write(f"""src_masu:{BoardHelper.sq_to_jsa(src_sq)}
先手成らず  通しインデックス                          先手成らず  絶対マス                                先手成り  通しインデックス                            先手成り  絶対マス
{DebugHelper.stringify_quadruple_4characters_board(
        a=label_table_for_npsi,
        b=label_table_for_npsq,
        c=label_table_for_psi,
        d=label_table_for_psq)}

""")

        # 打
        #
        #   - 打は SFEN では駒種類毎に分かれている。 R*, B*, G*, S*, N*, L*, P*
        #
        for drop in ['R*', 'B*', 'G*', 'S*', 'N*', 'L*', 'P*']:
            dst_sq_to_index_dictionary = drop_to_dst_sq_index[drop]

            label_table_for_drop = ['    '] * 81

            for dst_sq, effect_index in dst_sq_to_index_dictionary.items():
                label_table_for_drop[dst_sq] = f"{effect_index:4}"

            f.write(f"""
drop:{drop}
{DebugHelper.stringify_4characters_board(label_table_for_drop)}

""")

        # TODO 後手


def test_pk():
    # 後手
    expected_p_move_u = '3h3i+'
    expected_p_move_obj = Move.from_usi(expected_p_move_u)

    # 先手
    expected_k_move_u = '5h5i'
    expected_k_move_obj = Move.from_usi(expected_k_move_u)

    pk_index = EvaluationPkTable.get_index_of_pk_table(
            p_move_obj=expected_p_move_obj,
            k_move_obj=expected_k_move_obj,
            p_turn=cshogi.WHITE)

    (actual_p_move_obj,
     actual_k_move_obj) = EvaluationPkTable.destructure_pk_index(
            pk_index=pk_index,
            p_turn=cshogi.WHITE)

    if expected_p_move_obj.as_usi != actual_p_move_obj.as_usi or expected_k_move_obj.as_usi != actual_k_move_obj.as_usi:
        raise ValueError(f'unexpected error. move_obj expected P:`{expected_p_move_obj.as_usi}`  K:`{expected_k_move_obj.as_usi}`  actual P:`{actual_p_move_obj.as_usi}`  K:`{actual_k_move_obj.as_usi}`')


def test_bit_ope():
    init_value = 0b0000_0001
    bit_shift = 2
    expected_value = 0b0000_0101
    actual_value = BitOpe.stand_at(init_value, bit_shift)
    print(f"[{datetime.datetime.now()}] {init_value:08b} <<< {bit_shift} ----> actual_value:0b{actual_value:08b}")
    if actual_value != expected_value:
        raise ValueError(f"actual:{actual_value}  expected:{expected_value}")

    init_value = 0b0000_1000
    bit_shift = 3
    expected_value = 0b0000_1000
    actual_value = BitOpe.stand_at(init_value, bit_shift)
    print(f"[{datetime.datetime.now()}] {init_value:08b} <<< {bit_shift} ----> actual_value:0b{actual_value:08b}")
    if actual_value != expected_value:
        raise ValueError(f"actual:{actual_value}  expected:{expected_value}")

    init_value = 0b0000_0111
    bit_shift = 1
    expected_value = 0b0000_0101
    actual_value = BitOpe.sit_at(init_value, bit_shift)
    print(f"[{datetime.datetime.now()}] {init_value:08b} <<< {bit_shift} ----> actual_value:0b{actual_value:08b}")
    if actual_value != expected_value:
        raise ValueError(f"actual:{actual_value}  expected:{expected_value}")


    init_value = 0b1000_0000
    bit_shift = 7
    expected_value = 0b0000_0001
    actual_value = BitOpe.get_bit_at(init_value, bit_shift)
    print(f"[{datetime.datetime.now()}] ({init_value:08b} >>> {bit_shift}) % 2 ----> actual_value:0b{actual_value:08b}")
    if actual_value != expected_value:
        raise ValueError(f"actual:{actual_value}  expected:{expected_value}")


def test_lib():
    expected_move_u = '3h3i+'
    move_obj = Move.from_usi(expected_move_u)
    if move_obj.as_usi != expected_move_u:
        raise ValueError(f'unexpected error. move_obj expected:`{expected_move_u}`  actual:`{move_obj.as_usi}`')

    if not move_obj.promoted:
        raise ValueError(f'unexpected error. move_obj.promoted expected:True  actual:`{move_obj.promoted}`')

    move_obj = Move.from_src_dst_pro(
            src_location=MoveSourceLocation.from_sq_or_drop(
                sq=BoardHelper.jsa_to_sq(38)),
            dst_location=MoveDestinationLocation.from_sq(
                sq=BoardHelper.jsa_to_sq(39)),
            promoted=True)
    
    if move_obj.as_usi != expected_move_u:
        raise ValueError(f'unexpected error. expected:`{expected_move_u}`  actual:`{move_obj.as_usi}`')

    if not move_obj.promoted:
        raise ValueError(f'unexpected error. move_obj.promoted expected:True  actual:`{move_obj.promoted}`')


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    line = input('test name?')

    if line == 'k':
        test_k()

    elif line == 'kk':
        test_kk()

    elif line == 'p':
        test_p()

    elif line == 'pk':
        test_pk()

    elif line == 'bit_ope':
        test_bit_ope()

    elif line == 'lib':
        test_lib()

    else:
        print("please input test name 'k', ...")
