import cshogi
import os
import datetime


class Turn():
    """手番"""


    _turn_string = {
        cshogi.BLACK: 'black',
        cshogi.WHITE: 'white',
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
    def to_string(clazz, my_turn):
        return clazz._turn_string[my_turn]


class Move():
    """指し手"""


    _file_str_to_num = {
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
    """列数字を数に変換"""


    _file_num_to_str = {
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
    """列数を文字に変換"""


    _rank_str_to_num = {
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
    """段英字を数に変換"""


    _rank_num_to_str = {
        1:'a',
        2:'b',
        3:'c',
        4:'d',
        5:'e',
        6:'f',
        7:'g',
        8:'h',
        9:'i',
    }
    """段数を英字に変換"""


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


    _src_drops = ('R*', 'B*', 'G*', 'S*', 'N*', 'L*', 'P*')
    _src_drop_files = ('R', 'B', 'G', 'S', 'N', 'L', 'P')


    @staticmethod
    def get_rank_num_to_str(rank_num):
        return Move._rank_num_to_str[rank_num]


    @staticmethod
    def from_usi(move_as_usi):
        """生成

        Parameters
        ----------
        move_as_usi : str
            "7g7f" や "3d3c+"、 "R*5e" のような文字列を想定。 "resign" のような文字列は想定外
        """

        # 移動元
        src_str = move_as_usi[0: 2]

        # 移動先
        dst_str = move_as_usi[2: 4]

        #
        # 移動元の列番号を序数で。打にはマス番号は無い
        #
        if src_str in Move._src_drops:
            src_file_or_none = None

        else:
            file_str = src_str[0]

            try:
                src_file_or_none = Move._file_str_to_num[file_str]
            except:
                raise Exception(f"src file error: '{file_str}' in '{move_as_usi}'")

        #
        # 移動元の段番号を序数で。打は無い
        #
        if src_str in Move._src_drops:
            src_rank_or_none = None

        else:
            rank_str = src_str[1]

            try:
                src_rank_or_none = Move._rank_str_to_num[rank_str]
            except:
                raise Exception(f"src rank error: '{rank_str}' in '{move_as_usi}'")

        #
        # 移動元のマス番号を基数で。打にはマス番号は無い
        #
        if src_file_or_none is not None and src_rank_or_none is not None:
            src_sq_or_none = (src_file_or_none - 1) * 9 + (src_rank_or_none - 1)
        else:
            src_sq_or_none = None

        #
        # 移動先の列番号を序数で
        #
        file_str = dst_str[0]

        try:
            dst_file = Move._file_str_to_num[file_str]
        except:
            raise Exception(f"dst file error: '{file_str}' in '{move_as_usi}'")

        #
        # 移動先の段番号を序数で
        #
        rank_str = dst_str[1]

        try:
            dst_rank = Move._rank_str_to_num[rank_str]
        except:
            raise Exception(f"dst rank error: '{rank_str}' in '{move_as_usi}'")

        #
        # 移動先のマス番号を序数で
        #
        # 0～80 = (1～9     - 1) * 9 + (1～9      - 1)
        dst_sq  = (dst_file - 1) * 9 + (dst_rank - 1)

        #
        # 成ったか？
        #
        #   - ５文字なら成りだろう
        #
        promoted = 4 < len(move_as_usi)

        return Move(
                move_as_usi=move_as_usi,
                src_str=src_str,
                dst_str=dst_str,
                src_file_or_none=src_file_or_none,
                src_rank_or_none=src_rank_or_none,
                src_sq_or_none=src_sq_or_none,
                dst_file=dst_file,
                dst_rank=dst_rank,
                dst_sq=dst_sq,
                promoted=promoted)


    @staticmethod
    def from_src_dst_pro(
            src_sq,
            dst_sq,
            promoted):
        """生成

        Parameters
        ----------
        src_sq : str
            移動元マス
        dst_sq : str
            移動先マス
        promoted : bool
            成ったか？
        """

        src_file = src_sq // 9 + 1
        src_rank = src_sq % 9 + 1

        dst_file = dst_sq // 9 + 1
        dst_rank = dst_sq % 9 + 1

        src_str = f"{src_file}{Move._rank_num_to_str[src_rank]}"
        dst_str = f"{dst_file}{Move._rank_num_to_str[dst_rank]}"

        if promoted:
            pro_str = "+"
        else:
            pro_str = ""

        return Move(
                move_as_usi=f"{src_str}{dst_str}{pro_str}",
                src_str=src_str,
                dst_str=dst_str,
                src_file_or_none=src_file,
                src_rank_or_none=src_rank,
                src_sq_or_none=src_sq,
                dst_file=dst_file,
                dst_rank=dst_rank,
                dst_sq=dst_sq,
                promoted=promoted)


    def __init__(
            self,
            move_as_usi,
            src_str,
            dst_str,
            src_file_or_none,
            src_rank_or_none,
            src_sq_or_none,
            dst_file,
            dst_rank,
            dst_sq,
            promoted):
        """初期化

        Parameters
        ----------
        move_as_usi : str
            "7g7f" や "3d3c+"、 "R*5e" のような文字列を想定。 "resign" のような文字列は想定外
        src_str : str
            移動元
        dst_str : str
            移動先
        src_file_or_none : int
            移動元の列番号を序数で。打にはマス番号は無い
        src_rank_or_none : int
            移動元の段番号を序数で。打は無い
        src_sq_or_none : int
            移動元のマス番号を基数で。打にはマス番号は無い
        dst_file : int
            移動先の列番号を序数で
        dst_rank : int
            移動先の段番号を序数で
        dst_sq : int
            移動先のマス番号を序数で
        promoted : bool
            成ったか？
        """
        self._move_as_usi = move_as_usi
        self._src_str = src_str
        self._dst_str = dst_str
        self._src_file_or_none = src_file_or_none
        self._src_rank_or_none = src_rank_or_none
        self._src_sq_or_none = src_sq_or_none
        self._dst_file = dst_file
        self._dst_rank = dst_rank
        self._dst_sq = dst_sq
        self._promoted = promoted


    @property
    def as_usi(self):
        return self._move_as_usi


    @property
    def src_str(self):
        """移動元"""
        return self._src_str


    @property
    def dst_str(self):
        """移動先"""
        return self._dst_str


    @property
    def src_file_or_none(self):
        """移動元の列番号を序数で。打にはマス番号は無い"""
        return self._src_file_or_none


    @property
    def src_rank_or_none(self):
        """移動元の段番号を序数で。打にはマス番号は無い"""
        return self._src_rank_or_none


    @property
    def src_sq_or_none(self):
        """移動元のマス番号を基数で。打にはマス番号は無い"""
        return self._src_sq_or_none


    @property
    def dst_file(self):
        """移動先の列番号を序数で"""
        return self._dst_file


    @property
    def dst_rank(self):
        """移動先の段番号を序数で"""
        return self._dst_rank


    @property
    def dst_sq(self):
        """移動先のマス番号を序数で"""
        return self._dst_sq


    @property
    def promoted(self):
        """成ったか？"""
        return self._promoted


class MoveHelper():
    """指し手ヘルパー"""


    @staticmethod
    def is_king(
            k_sq,
            move_obj):
        """自玉か？"""

        src_sq_or_none = move_obj.src_sq_or_none

        # 自玉の指し手か？
        #print(f"［自玉の指し手か？］ move_as_usi: {move_as_usi}, src_sq_or_none: {src_sq_or_none}, k_sq: {k_sq}, board.turn: {board.turn}")
        return src_sq_or_none == k_sq


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
            move_obj):
        """応手の一覧を作成

        Parameters
        ----------
        board : Board
            局面
        move_obj : Move
            着手
        """
        #
        # 相手が指せる手の集合
        # -----------------
        #
        #   ヌルムーブをしたいが、 `board.push_pass()` が機能しなかったので、合法手を全部指してみることにする
        #

        # 敵玉（Lord）の指し手の集合
        l_move_u_set = set()
        # 敵玉を除く敵軍の指し手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_move_u_set = set()

        # １手指す
        board.push_usi(move_obj.as_usi)

        # 敵玉（L; Lord）の位置を調べる
        l_sq = BoardHelper.get_king_square(board)

        for counter_move_id in board.legal_moves:
            counter_move_u = cshogi.move_to_usi(counter_move_id)

            counter_move_obj = Move.from_usi(counter_move_u)

            # 敵玉の指し手か？
            if MoveHelper.is_king(l_sq, counter_move_obj):
                l_move_u_set.add(counter_move_u)
            # 敵玉を除く敵軍の指し手
            else:
                q_move_u_set.add(counter_move_u)

        # １手戻す
        board.pop()

        return (l_move_u_set, q_move_u_set)


class MoveListHelper():
    """指し手のリストのヘルパー"""


    @staticmethod
    def create_k_and_p_legal_moves(
            legal_moves,
            board):
        """自玉の合法手のリストと、自軍の玉以外の合法手のリストを作成

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面

        Returns
        -------
        - 自玉の合法手のリスト : USI符号表記
        - 自軍の玉以外の合法手のリスト : USI符号表記
        """

        k_sq = BoardHelper.get_king_square(board)

        # USIプロトコルでの符号表記に変換
        k_moves_u = []
        p_moves_u = []

        for move in legal_moves:
            move_u = cshogi.move_to_usi(move)

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
            file_name,
            table_as_array,
            is_file_modified):
        """初期化

        Parameters
        ----------
        file_name : str
            ファイル名
        table_as_array : []
            評価値テーブルの配列
        is_file_modified : bool
            このテーブルが変更されて、保存されていなければ真
        """

        self._file_name = file_name
        self._table_as_array = table_as_array
        self._is_file_modified = is_file_modified


    @property
    def file_name(self):
        """ファイル名"""
        return self._file_name


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

        # bit_index == 0 のとき、右から８桁目を指す（ビッグエンディアン）
        #
        #   1xxx xxxx
        #
        # bit_index == 7 のとき、右から１桁目を指す
        #
        #   xxxx xxx1
        #
        # そこで、 (8 - bit_index) 桁目を指す
        #
        figure = 8 - bit_index

        byte_value = self._table_as_array[byte_index]

        bit_value = byte_value // (0b1 << figure) % 2

        if is_debug:
            # format `:08b` - 0 supply, 8 figures, binary
            print(f"[evalution mm table > get_bit_by_index]  index:{index}  byte_index:{byte_index}  bit_index:{bit_index}  figure:{figure}  byte_value:0x{self._table_as_array[byte_index]:08b}  bit_value:{bit_value}")

        if bit_value < 0 or 1 < bit_value:
            raise ValueError(f"bit must be 0 or 1. bit:{bit_value}")

        return bit_value


    def set_bit_by_index(
            self,
            index,
            bit,
            is_debug=False):
        """インデックスを受け取ってビット値を設定します

        Parameters
        ----------
        index : int
            配列のインデックス
        bit : int
            0 か 1

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """

        if bit < 0 or 1 < bit:
            raise ValueError(f"bit must be 0 or 1. bit:{bit}")

        # ビット・インデックスを、バイトとビットに変換
        bit_index = index % 8
        byte_index = index // 8

        byte_value = self._table_as_array[byte_index]

        # bit_index == 0 のとき、右から８桁目を指す（ビッグエンディアン）
        #
        #   1xxx xxxx
        #
        # bit_index == 7 のとき、右から１桁目を指す
        #
        #   xxxx xxx1
        #
        # そこで、 (8 - bit_index) 桁目を指す
        #
        figure = 8 - bit_index

        old_byte_value = self._table_as_array[byte_index]

        if is_debug:
            # format `:08b` - 0 supply, 8 figures, binary
            print(f"[evalution mm table > set_bit_by_index]  index:{index}  byte_index:{byte_index}  bit_index:{bit_index}  figure:{figure}  bit:{bit}  old byte value:0x{old_byte_value:08b}")

        # ビットはめんどくさい。ビッグエンディアン
        if bit == 1:
            # 指定の桁を 1 で上書きする
            self._table_as_array[byte_index] = byte_value | (0b1 << figure)

        else:
            # 指定の桁を 0 で上書きする
            self._table_as_array[byte_index] = byte_value & (0b1111_1111 - (0b1 << figure))

        if is_debug:
            # format `:08b` - 0 supply, 8 figures, binary
            print(f"[evalution mm table > set_bit_by_index]  index:{index}  byte_index:{byte_index}  bit_index:{bit_index}  figure:{figure}  bit:{bit}  new byte_value:0x{self._table_as_array[byte_index]:08b}")

        # 変更が有ったら、フラグを立てるよう上書き
        is_changed = self._table_as_array[byte_index] != old_byte_value

        if is_changed:
            self._is_file_modified = True

        return is_changed


########################################
# ファイル関連
########################################

class GameResultFile():
    """対局結果ファイル"""


    def __init__(
            self,
            engine_version_str):
        """初期化

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        self._file_name = f'n1_game_result_{engine_version_str}.txt'


    @property
    def file_name(self):
        """ファイル名"""
        return self._file_name


    def exists(self):
        """ファイルの存在確認"""
        return os.path.isfile(self.file_name)


    def delete(self):
        """ファイルの削除"""

        try:
            print(f"[{datetime.datetime.now()}] {self.file_name} file delete...", flush=True)
            os.remove(self.file_name)
            print(f"[{datetime.datetime.now()}] {self.file_name} file deleted", flush=True)

        except FileNotFoundError:
            # ファイルが無いのなら、削除に失敗しても問題ない
            pass


    def read_lines(self):
        """結果の読込"""
        try:
            print(f"[{datetime.datetime.now()}] {self.file_name} file read ...", flush=True)

            with open(self.file_name, 'r', encoding="utf-8") as f:
                text = f.read()

            # 改行で分割
            lines = text.splitlines()
            print(f"[{datetime.datetime.now()}] {self.file_name} file read", flush=True)

            return lines

        # ファイルの読込に失敗
        except:
            return []


    def save_lose(self, my_turn, board):
        """負け

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        print(f"あ～あ、 {turn_text} 番で負けたぜ（＞＿＜）", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name} file save ...", flush=True)
        with open(self.file_name, 'w', encoding="utf-8") as f:
            f.write(f"""lose {turn_text}
sfen {board.sfen()}""")

        print(f"[{datetime.datetime.now()}] {self.file_name} file saved", flush=True)


    def save_win(self, my_turn, board):
        """勝ち

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        print(f"やったぜ {turn_text} 番で勝ったぜ（＾ｑ＾）", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name} file save ...", flush=True)
        with open(self.file_name, 'w', encoding="utf-8") as f:
            f.write(f"""win {turn_text}
sfen {board.sfen()}""")

        print(f"[{datetime.datetime.now()}] {self.file_name} file saved", flush=True)


    def save_draw(self, my_turn, board):
        """持将棋

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        print(f"持将棋か～（ー＿ー） turn: {turn_text}", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name} file save ...", flush=True)
        with open(self.file_name, 'w', encoding="utf-8") as f:
            f.write(f"""draw {turn_text}
sfen {board.sfen()}""")

        print(f"[{datetime.datetime.now()}] {self.file_name} file saved", flush=True)


    def save_otherwise(self, result_text, my_turn, board):
        """予期しない結果

        Parameters
        ----------
        result_text : str
            結果文字列
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        print(f"なんだろな（・＿・）？　'{result_text}', turn: '{turn_text}'", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name} file save ...", flush=True)
        with open(self.file_name, 'w', encoding="utf-8") as f:
            f.write(f"""{result_text} {turn_text}
sfen {board.sfen()}""")

        print(f"[{datetime.datetime.now()}] {self.file_name} file saved", flush=True)
