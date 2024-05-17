# python v_5_0.py
import cshogi
import datetime
import random


########################################
# USI ループ階層
########################################

class Kifuwarabe():
    """きふわらべ"""


    def __init__(self):
        """初期化"""

        # 盤
        self._board = cshogi.Board()


    def usi_loop(self):
        """USIループ"""

        while True:

            # 入力
            cmd = input().split(' ', 1)

            # USIエンジン握手
            if cmd[0] == 'usi':
                self.usi()

            # 対局準備
            elif cmd[0] == 'isready':
                self.isready()

            # 新しい対局
            elif cmd[0] == 'usinewgame':
                self.usinewgame()

            # 局面データ解析
            elif cmd[0] == 'position':
                self.position(cmd)

            # 思考開始～最善手返却
            elif cmd[0] == 'go':
                self.go()

            # 中断
            elif cmd[0] == 'stop':
                self.stop()

            # 対局終了
            elif cmd[0] == 'gameover':
                self.gameover(cmd)

            # アプリケーション終了
            elif cmd[0] == 'quit':
                break

            # 以下、独自拡張

            # 一手指す
            # example: ７六歩
            #       code: do 7g7f
            elif cmd[0] == 'do':
                self.do(cmd)

            # 一手戻す
            #       code: undo
            elif cmd[0] == 'undo':
                self.undo()


    def usi(self):
        """USIエンジン握手"""

        # エンジン名は別ファイルから読込。pythonファイルはよく差し替えるのでデータは外に出したい
        try:
            file_name = "v_5_0_engine_name.txt"
            with open(file_name, 'r', encoding="utf-8") as f:
                engine_name = f.read().strip()

        except FileNotFoundError as ex:
            print(f"[usi protocol > usi] '{file_name}' file not found.  ex:{ex}")
            raise

        print(f'id name {engine_name}')
        print('usiok', flush=True)


    def isready(self):
        """対局準備"""
        print('readyok', flush=True)


    def usinewgame(self):
        """新しい対局"""
        print(f"[{datetime.datetime.now()}] usinewgame end", flush=True)


    def position(self, cmd):
        """局面データ解析"""
        pos = cmd[1].split('moves')
        sfen_text = pos[0].strip()
        # 区切りは半角空白１文字とします
        moves_text_as_usi = (pos[1].split(' ') if len(pos) > 1 else [])

        #
        # 盤面解析
        #

        # 平手初期局面を設定
        if sfen_text == 'startpos':
            self._board.reset()

        # 指定局面を設定
        elif sfen_text[:5] == 'sfen ':
            self._board.set_sfen(sfen_text[5:])

        #
        # 棋譜再生
        #
        for move_as_usi in moves_text_as_usi:
            self._board.push_usi(move_as_usi)


    def go(self):
        """思考開始～最善手返却"""

        if self._board.is_game_over():
            """投了局面時"""

            # 投了
            print(f'bestmove resign', flush=True)
            return

        if self._board.is_nyugyoku():
            """入玉宣言局面時"""

            # 勝利宣言
            print(f'bestmove win', flush=True)
            return

        # 一手詰めを詰める
        if not self._board.is_check():
            """自玉に王手がかかっていない時で"""

            if (matemove := self._board.mate_move_in_1ply()):
                """一手詰めの指し手があれば、それを取得"""

                best_move = cshogi.move_to_usi(matemove)
                print('info score mate 1 pv {}'.format(best_move), flush=True)
                print(f'bestmove {best_move}', flush=True)
                return

        # くじを引く（投了のケースは対応済みなので、ここで対応しなくていい）
        best_move = Lottery.choice_best(
                legal_moves=list(self._board.legal_moves),
                board=self._board)

        print(f"info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move")
        print(f'bestmove {best_move}', flush=True)


    def stop(self):
        """中断"""
        print('bestmove resign', flush=True)


    def gameover(self, cmd):
        """対局終了"""

        if 2 <= len(cmd):
            # 負け
            if cmd[1] == 'lose':
                print("（＞＿＜）負けた")

            # 勝ち
            elif cmd[1] == 'win':
                print("（＾▽＾）勝ったぜ！")

            # 持将棋
            elif cmd[1] == 'draw':
                print("（ー＿ー）持将棋か～")

            # その他
            else:
                print(f"（・＿・）何だろな？：'{cmd[1]}'")


    def do(self, cmd):
        """一手指す
        example: ７六歩
            code: do 7g7f
        """
        self._board.push_usi(cmd[1])


    def undo(self):
        """一手戻す
            code: undo
        """
        self._board.pop()


########################################
# くじ引き階層
########################################

class Lottery():


    @staticmethod
    def choice_best(
            legal_moves,
            board):
        """くじを引く

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        """

        # 自玉の指し手の集合と、自玉を除く自軍の指し手の集合
        k_moves_u, p_moves_u = MoveListHelper.create_k_and_p_legal_moves(
                legal_moves,
                board)

        list_of_friend_moves_u = [
            k_moves_u,
            p_moves_u,
        ]

        #
        # 相手が指せる手の集合
        # -----------------
        #
        #   ヌルムーブをしたいが、 `board.push_pass()` が機能しなかったので、合法手を全部指してみることにする
        #

        # 敵玉（Lord）の指し手の集合
        l_moves_u_set = set()
        # 敵玉を除く敵軍の指し手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_moves_u_set = set()

        for friend_moves_u in list_of_friend_moves_u:
            for friend_move_u in friend_moves_u:
                board.push_usi(friend_move_u)

                # 敵玉（L; Lord）の位置を調べる
                l_sq = board.king_square(board.turn)

                for opponent_move_id in board.legal_moves:
                    opponent_move_u = cshogi.move_to_usi(opponent_move_id)

                    opponent_move_obj = Move.from_usi(opponent_move_u)
                    src_sq_or_none = opponent_move_obj.src_sq_or_none

                    # 敵玉の指し手
                    if src_sq_or_none is not None and src_sq_or_none == l_sq:
                        l_moves_u_set.add(opponent_move_u)
                    # 敵玉を除く敵軍の指し手
                    else:
                        q_moves_u_set.add(opponent_move_u)

                board.pop()

        #
        # 評価値テーブルを参照し、各指し手にポリシー値を付ける
        # ---------------------------------------------
        #
        k_move_u_and_policy_dictionary, p_move_u_and_policy_dictionary = EvaluationFacade.put_policy_to_move_u(
                k_moves_u=k_moves_u,
                p_moves_u=p_moves_u,
                l_moves_u_set=l_moves_u_set,
                q_moves_u_set=q_moves_u_set)

        list_of_friend_move_u_and_policy_dictionary = [
            k_move_u_and_policy_dictionary,
            p_move_u_and_policy_dictionary,
        ]

        # 一番高い評価値を探す。評価値は（改造して範囲がよく変わるのではっきりしないが）適当に小さな値を設定しておく
        # 指し手は１個以上あるとする
        best_moves_u = []
        best_policy = -10000
        for friend_move_u_and_policy_dictionary in list_of_friend_move_u_and_policy_dictionary:
            for friend_move_u, policy in friend_move_u_and_policy_dictionary.items():
                if best_policy == policy:
                    best_moves_u.append(friend_move_u)

                elif best_policy < policy:
                    best_policy = policy
                    best_moves_u = [friend_move_u]

        # 候補手の中からランダムに選ぶ。USIの指し手の記法で返却
        return random.choice(best_moves_u)


########################################
# 評価値付け階層
########################################

class EvaluationFacade():
    """評価値のファサード"""


    @staticmethod
    def put_policy_to_move_u(
            k_moves_u,
            p_moves_u,
            l_moves_u_set,
            q_moves_u_set):
        """指し手のUSI符号に対し、ポリシー値を付加した辞書を作成

        Parameters
        ----------
        k_moves_u : iterable
            自玉の指し手の収集
        p_moves_u : iterable
            自玉を除く自軍の指し手の収集
        l_moves_u_set : iterable
            敵玉の指し手の収集
        q_moves_u_set : iterable
            敵玉を除く敵軍の指し手の収集

        Returns
        -------
            - 自玉の指し手のポリシー値付き辞書
            - 自玉を除く自軍の指し手のポリシー値付き辞書
        """

        # 指し手に評価値を付ける
        k_move_u_and_policy_dictionary = {}
        p_move_u_and_policy_dictionary = {}

        # ポリシー値を累計していく
        for k_move_u in k_moves_u:
            k_move_u_and_policy_dictionary[k_move_u] = 0

            # TODO ＫＫ評価値テーブルを参照したい
            for l_moves_u in l_moves_u_set:
                policy = random.randint(0,1)
                k_move_u_and_policy_dictionary[k_move_u] += policy

            # TODO ＫＰ評価値テーブルを参照したい
            for q_moves_u in q_moves_u_set:
                policy = random.randint(0,1)
                k_move_u_and_policy_dictionary[k_move_u] += policy

        for p_move_u in p_moves_u:
            p_move_u_and_policy_dictionary[p_move_u] = 0

            # TODO ＰＫ評価値テーブルを参照したい
            for l_moves_u in l_moves_u_set:
                policy = random.randint(0,1)
                p_move_u_and_policy_dictionary[p_move_u] += policy

            # TODO ＰＰ評価値テーブルを参照したい
            for q_moves_u in q_moves_u_set:
                policy = random.randint(0,1)
                p_move_u_and_policy_dictionary[p_move_u] += policy

        return (k_move_u_and_policy_dictionary, p_move_u_and_policy_dictionary)


########################################
# データ構造関連
########################################

class BoardHelper():
    """局面のヘルパー"""


    def get_king_square(board):
        """自玉のマス番号

        Parameters
        ----------
        board : Board
            局面
        """
        return board.king_square(board.turn)


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
        dst_sq = (dst_rank - 1) * 9 + (dst_file - 1)

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



########################################
# スクリプト実行階層
########################################

if __name__ == '__main__':
    """コマンドから実行時"""
    try:
        kifuwarabe = Kifuwarabe()
        kifuwarabe.usi_loop()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise
