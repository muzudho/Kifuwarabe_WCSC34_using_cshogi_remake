# python v_a11_0.py
import cshogi
import os
import datetime
import random
from v_a11_0_lib import Turn, Move, MoveHelper, BoardHelper, MoveListHelper, MoveAndPolicyHelper, PolicyHelper, EvalutionMmTable, GameResultFile


########################################
# 設定
########################################

engine_version_str = "v_a11_0"
"""将棋エンジン・バージョン文字列。ファイル名などに使用"""

max_move_number = 2000
"""手数上限"""


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

        # ＫＬ評価値テーブル　[0:先手, 1:後手]
        self._evaluation_kl_table_obj_array = [
            EvaluationKkTable(),
            EvaluationKkTable(),
        ]

        # 自分の手番
        self._my_turn = None

        # 対局結果ファイル
        self._game_result_file = None


    @property
    def evaluation_kl_table_obj_array(self):
        """ＫＬ評価値テーブル　[0:先手, 1:後手]"""
        return self._evaluation_kl_table_obj_array


    def usi_loop(self):
        """USIループ"""

        while True:

            # 入力
            #cmd = input().split(' ', 1)
            cmd = input().split(' ')

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

            # 指定の手の評価値テーブルの関係を全て表示する
            #       code: relation 7g7f
            elif cmd[0] == 'relation':
                self.relation(cmd)

            # 指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
            # これによって、その着手のポリシー値は下がる
            #       code: weaken 5i5h
            elif cmd[0] == 'weaken':
                self.weaken(cmd)

            # 指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が有るようにする。
            # これによって、その着手のポリシー値は上がる
            #       code: strengthen 5i5h
            elif cmd[0] == 'strengthen':
                self.strengthen(cmd)

            # プレイアウト
            #       code: playout
            elif cmd[0] == 'playout':
                self.playout()

            # 局面表示
            #       code: board
            elif cmd[0] == 'board':
                self.print_board()

            # 作りかけ
            #       code: wip 5i5h
            elif cmd[0] == 'wip':
                self.wip(cmd)


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

        #
        # ＫＬ評価値テーブル　［0:先手, 1:後手］
        #
        for turn in [cshogi.BLACK, cshogi.WHITE]:
            turn_index = Turn.to_index(turn)
            self._evaluation_kl_table_obj_array[turn_index].load_on_usinewgame(
                    turn=turn)

            if self._evaluation_kl_table_obj_array[turn_index].mm_table_obj.is_file_modified:
                self._evaluation_kl_table_obj_array[turn_index].save_evaluation_table_file()
            else:
                print(f"[{datetime.datetime.now()}] kk file not changed.  turn_index:{turn_index}", flush=True)

        # 対局結果ファイル（デフォルト）
        self._game_result_file = GameResultFile(
                engine_version_str=engine_version_str)


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
        best_move_str = Lottery.choice_best(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self)

        print(f"info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move")
        print(f'bestmove {best_move_str}', flush=True)


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


    def get_weakest_moves(self):
        """最弱手の取得"""
        return MoveAndPolicyHelper.get_moves(
                weakest0_strongest1 = 0,
                board=self._board,
                kifuwarabe=self)


    def get_strongest_moves(self):
        """最強手の取得"""
        return MoveAndPolicyHelper.get_moves(
                weakest0_strongest1 = 1,
                board=self._board,
                kifuwarabe=self)


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
            print(f'  # bestmove resign', flush=True)
            return

        # 入玉宣言局面時
        if self._board.is_nyugyoku():
            print(f'  # bestmove win', flush=True)
            return

        # 一手詰めを詰める
        #
        #   自玉に王手がかかっていない時で
        #
        if not self._board.is_check():

            # 一手詰めの指し手があれば、それを取得
            if (matemove := self._board.mate_move_in_1ply()):

                best_move = cshogi.move_to_usi(matemove)
                print(f'  # bestmove {best_move} (mate)', flush=True)
                return

        #
        # USIプロトコルでの符号表記と、ポリシー値の辞書に変換
        # --------------------------------------------
        #
        #   自玉の指し手と、自玉を除く自軍の指し手を分けて取得
        #   ポリシー値は千分率の４桁の整数
        #
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = EvaluationFacade.create_list_of_friend_move_u_and_policy_dictionary(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self)

        # 表示
        number = 1

        best_policy = -1000
        best_move_dictionary = {}

        #
        # ＫＬ
        # ----
        #

        print('  自玉の着手と、敵玉の応手の評価一覧（ＫＬ）：')
        for move_u, policy in kl_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) K:{move_u:5} L:*****  policy:{policy:4}‰')

            # update
            if best_policy < policy:
                best_policy = policy
                best_move_dictionary = {move_u:policy}

            # tie
            elif best_policy == policy:
                best_move_dictionary[move_u] = policy

            number += 1

        #
        # ＫＱ
        # ----
        #

        print('  自玉の着手と、敵兵の応手の評価一覧（ＫＱ）：')
        for move_u, policy in kq_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) K:{move_u:5} Q:*****  policy:{policy:4}‰')

            # update
            if best_policy < policy:
                best_policy = policy
                best_move_dictionary = {move_u:policy}

            # tie
            elif best_policy == policy:
                best_move_dictionary[move_u] = policy

            number += 1

        #
        # ＰＬ
        # ----
        #

        print('  自兵の着手と、敵玉の応手の評価一覧（ＰＬ）：')
        for move_u, policy in pl_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) P:{move_u:5} L:*****  policy:{policy:4}')

            # update
            if best_policy < policy:
                best_policy = policy
                best_move_dictionary = {move_u:policy}

            # tie
            elif best_policy == policy:
                best_move_dictionary[move_u] = policy

            number += 1

        #
        # ＰＱ
        # ----
        #

        print('  自兵の着手と、敵兵の応手の評価一覧（ＰＱ）：')
        for move_u, policy in pq_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) P:{move_u:5} Q:*****  policy:{policy:4}')

            # update
            if best_policy < policy:
                best_policy = policy
                best_move_dictionary = {move_u:policy}

            # tie
            elif best_policy == policy:
                best_move_dictionary[move_u] = policy

            number += 1

        # TODO ポリシー順に並べたい。 Order by policy

        #
        # ベスト
        # ------
        #

        print(f'  ベスト一覧：')
        for move_u, policy in best_move_dictionary.items():
            print(f'    turn:{Turn.to_string(self._board.turn)}  F:{move_u:5}  O:*****  policy:{policy:4}‰')


    def weakest(self):
        """現局面の最弱手を返す"""
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = self.get_weakest_moves()

        print(f'最弱手一覧（ＫＬ）：', flush=True)
        for move_u, policy in kl_move_u_and_policy_dictionary.items():
            print(f'  K:{move_u:5} L:***** : {policy:4}', flush=True)

        print(f'最弱手一覧（ＫＱ）：', flush=True)
        for move_u, policy in kq_move_u_and_policy_dictionary.items():
            print(f'  K:{move_u:5} Q:***** : {policy:4}', flush=True)

        print(f'最弱手一覧（ＰＬ）：', flush=True)
        for move_u, policy in pl_move_u_and_policy_dictionary.items():
            print(f'  P:{move_u:5} L:***** : {policy:3}', flush=True)

        print(f'最弱手一覧（ＰＱ）：', flush=True)
        for move_u, policy in pq_move_u_and_policy_dictionary.items():
            print(f'  P:{move_u:5} Q:***** : {policy:3}', flush=True)


    def strongest(self):
        """現局面の最強手を返す"""
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = self.get_strongest_moves()

        print(f'最強手一覧（ＫＬ）：', flush=True)
        for move_u, policy in kl_move_u_and_policy_dictionary.items():
            print(f'  K:{move_u:5} L:***** : {policy:4}', flush=True)

        print(f'最強手一覧（ＫＱ）：', flush=True)
        for move_u, policy in kq_move_u_and_policy_dictionary.items():
            print(f'  K:{move_u:5} Q:***** : {policy:4}', flush=True)

        print(f'最強手一覧（ＰＬ）：', flush=True)
        for move_u, policy in pl_move_u_and_policy_dictionary.items():
            print(f'  P:{move_u:5} L:***** : {policy:4}', flush=True)

        print(f'最強手一覧（ＰＱ）：', flush=True)
        for move_u, policy in pq_move_u_and_policy_dictionary.items():
            print(f'  P:{move_u:5} Q:***** : {policy:4}', flush=True)


    def relation(self, cmd):
        """指定の手の評価値テーブルの関係を全て表示する
        code: relation 7g7f

        Parameters
        ----------
        cmd : str[]
            コマンドのトークン配列
        """
        if len(cmd) < 2:
            print(f"relation command must be move. ex: `relation 7g7f` token number:{len(cmd)}")
            return

        move_u = cmd[1]

        # 着手と応手をキー、関係の有無を値とする辞書を作成します
        (fl_index_to_relation_exists_dictionary,
         fq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fl_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                board=self._board,
                kifuwarabe=self)

        k_sq = BoardHelper.get_king_square(self._board)

        move_obj = Move.from_usi(move_u)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            # 表示
            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index)

                print(f"  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        else:
            # TODO 表示
            pass


    def weaken(self, cmd):
        """指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
        これによって、その着手のポリシー値は下がる
        code: weaken 5i5h

        Parameters
        ----------
        cmd : str[]
            コマンドのトークン配列
        """

        if len(cmd) < 2:
            print(f"weaken command must be 1 move. ex: `weaken 5i5h` token number:{len(cmd)}")
            return

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
                print(f'# failed to weaken (mate {best_move})', flush=True)
                return


        move_u = cmd[1]

        # 着手と応手をキー、関係の有無を値とする辞書を作成します
        (fl_index_to_relation_exists_dictionary,
         fq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fl_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                board=self._board,
                kifuwarabe=self)

        k_sq = BoardHelper.get_king_square(self._board)

        move_obj = Move.from_usi(move_u)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            exists_number = 0
            total = len(fl_index_to_relation_exists_dictionary)

            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index)

                # 表示
                print(f"kl_index:{kl_index}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                if relation_exists == 1:
                    exists_number += 1

            # この着手に対する応手の関係を減らしたい
            #
            #   とりあえず、半分になるよう調整する
            #
            expected_exists_number = exists_number // 2
            difference = exists_number - expected_exists_number

            # 表示
            print(f"K:{move_obj.as_usi:5}  L:*****  exists_number:{exists_number} / total:{total}  expected_exists_number:{expected_exists_number}  difference:{difference}")

            rest = difference

            # 関係を difference 個削除
            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                if rest < 1:
                    break

                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index)

                if k_move_obj.as_usi == move_u:
                    if relation_exists == 1:

                        print(f"turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index}  K:{move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  remove relation")

                        self._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
                                k_move_obj=k_move_obj,
                                l_move_obj=l_move_obj,
                                bit=0)

                        rest -= 1

        else:
            # TODO 表示
            pass


    def strengthen(self, cmd):
        """指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が有るようにする。
        これによって、その着手のポリシー値は上がる
        code: strengthen 5i5h

        Parameters
        ----------
        cmd : str[]
            コマンドのトークン配列
        """

        if len(cmd) < 2:
            print(f"strengthen command must be 1 move. ex: `strengthen 5i5h` token number:{len(cmd)}")
            return

        # 投了局面時
        if self._board.is_game_over():
            print(f'# failed to strengthen (game over)', flush=True)
            return

        # 入玉宣言局面時
        if self._board.is_nyugyoku():
            print(f'# failed to strengthen (nyugyoku win)', flush=True)
            return

        # 一手詰めを詰める
        #
        #   自玉に王手がかかっていない時で
        #
        if not self._board.is_check():

            # 一手詰めの指し手があれば、それを取得
            if (matemove := self._board.mate_move_in_1ply()):

                best_move = cshogi.move_to_usi(matemove)
                print(f'# failed to weaken (mate {best_move})', flush=True)
                return


        move_u = cmd[1]

        # 着手と応手をキー、関係の有無を値とする辞書を作成します
        (fl_index_to_relation_exists_dictionary,
         fq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fl_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                board=self._board,
                kifuwarabe=self)

        k_sq = BoardHelper.get_king_square(self._board)

        move_obj = Move.from_usi(move_u)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            exists_number = 0
            total = len(fl_index_to_relation_exists_dictionary)

            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index)

                # 表示
                print(f"  kl_index:{kl_index}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

                if relation_exists == 1:
                    exists_number += 1

            # この着手に対する応手の関係を増やしたい
            #
            #   とりあえず、増やせるなら、１増やす
            #
            if exists_number < total:
                expected_exists_number = exists_number + 1
            else:
                expected_exists_number = exists_number

            difference = expected_exists_number - exists_number

            # 表示
            print(f"  K:{move_obj.as_usi:5}  L:*****  exists_number:{exists_number} / total:{total}  expected_exists_number:{expected_exists_number}  difference:{difference}")

            rest = difference

            # 関係を difference 個追加
            for kl_index, relation_exists in fl_index_to_relation_exists_dictionary.items():
                if rest < 1:
                    break

                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index)

                if k_move_obj.as_usi == move_u:
                    if relation_exists == 0:

                        print(f"  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index}  K:{move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}  add relation")

                        self._evaluation_kl_table_obj_array[Turn.to_index(self._board.turn)].set_relation_esixts_by_kl_moves(
                                k_move_obj=k_move_obj,
                                l_move_obj=l_move_obj,
                                bit=1)

                        rest -= 1

        else:
            # TODO 表示
            pass


    def playout(self):
        """プレイアウト
        投了局面になるまで、適当に指します
        """

        while True:

            if max_move_number <= self._board.move_number:
                print(f'# move_number:{self._board.move_number} / max_move_number:{max_move_number}', flush=True)
                return

            if self._board.is_game_over():
                """投了局面時"""

                # 投了
                print(f'# bestmove resign', flush=True)
                return

            if self._board.is_nyugyoku():
                """入玉宣言局面時"""

                # 勝利宣言
                print(f'# bestmove win', flush=True)
                return

            # 一手詰めを詰める
            if not self._board.is_check():
                """自玉に王手がかかっていない時で"""

                if (matemove := self._board.mate_move_in_1ply()):
                    """一手詰めの指し手があれば、それを取得"""

                    best_move = cshogi.move_to_usi(matemove)
                    print('# info score mate 1 pv {}'.format(best_move), flush=True)
                    print(f'# bestmove {best_move}', flush=True)
                    return

            # くじを引く（投了のケースは対応済みなので、ここで対応しなくていい）
            best_move_str = Lottery.choice_best(
                    legal_moves=list(self._board.legal_moves),
                    board=self._board,
                    kifuwarabe=self)

            # 一手指す
            self._board.push_usi(best_move_str)


    def print_board(self):
        """局面表示"""
        print(self._board)


    def wip(self, cmd):
        """作りかけ

        指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
        これによって、その着手のポリシー値は下がる
        code: wip 5i5h

        Parameters
        ----------
        cmd : str[]
            コマンドのトークン配列
        """

        if len(cmd) < 2:
            print(f"weaken command must be 1 move. ex: `weaken 5i5h` token number:{len(cmd)}")
            return

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
                print(f'# failed to weaken (mate {best_move})', flush=True)
                return

        # 自玉のマス番号
        k_sq = BoardHelper.get_king_square(self._board)

        # 弱めたい着手
        weaken_move_u = cmd[1]
        weaken_move_obj = Move.from_usi(weaken_move_u)

        # 弱めたい着手に対する応手の一覧を取得
        weaken_l_move_u_set, weaken_q_move_u_set = BoardHelper.create_counter_move_u_set(
                board=self._board,
                move_obj=weaken_move_obj)

        # 弱めたい着手は、玉の指し手か？
        is_weaken_king_move = MoveHelper.is_king(k_sq, weaken_move_obj)
        print(f"is_weaken_king_move:{is_weaken_king_move}")

        if is_weaken_king_move:
            #
            # ＫＬ，ＫＱ
            #
            (weaken_kl_index_and_relation_bit_dictionary,
             weaken_kq_index_and_relation_bit_dictionary,
             weaken_pl_index_and_relation_bit_dictionary,
             weaken_pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_mm_index_and_relation_bit(
                    k_moves_u=[weaken_move_u],
                    kl_move_u_set=weaken_l_move_u_set,
                    kq_move_u_set=weaken_q_move_u_set,
                    p_moves_u=[],
                    pl_move_u_set=set(),
                    pq_move_u_set=set(),
                    turn=self._board.turn,
                    kifuwarabe=self,)

        else:
            #
            # ＰＬ，ＰＱ
            #
            (weaken_kl_index_and_relation_bit_dictionary,
             weaken_kq_index_and_relation_bit_dictionary,
             weaken_pl_index_and_relation_bit_dictionary,
             weaken_pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_mm_index_and_relation_bit(
                    k_moves_u=[],
                    kl_move_u_set=set(),
                    kq_move_u_set=set(),
                    p_moves_u=[weaken_move_u],
                    pl_move_u_set=weaken_l_move_u_set,
                    pq_move_u_set=weaken_q_move_u_set,
                    turn=self._board.turn,
                    kifuwarabe=self,)

        for fo_index, relation_bit in weaken_kl_index_and_relation_bit_dictionary.items():
            print(f"KL:{fo_index:6}  relation_bit:{relation_bit}")

        for fo_index, relation_bit in weaken_kq_index_and_relation_bit_dictionary.items():
            print(f"KQ:{fo_index:6}  relation_bit:{relation_bit}")

        for fo_index, relation_bit in weaken_pl_index_and_relation_bit_dictionary.items():
            print(f"PL:{fo_index:6}  relation_bit:{relation_bit}")

        for fo_index, relation_bit in weaken_pq_index_and_relation_bit_dictionary.items():
            print(f"PQ:{fo_index:6}  relation_bit:{relation_bit}")

        # 関係のキーをインデックスから着手へ変換
        (k_move_u_and_l_to_relation_number_dictionary,
         k_move_u_and_q_to_relation_number_dictionary,
         p_move_u_and_l_to_relation_number_dictionary,
         p_move_u_and_q_to_relation_number_dictionary) = EvaluationFacade.select_move_u_and_relation_number_group_by_move_u(
                weaken_kl_index_and_relation_bit_dictionary,
                weaken_kq_index_and_relation_bit_dictionary,
                weaken_pl_index_and_relation_bit_dictionary,
                weaken_pq_index_and_relation_bit_dictionary)

        for move_u, relation_number in k_move_u_and_l_to_relation_number_dictionary.items():
            print(f"KL F:{move_u:5}  O:*****  relation_number:{relation_number}")

        for move_u, relation_number in k_move_u_and_q_to_relation_number_dictionary.items():
            print(f"KQ F:{move_u:5}  O:*****  relation_number:{relation_number}")

        for move_u, relation_number in p_move_u_and_l_to_relation_number_dictionary.items():
            print(f"PL F:{move_u:5}  O:*****  relation_number:{relation_number}")

        for move_u, relation_number in p_move_u_and_q_to_relation_number_dictionary.items():
            print(f"PQ F:{move_u:5}  O:*****  relation_number:{relation_number}")


        # 関係をポリシー値に変換
        (weaken_k_move_u_and_l_and_policy_dictionary,
         weaken_k_move_u_and_q_and_policy_dictionary,
         weaken_p_move_u_and_l_and_policy_dictionary,
         weaken_p_move_u_and_q_and_policy_dictionary) = EvaluationFacade.select_move_u_and_policy_permille_group_by_move_u(
                k_move_u_and_l_to_relation_number_dictionary=k_move_u_and_l_to_relation_number_dictionary,
                k_move_u_and_q_to_relation_number_dictionary=k_move_u_and_q_to_relation_number_dictionary,
                p_move_u_and_l_to_relation_number_dictionary=p_move_u_and_l_to_relation_number_dictionary,
                p_move_u_and_q_to_relation_number_dictionary=p_move_u_and_q_to_relation_number_dictionary)

        for move_u, policy in weaken_k_move_u_and_l_and_policy_dictionary.items():
            print(f"K:{move_u:5}  L:*****  policy:{policy:4}‰")

        for move_u, policy in weaken_k_move_u_and_q_and_policy_dictionary.items():
            print(f"K:{move_u:5}  Q:*****  policy:{policy:4}‰")

        for move_u, policy in weaken_p_move_u_and_l_and_policy_dictionary.items():
            print(f"K:{move_u:5}  L:*****  policy:{policy:4}‰")

        for move_u, policy in weaken_p_move_u_and_q_and_policy_dictionary.items():
            print(f"K:{move_u:5}  Q:*****  policy:{policy:4}‰")

        # ポリシー毎に指し手をまとめ直す
        (weaken_kl_policy_to_f_move_u_set_dictionary,
         weaken_kq_policy_to_f_move_u_set_dictionary,
         weaken_pl_policy_to_f_move_u_set_dictionary,
         weaken_pq_policy_to_f_move_u_set_dictionary) = EvaluationFacade.select_policy_to_f_move_u_set_group_by_policy(
                weaken_k_move_u_and_l_and_policy_dictionary,
                weaken_k_move_u_and_q_and_policy_dictionary,
                weaken_p_move_u_and_l_and_policy_dictionary,
                weaken_p_move_u_and_q_and_policy_dictionary)

        for policy, move_u_set in weaken_kl_policy_to_f_move_u_set_dictionary.items():
            print(f"KL policy:{policy}  --->", end='')
            for move_u in move_u_set:
                print(f"  {move_u:5}", end='')

            print('', flush=True)

        for policy, move_u_set in weaken_kq_policy_to_f_move_u_set_dictionary.items():
            print(f"KQ policy:{policy}  --->", end='')
            for move_u in move_u_set:
                print(f"  {move_u:5}", end='')

            print('', flush=True)

        for policy, move_u_set in weaken_pl_policy_to_f_move_u_set_dictionary.items():
            print(f"PL policy:{policy}  --->", end='')
            for move_u in move_u_set:
                print(f"  {move_u:5}", end='')

            print('', flush=True)

        for policy, move_u_set in weaken_pq_policy_to_f_move_u_set_dictionary.items():
            print(f"PQ policy:{policy}  --->", end='')
            for move_u in move_u_set:
                print(f"  {move_u:5}", end='')

            print('', flush=True)

        # ポリシー値を小さい順に並べた配列を作ります
        weaken_kl_policy_list_asc = sorted(weaken_kl_policy_to_f_move_u_set_dictionary.keys())

        for policy in weaken_kl_policy_list_asc:
            print(f"KL asc policy:{policy}")

        # TODO 弱めたい関係を１個選ぶ
        # TODO 強めたい関係を１個選ぶ
        # TODO 両方選べたら、そうする。選べなくなったら終わり
        # TODO ベストな候補手を並べ、そこに弱めたい手が含まれなくなるまで、繰り返す。弱めたい手がベストに現れなければ終わり


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
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = EvaluationFacade.create_list_of_friend_move_u_and_policy_dictionary(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe)

        list_of_friend_move_u_and_policy_dictionary = [
            kl_move_u_and_policy_dictionary,
            kq_move_u_and_policy_dictionary,
            pl_move_u_and_policy_dictionary,
            pq_move_u_and_policy_dictionary,
        ]

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


class MoveAndPolicyHelper():
    """評価値付きの指し手のリストのヘルパー"""


    @staticmethod
    def get_moves(
            weakest0_strongest1,
            board,
            kifuwarabe):
        """最強手または最弱手の取得

        Parameters
        ----------
        weakest0_strongest1 : int
            0なら最弱手、1なら最強手を取得
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        """
        #
        # USIプロトコルでの符号表記と、ポリシー値の辞書に変換
        # --------------------------------------------
        #
        #   自玉の指し手と、自玉を除く自軍の指し手を分けて取得
        #   ポリシー値は千分率の４桁の整数
        #
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = EvaluationFacade.create_list_of_friend_move_u_and_policy_dictionary(
                legal_moves=list(board.legal_moves),
                board=board,
                kifuwarabe=kifuwarabe)

        if weakest0_strongest1 == 1:
            best_kl_policy = -1000
            best_kq_policy = -1000
            best_pl_policy = -1000
            best_pq_policy = -1000

        else:
            best_kl_policy = 1000
            best_kq_policy = 1000
            best_pl_policy = 1000
            best_pq_policy = 1000

        best_kl_move_dictionary = {}
        best_kq_move_dictionary = {}
        best_pl_move_dictionary = {}
        best_pq_move_dictionary = {}

        #
        # ＫＬ
        # ----
        #

        for move_u, policy in kl_move_u_and_policy_dictionary.items():

            # tie
            if best_kl_policy == policy:
                best_kl_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_kl_policy < policy) or (weakest0_strongest1 == 0 and policy < best_kl_policy):
                best_kl_policy = policy
                best_kl_move_dictionary = {move_u:policy}

        #
        # ＫＱ
        # ----
        #

        for move_u, policy in kq_move_u_and_policy_dictionary.items():

            # tie
            if best_kq_policy == policy:
                best_kq_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_kq_policy < policy) or (weakest0_strongest1 == 0 and policy < best_kq_policy):
                best_kq_policy = policy
                best_kq_move_dictionary = {move_u:policy}

        #
        # ＰＬ
        # ----
        #

        for move_u, policy in pl_move_u_and_policy_dictionary.items():

            # tie
            if best_pl_policy == policy:
                best_pl_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_pl_policy < policy) or (weakest0_strongest1 == 0 and policy < best_pl_policy):
                best_pl_policy = policy
                best_pl_move_dictionary = {move_u:policy}

        #
        # ＰＱ
        # ----
        #

        for move_u, policy in pq_move_u_and_policy_dictionary.items():

            # tie
            if best_pq_policy == policy:
                best_pq_move_dictionary[move_u] = policy

            # update
            elif (weakest0_strongest1 == 1 and best_pq_policy < policy) or (weakest0_strongest1 == 0 and policy < best_pq_policy):
                best_pq_policy = policy
                best_pq_move_dictionary = {move_u:policy}

        #
        # ベスト
        # ------
        #

        return (best_kl_move_dictionary,
                best_kq_move_dictionary,
                best_pl_move_dictionary,
                best_pq_move_dictionary)


########################################
# 評価値付け階層
########################################

class EvaluationFacade():
    """評価値のファサード"""


    #query_mm_move_u_and_relation_bit
    @staticmethod
    def select_mm_index_and_relation_bit(
            k_moves_u,
            kl_move_u_set,
            kq_move_u_set,
            p_moves_u,
            pl_move_u_set,
            pq_move_u_set,
            turn,
            kifuwarabe):
        """着手と応手の関係を４つの辞書として取得

        Parameters
        ----------
        k_moves_u : iterable
            自玉の着手の収集
        kl_moves_u_set : iterable
            自玉の着手に対する、敵玉の応手の収集
        kq_moves_u_set : iterable
            自玉の着手に対する、敵兵の応手の収集
        p_moves_u : iterable
            自兵の着手の収集
        pl_moves_u_set : iterable
            自兵の着手に対する、敵玉の応手の収集
        pq_moves_u_set : iterable
            自兵の着手に対する、敵兵の応手の収集
        turn : int
            手番
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている

        Returns
        -------
        kl_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵玉の応手の数
        kq_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵兵の応手の数
        pl_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵玉の応手の数
        pq_index_and_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵兵の応手の数
        """
        # 指し手と、ビット値を紐づける
        kl_index_and_relation_bit_dictionary = {}
        kq_index_and_relation_bit_dictionary = {}
        pl_index_and_relation_bit_dictionary = {}
        pq_index_and_relation_bit_dictionary = {}

        # ポリシー値を累計していく
        for k_move_u in k_moves_u:
            k_move_obj = Move.from_usi(k_move_u)

            #
            # ＫＬ
            #
            for l_move_u in kl_move_u_set:
                l_move_obj = Move.from_usi(l_move_u)

                kl_index = EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj)

                relation_bit = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(turn)].get_relation_esixts_by_index(
                        kl_index=kl_index)

                kl_index_and_relation_bit_dictionary[kl_index] = relation_bit

            #
            # ＫＱ
            #
            #   TODO ＫＰ評価値テーブルを参照したい
            #
            #kq_move_u_and_policy_dictionary[k_move_u] = 0
            #
            #for q_move_u in kq_move_u_set:
            #    relation_bit = 0 # random.randint(0,1)
            #    kq_move_u_and_relation_bit_dictionary[k_move_u] += relation_bit

        #for p_move_u in p_moves_u:

            #
            # ＰＬ
            #
            #   TODO ＰＫ評価値テーブルを参照したい
            #
            #pl_move_u_and_policy_dictionary[p_move_u] = 0
            #
            #for l_move_u in pl_move_u_set:
            #    relation_bit = 0 # random.randint(0,1)
            #    pl_move_u_and_relation_bit_dictionary[p_move_u] += relation_bit

            #
            # ＰＱ
            #
            #   TODO ＰＰ評価値テーブルを参照したい
            #
            #pq_move_u_and_relation_bit_dictionary[p_move_u] = 0
            #
            #for q_move_u in pq_move_u_set:
            #    relation_bit = 0 # random.randint(0,1)
            #    pq_move_u_and_relation_bit_dictionary[p_move_u] += relation_bit

        return (kl_index_and_relation_bit_dictionary,
                kq_index_and_relation_bit_dictionary,
                pl_index_and_relation_bit_dictionary,
                pq_index_and_relation_bit_dictionary)


    #put_policy_permille_to_move_u
    #merge_policy_permille
    #map_relation_bit_to_policy_permille
    @staticmethod
    def select_move_u_and_policy_permille_group_by_move_u(
            k_move_u_and_l_to_relation_number_dictionary,
            k_move_u_and_q_to_relation_number_dictionary,
            p_move_u_and_l_to_relation_number_dictionary,
            p_move_u_and_q_to_relation_number_dictionary):
        """ＭＮ関係を、Ｍ毎にまとめ直して、関係の有無は件数に変換し、スケールを千分率に揃える

        Parameters
        ----------
        k_move_u_and_l_to_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵玉の応手の数
        k_move_u_and_q_to_relation_number_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵兵の応手の数
        p_move_u_and_l_to_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵玉の応手の数
        p_move_u_and_q_to_relation_number_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵兵の応手の数

        Returns
        -------
        k_move_u_and_l_and_policy_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵玉の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        k_move_u_and_q_and_policy_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵兵の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        p_move_u_and_l_and_policy_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵玉の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        p_move_u_and_q_and_policy_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵兵の応手のポリシー値付き辞書。ポリシー値は千分率の４桁の整数
        """

        k_move_u_and_l_to_policy_dictionary = {}
        k_move_u_and_q_to_policy_dictionary = {}
        p_move_u_and_l_to_policy_dictionary = {}
        p_move_u_and_q_to_policy_dictionary = {}

        #
        # Ｋ
        #

        # ＫＬ
        for k_move_u, relation_number in k_move_u_and_l_to_relation_number_dictionary.items():
            print(f"K:{k_move_u:5}  L:*****  relation_number:{relation_number:3}  /  size:{len(k_move_u_and_l_to_relation_number_dictionary)}")

        for k_move_u, relation_number in k_move_u_and_l_to_relation_number_dictionary.items():
            k_move_u_and_l_to_policy_dictionary[k_move_u] = PolicyHelper.get_permille_from_relation_number(
                    relation_number=relation_number,
                    counter_move_size=len(k_move_u_and_l_to_relation_number_dictionary))

            print(f"K:{k_move_u:5}  L:*****  sum(k policy):{k_move_u_and_l_to_policy_dictionary[k_move_u]:4}‰")

        # TODO ＫＱ

        #
        # Ｐ
        #

        # TODO ＰＬ

        # TODO ＰＱ

        return (k_move_u_and_l_to_policy_dictionary,
                k_move_u_and_q_to_policy_dictionary,
                p_move_u_and_l_to_policy_dictionary,
                p_move_u_and_q_to_policy_dictionary)


    @staticmethod
    def select_move_u_and_relation_number_group_by_move_u(
            kl_index_and_relation_bit_dictionary,
            kq_index_and_relation_bit_dictionary,
            pl_index_and_relation_bit_dictionary,
            pq_index_and_relation_bit_dictionary):
        """ＭＮ関係を、Ｍ毎にまとめ直して、関係の有無は件数に変換します

        Parameters
        ----------
        kl_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵玉の応手の数
        kq_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自玉の着手に対する、敵兵の応手の数
        pl_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵玉の応手の数
        pq_index_and_relation_bit_dictionary - Dictionary<int, int>
            - 自兵の着手に対する、敵兵の応手の数

        Returns
        -------
        k_move_u_and_l_and_relation_number_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵玉の応手の数
        k_move_u_and_q_and_relation_number_dictionary - Dictionary<str, int>
            - 自玉の着手に対する、敵兵の応手の数
        p_move_u_and_l_and_relation_number_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵玉の応手の数
        p_move_u_and_q_and_relation_number_dictionary - Dictionary<str, int>
            - 自兵の着手に対する、敵兵の応手の数
        """

        k_move_u_and_l_and_relation_number_dictionary = {}
        k_move_u_and_q_and_relation_number_dictionary = {}
        p_move_u_and_l_and_relation_number_dictionary = {}
        p_move_u_and_q_and_relation_number_dictionary = {}

        #
        # Ｋ
        #

        # ＫＬ
        for kl_index, relation_bit in kl_index_and_relation_bit_dictionary.items():
            k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(kl_index)

            if k_move_obj.as_usi in k_move_u_and_l_and_relation_number_dictionary.keys():
                k_move_u_and_l_and_relation_number_dictionary[k_move_obj.as_usi] += relation_bit

            else:
                k_move_u_and_l_and_relation_number_dictionary[k_move_obj.as_usi] = relation_bit

            print(f"kl_index:{kl_index}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_bit:{relation_bit}  sum(k relation):{k_move_u_and_l_and_relation_number_dictionary[k_move_obj.as_usi]}")

        # TODO ＫＱ

        #
        # Ｐ
        #

        # TODO ＰＬ

        # TODO ＰＱ

        return (k_move_u_and_l_and_relation_number_dictionary,
                k_move_u_and_q_and_relation_number_dictionary,
                p_move_u_and_l_and_relation_number_dictionary,
                p_move_u_and_q_and_relation_number_dictionary)

    @staticmethod
    def select_policy_to_f_move_u_set_group_by_policy(
            k_move_u_and_l_and_policy_dictionary,
            k_move_u_and_q_and_policy_dictionary,
            p_move_u_and_l_and_policy_dictionary,
            p_move_u_and_q_and_policy_dictionary):
        """ポリシー毎に指し手をまとめ直す"""
        kl_policy_to_f_move_u_set_dictionary = {}
        kq_policy_to_f_move_u_set_dictionary = {}
        pl_policy_to_f_move_u_set_dictionary = {}
        pq_policy_to_f_move_u_set_dictionary = {}

        # ＫＬ
        for move_u, policy in k_move_u_and_l_and_policy_dictionary.items():
            if policy in kl_policy_to_f_move_u_set_dictionary.keys():
                print(f"KL  policy:{policy}‰  add K:{move_u}")
                kl_policy_to_f_move_u_set_dictionary[policy].add(move_u)

            else:
                print(f"KL  policy:{policy}‰  new K:{move_u}")
                kl_policy_to_f_move_u_set_dictionary[policy] = set()
                kl_policy_to_f_move_u_set_dictionary[policy].add(move_u)

        # ＫＱ
        for move_u, policy in k_move_u_and_q_and_policy_dictionary.items():
            if policy in kq_policy_to_f_move_u_set_dictionary.keys():
                kq_policy_to_f_move_u_set_dictionary[policy].add(move_u)

            else:
                kq_policy_to_f_move_u_set_dictionary[policy] = set()
                kq_policy_to_f_move_u_set_dictionary[policy].add(move_u)

        # ＰＬ
        for move_u, policy in p_move_u_and_l_and_policy_dictionary.items():
            if policy in pl_policy_to_f_move_u_set_dictionary.keys():
                pl_policy_to_f_move_u_set_dictionary[policy].add(move_u)

            else:
                pl_policy_to_f_move_u_set_dictionary[policy] = set()
                pl_policy_to_f_move_u_set_dictionary[policy].add(move_u)

        # ＰＱ
        for move_u, policy in p_move_u_and_q_and_policy_dictionary.items():
            if policy in pq_policy_to_f_move_u_set_dictionary.keys():
                pq_policy_to_f_move_u_set_dictionary[policy].add(move_u)

            else:
                pq_policy_to_f_move_u_set_dictionary[policy] = set()
                pq_policy_to_f_move_u_set_dictionary[policy].add(move_u)

        return (kl_policy_to_f_move_u_set_dictionary,
                kq_policy_to_f_move_u_set_dictionary,
                pl_policy_to_f_move_u_set_dictionary,
                pq_policy_to_f_move_u_set_dictionary)


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
        """自玉の着手と、ポリシー値の紐づいた辞書を作成する

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
        - kl_move_u_and_policy_dictionary : Dictionary<str, int>
            自玉の着手と、敵玉の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        - kq_move_u_and_policy_dictionary,
            自玉の着手と、敵兵の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        - pl_move_u_and_policy_dictionary,
            自兵の着手と、敵玉の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        - pq_move_u_and_policy_dictionary
            自兵の着手と、敵兵の応手の、関係のポリシー値。ポリシー値は千分率の４桁の整数
        """

        # 自玉の着手の集合と、自軍の玉以外の着手の集合
        k_moves_u, p_moves_u = MoveListHelper.create_k_and_p_legal_moves(
                legal_moves,
                board)

        #
        # 相手が指せる手の集合
        # -----------------
        #
        #   ヌルムーブをしたいが、 `board.push_pass()` が機能しなかったので、合法手を全部指してみることにする
        #

        # 自玉の着手に対する、敵玉（Lord）の応手の集合
        kl_move_u_set = set()
        # 自玉の着手に対する、敵軍の玉以外の応手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        kq_move_u_set = set()
        # 自軍の玉以外の着手に対する、敵玉（Lord）の応手の集合
        pl_move_u_set = set()
        # 自軍の玉以外の着手に対する、敵軍の玉以外の応手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        pq_move_u_set = set()

        # Ｋに対する、応手の一覧を作成
        for move_u in k_moves_u:
            move_obj = Move.from_usi(move_u)

            kl_move_u_set, kq_move_u_set = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

        # Ｐに対する、応手の一覧を作成
        for move_u in p_moves_u:
            move_obj = Move.from_usi(move_u)

            pl_move_u_set, pq_move_u_set = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

        #
        # 着手と応手の関係を全部取得
        # -----------------------
        #
        (kl_index_and_relation_bit_dictionary,
         kq_index_and_relation_bit_dictionary,
         pl_index_and_relation_bit_dictionary,
         pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_mm_index_and_relation_bit(
                k_moves_u=k_moves_u,
                kl_move_u_set=kl_move_u_set,
                kq_move_u_set=kq_move_u_set,
                p_moves_u=p_moves_u,
                pl_move_u_set=pl_move_u_set,
                pq_move_u_set=pq_move_u_set,
                turn=board.turn,
                kifuwarabe=kifuwarabe)

        # 関係のキーをインデックスから着手へ変換
        (k_move_u_and_l_to_relation_number_dictionary,
         k_move_u_and_q_to_relation_number_dictionary,
         p_move_u_and_l_to_relation_number_dictionary,
         p_move_u_and_q_to_relation_number_dictionary) = EvaluationFacade.select_move_u_and_relation_number_group_by_move_u(
                kl_index_and_relation_bit_dictionary,
                kq_index_and_relation_bit_dictionary,
                pl_index_and_relation_bit_dictionary,
                pq_index_and_relation_bit_dictionary)

        #
        # 評価値テーブルを参照し、各指し手にポリシー値を付ける
        # ---------------------------------------------
        #
        #   ポリシー値は千分率の４桁の整数
        #
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = EvaluationFacade.select_move_u_and_policy_permille_group_by_move_u(
                k_move_u_and_l_to_relation_number_dictionary=k_move_u_and_l_to_relation_number_dictionary,
                k_move_u_and_q_to_relation_number_dictionary=k_move_u_and_q_to_relation_number_dictionary,
                p_move_u_and_l_to_relation_number_dictionary=p_move_u_and_l_to_relation_number_dictionary,
                p_move_u_and_q_to_relation_number_dictionary=p_move_u_and_q_to_relation_number_dictionary)

        return (kl_move_u_and_policy_dictionary,
                kq_move_u_and_policy_dictionary,
                pl_move_u_and_policy_dictionary,
                pq_move_u_and_policy_dictionary)


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


    def select_fl_index_to_relation_exists(
            move_obj,
            board,
            kifuwarabe):
        """１つの着手と全ての応手をキー、関係の有無を値とする辞書を作成します

        Parameters
        ----------
        move_obj : Move
            着手
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            きふわらべ

        Returns
        -------
        fl_index_to_relation_exists_dic
            自軍の着手と、敵玉の応手の関係の有無を格納した辞書
        fq_index_to_relation_exists_dic
            自軍の着手と、敵兵の応手の関係の有無を格納した辞書
        """

        fl_index_to_relation_exists_dic = {}
        fq_index_to_relation_exists_dic = {}

        # 自玉のマス番号
        k_sq = BoardHelper.get_king_square(board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        # 応手の一覧を作成
        l_move_u_set, q_move_u_set = BoardHelper.create_counter_move_u_set(
                board=board,
                move_obj=move_obj)

        if is_king_move:
            # 自玉の着手と、敵玉の応手の一覧から、ＫＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            fl_index_to_relation_exists_dic = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(board.turn)].select_kl_index_and_relation_exists(
                    k_move_obj=move_obj,
                    l_move_u_set=l_move_u_set)

            # TODO 自玉の着手と、敵兵の応手の一覧から、ＫＱテーブルのインデックスと、関係の有無を格納した辞書を作成

        else:
            # TODO 自兵の着手と、敵玉の応手の一覧から、ＰＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            # TODO 自兵の着手と、敵兵の応手の一覧から、ＰＰテーブルのインデックスと、関係の有無を格納した辞書を作成
            pass

        return (fl_index_to_relation_exists_dic, fq_index_to_relation_exists_dic)


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


    _relative_index_to_relative_sq = {
        0: -10,
        1: -9,
        2: -8,
        3: -1,
        4: 1,
        5: 8,
        6: 9,
        7: 10,
    }
    """玉の指し手のインデックスを相対SQへ変換"""


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
            self,
            turn):
        """ＫＫ評価値テーブル読込

        Parameters
        ----------
        turn : int
            手番

        Returns
        -------
        - テーブル
        - バージョンアップしたので保存要求の有無
        """
        file_name=f'n1_eval_kk_{Turn.to_string(turn)}_{engine_version_str}.bin'

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


    def get_relation_esixts_by_kl_moves(
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
        return self.get_relation_esixts_by_index(
                kl_index=EvaluationKkTable.get_index_of_kk_table(
                    k_move_obj=k_move_obj,
                    l_move_obj=l_move_obj))


    def get_relation_esixts_by_index(
            self,
            kl_index):
        """配列のインデックスを受け取って、関係の有無を返します

        Parameters
        ----------
        index : int
            配列のインデックス

        Returns
        -------
        bit : int
            0 or 1
        """
        return self._mm_table_obj.get_bit_by_index(
                index=kl_index)


    def set_relation_esixts_by_kl_moves(
            self,
            k_move_obj,
            l_move_obj,
            bit):
        """自玉の着手と敵玉の応手を受け取って、関係の有無を設定します

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


    # create_relation_exists_dictionary_by_k_move_and_l_moves
    def select_kl_index_and_relation_exists(
            self,
            k_move_obj,
            l_move_u_set):
        """自玉の指し手と、敵玉の応手のリストを受け取ると、すべての関係の有無を辞書に入れて返します
        ＫＫ評価値テーブル用

        Parameters
        ----------
        k_move_obj : Move
            自玉の着手
        l_move_u_set : List<str>
            敵玉の応手のリスト

        Returns
        -------
        - relations : Dictionary<int, int>
            キー：　ＫＫ評価値テーブルのインデックス
            値　：　関係の有無
        """

        relations = {}

        for l_move_u in l_move_u_set:
            kl_index = EvaluationKkTable.get_index_of_kk_table(
                k_move_obj=k_move_obj,
                l_move_obj=Move.from_usi(l_move_u))

            relation_bit = self.get_relation_esixts_by_index(
                    kl_index=kl_index)

            relations[kl_index] = relation_bit

        return relations


    @staticmethod
    def destructure_k_index(
            k_index):
        """Ｋインデックス分解

        Parameter
        ---------
        k_index : int
            玉の指し手のインデックス

        Returns
        -------
        - move_obj : Move
            指し手
        """
        rest = k_index

        king_direction_max_number = EvaluationKkTable.get_king_direction_max_number()

        relative_index = rest % king_direction_max_number
        rest //= king_direction_max_number

        src_sq = rest

        relative_sq = EvaluationKkTable._relative_index_to_relative_sq[relative_index]
        dst_sq = src_sq + relative_sq

        return Move.from_src_dst_pro(
                src_sq=src_sq,
                dst_sq=dst_sq,
                promoted=False)


    @staticmethod
    def destructure_kl_index(
            kl_index):
        """ＫＬインデックス分解

        Parameter
        ---------
        kl_index : int
            自玉と敵玉の関係の通しインデックス

        Returns
        -------
        - k_move_obj : Move
            自玉の着手
        - l_move_obj : Move
            敵玉の応手
        """
        king_move_number = EvaluationKkTable.get_king_move_number()

        l_index = kl_index % king_move_number
        k_index = kl_index // king_move_number

        l_move = EvaluationKkTable.destructure_k_index(
            k_index=l_index)
        k_move = EvaluationKkTable.destructure_k_index(
            k_index=k_index)

        return (k_move, l_move)


########################################
# スクリプト実行階層
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    #print(f"cshogi.BLACK:{cshogi.BLACK}  cshogi.WHITE:{cshogi.WHITE}")

    try:
        kifuwarabe = Kifuwarabe()
        kifuwarabe.usi_loop()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise
