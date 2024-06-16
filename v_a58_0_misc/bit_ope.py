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
