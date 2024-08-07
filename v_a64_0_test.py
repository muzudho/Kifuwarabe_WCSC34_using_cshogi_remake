import cshogi
import datetime

# python v_a64_0_test.py
from     v_a64_0_eval.k import EvaluationKMove
from     v_a64_0_eval.kk import EvaluationKkTable
from     v_a64_0_eval.p import EvaluationPMove
from     v_a64_0_eval.pk import EvaluationPkTable
from     v_a64_0_misc.bit_ope import BitOpe
from     v_a64_0_misc.debug import DebugHelper
from     v_a64_0_misc.lib import Turn, Move
from     v_a64_0_misc.usi import Usi


def test_k():
    # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
    (srcsq_to_dstsq_index_dictionary, index_to_srcsq_dstsq_dictionary) = EvaluationKMove.get_srcsq_to_dstsq_blackright_index_dictionary_tuple()

    base_name = "test_eval_k.log"
    print(f"please read `{base_name}` file")

    with open(base_name, 'w', encoding="utf-8") as f:

        #
        #
        # １マスが３桁のテーブルを２つ並べる
        #
        #

        #
        # 元マス・先マスを渡して、インデックスを返す関数
        #
        #   （先手視点、右辺のみ使用）
        #
        f.write(f"""\
#
#  元マス・先マスを渡して、インデックスを返す関数
#
#       （先手視点、右辺使用）
#
""")

        for src_file in range(0,5):
            for src_rank in range(0,9):
                srcsq = Usi.file_rank_to_sq(
                        file=src_file,
                        rank=src_rank)

                dstsq_to_index_dictionary = srcsq_to_dstsq_index_dictionary[srcsq]

                #   - １マスが３桁の文字列の表
                #   - 元マス
                label_table_for_serial_index = ['   '] * 81
                label_table_for_src_dst = ['   '] * 81

                label_table_for_serial_index[srcsq] = 'you'
                label_table_for_src_dst[srcsq] = 'you'

                for dstsq, serial_index in dstsq_to_index_dictionary.items():
                    label_table_for_serial_index[dstsq] = f'{serial_index:3}'
                    label_table_for_src_dst[dstsq] = f'{dstsq:3}'

                # 出力
                f.write(f"""src_masu:{Usi.sq_to_jsa(srcsq):2}
通しインデックス                          src と dst
{DebugHelper.stringify_double_3characters_boards(label_table_for_serial_index, label_table_for_src_dst)}
""")


        #
        # インデックスを渡して、元マス・先マスを返す関数
        #
        #       （先手視点、右辺使用）
        #
        f.write(f"""\
#
# インデックスを渡して、元マス・先マスを返す関数
#
#       （先手視点、右辺使用）
#
""")

        def init_table():
            return (['   '] * 81,
                    ['   '] * 81)

        def flush_table(
                label_table_for_src_dst,
                label_table_for_serial_index,
                previous_srcsq):
            f.write(f"""src_masu:{Usi.sq_to_jsa(previous_srcsq):2}
通しインデックス                           src と dst
{DebugHelper.stringify_double_3characters_boards(label_table_for_serial_index, label_table_for_src_dst)}
""")
            (label_table_for_src_dst,
             label_table_for_serial_index) = init_table()

            return (label_table_for_src_dst,
                    label_table_for_serial_index)

        previous_srcsq = -1

        (label_table_for_src_dst,
         label_table_for_serial_index) = init_table()

        for serial_index in range(0, EvaluationKMove.get_serial_number_size()):
            (srcsq, dstsq) = index_to_srcsq_dstsq_dictionary[serial_index]

            # 初回
            if previous_srcsq == -1:
                label_table_for_src_dst[srcsq] = 'you'
                label_table_for_serial_index[srcsq] = 'you'

            # srcsq が変わったら、 srcsq が変わる前のものをフラッシュ
            elif previous_srcsq != srcsq:
                print(f"flush  previous_srcmasu:{Usi.sq_to_jsa(previous_srcsq)}  srcmasu:{Usi.sq_to_jsa(srcsq)}")
                (label_table_for_src_dst,
                 label_table_for_serial_index) = flush_table(
                        label_table_for_src_dst,
                        label_table_for_serial_index,
                        previous_srcsq)

                label_table_for_src_dst[srcsq] = 'you'
                label_table_for_serial_index[srcsq] = 'you'

            print(f"(src_masu:{Usi.sq_to_jsa(srcsq):2}, dst_masu:{Usi.sq_to_jsa(dstsq):2}) = dictionary[ serial_index:{serial_index:3} ]")

            # 対象マスを追加
            label_table_for_src_dst[dstsq] = f'{dstsq:3}'
            label_table_for_serial_index[dstsq] = f'{serial_index:3}'

            previous_srcsq = srcsq

        # 残りがある想定で、フラッシュ
        print(f"flush_rest  previous_srcmasu:{Usi.sq_to_jsa(previous_srcsq)}  srcmasu:{Usi.sq_to_jsa(srcsq)}")
        (label_table_for_src_dst,
            label_table_for_serial_index) = flush_table(
                label_table_for_src_dst,
                label_table_for_serial_index,
                previous_srcsq)


def test_kk():
    k_strict_move_obj_expected = Move.from_usi('5i5h')
    l_strict_move_obj_expected = Move.from_usi('5a5b')
    k_turn = cshogi.BLACK

    k_blackright_move_obj = Move.from_move_obj(
            f_strict_move_obj=k_strict_move_obj_expected,
            shall_white_to_black=False,
            use_only_right_side=True)
    l_blackright_move_obj = Move.from_move_obj(
            f_strict_move_obj=l_strict_move_obj_expected,
            shall_white_to_black=True,
            use_only_right_side=True)

    k_blackright_l_blackright_index = EvaluationKkTable.get_blackright_k_blackright_l_index(
            k_blackright_move_obj=k_blackright_move_obj,
            l_blackright_move_obj=l_blackright_move_obj)

    (blackright_k_move_obj_actual,
     blackright_l_move_obj_actual) = EvaluationKkTable.build_k_blackright_l_blackright_moves_by_kl_index(
            k_blackright_l_blackright_index=k_blackright_l_blackright_index)

    if k_strict_move_obj_expected.as_usi != blackright_k_move_obj_actual.as_usi:
        raise ValueError(f"not match. k_turn:{Turn.to_string(k_turn)} K expected:`{k_strict_move_obj_expected.as_usi}`  actual:`{blackright_k_move_obj_actual.as_usi}`")

    if l_strict_move_obj_expected.as_usi != blackright_l_move_obj_actual.as_usi:
        raise ValueError(f"not match. k_turn:{Turn.to_string(k_turn)} L expected:`{l_strict_move_obj_expected.as_usi}`  actual:`{blackright_l_move_obj_actual.as_usi}`")


def test_p():
    def test_p_3h3ip():
        """後手の歩を９段目に突いて成る"""
        # 本来の指し手
        strict_p_move_u = '3h3i+'
        strict_p_move_obj = Move.from_usi(strict_p_move_u)

        # 期待する（先手視点、右辺使用）の指し手
        expected_p_blackright_move_u = '3b3a+'
        expected_p_blackright_move_obj = Move.from_usi(expected_p_blackright_move_u)

        # （先手視点、右辺使用）に合わせる
        p_blackright_move_obj = Move.from_move_obj(
                f_strict_move_obj=strict_p_move_obj,
                shall_white_to_black=True,
                use_only_right_side=True)

        p_blackright_index = EvaluationPMove.get_blackright_index_by_p_move(
                p_blackright_move_obj=p_blackright_move_obj,
                ignore_error=True)

        if p_blackright_index == -1:
            return

        # Ｐ
        (p_blackright_srcloc,
        p_blackright_dstsq,
        p_promote) = EvaluationPMove.destructure_srcloc_dstsq_promoted_by_p_index(
                p_blackright_index=p_blackright_index)

        actual_p_blackright_move_obj = Move.from_src_dst_pro(
                srcloc=p_blackright_srcloc,
                dstsq=p_blackright_dstsq,
                promoted=p_promote,
                # 既に（先手視点、右辺使用）なので回転させません
                is_rotate=False)

        if expected_p_blackright_move_obj.as_usi != actual_p_blackright_move_obj.as_usi:
            raise ValueError(f"""unexpected error.
expected_p_blackright_move_obj:`{expected_p_blackright_move_obj.as_usi}`
p_blackright_move_obj_u       :`{p_blackright_move_obj.as_usi}`
actual_p_blackright_move_obj  :`{actual_p_blackright_move_obj.as_usi}`
""")

    test_p_3h3ip()


    #
    # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
    #
    (srcsq_to_dstsq_to_blackright_index_for_npsi_dictionary,
     srcsq_to_dstsq_to_blackright_index_for_psi_dictionary,
     srcdrop_to_dstsq_blackright_index,
     index_to_srcsq_dstsq_promotion_dictionary) = EvaluationPMove.get_src_lists_to_dstsq_blackright_index_dictionary_tuple()

    base_name = "test_eval_p.log"
    print(f"please read `{base_name}` file")

    with open(base_name, 'w', encoding="utf-8") as f:

        #
        #
        # １マスが４桁のテーブルを４つ並べる
        #
        #

        #
        # 元マス・先マスを渡して、インデックスを返す関数
        #
        #   （先手視点、右辺のみ使用）
        #
        for src_file in range(0,5):
            for src_rank in range(0,9):
                # 移動元マス番号
                srcsq = Usi.file_rank_to_sq(
                        file=src_file,
                        rank=src_rank)

                dstsq_to_index_for_npsi_dictionary = srcsq_to_dstsq_to_blackright_index_for_npsi_dictionary[srcsq]
                dstsq_to_index_for_b_dictionary = srcsq_to_dstsq_to_blackright_index_for_psi_dictionary[srcsq]

                # 成らない指し手（no promote）の各マス　値：通しインデックス（serial index）
                label_table_for_npsi = ["    "] * 81

                # 成る指し手（promote）の各マス　値：通しインデックス
                label_table_for_psi = ["    "] * 81

                # 成らない指し手の各マス　値：絶対マス番号（sq）
                label_table_for_npsq = ["    "] * 81

                # 成る指し手の各マス　値：絶対マス番号
                label_table_for_psq = ["    "] * 81

                label_table_for_npsi[srcsq] = " you"
                label_table_for_psi[srcsq] = " you"
                label_table_for_npsq[srcsq] = " you"
                label_table_for_psq[srcsq] = " you"

                for dstsq, effect_index in dstsq_to_index_for_npsi_dictionary.items():
                    label_table_for_npsi[dstsq] = f"{effect_index:4}"
                    label_table_for_npsq[dstsq] = f"{dstsq:4}"

                for dstsq, effect_index in dstsq_to_index_for_b_dictionary.items():
                    label_table_for_psi[dstsq] = f"{effect_index:4}"
                    label_table_for_psq[dstsq] = f"{dstsq:4}"


                f.write(f"""src_masu:{Usi.sq_to_jsa(srcsq)}
先手成らず  通しインデックス                             先手成らず  絶対マス                                   先手成り  通しインデックス                               先手成り  絶対マス
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
        for drop_code in ['R*', 'B*', 'G*', 'S*', 'N*', 'L*', 'P*']:
            srcdrop = Usi.code_to_srcloc(drop_code)
            dstsq_to_index_dictionary = srcdrop_to_dstsq_blackright_index[srcdrop]

            label_table_for_drop = ['    '] * 81

            for dstsq, effect_index in dstsq_to_index_dictionary.items():
                label_table_for_drop[dstsq] = f"{effect_index:4}"

            f.write(f"""
drop_code:{drop_code}
{DebugHelper.stringify_4characters_board(label_table_for_drop)}

""")

        # TODO 後手


def test_pk():
    for data_set in [
        # 着手側の手番   # 着手   # 応手   # 着手、応手ともに先手番にひっくり返したとき
        [cshogi.BLACK, '7b7a+', '5b5a', '7b7a+', '5h5i'],
        [cshogi.WHITE, '3h3i+', '5h5i', '7b7a+', '5h5i'],
        ]:

        # 着手側の手番
        f_turn = data_set[0]

        # 着手
        input_p_strict_move_u = data_set[1]

        # 応手
        input_k_strict_move_u = data_set[2]

        # 着手
        expected_black_p_move_u = data_set[3]

        # 応手
        expected_black_k_move_u = data_set[4]

        # 先手の向きに合わせる
        input_p_black_move_obj = Move.from_move_obj(
                f_strict_move_obj=Move.from_usi(input_p_strict_move_u),
                shall_white_to_black=False)

        # 先手の向きに合わせる
        input_k_black_move_obj = Move.from_move_obj(
                f_strict_move_obj=Move.from_usi(input_k_strict_move_u),
                shall_white_to_black=True)

        # 関連
        #
        #   後手では、指し手を盤上で１８０°回転させてインデックスを取得します
        #
        p_blackright_k_blackright_index = EvaluationPkTable.get_p_blackright_k_blackright_index(
                p_blackright_move_obj=input_p_black_move_obj,
                k_blackright_move_obj=input_k_black_move_obj)

        # pi_index から、指し手オブジェクトを生成します
        #
        #   １８０°回転はさせません
        #
        (remaked_black_p_move_obj,
         remaked_black_k_move_obj) = EvaluationPkTable.build_p_blackright_k_blackright_moves_by_pk_index(
                p_blackright_k_blackright_index=p_blackright_k_blackright_index)

        # Ｐ
        if expected_black_p_move_u != remaked_black_p_move_obj.as_usi:
            raise ValueError(f"""[test pk > p] 着手は{Turn.to_string(f_turn)}  P expected:{expected_black_p_move_u:5}  remaked:{remaked_black_p_move_obj.as_usi:5}
（指し手が１８０°ひっくり返っていないように注意）
""")

        # Ｋ
        if expected_black_k_move_u != remaked_black_k_move_obj.as_usi:
            raise ValueError(f"""[test pk > k] 着手は{Turn.to_string(f_turn)}  K expected:{expected_black_k_move_u:5}  actual:{remaked_black_k_move_obj.as_usi:5}
（指し手が１８０°ひっくり返っていないように注意）
""")


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
            srcloc=Usi.jsa_to_sq(38),
            dstsq=Usi.jsa_to_sq(39),
            promoted=True)

    if move_obj.as_usi != expected_move_u:
        raise ValueError(f'unexpected error. expected:`{expected_move_u}`  actual:`{move_obj.as_usi}`')

    if not move_obj.promoted:
        raise ValueError(f'unexpected error. move_obj.promoted expected:True  actual:`{move_obj.promoted}`')


def test_move_rotate():
    # １８０°回転
    srcloc_u = "1g"
    expected_rot_srcloc_u = "9c"
    srcloc = Usi.code_to_srcloc(srcloc_u)

    actual = Usi.srcloc_to_code(srcloc)
    if srcloc_u != actual:
        raise ValueError(f"[test move rotate]  expected:{srcloc_u}  actual:{actual}")

    rot_srcloc = Usi.rotate_srcloc(srcloc)
    actual = Usi.srcloc_to_code(rot_srcloc)
    if expected_rot_srcloc_u != actual:
        raise ValueError(f"[test move rotate]  expected:{expected_rot_srcloc_u}  actual:{actual}")

    # １８０°回転
    dstsq_u = "1g"
    expected_rot_dstsq_u = "9c"
    dstsq = Usi.srcloc_to_sq(Usi.code_to_srcloc(dstsq_u))
    rot_dstsq = Usi.rotate_srcloc(dstsq)
    actual = Usi.srcloc_to_code(rot_dstsq)

    if expected_rot_dstsq_u != actual:
        raise ValueError(f"[test move rotate]  expected:{expected_rot_dstsq_u}  actual:{actual}")

    # １８０°回転
    move_u = "1g1f"
    expected_rot_move_u = "9c9d"
    move_obj = Move.from_usi(move_u)
    rot_move_u = move_obj.rotate().as_usi

    if expected_rot_move_u != rot_move_u:
        raise ValueError(f"[test move rotate]  expected:{expected_rot_move_u}  actual:{rot_move_u}")


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

    elif line == 'move_rotate':
        test_move_rotate()

    else:
        print("please input test name 'k', ...")
