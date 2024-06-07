# ビット操作
# python v_a46_0_bit_ope.py
import datetime


class BitOpe():
    """ビット操作"""


    @staticmethod
    def stand_at(
            byte_value,
            left_shift):
        """指定の桁のフラグを立てる

        Parameters
        ----------
        byte_value : int
            元の値
        left_shift : int
            一の位から数えて何桁目のビットを立てるか？

        Returns
        -------
        byte_value
        """
        return byte_value | (0b1 << left_shift)


    @staticmethod
    def sit_at(
            byte_value,
            left_shift):
        """指定の桁のフラグを下ろす

        Parameters
        ----------
        byte_value : int
            元の値
        left_shift : int
            一の位から数えて何桁目のビットを下ろすか？

        Returns
        -------
        byte_value
        """
        return byte_value & (0b1111_1111 - (0b1 << left_shift))


    @staticmethod
    def get_bit_at(
            byte_value,
            right_shift):
        """指定の桁のフラグを下ろす

        Parameters
        ----------
        byte_value : int
            元の値
        right_shift : int
            一の位から数えて何桁目のビットを下ろすか？

        Returns
        -------
        byte_value
        """
        return (byte_value >> right_shift) % 2


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

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
