# ビット操作
# python v_a31_0_bit_ope.py
import datetime


class BitOpe():
    """ビット操作"""


    @staticmethod
    def stand_at(
            byte_value,
            figure):
        """指定の桁のフラグを立てる

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


    @staticmethod
    def sit_at(
            byte_value,
            figure):
        """指定の桁のフラグを下ろす

        Parameters
        ----------
        byte_value : int
            元の値
        figure : int
            一の位から数えて何桁目のビットを下ろすか？

        Returns
        -------
        byte_value
        """
        return byte_value & (0b1111_1111 - (0b1 << figure))



########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    init_value = 0b0000_0001
    figure = 2
    expected_value = 0b0000_0101
    byte_value = BitOpe.stand_at(init_value, figure)
    print(f"[{datetime.datetime.now()}] {init_value:08b} <<< {figure} ----> byte_value:0b{byte_value:08b}")
    if byte_value != expected_value:
        raise ValueError(f"actual:{byte_value}  expected:{expected_value}")

    init_value = 0b0000_1000
    figure = 3
    expected_value = 0b0000_1000
    byte_value = BitOpe.stand_at(init_value, figure)
    print(f"[{datetime.datetime.now()}] {init_value:08b} <<< {figure} ----> byte_value:0b{byte_value:08b}")
    if byte_value != expected_value:
        raise ValueError(f"actual:{byte_value}  expected:{expected_value}")

    init_value = 0b0000_0111
    figure = 1
    expected_value = 0b0000_0101
    byte_value = BitOpe.sit_at(init_value, figure)
    print(f"[{datetime.datetime.now()}] {init_value:08b} <<< {figure} ----> byte_value:0b{byte_value:08b}")
    if byte_value != expected_value:
        raise ValueError(f"actual:{byte_value}  expected:{expected_value}")
