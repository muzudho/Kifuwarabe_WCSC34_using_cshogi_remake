# python v_9_1_0.py
import cshogi
import os
import datetime
import random


########################################
# 設定
########################################

engine_version_str = "v_9_1_0"
"""将棋エンジン・バージョン文字列。ファイル名などに使用"""


########################################
# 有名な定数
########################################

# [コンピュータ将棋基礎情報研究所 > 一局面の合法手の最大数が593手であることの証明](http://lfics81.techblog.jp/archives/2041940.html)
#max_legal_move_number = 593


########################################
# USI ループ階層
########################################

class Kifuwarabe():
    """きふわらべ"""

    def __init__(self):
        """初期化"""

        # 盤
        self._board = cshogi.Board()

        # ＫＫ評価値テーブル
        self._evaluation_kk_table_obj = EvaluationKkTable()

        # 自分の手番
        self._my_turn = None

        # 対局結果ファイル
        self._game_result_file = None


    @property
    def evaluation_kk_table_obj(self):
        """ＫＫ評価値テーブル"""
        return self._evaluation_kk_table_obj


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

            # 現局面のポリシー値を確認する
            #       code: policy
            elif cmd[0] == 'policy':
                self.policy()

            # 現局面の最弱手を確認する
            #       code: weakest
            elif cmd[0] == 'weakest':
                self.weakest()

            # 現局面の最強手を確認する
            #       code: strongest
            elif cmd[0] == 'strongest':
                self.strongest()

            # 指定の指し手Ａのポリシー値を１つ、指定の指し手Ｂのポリシー値に移す
            #       code: weaken 6g6f 7g7f
            elif cmd[0] == 'weaken':
                self.weaken(cmd)


    def usi(self):
        """USIエンジン握手"""

        # エンジン名は別ファイルから読込。pythonファイルはよく差し替えるのでデータは外に出したい
        try:
            file_name = f"{engine_version_str}_engine_name.txt"
            with open(file_name, 'r', encoding="utf-8") as f:
                engine_name = f.read().strip()

        except FileNotFoundError as ex:
            print(f"[usi protocol > usi] '{file_name}' file not found.  ex:{ex}")
            raise

        print(f'id name {engine_name}')
        print(f'id author Muzudho')
        print('usiok', flush=True)


    def isready(self):
        """対局準備"""
        print('readyok', flush=True)


    def usinewgame(self):
        """新しい対局"""

        # ＫＫ評価値テーブル
        self._evaluation_kk_table_obj.load_on_usinewgame()

        if self._evaluation_kk_table_obj.mm_table_obj.is_file_modified:
            self._evaluation_kk_table_obj.save_evaluation_table_file()
        else:
            print(f"[{datetime.datetime.now()}] kk file not changed", flush=True)

        print(f"[{datetime.datetime.now()}] usinewgame end", flush=True)

        # 対局結果ファイル（デフォルト）
        self._game_result_file = GameResultFile()


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

        # 現局面の手番を、自分の手番とする
        self._my_turn = self._board.turn


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
                board=self._board,
                kifuwarabe=self)

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
                # ［対局結果］　常に記憶する
                self._game_result_file.save_lose(self._my_turn, self._board)

            # 勝ち
            elif cmd[1] == 'win':
                # ［対局結果］　常に記憶する
                self._game_result_file.save_win(self._my_turn, self._board)

            # 持将棋
            elif cmd[1] == 'draw':
                # ［対局結果］　常に記憶する
                self._game_result_file.save_draw(self._my_turn, self._board)

            # その他
            else:
                # ［対局結果］　常に記憶する
                self._game_result_file.save_otherwise(cmd[1], self._my_turn, self._board)


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


    def get_moves(
            self,
            weakest0_strongest1):
        """最強手または最弱手の取得"""
        #
        # USIプロトコルでの符号表記と、ポリシー値の辞書に変換
        # --------------------------------------------
        #
        #   自玉の指し手と、自玉を除く自軍の指し手を分けて取得
        #   ポリシー値は千分率の４桁の整数
        #
        list_of_friend_move_u_and_policy_dictionary = EvaluationFacade.create_list_of_friend_move_u_and_policy_dictionary(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self)

        k_move_u_and_policy_dictionary = list_of_friend_move_u_and_policy_dictionary[0]
        p_move_u_and_policy_dictionary = list_of_friend_move_u_and_policy_dictionary[1]

        if weakest0_strongest1 == 1:
            best_k_policy = -1000
            best_p_policy = -1000

        else:
            best_k_policy = 1000
            best_p_policy = 1000

        best_k_move_dictionary = {}
        best_p_move_dictionary = {}

        #
        # キングから
        # ---------
        #

        for move_u, policy in k_move_u_and_policy_dictionary.items():

            # tie
            if best_k_policy == policy:
                best_k_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_k_policy < policy) or (weakest0_strongest1 == 0 and policy < best_k_policy):
                best_k_policy = policy
                best_k_move_dictionary = {move_u:policy}

        #
        # 次にピースズ
        # -----------
        #

        for move_u, policy in p_move_u_and_policy_dictionary.items():

            # tie
            if best_p_policy == policy:
                best_p_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_p_policy < policy) or (weakest0_strongest1 == 0 and policy < best_p_policy):
                best_p_policy = policy
                best_p_move_dictionary = {move_u:policy}

        #
        # ベスト
        # ------
        #

        return (best_k_move_dictionary, best_p_move_dictionary)


    def get_weakest_moves(self):
        """最弱手の取得"""
        return self.get_moves(
                weakest0_strongest1 = 0)


    def get_strongest_moves(self):
        """最強手の取得"""
        return self.get_moves(
                weakest0_strongest1 = 1)


    def policy(self):
        """現局面のポリシー値を確認する
            code: policy
        """

        print(f"""\
先手玉の位置：　{self._board.king_square(cshogi.BLACK)}
後手玉の位置：　{self._board.king_square(cshogi.WHITE)}
""")

        if self._my_turn == cshogi.BLACK:
            # 自玉（King）のマス番号
            k_sq = self._board.king_square(cshogi.BLACK)
            # 敵玉（Lord）のマス番号
            l_sq = self._board.king_square(cshogi.WHITE)
            print(f"""\
自分の手番　：　先手
自玉の位置　：　{k_sq}
敵玉の位置　：　{l_sq}
""")
        else:
            k_sq = self._board.king_square(cshogi.WHITE)
            l_sq = self._board.king_square(cshogi.BLACK)
            print(f"""\
自分の手番　：　後手
自玉の位置　：　{k_sq}
敵玉の位置　：　{l_sq}
""")

        # 投了局面時
        if self._board.is_game_over():
            print(f'# bestmove resign', flush=True)
            return

        # 入玉宣言局面時
        if self._board.is_nyugyoku():
            print(f'# bestmove win', flush=True)
            return

        # 一手詰めを詰める
        #
        #   自玉に王手がかかっていない時で
        #
        if not self._board.is_check():

            # 一手詰めの指し手があれば、それを取得
            if (matemove := self._board.mate_move_in_1ply()):

                best_move = cshogi.move_to_usi(matemove)
                print(f'# bestmove {best_move} (mate)', flush=True)
                return

        #
        # USIプロトコルでの符号表記と、ポリシー値の辞書に変換
        # --------------------------------------------
        #
        #   自玉の指し手と、自玉を除く自軍の指し手を分けて取得
        #   ポリシー値は千分率の４桁の整数
        #
        list_of_friend_move_u_and_policy_dictionary = EvaluationFacade.create_list_of_friend_move_u_and_policy_dictionary(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self)

        k_move_u_and_policy_dictionary = list_of_friend_move_u_and_policy_dictionary[0]
        p_move_u_and_policy_dictionary = list_of_friend_move_u_and_policy_dictionary[1]

        # 表示
        number = 1

        best_policy = -1000
        best_move_dictionary = {}

        #
        # キングから
        # ---------
        #

        print('くじ一覧（自玉の合法手）：')
        for move_u, policy in k_move_u_and_policy_dictionary.items():
            print(f'  ({number:3}) K:{move_u:5}  policy:{policy:4}')

            # update
            if best_policy < policy:
                best_policy = policy
                best_move_dictionary = {move_u:policy}

            # tie
            elif best_policy == policy:
                best_move_dictionary[move_u] = policy

            number += 1

        #
        # 次にピースズ
        # -----------
        #

        print('くじ一覧（自玉以外の自軍の合法手）：')
        for move_u, policy in p_move_u_and_policy_dictionary.items():
            print(f'  ({number:3}) P:{move_u:5}  policy:{policy:4}')

            # update
            if best_policy < policy:
                best_policy = policy
                best_move_dictionary = {move_u:policy}

            # tie
            elif best_policy == policy:
                best_move_dictionary[move_u] = policy

            number += 1

        #
        # ベスト
        # ------
        #

        # FIXME Ｋ と Ｐ では、数のスケールが違うのでは？（合法手の数が違う）　百分率に変換するか？

        print(f'ベスト一覧：')
        for move_u, policy in best_move_dictionary.items():
            print(f'  {move_u:5} : {policy:4}')


    def weakest(self):
        """現局面の最弱手を返す"""
        k_move_u_and_policy_dictionary , p_move_u_and_policy_dictionary = self.get_weakest_moves()

        print(f'最弱手一覧（Ｋ）：', flush=True)
        for move_u, policy in k_move_u_and_policy_dictionary.items():
            print(f'  K {move_u:5} : {policy:4}', flush=True)

        print(f'最弱手一覧（Ｐ）：', flush=True)
        for move_u, policy in p_move_u_and_policy_dictionary.items():
            print(f'  P {move_u:5} : {policy:3}', flush=True)


    def strongest(self):
        """現局面の最強手を返す"""
        k_move_u_and_policy_dictionary , p_move_u_and_policy_dictionary = self.get_strongest_moves()

        print(f'最強手一覧（Ｋ）：', flush=True)
        for move_u, policy in k_move_u_and_policy_dictionary.items():
            print(f'  K {move_u:5} : {policy:4}', flush=True)

        print(f'最強手一覧（Ｐ）：', flush=True)
        for move_u, policy in p_move_u_and_policy_dictionary.items():
            print(f'  P {move_u:5} : {policy:4}', flush=True)


    def weaken(self, cmd):
        """指定の指し手のポリシー値を、最弱のポリシー値を持つ指し手に分ける
        code: weaken 6g6f 7g7f

        Parameters
        ----------
        cmd : str[]
            コマンドのトークン配列
        """

        # 投了局面時
        if self._board.is_game_over():
            print(f'# failed to weaken (game over)', flush=True)
            return

        # 入玉宣言局面時
        if self._board.is_nyugyoku():
            print(f'# failed to weaken (nyugyoku win)', flush=True)
            return

        # 一手詰めを詰める
        #
        #   自玉に王手がかかっていない時で
        #
        if not self._board.is_check():

            # 一手詰めの指し手があれば、それを取得
            if (matemove := self._board.mate_move_in_1ply()):

                best_move = cshogi.move_to_usi(matemove)
                print(f'# failed to waken (mate {best_move})', flush=True)
                return


########################################
# くじ引き階層
########################################

class Lottery():


    @staticmethod
    def choice_best(
            legal_moves,
            board,
            kifuwarabe):
        """くじを引く

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている
        """

        # ポリシー値は千分率の４桁の整数
        list_of_friend_move_u_and_policy_dictionary = EvaluationFacade.create_list_of_friend_move_u_and_policy_dictionary(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe)

        # 一番高いポリシー値を探す。
        # 指し手は１個以上あるとする
        best_moves_u = []
        best_policy = -1000
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
    def put_policy_permille_to_move_u(
            k_moves_u,
            p_moves_u,
            l_move_u_set,
            q_move_u_set,
            kifuwarabe):
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
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている

        Returns
        -------
            - 自玉の指し手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
            - 自玉を除く自軍の指し手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        """

        # 指し手に評価値を付ける
        k_move_u_and_policy_dictionary = {}
        p_move_u_and_policy_dictionary = {}

        # ポリシー値を累計していく
        for k_move_u in k_moves_u:
            k_move_u_and_policy_dictionary[k_move_u] = 0

            # ＫＫ評価値テーブルを参照
            for l_move_u in l_move_u_set:
                # FIXME bit 値で２以上が返ってくる
                policy_bit = kifuwarabe.evaluation_kk_table_obj.get_bit_by_kl_moves(
                        k_move_obj=Move.from_usi(k_move_u),
                        l_move_obj=Move.from_usi(l_move_u))
                #print(f"kk policy_bit:{policy_bit}")
                k_move_u_and_policy_dictionary[k_move_u] += policy_bit

            # TODO ＫＰ評価値テーブルを参照したい
            for q_move_u in q_move_u_set:
                policy_bit = 0 # random.randint(0,1)
                k_move_u_and_policy_dictionary[k_move_u] += policy_bit

        for p_move_u in p_moves_u:
            p_move_u_and_policy_dictionary[p_move_u] = 0

            # TODO ＰＫ評価値テーブルを参照したい
            for l_move_u in l_move_u_set:
                policy_bit = 0 # random.randint(0,1)
                p_move_u_and_policy_dictionary[p_move_u] += policy_bit

            # TODO ＰＰ評価値テーブルを参照したい
            for q_move_u in q_move_u_set:
                policy_bit = 0 # random.randint(0,1)
                p_move_u_and_policy_dictionary[p_move_u] += policy_bit

        #
        # スケールを揃えて、千分率に変換する
        #

        l_size = len(l_move_u_set)
        q_size = len(q_move_u_set)
        opponent_size = l_size + q_size
        #print(f"l_size:{l_size}  q_size:{q_size}  opponent_size:{opponent_size}")

        for move_u, policy in k_move_u_and_policy_dictionary.items():
            k_move_u_and_policy_dictionary[move_u] = policy * 1000 // opponent_size
            #print(f"{k_move_u_and_policy_dictionary[move_u]}  =  old:{policy}  opponent_size:{opponent_size}")

        for move_u, policy in p_move_u_and_policy_dictionary.items():
            p_move_u_and_policy_dictionary[move_u] = policy * 1000 // opponent_size
            #print(f"{p_move_u_and_policy_dictionary[move_u]}  =  old:{opponent_size}  p_size:{opponent_size}")

        return (k_move_u_and_policy_dictionary, p_move_u_and_policy_dictionary)


    def create_random_evaluation_table_as_array(
            a_move_size,
            b_move_size):
        """ランダム値の入った評価値テーブルの配列を新規作成する

        Parameters
        ----------
        a_move_size : int
            指し手Ａのサイズ
        b_move_size : int
            指し手Ｂのサイズ
        """

        # ダミーデータを入れる。１分ほどかかる
        print(f"[{datetime.datetime.now()}] make random evaluation table in memory... (a_move_size:{a_move_size} b_move_size:{b_move_size})", flush=True)

        new_table_as_array = []

        for _index in range(0, a_move_size * b_move_size):
            # 値は 0, 1 の２値
            new_table_as_array.append(random.randint(0,1))

        print(f"[{datetime.datetime.now()}] random evaluation table maked in memory. (size:{len(new_table_as_array)})", flush=True)
        return new_table_as_array


    @staticmethod
    def create_list_of_friend_move_u_and_policy_dictionary(
            legal_moves,
            board,
            kifuwarabe):
        """くじを引く

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている

        Returns
        -------
        - ポリシー値は千分率の４桁の整数
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
        l_move_u_set = set()
        # 敵玉を除く敵軍の指し手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_move_u_set = set()

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
                        l_move_u_set.add(opponent_move_u)
                    # 敵玉を除く敵軍の指し手
                    else:
                        q_move_u_set.add(opponent_move_u)

                board.pop()

        #
        # 評価値テーブルを参照し、各指し手にポリシー値を付ける
        # ---------------------------------------------
        #
        #   ポリシー値は千分率の４桁の整数
        #
        k_move_u_and_policy_dictionary, p_move_u_and_policy_dictionary = EvaluationFacade.put_policy_permille_to_move_u(
                k_moves_u=k_moves_u,
                p_moves_u=p_moves_u,
                l_move_u_set=l_move_u_set,
                q_move_u_set=q_move_u_set,
                kifuwarabe=kifuwarabe)

        list_of_friend_move_u_and_policy_dictionary = [
            k_move_u_and_policy_dictionary,
            p_move_u_and_policy_dictionary,
        ]

        return list_of_friend_move_u_and_policy_dictionary


    @staticmethod
    def read_evaluation_table_as_array_from_file(
            file_name):
        """評価値テーブル・ファイルの読込"""

        # ロードする。数分ほどかかる
        print(f"[{datetime.datetime.now()}] read {file_name} file ...", flush=True)

        table_as_array = []

        try:
            with open(file_name, 'rb') as f:

                one_byte_binary = f.read(1)

                while one_byte_binary:
                    one_byte_num = int.from_bytes(one_byte_binary, signed=False)

                    # 大きな桁から、リストに追加していきます
                    table_as_array.append(one_byte_num//128 % 2)
                    table_as_array.append(one_byte_num// 64 % 2)
                    table_as_array.append(one_byte_num// 32 % 2)
                    table_as_array.append(one_byte_num// 16 % 2)
                    table_as_array.append(one_byte_num//  8 % 2)
                    table_as_array.append(one_byte_num//  4 % 2)
                    table_as_array.append(one_byte_num//  2 % 2)
                    table_as_array.append(one_byte_num//      2)

                    one_byte_binary = f.read(1)

            print(f"[{datetime.datetime.now()}] '{file_name}' file loaded. evaluation table size: {len(table_as_array)}", flush=True)

        except FileNotFoundError as ex:
            print(f"[evaluation table / load from file] [{file_name}] file error. {ex}")
            raise

        return table_as_array


    @staticmethod
    def save_evaluation_table_file(
            file_name,
            table_as_array):
        """ファイルへ保存します"""

        print(f"[{datetime.datetime.now()}] save {file_name} file ...", flush=True)

        # バイナリ・ファイルに出力する
        with open(file_name, 'wb') as f:

            length = 0
            sum = 0

            for bit in table_as_array:
                if bit==0:
                    # byte型配列に変換して書き込む
                    # 1 byte の数 0
                    sum *= 2
                    sum += 0
                    length += 1
                else:
                    # 1 byte の数 1
                    sum *= 2
                    sum += 1
                    length += 1

                if 8 <= length:
                    # 整数型を、１バイトのバイナリーに変更
                    f.write(sum.to_bytes(1))
                    sum = 0
                    length = 0

            # 末端にはみ出た１バイト
            if 0 < length and length < 8:
                while length < 8:
                    sum *= 2
                    length += 1

                f.write(sum.to_bytes(1))

        print(f"[{datetime.datetime.now()}] {file_name} file saved", flush=True)


class EvaluationKkTable():
    """ＫＫ評価値テーブル"""


    _relative_sq_to_move_index = {
        -10: 0,
        -9: 1,
        -8: 2,
        -1: 3,
        1: 4,
        8: 5,
        9: 6,
        10: 7,
    }
    """相対SQを、玉の指し手のインデックスへ変換"""


    @staticmethod
    def get_king_direction_max_number():
        """玉の移動方向の最大数

        Returns
        -------
        - int
        """
        return 8


    @staticmethod
    def get_king_move_number():
        """玉の指し手の数

        Returns
        -------
        - int
        """
        # move_number = sq_size * directions
        #         648 =      81 *          8
        return    648


    @staticmethod
    def get_index_of_kk_table(
            k_move_obj,
            l_move_obj):
        """ＫＫ評価値テーブルのインデックスを算出

        Parameters
        ----------
        k_move_obj : Move
            自玉の指し手
        l_move_obj : Move
            敵玉の指し手
        """

        # 0 ～ 419_903 =                                          0 ～ 647 *                                      648 +                                          0 ～ 647
        return           EvaluationKkTable.get_index_of_k_move(k_move_obj) * EvaluationKkTable.get_king_move_number() + EvaluationKkTable.get_index_of_k_move(l_move_obj)


    @staticmethod
    def get_index_of_k_move(
            move_obj):
        """指し手を指定すると、指し手のインデックスを返す。
        ＫＫ評価値テーブル用

        指し手から、以下の相対SQを算出します

        +----+----+----+
        | +8 | -1 |-10 |
        |    |    |    |
        +----+----+----+
        | +9 | You| -9 |
        |    |    |    |
        +----+----+----+
        |+10 | +1 | -8 |
        |    |    |    |
        +----+----+----+

        例えば　5g5f　なら相対SQは -1 が該当する

        相対SQを、以下の 指し手の相対index に変換します

        +----+----+----+
        |  5 |  3 |  0 |
        |    |    |    |
        +----+----+----+
        |  6 | You|  1 |
        |    |    |    |
        +----+----+----+
        |  7 |  4 |  2 |
        |    |    |    |
        +----+----+----+


        Parameters
        ----------
        move_obj : Move
            指し手

        Returns
        -------
            - 指し手のインデックス
        """

        # 移動元マス番号
        #
        #   - 打はありません。したがって None にはなりません
        #
        src_sq = move_obj.src_sq_or_none

        # 玉は成らない

        # 相対SQ    =  移動先マス番号    - 移動元マス番号
        relative_sq = move_obj.dst_sq - src_sq

        try:
            relative_index = EvaluationKkTable._relative_sq_to_move_index[relative_sq]

        except KeyError as ex:
            # move_obj.as_usi:5a5b / relative_sq:1 move_obj.dst_sq:37 src_sq:36
            print(f"move_obj.as_usi:{move_obj.as_usi} / relative_sq:{relative_sq} move_obj.dst_sq:{move_obj.dst_sq} src_sq:{src_sq}")
            raise


        # 0～647 =  0～80  *                                                 8 +           0～7
        return     src_sq * EvaluationKkTable.get_king_direction_max_number() + relative_index


    def __init__(self):
        self._mm_table_obj = None


    @property
    def mm_table_obj(self):
        return self._mm_table_obj


    def load_on_usinewgame(
            self):
        """ＫＫ評価値テーブル読込

        Returns
        -------
        - テーブル
        - バージョンアップしたので保存要求の有無
        """
        file_name=f'n1_eval_kk_{engine_version_str}.bin'

        print(f"[{datetime.datetime.now()}] {file_name} file exists check ...", flush=True)
        is_file_exists = os.path.isfile(file_name)

        if is_file_exists:
            # 読込
            table_as_array = EvaluationFacade.read_evaluation_table_as_array_from_file(
                    file_name=file_name)
        else:
            table_as_array = None


        # ファイルが存在しないとき
        if table_as_array is None:
            table_as_array = EvaluationFacade.create_random_evaluation_table_as_array(
                    a_move_size=EvaluationKkTable.get_king_move_number(),
                    b_move_size=EvaluationKkTable.get_king_move_number())
            is_file_modified = True     # 新規作成だから

        else:
            is_file_modified = False


        self._mm_table_obj = EvalutionMmTable(
                file_name=file_name,
                table_as_array=table_as_array,
                is_file_modified=is_file_modified)


    def save_evaluation_table_file(
            self):
        """ファイルへの保存"""

        # 保存するかどうかは先に判定しておくこと
        EvaluationFacade.save_evaluation_table_file(
                file_name=self.mm_table_obj.file_name,
                table_as_array=self.mm_table_obj.table_as_array)


    def get_bit_by_kl_moves(
            self,
            k_move_obj,
            l_move_obj):
        """自玉と敵玉の指し手を受け取って、関係の有無を返します

        Parameters
        ----------
        k_move_obj : Move
            自玉の指し手
        l_move_obj : Move
            敵玉の指し手

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj))


    def set_bit_by_indexes(
            self,
            k_move_obj,
            l_move_obj,
            bit):
        """２つのインデックスを受け取って、ビット値を設定します

        Parameters
        ----------
        k_move_obj : Move
            自玉の指し手
        l_move_obj : Move
            敵玉の指し手
        bit : int
            0 か 1
        """
        return self._mm_table_obj.set_bit_by_index(
                index=EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj),
                bit=bit)


########################################
# ファイル関連
########################################

class GameResultFile():
    """対局結果ファイル"""


    def __init__(self):
        """初期化"""
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


########################################
# データ構造階層
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
            index):
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
        byte_index = index // 8
        bit_index = index % 8

        byte_value = self._table_as_array[byte_index]

        # ビットはめんどくさい。ビッグエンディアン
        if bit_index == 0:
            bit_value = byte_value // 128 % 2
        elif bit_index == 1:
            bit_value = byte_value // 64 % 2
        elif bit_index == 2:
            bit_value = byte_value // 32 % 2
        elif bit_index == 3:
            bit_value = byte_value // 16 % 2
        elif bit_index == 4:
            bit_value = byte_value // 8 % 2
        elif bit_index == 5:
            bit_value = byte_value // 4 % 2
        elif bit_index == 6:
            bit_value = byte_value // 2 % 2
        else:
            bit_value = byte_value % 2

        if bit_value < 0 or 1 < bit_value:
            raise ValueError(f"bit must be 0 or 1. bit:{bit_value}")

        return bit_value


    def set_bit_by_index(
            self,
            index,
            bit):
        """インデックスを受け取ってビット値を設定します

        Parameters
        ----------
        index : int
            配列のインデックス
        bit : int
            0 か 1
        """

        if bit < 0 or 1 < bit:
            raise ValueError(f"bit must be 0 or 1. bit:{bit}")

        self._table_as_array[index] = bit


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

        # 自玉のマス番号
        k_sq = board.king_square(board.turn)

        # USIプロトコルでの符号表記に変換
        k_moves_u = []
        p_moves_u = []

        for move in legal_moves:
            move_u = cshogi.move_to_usi(move)

            # 指し手の移動元を取得
            move_obj = Move.from_usi(move_u)
            src_sq_or_none = move_obj.src_sq_or_none

            # 自玉の指し手か？
            #print(f"［自玉の指し手か？］ move_as_usi: {move_as_usi}, src_sq_or_none: {src_sq_or_none}, k_sq: {k_sq}, board.turn: {board.turn}")
            if src_sq_or_none == k_sq:
                k_moves_u.append(move_u)

            else:
                p_moves_u.append(move_u)

        return (k_moves_u, p_moves_u)


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


class Turn():
    """手番"""


    _turn_string = {
        cshogi.BLACK: 'black',
        cshogi.WHITE: 'white',
    }


    @classmethod
    def to_string(clazz, my_turn):
        return clazz._turn_string[my_turn]


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
