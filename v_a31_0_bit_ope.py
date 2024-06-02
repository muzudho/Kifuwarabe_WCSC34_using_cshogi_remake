# ビット操作
# python v_a31_0_bit_ope.py
import datetime


class BitOpe():
    """ビット操作"""


    @staticmethod
    def stand_at(
            byte_value,
            figure):
        """指定の桁を立てる

        Parameters
        ----------
        byte_value : int
            元の値
        figure : int
            一の位から数えて何桁目のビットを立てるか？

        Returns
        -------
        byte_value
        """
        return byte_value | (0b1 << figure)



########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    byte_value = BitOpe.stand_at(0b0000_0001, 2)
    expected_value = 0b0000_0101
    print(f"[{datetime.datetime.now()}] 0b0000_0001 <<< 2 ----> byte_value:0b{byte_value:08b}")
    if byte_value != expected_value:
        raise ValueError(f"actual:{byte_value}  expected:{expected_value}")

    byte_value = BitOpe.stand_at(0b0000_1000, 3)
    expected_value = 0b0000_1000
    print(f"[{datetime.datetime.now()}] 0b0000_1000 <<< 3 ----> byte_value:0b{byte_value:08b}")
    if byte_value != expected_value:
        raise ValueError(f"actual:{byte_value}  expected:{expected_value}")
