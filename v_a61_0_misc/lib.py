import cshogi
import datetime

from v_a61_0_misc.bit_ope import BitOpe
from v_a61_0_misc.usi import Usi
from v_a61_0_debug_plan import DebugPlan


class FileName():
    """ファイル名"""


    def __init__(
            self,
            file_stem,
            file_extension):
        """初期化

        Parameters
        ----------
        file_stem : str
            ファイル名の幹
        file_extension : str
            ドット付きファイル拡張子
        """
        self._file_stem = file_stem
        self._file_extension = file_extension


    @property
    def file_stem(self):
        """ファイル名の幹"""
        return self._file_stem


    @property
    def file_extension(self):
        """ドット付きファイル拡張子"""
        return self._file_extension


    @property
    def base_name(self):
        """ベース名"""
        return f'{self._file_stem}{self._file_extension}'


    @property
    def temporary_base_name(self):
        """一時的なベース名"""
        return f'{self._file_stem}_temp{self._file_extension}'



class Turn():
    """手番"""


    _turn_string = {
        None: 'None',
        cshogi.BLACK: 'black',
        cshogi.WHITE: 'white',
    }


    _turn_symbol = {
        None: 'None',
        cshogi.BLACK: '▲',
        cshogi.WHITE: '▽',
    }


    _turn_kanji = {
        None: 'None',
        cshogi.BLACK: '先',
        cshogi.WHITE: '後',
    }


    _str_to_int = {
        'None': None,
        'black': cshogi.BLACK,
        'white': cshogi.WHITE,
    }


    _flip = {
        None: None,
        cshogi.BLACK: cshogi.WHITE,
        cshogi.WHITE: cshogi.BLACK,
    }


    @staticmethod
    def to_index(turn):
        """先手を0、後手を1とするのを明示する

        turn をそのまま使っても同じ
        """
        if turn == cshogi.BLACK:
            return 0
        elif turn == cshogi.WHITE:
            return 1
        else:
            raise ValueError(f"unexpected turn:{turn}")


    @classmethod
    def to_string(clazz, turn):
        return clazz._turn_string[turn]


    @classmethod
    def to_symbol(clazz, turn):
        return clazz._turn_symbol[turn]


    @classmethod
    def to_kanji(clazz, turn):
        return clazz._turn_kanji[turn]


    @classmethod
    def str_to_int(clazz, turn_str):
        return clazz._str_to_int[turn_str]


    @classmethod
    def flip(clazz, turn):
        return clazz._flip[turn]


class Move():
    """指し手"""


    _file_th_str_to_num = {
        '1':1,
        '2':2,
        '3':3,
        '4':4,
        '5':5,
        '6':6,
        '7':7,
        '8':8,
        '9':9,
    }
    """1 から始まる列番号の数字を整数に変換"""


    _file_th_num_to_str = {
        1:'1',
        2:'2',
        3:'3',
        4:'4',
        5:'5',
        6:'6',
        7:'7',
        8:'8',
        9:'9',
    }
    """1 から始まる列番号の整数を文字に変換"""


    _rank_str_to_th_num = {
        'a':1,
        'b':2,
        'c':3,
        'd':4,
        'e':5,
        'f':6,
        'g':7,
        'h':8,
        'i':9,
    }
    """段英字を 1 から始まる整数に変換"""


    _src_dst_str_1st_figure_to_sq = {
        'R' : 81,   # 'R*' 移動元の打 72+9=81
        'B' : 82,   # 'B*'
        'G' : 83,   # 'G*'
        'S' : 84,   # 'S*'
        'N' : 85,   # 'N*'
        'L' : 86,   # 'L*'
        'P' : 87,   # 'P*'
        '1' : 0,
        '2' : 9,
        '3' : 18,
        '4' : 27,
        '5' : 36,
        '6' : 45,
        '7' : 54,
        '8' : 63,
        '9' : 72,
    }
    """移動元の１文字目をマス番号へ変換"""


    _src_dst_str_2nd_figure_to_index = {
        '*': 0,     # 移動元の打
        'a': 0,
        'b': 1,
        'c': 2,
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7,
        'i': 8,
    }
    """移動元、移動先の２文字目をインデックスへ変換"""


    @staticmethod
    def from_usi(move_as_usi):
        """生成

        Parameters
        ----------
        move_as_usi : str
            "7g7f" や "3d3c+"、 "R*5e" のような文字列を想定。 "resign" のような文字列は想定外
        """

        # 移動元番号
        srcloc = Usi.code_to_srcloc(
                code=move_as_usi[0: 2])

        # 移動先オブジェクト生成
        dstsq = Usi.srcloc_to_sq(Usi.code_to_srcloc(
                code=move_as_usi[2: 4]))

        #
        # 成ったか？
        #
        #   - ５文字なら成りだろう
        #
        promoted = 4 < len(move_as_usi)

        return Move(
                srcloc=srcloc,
                dstsq=dstsq,
                promoted=promoted)


    @staticmethod
    def from_src_dst_pro(
            srcloc,
            dstsq,
            promoted,
            is_rotate=False,
            use_only_right_side=False):
        """初期化

        Parameters
        ----------
        srcloc : int
            移動元番号
        dstsq : int
            移動先マス番号
        promoted : bool
            成ったか？
        is_rotate : bool
            盤を１８０°回転させたときの指し手にするか？
        use_only_right_side : bool
            移動元マスを盤の１筋～５筋だけ使うように指し手を揃えるか？
        """
        if is_rotate:
            srcloc = Usi.rotate_srcloc(srcloc)
            dstsq = Usi.rotate_srcloc(dstsq)

        if use_only_right_side:
            (file_th, rank_th) = Usi.srcloc_to_file_th_rank_th(srcloc)

            if 5 < file_th:
                srcloc = Usi.flip_srcloc(srcloc)
                dstsq = Usi.flip_srcloc(dstsq)

        return Move(
                srcloc=srcloc,
                dstsq=dstsq,
                promoted=promoted)


    def from_move_obj(
            strict_move_obj,
            shall_white_to_black,
            use_only_right_side=False):
        """変形

        Parameters
        ----------
        strict_move_obj : Move
            指し手
        shall_white_to_black : bool
            評価値テーブルは先手用しかないので、後手なら指し手を１８０°回転させて先手の向きに合わせるか？
        use_only_right_side : bool
            移動元マスを盤の１筋～５筋だけ使うように指し手を揃えるか？
        """
        if shall_white_to_black or use_only_right_side:
            return Move.from_src_dst_pro(
                    srcloc=strict_move_obj.srcloc,
                    dstsq=strict_move_obj.dstsq,
                    promoted=strict_move_obj.promoted,
                    is_rotate=shall_white_to_black,
                    use_only_right_side=use_only_right_side)

        return strict_move_obj


    def __init__(
            self,
            srcloc,
            dstsq,
            promoted):
        """初期化

        Parameters
        ----------
        srcloc : int
            移動元番号
        dstsq : int
            移動先マス番号
        promoted : bool
            成ったか？
        """
        self._srcloc = srcloc
        self._dstsq = dstsq
        self._promoted = promoted


    def dump(self):
        return f"as_usi:{self.as_usi}  srcloc_jsa:{Usi.srcloc_to_jsa(self._srcloc)}  dstmasu:{Usi.srcloc_to_jsa(self._dstsq)}  promoted:{self._promoted}"


    @property
    def srcloc(self):
        """移動元番号"""
        return self._srcloc


    @property
    def dstsq(self):
        """移動先マス番号"""
        return self._dstsq


    @property
    def promoted(self):
        """成ったか？"""
        return self._promoted


    @property
    def as_usi(self):
        """USI形式の指し手の符号。
        "7g7f" や "3d3c+"、 "R*5e" のような文字列を想定。 "resign" のような文字列は想定外
        """
        return f"{Usi.srcloc_to_code(self.srcloc)}{Usi.sq_to_code(self.dstsq)}{Usi.promotion_to_code(self.promoted)}"


    def rotate(self):
        """盤を１８０°回転させたときの指し手を返します"""
        rot_srcloc = Usi.rotate_srcloc(self.srcloc)
        rot_dstsq = Usi.rotate_srcloc(self._dstsq)

        return Move(
                srcloc=rot_srcloc,
                dstsq=rot_dstsq,
                promoted=self.promoted)


class MoveHelper():
    """指し手ヘルパー"""


    @staticmethod
    def is_king(
            k_sq,
            move_obj):
        """自玉か？"""

        # 自玉の指し手か？（打なら None なので False）
        #print(f"［自玉の指し手か？］ move_u: {move_obj.as_usi}, srcloc:{move_obj.srcloc}, k_sq: {k_sq}, board.turn: {board.turn}")
        if Usi.is_drop_by_srcloc(move_obj.srcloc):
            return False

        return move_obj.srcloc == k_sq


class BoardHelper():
    """局面のヘルパー"""


    @staticmethod
    def get_king_square(board):
        """自玉のマス番号

        Parameters
        ----------
        board : Board
            局面

        Returns
        -------
        k_sq : int
            自玉のマス番号
        """
        return board.king_square(board.turn)


    @staticmethod
    def create_counter_move_u_set(
            board,
            strict_move_obj):
        """応手の一覧を作成

        Parameters
        ----------
        board : Board
            局面
        strict_move_obj : Move
            着手

        Returns
        -------
        - l_strict_move_u_set
        - q_strict_move_u_set
        """

        #
        # 相手が指せる手の集合
        # -----------------
        #
        #   ヌルムーブをしたいが、 `board.push_pass()` が機能しなかったので、合法手を全部指してみることにする
        #

        # 敵玉（Lord）の指し手の集合
        l_strict_move_u_set = set()
        # 敵玉を除く敵軍の指し手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_strict_move_u_set = set()

        # １手指す
        board.push_usi(strict_move_obj.as_usi)

        # 敵玉（L; Lord）の位置を調べる
        l_sq = BoardHelper.get_king_square(board)

        for strict_counter_move_id in board.legal_moves:
            strict_counter_move_u = cshogi.move_to_usi(strict_counter_move_id)
            strict_counter_move_obj = Move.from_usi(strict_counter_move_u)

            # 敵玉の指し手か？
            if MoveHelper.is_king(l_sq, strict_counter_move_obj):
                l_strict_move_u_set.add(strict_counter_move_u)
            # 敵玉を除く敵軍の指し手
            else:
                q_strict_move_u_set.add(strict_counter_move_u)

        # １手戻す
        board.pop()

        return (l_strict_move_u_set, q_strict_move_u_set)


    @staticmethod
    def get_position_command(
            board):
        """現局面から position コマンドを取得

        Parameters
        ----------
        board : csohgi.Board
            現局面
        """
        # 本譜の指し手を覚えておく
        principal_history = board.history

        # 開始局面を知りたいので、全部巻き戻す
        while 1 < board.move_number:
            board.pop()

        # 開始局面
        start_position = board.sfen()

        if start_position == 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL':
            position_command = "position startpos moves"
        else:
            position_command = f"position sfen {start_position} moves"

        # 開始局面を取得したので、巻き戻したのを全部戻す
        for move_id in principal_history:
            board.push(move_id)
            position_command += f" {cshogi.move_to_usi(move_id)}"

        return position_command

class MoveListHelper():
    """指し手のリストのヘルパー"""


    @staticmethod
    def create_k_and_p_legal_moves(
            legal_moves,
            board,
            is_debug=False):
        """自玉の合法手のリストと、自軍の玉以外の合法手のリストを作成

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        is_debug : bool
            デバッグモードか？

        Returns
        -------
        - 自玉の合法手のリスト : USI符号表記
        - 自軍の玉以外の合法手のリスト : USI符号表記
        """

        k_sq = BoardHelper.get_king_square(board)

        if is_debug and DebugPlan.create_k_and_p_legal_moves():
            print(f"[{datetime.datetime.now()}] [create k and p legal moves]  k_masu:{Usi.sq_to_jsa(k_sq)}")

        # USIプロトコルでの符号表記に変換
        k_moves_u = []
        p_moves_u = []

        for move in legal_moves:
            move_u = cshogi.move_to_usi(move)

            if is_debug and DebugPlan.create_k_and_p_legal_moves():
                print(f"[{datetime.datetime.now()}] [create k and p legal moves]  move_u:{move_u}")

            # 指し手の移動元を取得
            move_obj = Move.from_usi(move_u)

            # 自玉の指し手か？
            if MoveHelper.is_king(k_sq, move_obj):
                k_moves_u.append(move_u)

            else:
                p_moves_u.append(move_u)

        return (k_moves_u, p_moves_u)


class PolicyHelper():
    """ポリシー値のヘルパー"""


    def get_permille_from_relation_number(
            relation_number,
            counter_move_size):
        """着手と応手の関連を、千分率の整数のポリシー値に変換

        Parameters
        ----------
        relation_number : int
            着手と応手の関連の数
        counter_move_size : int
            着手に対する応手の数

        Returns
        -------
        - policy_permille : int
            千分率の整数のポリシー値
        """
        return relation_number * 1000 // counter_move_size


########################################
# データ構造関連
########################################

class EvalutionMmTable():
    """評価値ＭＭテーブル"""


    def __init__(
            self,
            file_name_obj,
            table_as_array,
            is_file_modified):
        """初期化

        Parameters
        ----------
        file_name_obj : FileName
            ファイル名オブジェクト
        table_as_array : []
            評価値テーブルの配列
        is_file_modified : bool
            このテーブルが変更されて、保存されていなければ真
        """

        self._file_name_obj = file_name_obj
        self._table_as_array = table_as_array
        self._is_file_modified = is_file_modified


    @property
    def file_name_obj(self):
        """ファイル名オブジェクト"""
        return self._file_name_obj


    @property
    def table_as_array(self):
        """評価値テーブルの配列"""
        return self._table_as_array


    @property
    def is_file_modified(self):
        """このテーブルが変更されて、保存されていなければ真"""
        return self._is_file_modified


    def get_bit_by_index(
            self,
            index,
            is_debug=False):
        """インデックスを受け取ってビット値を返します

        Parameters
        ----------
        index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """

        # ビット・インデックスを、バイトとビットに変換
        bit_index = index % 8
        byte_index = index // 8

        # bit_index == 0 のとき、左端のビットを取得する（左端から右へ７ビット移動して、右端のビットを取得する）（ビッグエンディアン）
        #
        #   1xxx xxxx
        #
        # bit_index == 7 のとき、右端のビットを取得する（右端から右へ０ビット移動して、右端のビットを取得する）
        #
        #   xxxx xxx1
        #
        # そこで、 (7 - bit_index) ビットずらせばよい
        #
        right_shift = 7 - bit_index

        byte_value = self._table_as_array[byte_index]

        bit_value = BitOpe.get_bit_at(byte_value, right_shift)

        # デバッグ
        if is_debug:
            # format `:08b` - 0 supply, 8 left shift, binary
            print(f"[evalution mm table > get_bit_by_index]  index:{index}  byte_index:{byte_index}  bit_index:{bit_index}  right_shift:{right_shift}  byte_value:0x{self._table_as_array[byte_index]:08b}  bit_value:{bit_value}")

            # assert
            if bit_value < 0 or 1 < bit_value:
                raise ValueError(f"bit must be 0 or 1. bit:{bit_value}")

        return bit_value


    def set_bit_by_index(
            self,
            black_f_black_o_index,
            bit,
            is_debug=False):
        """インデックスを受け取ってビット値を設定します

        Parameters
        ----------
        black_f_black_o_index : int
            配列のインデックス。着手、応手ともに先手の視点
        bit : int
            0 か 1
        is_debug : bool
            デバッグか？

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        result_comment : str
            変更できなかった場合の説明
        """

        # ビット・インデックスを、バイトとビットに変換
        bit_index = black_f_black_o_index % 8
        byte_index = black_f_black_o_index // 8

        # bit_index == 0 のとき、右端から左へ７桁移動したところのビットを立てる（ビッグエンディアン）
        #
        #   1xxx xxxx
        #
        # bit_index == 7 のとき、右端から左へ０桁移動したところのビットを立てる
        #
        #   xxxx xxx1
        #
        # そこで、左へ (7 - bit_index) 桁移動すればよい
        #
        left_shift = 7 - bit_index

        old_byte_value = self._table_as_array[byte_index]

        # デバッグ
        if is_debug:
            # format `:08b` - 0 supply, 8 left shift, binary
            print(f"[evalution mm table > set bit by index]  black_f_black_o_index:{black_f_black_o_index}  byte_index:{byte_index}  bit_index:{bit_index}  left_shift:{left_shift}  bit:{bit}  old byte value:0x{old_byte_value:08b}")

            # assert
            if bit < 0 or 1 < bit:
                raise ValueError(f"bit must be 0 or 1. bit:{bit}")

        # ビットはめんどくさい。ビッグエンディアン
        if bit == 1:
            # 指定の桁を 1 で上書きする
            self._table_as_array[byte_index] = BitOpe.stand_at(old_byte_value, left_shift)

        else:
            # 指定の桁を 0 で上書きする
            self._table_as_array[byte_index] = BitOpe.sit_at(old_byte_value, left_shift)

        if is_debug:
            # format `:08b` - 0 supply, 8 left shift, binary
            print(f"[evalution mm table > set bit by index]  black_f_black_o_index:{black_f_black_o_index}  byte_index:{byte_index}  bit_index:{bit_index}  left_shift:{left_shift}  bit:{bit}  new byte_value:0x{self._table_as_array[byte_index]:08b}")

        # 変更が有ったら、フラグを立てるよう上書き
        is_changed = self._table_as_array[byte_index] != old_byte_value

        if is_changed:
            self._is_file_modified = True
            return (True, '')

        return (False, f'old_byte_value:`0x{old_byte_value:08b}`  left_shift:{left_shift}  bit:{bit}')
