# python v_a51_0_test.py
from     v_a51_0_eval.k import EvaluationKMove
from     v_a51_0_misc.lib import BoardHelper
from     v_a51_0_misc.debug import DebugHelper


def test_k():
    # 元マスと移動先マスを渡すと、マスの通し番号を返す入れ子の辞書を返します
    (src_to_dst_index_dictionary, index_to_src_dst_dictionary) = EvaluationKMove.get_src_sq_to_dst_sq_index_dictionary_tuple()

    with open("test_eval_k.log", 'w', encoding="utf-8") as f:

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


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    line = input('test name?')

    if line == 'k':
        test_k()

    else:
        print("please input test name 'k', ...")
