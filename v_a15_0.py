# python v_a15_0.py
import cshogi
import datetime
import random
from v_a15_0_lib import Turn, Move, MoveHelper, BoardHelper, MoveListHelper, PolicyHelper, GameResultFile
from v_a15_0_eval_kk import EvaluationKkTable


########################################
# 設定
########################################

engine_version_str = "v_a15_0"
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
            EvaluationKkTable(
                    engine_version_str=engine_version_str),
            EvaluationKkTable(
                    engine_version_str=engine_version_str),
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
                self._evaluation_kl_table_obj_array[turn_index].save_kk_evaluation_table_file()
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
        return MoveAndPolicyHelper.get_best_moves(
                weakest0_strongest1 = 0,
                board=self._board,
                kifuwarabe=self)


    def get_strongest_moves(self):
        """最強手の取得"""
        return MoveAndPolicyHelper.get_best_moves(
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
         pq_move_u_and_policy_dictionary) = EvaluationFacade.select_fo_move_u_and_policy_dictionary(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self)

        #
        # グッド着手一覧
        # -------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set(
                kl_move_u_and_policy_dictionary,
                kq_move_u_and_policy_dictionary,
                pl_move_u_and_policy_dictionary,
                pq_move_u_and_policy_dictionary)

        print(f'  グッド着手一覧：')
        for move_u in good_move_u_set:
            print(f'    turn:{Turn.to_string(self._board.turn)}  F:{move_u:5}  O:*****  is good')

        print(f'  バッド着手一覧：')
        for move_u in bad_move_u_set:
            print(f'    turn:{Turn.to_string(self._board.turn)}  F:{move_u:5}  O:*****  is bad')


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
        (kl_index_to_relation_exists_dictionary,
         kq_index_to_relation_exists_dictionary,
         pl_index_to_relation_exists_dictionary,
         pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                board=self._board,
                kifuwarabe=self)

        k_sq = BoardHelper.get_king_square(self._board)

        move_obj = Move.from_usi(move_u)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        # 表示
        if is_king_move:

            # ＫＬ
            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index)

                print(f"  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # TODO ＫＱ

        else:
            # TODO ＰＬ
            # TODO ＰＱ
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
                print(f'# failed to waken (mate {best_move})', flush=True)
                return


        move_u = cmd[1]

        # 着手と応手をキー、関係の有無を値とする辞書を作成します
        (kl_index_to_relation_exists_dictionary,
         kq_index_to_relation_exists_dictionary,
         pl_index_to_relation_exists_dictionary,
         pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                board=self._board,
                kifuwarabe=self)

        k_sq = BoardHelper.get_king_square(self._board)

        move_obj = Move.from_usi(move_u)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            # ＫＬ
            exists_number = 0
            total = len(kl_index_to_relation_exists_dictionary)

            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
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
            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
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

            # TODO ＫＱ

        else:
            # TODO ＰＬ
            # TODO ＰＱ
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
                print(f'# failed to waken (mate {best_move})', flush=True)
                return


        move_u = cmd[1]

        # 着手と応手をキー、関係の有無を値とする辞書を作成します
        (kl_index_to_relation_exists_dictionary,
         kq_index_to_relation_exists_dictionary,
         pl_index_to_relation_exists_dictionary,
         pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                board=self._board,
                kifuwarabe=self)

        k_sq = BoardHelper.get_king_square(self._board)

        move_obj = Move.from_usi(move_u)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        if is_king_move:

            # ＫＬ
            exists_number = 0
            total = len(kl_index_to_relation_exists_dictionary)

            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
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
            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():
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

            # TODO ＫＱ

        else:
            # TODO ＰＬ
            # TODO ＰＱ
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
                print(f'# failed to waken (mate {best_move})', flush=True)
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
                    l_move_u_for_k_set=weaken_l_move_u_set,
                    q_move_u_for_k_set=weaken_q_move_u_set,
                    p_moves_u=[],
                    l_move_u_for_p_set=set(),
                    q_move_u_for_p_set=set(),
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
                    l_move_u_for_k_set=set(),
                    q_move_u_for_k_set=set(),
                    p_moves_u=[weaken_move_u],
                    l_move_u_for_p_set=weaken_l_move_u_set,
                    q_move_u_for_p_set=weaken_q_move_u_set,
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

        # 合法手を、着手と応手に紐づくポリシー値を格納した辞書に変換します
        #
        #   ポリシー値は千分率の４桁の整数
        #
        (kl_move_u_and_policy_dictionary,
         kq_move_u_and_policy_dictionary,
         pl_move_u_and_policy_dictionary,
         pq_move_u_and_policy_dictionary) = EvaluationFacade.select_fo_move_u_and_policy_dictionary(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe)

        # ポリシー値は　分母の異なる集団の　投票数なので、
        # 絶対値に意味はなく、
        # 賛同か否定か（0.5 より高いか、低いか）ぐらいの判断にしか使えないと思うので、
        # そのようにします

        #
        # グッド着手一覧
        # -------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set(
                kl_move_u_and_policy_dictionary,
                kq_move_u_and_policy_dictionary,
                pl_move_u_and_policy_dictionary,
                pq_move_u_and_policy_dictionary)

        # 候補手の中からランダムに選ぶ。USIの指し手の記法で返却
        move_u_list = list(good_move_u_set)
        if len(move_u_list) < 1:
            # 何も指さないよりはマシ
            move_u_list = list(bad_move_u_set)

        return random.choice(move_u_list)


    def get_best_move(
            kl_move_u_and_policy_dictionary,
            kq_move_u_and_policy_dictionary,
            pl_move_u_and_policy_dictionary,
            pq_move_u_and_policy_dictionary):
        """ポリシー値が最高のものをどれか１つ選ぶ"""

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


    #get_moves
    @staticmethod
    def get_best_moves(
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
         pq_move_u_and_policy_dictionary) = EvaluationFacade.select_fo_move_u_and_policy_dictionary(
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


    def select_good_f_move_u_set(
            kl_move_u_and_policy_dictionary,
            kq_move_u_and_policy_dictionary,
            pl_move_u_and_policy_dictionary,
            pq_move_u_and_policy_dictionary):
        """ポリシー値が 0.5 以上の着手と、それ以外の着手の２つのリストを返します"""

        number = 1

        # ポリシー値が 0.5 以上の指し手
        good_move_u_set = set()

        # ポリシー値が 0.5 未満の指し手
        bad_move_u_set = set()

        #
        # ＫＬ
        # ----
        #

        print('  自玉の着手と、敵玉の応手の評価一覧（ＫＬ）：')
        for move_u, policy in kl_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) K:{move_u:5} L:*****  policy:{policy:4}‰')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        #
        # ＫＱ
        # ----
        #

        print('  自玉の着手と、敵兵の応手の評価一覧（ＫＱ）：')
        for move_u, policy in kq_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) K:{move_u:5} Q:*****  policy:{policy:4}‰')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        #
        # ＰＬ
        # ----
        #

        print('  自兵の着手と、敵玉の応手の評価一覧（ＰＬ）：')
        for move_u, policy in pl_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) P:{move_u:5} L:*****  policy:{policy:4}')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        #
        # ＰＱ
        # ----
        #

        print('  自兵の着手と、敵兵の応手の評価一覧（ＰＱ）：')
        for move_u, policy in pq_move_u_and_policy_dictionary.items():
            print(f'    ({number:3}) P:{move_u:5} Q:*****  policy:{policy:4}')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        return (good_move_u_set, bad_move_u_set)


########################################
# 評価値付け階層
########################################

class EvaluationFacade():
    """評価値のファサード"""


    #query_mm_move_u_and_relation_bit
    @staticmethod
    def select_mm_index_and_relation_bit(
            k_moves_u,
            l_move_u_for_k_set,
            q_move_u_for_k_set,
            p_moves_u,
            l_move_u_for_p_set,
            q_move_u_for_p_set,
            turn,
            kifuwarabe):
        """着手と応手の関係を４つの辞書として取得

        Parameters
        ----------
        k_moves_u : iterable
            自玉の着手の収集
        l_move_u_for_k_set : iterable
            自玉の着手に対する、敵玉の応手の収集
        q_move_u_for_k_set : iterable
            自玉の着手に対する、敵兵の応手の収集
        p_moves_u : iterable
            自兵の着手の収集
        l_move_u_for_p_set : iterable
            自兵の着手に対する、敵玉の応手の収集
        q_move_u_for_p_set : iterable
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

        def select_fo_index_and_relation_bit(
                kind,
                f_move_obj,
                o_move_u_for_f_set):
            """指定の着手と、指定の応手のセットに対して、

            Parameters
            ----------
            kind : str
                'KL', 'KQ', 'PL', 'PQ' のいずれか
            f_move_obj : Move
                指定の着手
            o_move_u_for_f_set : set<str>
                指定の応手のセット
            """
            fo_index_and_relation_bit_dictionary = {}

            for o_move_u in o_move_u_for_f_set:
                o_move_obj = Move.from_usi(o_move_u)

                if kind == 'KL':
                    fo_index = EvaluationKkTable.get_index_of_kk_table(
                        k_move_obj=f_move_obj,
                        l_move_obj=o_move_obj)
                # FIXME ＫＱ
                elif kind == 'KQ':
                    pass
                # FIXME ＰＬ
                elif kind == 'PL':
                    pass
                # FIXME ＰＱ
                elif kind == 'PQ':
                    pass
                else:
                    raise ValueError(f"unexpected kind:{kind}")

                if kind == 'KL':
                    relation_bit = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(turn)].get_relation_esixts_by_index(
                            kl_index=fo_index)
                # FIXME ＫＱ
                elif kind == 'KQ':
                    continue
                # FIXME ＰＬ
                elif kind == 'PL':
                    continue
                # FIXME ＰＱ
                elif kind == 'PQ':
                    continue
                else:
                    raise ValueError(f"unexpected kind:{kind}")

                fo_index_and_relation_bit_dictionary[fo_index] = relation_bit

            return fo_index_and_relation_bit_dictionary

        # ポリシー値を累計していく
        for k_move_u in k_moves_u:
            k_move_obj = Move.from_usi(k_move_u)

            # ＫＬ
            kl_index_and_relation_bit_dictionary = select_fo_index_and_relation_bit(
                    kind='KL',
                    f_move_obj=k_move_obj,
                    o_move_u_for_f_set=l_move_u_for_k_set)

            # ＫＱ
            kq_index_and_relation_bit_dictionary = select_fo_index_and_relation_bit(
                    kind='KQ',
                    f_move_obj=k_move_obj,
                    o_move_u_for_f_set=q_move_u_for_k_set)

        for p_move_u in p_moves_u:
            p_move_obj = Move.from_usi(p_move_u)

            # ＰＬ
            pl_index_and_relation_bit_dictionary = select_fo_index_and_relation_bit(
                    kind='PL',
                    f_move_obj=p_move_obj,
                    o_move_u_for_f_set=l_move_u_for_p_set)

            # ＰＱ
            pq_index_and_relation_bit_dictionary = select_fo_index_and_relation_bit(
                    kind='PQ',
                    f_move_obj=p_move_obj,
                    o_move_u_for_f_set=q_move_u_for_p_set)

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

        def select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary,
                label_f,
                label_o
        ):
            f_move_u_and_o_to_policy_dictionary = {}
            counter_move_size = len(f_move_u_and_o_to_relation_number_dictionary)

            for move_u, relation_number in f_move_u_and_o_to_relation_number_dictionary.items():
                print(f"{label_f}:{move_u:5}  {label_o}:*****  relation_number:{relation_number:3}  /  size:{counter_move_size}")

            for move_u, relation_number in f_move_u_and_o_to_relation_number_dictionary.items():
                f_move_u_and_o_to_policy_dictionary[move_u] = PolicyHelper.get_permille_from_relation_number(
                        relation_number=relation_number,
                        counter_move_size=counter_move_size)

                print(f"{label_f}:{move_u:5}  {label_o}:*****  sum(f policy):{f_move_u_and_o_to_policy_dictionary[move_u]:4}‰")

            return f_move_u_and_o_to_policy_dictionary

        # ＫＬ
        k_move_u_and_l_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=k_move_u_and_l_to_relation_number_dictionary,
                label_f='K',
                label_o='L')

        # ＫＱ
        k_move_u_and_q_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=k_move_u_and_q_to_relation_number_dictionary,
                label_f='K',
                label_o='Q')

        # ＰＬ
        p_move_u_and_l_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=p_move_u_and_l_to_relation_number_dictionary,
                label_f='P',
                label_o='L')

        # ＰＱ
        p_move_u_and_q_to_policy_dictionary = select_f_move_u_and_policy(
                f_move_u_and_o_to_relation_number_dictionary=p_move_u_and_q_to_relation_number_dictionary,
                label_f='P',
                label_o='Q')

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

        def select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary,
                label_f,
                label_o):

            f_move_u_and_o_and_relation_number_dictionary = {}

            kind = f"{label_f}{label_o}"

            for fo_index, relation_bit in fo_index_and_relation_bit_dictionary.items():

                if kind == 'KL':
                    f_move_obj, o_move_obj = EvaluationKkTable.destructure_kl_index(fo_index)
                # TODO ＫＱ
                elif kind == 'KQ':
                    continue
                # TODO ＰＬ
                elif kind == 'PL':
                    continue
                # TODO ＰＱ
                elif kind == 'PQ':
                    continue
                else:
                    raise ValueError(f"unexpected kind:{kind}")

                if f_move_obj.as_usi in f_move_u_and_o_and_relation_number_dictionary.keys():
                    f_move_u_and_o_and_relation_number_dictionary[f_move_obj.as_usi] += relation_bit

                else:
                    f_move_u_and_o_and_relation_number_dictionary[f_move_obj.as_usi] = relation_bit

                print(f"{label_f.lower()}{label_o.lower()}_index:{fo_index}  {label_f}:{f_move_obj.as_usi:5}  {label_o}:{o_move_obj.as_usi:5}  relation_bit:{relation_bit}  sum(f relation):{f_move_u_and_o_and_relation_number_dictionary[f_move_obj.as_usi]}")

            return f_move_u_and_o_and_relation_number_dictionary

        # ＫＬ
        k_move_u_and_l_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=kl_index_and_relation_bit_dictionary,
                label_f='K',
                label_o='L')

        # TODO ＫＱ
        k_move_u_and_q_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=kq_index_and_relation_bit_dictionary,
                label_f='K',
                label_o='Q')

        # TODO ＰＬ
        p_move_u_and_l_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=pl_index_and_relation_bit_dictionary,
                label_f='P',
                label_o='L')

        # TODO ＰＱ
        p_move_u_and_q_and_relation_number_dictionary = select_f_move_u_and_o_and_relation_number(
                fo_index_and_relation_bit_dictionary=pq_index_and_relation_bit_dictionary,
                label_f='P',
                label_o='Q')

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

        def select_policy_and_f_move_u_set(
                f_move_u_and_o_and_policy_dictionary,
                label_f,
                label_o):
            policy_and_move_u_set_dictionary = {}

            for move_u, policy in f_move_u_and_o_and_policy_dictionary.items():
                if policy in policy_and_move_u_set_dictionary.keys():
                    print(f"{label_f}{label_o}  policy:{policy}‰  add {label_f}:{move_u}")
                    policy_and_move_u_set_dictionary[policy].add(move_u)

                else:
                    print(f"{label_f}{label_o}  policy:{policy}‰  new {label_f}:{move_u}")
                    policy_and_move_u_set_dictionary[policy] = set()
                    policy_and_move_u_set_dictionary[policy].add(move_u)

            return policy_and_move_u_set_dictionary

        # ＫＬ
        kl_policy_to_f_move_u_set_dictionary = select_policy_and_f_move_u_set(
                f_move_u_and_o_and_policy_dictionary=k_move_u_and_l_and_policy_dictionary,
                label_f='K',
                label_o='L')

        # ＫＱ
        kq_policy_to_f_move_u_set_dictionary = select_policy_and_f_move_u_set(
                f_move_u_and_o_and_policy_dictionary=k_move_u_and_q_and_policy_dictionary,
                label_f='K',
                label_o='Q')

        # ＰＬ
        pl_policy_to_f_move_u_set_dictionary = p_move_u_and_l_and_policy_dictionary(
                f_move_u_and_o_and_policy_dictionary=k_move_u_and_q_and_policy_dictionary,
                label_f='P',
                label_o='L')

        # ＰＱ
        pq_policy_to_f_move_u_set_dictionary = p_move_u_and_l_and_policy_dictionary(
                f_move_u_and_o_and_policy_dictionary=p_move_u_and_q_and_policy_dictionary,
                label_f='P',
                label_o='Q')

        return (kl_policy_to_f_move_u_set_dictionary,
                kq_policy_to_f_move_u_set_dictionary,
                pl_policy_to_f_move_u_set_dictionary,
                pq_policy_to_f_move_u_set_dictionary)


    #create_list_of_friend_move_u_and_policy_dictionary
    @staticmethod
    def select_fo_move_u_and_policy_dictionary(
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

            (temp_kl_move_u_set,
             temp_kq_move_u_set) = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

            # 和集合を作成
            kl_move_u_set = kl_move_u_set.union(temp_kl_move_u_set)
            kq_move_u_set = kq_move_u_set.union(temp_kq_move_u_set)

        # Ｐに対する、応手の一覧を作成
        for move_u in p_moves_u:
            move_obj = Move.from_usi(move_u)

            (temp_pl_move_u_set,
             temp_pq_move_u_set) = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

            # 和集合を作成
            pl_move_u_set = kl_move_u_set.union(temp_pl_move_u_set)
            pq_move_u_set = kq_move_u_set.union(temp_pq_move_u_set)

        #
        # 着手と応手の関係を全部取得
        # -----------------------
        #
        (kl_index_and_relation_bit_dictionary,
         kq_index_and_relation_bit_dictionary,
         pl_index_and_relation_bit_dictionary,
         pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_mm_index_and_relation_bit(
                k_moves_u=k_moves_u,
                l_move_u_for_k_set=kl_move_u_set,
                q_move_u_for_k_set=kq_move_u_set,
                p_moves_u=p_moves_u,
                l_move_u_for_p_set=pl_move_u_set,
                q_move_u_for_p_set=pq_move_u_set,
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


    #select_fl_index_to_relation_exists
    def select_fo_index_to_relation_exists(
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
        kl_index_to_relation_exists_dic
            自玉の着手と、敵玉の応手の関係の有無を格納した辞書
        kq_index_to_relation_exists_dic
            自玉の着手と、敵兵の応手の関係の有無を格納した辞書
        pl_index_to_relation_exists_dic
            自兵の着手と、敵玉の応手の関係の有無を格納した辞書
        pq_index_to_relation_exists_dic
            自兵の着手と、敵兵の応手の関係の有無を格納した辞書
        """

        kl_index_to_relation_exists_dic = {}
        kq_index_to_relation_exists_dic = {}
        pl_index_to_relation_exists_dic = {}
        pq_index_to_relation_exists_dic = {}

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
            kl_index_to_relation_exists_dic = kifuwarabe.evaluation_kl_table_obj_array[Turn.to_index(board.turn)].select_kl_index_and_relation_exists(
                    k_move_obj=move_obj,
                    l_move_u_set=l_move_u_set)

            # TODO 自玉の着手と、敵兵の応手の一覧から、ＫＱテーブルのインデックスと、関係の有無を格納した辞書を作成

        else:
            # TODO 自兵の着手と、敵玉の応手の一覧から、ＰＬテーブルのインデックスと、関係の有無を格納した辞書を作成
            # TODO 自兵の着手と、敵兵の応手の一覧から、ＰＰテーブルのインデックスと、関係の有無を格納した辞書を作成
            pass

        return (kl_index_to_relation_exists_dic,
                kq_index_to_relation_exists_dic,
                pl_index_to_relation_exists_dic,
                pq_index_to_relation_exists_dic)


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    #print(f"cshogi.BLACK:{cshogi.BLACK}  cshogi.WHITE:{cshogi.WHITE}")

    try:
        kifuwarabe = Kifuwarabe()
        kifuwarabe.usi_loop()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise
