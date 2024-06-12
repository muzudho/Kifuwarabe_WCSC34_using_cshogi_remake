import cshogi
import datetime

from v_a53_0_misc.bit_ope import BitOpe
from v_a53_0_misc.usi import Usi
from v_a53_0_debug_plan import DebugPlan


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


class MoveSourceLocation():
    """指し手の移動元は、マス番号と駒種類の２通りある"""


    @staticmethod
    def get_file_th_with_rotate(file_th):
        """１８０°回転"""
        if file_th is None:
            return None

        else:
            return 8 - (file_th - 1) + 1


    @staticmethod
    def get_rank_th_with_rotate(rank_th):
        return MoveSourceLocation.get_file_th_with_rotate(rank_th)


    @staticmethod
    def get_sq_with_rotate(sq):
        """マス番号を１８０°回転"""
        if sq is None:
            # 打だろう。 None を返す
            return None

        else:
            return 80 - sq


    @staticmethod
    def from_sq(
            sq):
            (file_th, rank_th) = Usi.sq_to_file_th_rank_th(sq)

            return MoveSourceLocation(
                    srcloc=sq,
                    sq=sq,
                    drop=None,
                    file_th=file_th,
                    rank_th=rank_th)


    @staticmethod
    def from_srcloc(
            srcloc):
        """マス番号か、打の駒種類か分かってない状態

        Parameter
        ---------
        srcloc : str
            マス番号か、打の駒種類のどちらか
        """

        # TODO そもそも、この打とマス番号を分けるようにしなくていいようなフローにできないか？

        # 打なら
        if 81 <= srcloc:
            return MoveSourceLocation(
                    srcloc=srcloc,
                    sq=None,
                    drop=srcloc,
                    file_th=None,
                    rank_th=None)

        # マス番号なら
        else:
            (file_th, rank_th) = Usi.sq_to_file_th_rank_th(sq=srcloc)

            return MoveSourceLocation(
                    srcloc=srcloc,
                    sq=int(srcloc),
                    drop=None,
                    file_th=file_th,
                    rank_th=rank_th)


    @staticmethod
    def from_string(code):
        """文字列から生成

        Parameters
        ----------
        code : str
            元位置。 '7g' とか 'R*' とか
        """
        file_th=None
        rank_th=None
        sq=None
        drop=None

        #
        # 移動元の列番号を 1 から始まる整数で返す。打にはマス番号は無い
        # 移動元の段番号を 1 から始まる整数で返す。打は無い
        #
        if code in Usi.get_srcdrop_str_list():
            file_th = None
            rank_th = None
            drop = code

        else:
            file_str = code[0]
            drop = None

            try:
                file_th = Move._file_th_str_to_num[file_str]
            except:
                raise Exception(f"src file error: `{file_str}` in code:`{code}`")

            rank_str = code[1]

            try:
                rank_th = Move._rank_str_to_th_num[rank_str]
            except:
                raise Exception(f"src rank error: `{rank_str}` in code:'{code}'")

        #
        # 移動元のマス番号を基数で。打なら None が入る
        #
        if file_th is not None and rank_th is not None:
            sq = (file_th - 1) * 9 + (rank_th - 1)
        else:
            sq = None

        return MoveSourceLocation(
                srcloc=Usi.code_to_srcloc(code),
                sq=sq,
                drop=drop,
                file_th=file_th,
                rank_th=rank_th)


    def __init__(
            self,
            srcloc,
            sq,
            drop,
            file_th,
            rank_th):
        """初期化

        Parameters
        ----------
        srcloc : int
            盤上のマス番号（0 ～ 80）、または打つ駒の種類番号（81 ～ 87）
        sq : int
            マス番号。 0～80
        drop : str
            打の駒種類
        file_th : int
            列番号。 1 から始まる整数で返す。打には None を入れる
        rank_th : int
            段番号。 1 から始まる整数で返す。打には None を入れる
        """

        try:
            self._srcloc = srcloc
            self._sq = sq
            self._drop = drop
            self._file_th = file_th
            self._rank_th = rank_th

            #
            # １８０°回転
            #
            # 筋
            self._rot_file_th = MoveSourceLocation.get_file_th_with_rotate(self._file_th)

            # 段
            self._rot_rank_th = MoveSourceLocation.get_rank_th_with_rotate(self._file_th)

            # 打
            self._rot_sq = MoveSourceLocation.get_sq_with_rotate(self._sq)


        except TypeError as ex:
            # file_th:1  rank_th:7  sq:6  drop:None  ex:unsupported operand type(s) for -: 'tuple' and 'int'
            print(f"[move source location > __init__]  file_th:{file_th}  rank_th:{rank_th}  sq:{sq}  drop:{drop}  ex:{ex}")
            raise


    def dump(self):
        return f"""\
_srcloc:{self._srcloc}
_sq:{self._sq}
_drop:{self._drop}
is_drop?:{self.is_drop()}
_file_th:{self._file_th}
_rank_th:{self._rank_th}
_rot_file_th:{self._rot_file_th}
_rot_rank_th:{self._rot_rank_th}
_rot_sq:{self._rot_sq}
"""


    @property
    def file_th(self):
        """列番号。 1 から始まる整数で返す。打には None を入れる"""
        return self._file_th


    @property
    def rank_th(self):
        """段番号。 1 から始まる整数で返す。打には None を入れる"""
        return self._rank_th


    @property
    def srcloc(self):
        """USI 形式の指し手符号の先頭2文字。盤上のマス、または打つ駒の種類"""
        return self._srcloc


    @property
    def sq(self):
        """移動元のマス番号を 0 から始まる整数で返す。打には None を入れる"""
        return self._sq


    @property
    def drop(self):
        """打なら "R*" などを入れる。打でなければ None を入れる"""
        return self._drop


    @property
    def rot_file_th(self):
        """指し手を盤上で１８０°回転したときの列番号。 1 から始まる整数で返す。打なら None を返す"""
        return self._rot_file_th


    @property
    def rot_rank_th(self):
        """指し手を盤上で１８０°回転したときの段番号。 1 から始まる整数で返す。打なら None を返す"""
        return self._rot_rank_th


    @property
    def rot_sq(self):
        """指し手を盤上で１８０°回転したときのマス番号。 0 から始まる整数で返す。打なら None を返す"""
        return self._rot_sq


    def is_drop(self):
        """駒を打つ手か？"""
        return self._drop is not None


    def rotate(self):
        """指し手を盤上で１８０°回転"""
        return MoveSourceLocation(
            srcloc=self._srcloc,
            sq=self._rot_sq,
            # 打の駒種類は回転しません
            drop=self._drop,
            file_th=self._rot_file_th,
            rank_th=self._rot_rank_th)


class MoveDestinationLocation():
    """移動先マス"""


    @staticmethod
    def from_string(dst_str):
        """文字列からオブジェクトを生成"""
        file_th = None
        rank_th = None
        sq = None

        #
        # 移動先の列番号を 1 から始まる整数で返す
        #
        file_char = dst_str[0]

        try:
            file_th = Move._file_th_str_to_num[file_char]
        except:
            raise Exception(f"dst file error: `{file_char}` in dst_str:`{dst_str}`")

        #
        # 移動先の段番号を 1 から始まる整数で返す
        #
        rank_char = dst_str[1]

        try:
            rank_th = Move._rank_str_to_th_num[rank_char]
        except:
            raise Exception(f"dst rank error: '{rank_char}' in rank_th:`{rank_th}`")

        #
        # 移動先のマス番号を 0 から始まる整数で返す
        #
        # 0～80 = (1～9     - 1) * 9 + (1～9    - 1)
        sq  = (file_th - 1) * 9 + (rank_th - 1)

        return MoveDestinationLocation(
            file_th=file_th,
            rank_th=rank_th,
            sq=sq)


    @staticmethod
    def from_sq(sq):
        return MoveDestinationLocation(
                file_th=sq // 9 + 1,
                rank_th=sq % 9 + 1,
                sq=sq)


    def __init__(
            self,
            file_th,
            rank_th,
            sq):
        """初期化

        Parameters
        ----------
        file_th : int
            筋番号。 1 から始まる整数
        rank_th : int
            段番号。 1 から始まる整数
        sq : int
            マス番号。 0 ～ 80 の整数
        """
        self._file_th = file_th
        self._rank_th = rank_th
        self._sq = sq

        self._usi_code = f"{self._file_th}{Usi._rank_th_num_to_alphabet[self._rank_th]}"

        # 指し手を盤上で１８０°回転
        self._rot_file_th = 8 - (self._file_th - 1) + 1
        self._rot_rank_th = 8 - (self._rank_th - 1) + 1
        self._rot_sq = 80 - self._sq


    def dump(self):
        return f"""\
_file_th:{self._file_th}
_rank_th:{self._rank_th}
_sq:{self._sq}
_usi_code:`{self._usi_code}`
_rot_file_th:{self._rot_file_th}
_rot_rank_th:{self._rot_rank_th}
_rot_sq:{self._rot_sq}
"""


    @property
    def file_th(self):
        """筋番号。 1 から始まる整数"""
        return self._file_th


    @property
    def rank_th(self):
        """段番号。 1 から始まる整数"""
        return self._rank_th


    @property
    def sq(self):
        """マス番号。 0 ～ 80 の整数"""
        return self._sq


    @property
    def rot_file_th(self):
        """指し手を１８０°回転したときの筋番号。 1 から始まる整数"""
        return self._rot_file_th


    @property
    def rot_rank_th(self):
        """指し手を１８０°回転したときの段番号。 1 から始まる整数"""
        return self._rot_rank_th


    @property
    def rot_sq(self):
        """指し手を１８０°回転したときのマス番号。 0 ～ 80 の整数"""
        return self._rot_sq


    @property
    def usi_code(self):
        """USI形式文字列

        例： `7g` など
        """
        return self._usi_code


    def rotate(self):
        """指し手を盤上で１８０°回転"""
        return MoveDestinationLocation(
            file_th=self._rot_file_th,
            rank_th=self._rot_rank_th,
            sq=self._rot_sq)


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

        # 移動元オブジェクト生成
        src_location = MoveSourceLocation.from_string(
                code=move_as_usi[0: 2])

        # 移動先オブジェクト生成
        dst_location = MoveDestinationLocation.from_string(
                dst_str=move_as_usi[2: 4])

        #
        # 成ったか？
        #
        #   - ５文字なら成りだろう
        #
        promoted = 4 < len(move_as_usi)

        return Move(
                as_usi=move_as_usi,
                src_location=src_location,
                dst_location=dst_location,
                promoted=promoted)


    @staticmethod
    def from_src_dst_pro(
            src_location,
            dst_location,
            promoted):
        """初期化

        Parameters
        ----------
        src_location : MoveSourceLocation
            移動元オブジェクト
        dst_location : MoveDestinationLocation
            移動先オブジェクト
        promoted : bool
            成ったか？
        """

        if promoted:
            pro_str = "+"
        else:
            pro_str = ""

        return Move(
                as_usi=f"{Usi.srcloc_to_code(src_location.srcloc)}{dst_location.usi_code}{pro_str}",
                src_location=src_location,
                dst_location=dst_location,
                promoted=promoted)


    def __init__(
            self,
            as_usi,
            src_location,
            dst_location,
            promoted):
        """初期化

        Parameters
        ----------
        as_usi:
            USI形式の指し手の符号。
            "7g7f" や "3d3c+"、 "R*5e" のような文字列を想定。 "resign" のような文字列は想定外
        src_location : MoveSourceLocation
            移動元オブジェクト
        dst_location : MoveDestinationLocation
            移動先オブジェクト
        promoted : bool
            成ったか？
        """
        self._as_usi = as_usi
        self._src_location = src_location
        self._dst_location = dst_location
        self._promoted = promoted


    def dump(self):
        return f"""\
_as_usi:`{self._as_usi}`
_src_location:
{self._src_location.dump()}
_dst_location:
{self._dst_location.dump()}
_promoted:`{self._promoted}`
"""

    @property
    def as_usi(self):
        return self._as_usi


    @property
    def src_location(self):
        """移動元"""
        return self._src_location


    @property
    def dst_location(self):
        """移動先"""
        return self._dst_location


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

        # 自玉の指し手か？（打なら None なので False）
        #print(f"［自玉の指し手か？］ move_u: {move_obj.as_usi}, src sq:{move_obj.src_location.sq}, k_sq: {k_sq}, board.turn: {board.turn}")
        return move_obj.src_location.sq == k_sq


class BoardHelper():
    """局面のヘルパー"""

    @staticmethod
    def get_sq_by_file_rank(file, rank):
        return file * 9 + rank


    @staticmethod
    def get_file_rank_by_sq(sq):
        return (sq // 9,
                sq % 9)


    @staticmethod
    def jsa_to_sq(jsa_sq):
        """プロ棋士も使っているマス番号の書き方は
        コンピューターには使いづらいので、
        0 から始まるマスの通し番号に変換します

        豆知識：　十の位を筋、一の位を段とするマス番号は、
                将棋の棋士も棋譜に用いている記法です。
                JSA は日本将棋連盟（Japan Shogi Association）

        Parameters
        ----------
        jsa_sq : int
            筋と段は 1 から始まる整数とし、
            十の位を筋、一の位を段とするマス番号
        """

        file = jsa_sq // 10 - 1
        rank = jsa_sq % 10 - 1

        return BoardHelper.get_sq_by_file_rank(file, rank)


    @staticmethod
    def sq_to_jsa(serial_sq_or_none):
        """0 から始まるマスの通し番号は読みずらいので、
        十の位を筋、一の位を段になるよう変換します。
        これは将棋の棋士も棋譜に用いている記法です。
        JSA は日本将棋連盟（Japan Shogi Association）

        Parameters
        ----------
        serial_sq_or_none : int
            0 から始まるマスの通し番号。打のときは None
        """

        if serial_sq_or_none is None:
            return None

        (file,
         rank) = BoardHelper.get_file_rank_by_sq(serial_sq_or_none)

        return 10 * (file + 1) + (rank + 1)


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

        Returns
        -------
        - l_move_u_set
        - q_move_u_set
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
            print(f"[{datetime.datetime.now()}] [create k and p legal moves]  k_masu:{BoardHelper.sq_to_jsa(k_sq)}")

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
        is_debug : bool
            デバッグか？

        Returns
        -------
        is_changed : bool
            変更が有ったか？
        """

        # ビット・インデックスを、バイトとビットに変換
        bit_index = index % 8
        byte_index = index // 8

        byte_value = self._table_as_array[byte_index]

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
            print(f"[evalution mm table > set_bit_by_index]  index:{index}  byte_index:{byte_index}  bit_index:{bit_index}  left_shift:{left_shift}  bit:{bit}  old byte value:0x{old_byte_value:08b}")

            # assert
            if bit < 0 or 1 < bit:
                raise ValueError(f"bit must be 0 or 1. bit:{bit}")

        # ビットはめんどくさい。ビッグエンディアン
        if bit == 1:
            # 指定の桁を 1 で上書きする
            self._table_as_array[byte_index] = BitOpe.stand_at(byte_value, left_shift)

        else:
            # 指定の桁を 0 で上書きする
            self._table_as_array[byte_index] = BitOpe.sit_at(byte_value, left_shift)

        if is_debug:
            # format `:08b` - 0 supply, 8 left shift, binary
            print(f"[evalution mm table > set_bit_by_index]  index:{index}  byte_index:{byte_index}  bit_index:{bit_index}  left_shift:{left_shift}  bit:{bit}  new byte_value:0x{self._table_as_array[byte_index]:08b}")

        # 変更が有ったら、フラグを立てるよう上書き
        is_changed = self._table_as_array[byte_index] != old_byte_value

        if is_changed:
            self._is_file_modified = True

        return is_changed
