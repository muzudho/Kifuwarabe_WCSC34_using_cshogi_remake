# python v_a16_0.py
import cshogi
import datetime
import random
from v_a16_0_lib import Turn, Move, MoveHelper, BoardHelper, MoveListHelper, PolicyHelper, GameResultFile
from v_a16_0_eval_kk import EvaluationKkTable


########################################
# 設定
########################################

engine_version_str = "v_a16_0"
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

            #
            # 入力
            #
            #   全部バラバラにすると position コマンドとか解析しにくいので、コマンド名とそれ以外で分ける
            #
            head_tail = input().split(' ', 1)
            print(f"head_tail:`{head_tail}`")

            if len(head_tail) == 1:
                head = head_tail[0]
                tail = ''
            else:
                head = head_tail[0]
                tail = head_tail[1]

            # USIエンジン握手
            if head == 'usi':
                self.usi()

            # 対局準備
            elif head == 'isready':
                self.isready()

            # 新しい対局
            elif head == 'usinewgame':
                self.usinewgame()

            # 局面データ解析
            elif head == 'position':
                self.position(
                        cmd_tail=tail)

            # 思考開始～最善手返却
            elif head == 'go':
                self.go()

            # 中断
            elif head == 'stop':
                self.stop()

            # 対局終了
            elif head == 'gameover':
                self.gameover(
                        cmd_tail=tail)

            # アプリケーション終了
            elif head == 'quit':
                break

            # 以下、独自拡張

            # 一手指す
            # example: ７六歩
            #       code: do 7g7f
            elif head == 'do':
                self.do(
                        cmd_tail=tail)

            # 一手戻す
            #       code: undo
            elif head == 'undo':
                self.undo()

            # 現局面のポリシー値を確認する
            #       code: policy
            elif head == 'policy':
                self.policy()

            # 現局面の最弱手を確認する
            #       code: weakest
            elif head == 'weakest':
                self.weakest()

            # 現局面の最強手を確認する
            #       code: strongest
            elif head == 'strongest':
                self.strongest()

            # 指定の手の評価値テーブルの関係を全て表示する
            #       code: relation 7g7f
            elif head == 'relation':
                self.relation(
                        cmd_tail=tail)

            # 指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
            # これによって、その着手のポリシー値は下がる
            #       code: weaken 5i5h
            elif head == 'weaken':
                self.weaken(
                        cmd_tail=tail)

            # 指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が有るようにする。
            # これによって、その着手のポリシー値は上がる
            #       code: strengthen 5i5h
            elif head == 'strengthen':
                self.strengthen(
                        cmd_tail=tail)

            # プレイアウト
            #       code: playout
            elif head == 'playout':
                self.playout()

            # 局面表示
            #       code: board
            elif head == 'board':
                self.print_board()

            # 作りかけ
            #       code: wip 5i5h
            elif head == 'wip':
                self.wip(
                        cmd_tail=tail)


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


    def position(self, cmd_tail):
        """局面データ解析

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """

        board_and_moves = cmd_tail.split('moves')
        board_str = board_and_moves[0].strip()

        # `moves` で分割できたなら
        if len(board_and_moves) > 1:
            moves_str = board_and_moves[1].strip()
            print(f"[kifuwarabe > position] moves:`{moves_str}`")

            # 区切りは半角空白１文字とします
            moves_text_as_usi = moves_str.split(' ')
        else:
            moves_text_as_usi = []

        print(f"[kifuwarabe > position] move size:{len(moves_text_as_usi)}")

        #
        # 盤面解析
        #

        # 平手初期局面を設定
        if board_str == 'startpos':
            self._board.reset()

        # 指定局面を設定
        elif board_str[:5] == 'sfen ':
            self._board.set_sfen(board_str[5:])

        #
        # 棋譜再生
        #
        for move_as_usi in moves_text_as_usi:
            self._board.push_usi(move_as_usi)
            print(f"[kifuwarabe > position] done  M:{move_as_usi:5}  board turn:{Turn.to_string(self._board.turn)}")

        # 現局面の手番を、自分の手番とする
        self._my_turn = self._board.turn
        print(f"[kifuwarabe > position] my turn is {Turn.to_string(self._my_turn)}")


    def go(self):
        """思考開始～最善手返却"""

        # 自分の手番と、局面の手番が一致なら自分のターン
        if self._board.turn == self._my_turn:
            print(f"[kifuwarabe > go] my turn.  board.turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")
        else:
            print(f"[kifuwarabe > go] opponent turn.  board.turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")

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


    def gameover(self, cmd_tail):
        """対局終了

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """

        if cmd_tail.strip() == '':
            print(f"`do` command must be result.  ex:`gameover lose`  cmd_tail:`{cmd_tail}`")
            return

        # 負け
        if cmd_tail == 'lose':
            # ［対局結果］　常に記憶する
            self._game_result_file.save_lose(self._my_turn, self._board)

        # 勝ち
        elif cmd_tail == 'win':
            # ［対局結果］　常に記憶する
            self._game_result_file.save_win(self._my_turn, self._board)

        # 持将棋
        elif cmd_tail == 'draw':
            # ［対局結果］　常に記憶する
            self._game_result_file.save_draw(self._my_turn, self._board)

        # その他
        else:
            # ［対局結果］　常に記憶する
            self._game_result_file.save_otherwise(cmd_tail, self._my_turn, self._board)


    def do(self, cmd_tail):
        """一手指す
        example: ７六歩
            code: do 7g7f

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """
        if cmd_tail.strip() == '':
            print(f"`do` command must be move.  ex:`do 7g7f`  cmd_tail:`{cmd_tail}`")
            return

        self._board.push_usi(cmd_tail)


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

        # 自分の手番と、局面の手番が一致なら自分のターン
        if self._board.turn == self._my_turn:
            print(f"[kifuwarabe > policy] my turn.  board.turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")
        else:
            print(f"[kifuwarabe > policy] opponent turn.  board.turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")

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

        (k_move_u_to_policy_dictionary,
         p_move_u_to_policy_dictionary) = MoveAndPolicyHelper.seleft_f_move_u_add_l_and_q(
                kl_move_u_and_policy_dictionary=kl_move_u_and_policy_dictionary,
                kq_move_u_and_policy_dictionary=kq_move_u_and_policy_dictionary,
                pl_move_u_and_policy_dictionary=pl_move_u_and_policy_dictionary,
                pq_move_u_and_policy_dictionary=pq_move_u_and_policy_dictionary)

        #
        # グッド着手一覧
        # -------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set(
                k_move_u_to_policy_dictionary=k_move_u_to_policy_dictionary,
                p_move_u_to_policy_dictionary=p_move_u_to_policy_dictionary,
                turn=self._board.turn)

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


    def relation(self, cmd_tail):
        """指定の手の評価値テーブルの関係を全て表示する
        code: relation 7g7f

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """
        if cmd_tail.strip() == '':
            print(f"relation command must be move.  ex:`relation 7g7f`  cmd_tail:`{cmd_tail}`")
            return

        move_u = cmd_tail

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


    def weaken(self, cmd_tail):
        """指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
        これによって、その着手のポリシー値は下がる
        code: weaken 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """

        if cmd_tail.strip() == '':
            print(f"weaken command must be 1 move.  ex:`weaken 5i5h`  cmd_tail:`{cmd_tail}`")
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


        move_u = cmd_tail

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


    def strengthen(self, cmd_tail):
        """指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が有るようにする。
        これによって、その着手のポリシー値は上がる
        code: strengthen 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """

        if cmd_tail.strip() == '':
            print(f"strengthen command must be 1 move.  ex:`strengthen 5i5h`  cmd_tail:`{cmd_tail}`")
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


        move_u = cmd_tail

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


    def wip(self, cmd_tail):
        """作りかけ

        指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
        これによって、その着手のポリシー値は下がる
        code: wip 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """

        if cmd_tail.strip() == '':
            print(f"weaken command must be 1 move.  ex:`wip 5i5h`.  cmd_tail:`{cmd_tail}`")
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
        weaken_move_u = cmd_tail
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
             weaken_pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_fo_index_and_relation_bit(
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
             weaken_pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_fo_index_and_relation_bit(
                    k_moves_u=[],
                    l_move_u_for_k_set=set(),
                    q_move_u_for_k_set=set(),
                    p_moves_u=[weaken_move_u],
                    l_move_u_for_p_set=weaken_l_move_u_set,
                    q_move_u_for_p_set=weaken_q_move_u_set,
                    turn=self._board.turn,
                    kifuwarabe=self,)

        for fo_index, relation_bit in weaken_kl_index_and_relation_bit_dictionary.items():
            print(f"  KL:{fo_index:6}  relation_bit:{relation_bit}")

        for fo_index, relation_bit in weaken_kq_index_and_relation_bit_dictionary.items():
            print(f"  KQ:{fo_index:6}  relation_bit:{relation_bit}")

        for fo_index, relation_bit in weaken_pl_index_and_relation_bit_dictionary.items():
            print(f"  PL:{fo_index:6}  relation_bit:{relation_bit}")

        for fo_index, relation_bit in weaken_pq_index_and_relation_bit_dictionary.items():
            print(f"  PQ:{fo_index:6}  relation_bit:{relation_bit}")

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

        (k_move_u_to_policy_dictionary,
         p_move_u_to_policy_dictionary) = MoveAndPolicyHelper.seleft_f_move_u_add_l_and_q(
                kl_move_u_and_policy_dictionary=kl_move_u_and_policy_dictionary,
                kq_move_u_and_policy_dictionary=kq_move_u_and_policy_dictionary,
                pl_move_u_and_policy_dictionary=pl_move_u_and_policy_dictionary,
                pq_move_u_and_policy_dictionary=pq_move_u_and_policy_dictionary)

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
                k_move_u_to_policy_dictionary=k_move_u_to_policy_dictionary,
                p_move_u_to_policy_dictionary=p_move_u_to_policy_dictionary,
                turn=board.turn)

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


    def seleft_f_move_u_add_l_and_q(
            kl_move_u_and_policy_dictionary,
            kq_move_u_and_policy_dictionary,
            pl_move_u_and_policy_dictionary,
            pq_move_u_and_policy_dictionary):
        """ＫＬとＫＱをマージしてＫにし、ＰＬとＰＱをマージしてＰにする"""

        k_move_u_to_policy_dictionary = {}
        p_move_u_to_policy_dictionary = {}

        #
        # Ｋ
        #

        for move_u, policy in kl_move_u_and_policy_dictionary.items():
            k_move_u_to_policy_dictionary[move_u] = policy

        for move_u, policy in kq_move_u_and_policy_dictionary.items():
            if move_u in k_move_u_to_policy_dictionary.keys():
                k_move_u_to_policy_dictionary[move_u] = (k_move_u_to_policy_dictionary[move_u] + policy) // 2
            else:
                k_move_u_to_policy_dictionary[move_u] = policy

        #
        # Ｐ
        #

        for move_u, policy in pl_move_u_and_policy_dictionary.items():
            p_move_u_to_policy_dictionary[move_u] = policy

        for move_u, policy in pq_move_u_and_policy_dictionary.items():
            if move_u in p_move_u_to_policy_dictionary.keys():
                p_move_u_to_policy_dictionary[move_u] = (p_move_u_to_policy_dictionary[move_u] + policy) // 2
            else:
                p_move_u_to_policy_dictionary[move_u] = policy

        return (k_move_u_to_policy_dictionary,
                p_move_u_to_policy_dictionary)


    def select_good_f_move_u_set(
            k_move_u_to_policy_dictionary,
            p_move_u_to_policy_dictionary,
            turn):
        """ポリシー値が 0.5 以上の着手と、それ以外の着手の２つのリストを返します

        Parameters
        ----------
        k_move_u_to_policy_dictionary : Dictionary<str, int>
            自玉の着手と、そのポリシー値を格納した辞書
        p_move_u_to_policy_dictionary : Dictionary<str, int>
            自兵の着手と、そのポリシー値を格納した辞書
        turn : int
            手番
        """

        number = 1

        # ポリシー値が 0.5 以上の指し手
        good_move_u_set = set()

        # ポリシー値が 0.5 未満の指し手
        bad_move_u_set = set()

        #
        # Ｋ
        #

        print('  自玉の着手のポリシー値一覧（Ｋ）：')
        for move_u, policy in k_move_u_to_policy_dictionary.items():
            print(f'    ({number:3})  turn:{Turn.to_string(turn)}  K:{move_u:5}  L:*****  policy:{policy:4}‰')

            if 500 <= policy:
                good_move_u_set.add(move_u)
            else:
                bad_move_u_set.add(move_u)

            number += 1

        #
        # Ｐ
        #

        print('  自兵の着手のポリシー値一覧（Ｐ）：')
        for move_u, policy in p_move_u_to_policy_dictionary.items():
            print(f'    ({number:3})  turn:{Turn.to_string(turn)}  P:{move_u:5}  L:*****  policy:{policy:4}‰')

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
    #select_mm_index_and_relation_bit
    @staticmethod
    def select_fo_index_and_relation_bit(
            k_moves_u,
            l_move_u_for_k_set,
            q_move_u_for_k_set,
            p_moves_u,
            l_move_u_for_p_set,
            q_move_u_for_p_set,
            turn,
            kifuwarabe):
        """着手と応手の関係を４つの辞書として取得

        第１階層の根と、第２階層の着手の葉と、第３階層の応手の葉から成る、ツリー構造になっているだろうから、
        それを、以下の４つの辞書に分ける

        （１）第２階層が自玉の着手、第３階層が敵玉の応手
        （２）第２階層が自玉の着手、第３階層が敵兵の応手
        （３）第２階層が自兵の着手、第３階層が敵玉の応手
        （４）第２階層が自兵の着手、第３階層が敵兵の応手

        ここで、第２階層の着手と、第３階層の着手の２つを合わせて１つのインデックスを作り、それをキーとする。
        値は、関係の有無を無いとき 0、有るときを 1 としたリレーション・ビットとする


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

                #
                # キー。fo_index
                #

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

                #
                # 値。relation bit
                #

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

        # 指し手と、ビット値を紐づける
        kl_index_and_relation_bit_dictionary = {}
        kq_index_and_relation_bit_dictionary = {}
        pl_index_and_relation_bit_dictionary = {}
        pq_index_and_relation_bit_dictionary = {}

        # ポリシー値を累計していく
        for k_move_u in k_moves_u:
            k_move_obj = Move.from_usi(k_move_u)

            # ＫＬ
            temp_dictionary = select_fo_index_and_relation_bit(
                    kind='KL',
                    f_move_obj=k_move_obj,
                    o_move_u_for_f_set=l_move_u_for_k_set)

            # 和集合
            kl_index_and_relation_bit_dictionary = kl_index_and_relation_bit_dictionary | temp_dictionary

            # ＫＱ
            temp_dictionary = select_fo_index_and_relation_bit(
                    kind='KQ',
                    f_move_obj=k_move_obj,
                    o_move_u_for_f_set=q_move_u_for_k_set)

            kq_index_and_relation_bit_dictionary = kq_index_and_relation_bit_dictionary | temp_dictionary

        for p_move_u in p_moves_u:
            p_move_obj = Move.from_usi(p_move_u)

            # ＰＬ
            temp_dictionary = select_fo_index_and_relation_bit(
                    kind='PL',
                    f_move_obj=p_move_obj,
                    o_move_u_for_f_set=l_move_u_for_p_set)

            pl_index_and_relation_bit_dictionary = pl_index_and_relation_bit_dictionary | temp_dictionary

            # ＰＱ
            temp_dictionary = select_fo_index_and_relation_bit(
                    kind='PQ',
                    f_move_obj=p_move_obj,
                    o_move_u_for_f_set=q_move_u_for_p_set)

            pq_index_and_relation_bit_dictionary = pq_index_and_relation_bit_dictionary | temp_dictionary

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
        """自玉の着手の一覧が渡されるので、
        各着手についてポリシー値が紐づいた辞書を作成する

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

        # 自軍の着手の集合を、自玉の着手の集合と、自兵の着手の集合に分ける
        k_moves_u, p_moves_u = MoveListHelper.create_k_and_p_legal_moves(
                legal_moves,
                board)

        print(f"  自玉の着手の一覧：")
        for move_u in k_moves_u:
            print(f"    turn:{Turn.to_string(board.turn)}  K:{move_u:5}")

        print(f"  自兵の着手の一覧：")
        for move_u in p_moves_u:
            print(f"    turn:{Turn.to_string(board.turn)}  P:{move_u:5}")

        #
        # 相手が指せる手の集合
        # -----------------
        #
        #   ヌルムーブをしたいが、 `board.push_pass()` が機能しなかったので、合法手を全部指してみることにする
        #

        # 自玉の着手に対する、敵玉（Lord）の応手の集合
        l_move_u_for_k_set = set()
        # 自玉の着手に対する、敵軍の玉以外の応手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_move_u_for_k_set = set()
        # 自軍の玉以外の着手に対する、敵玉（Lord）の応手の集合
        l_move_u_for_p_set = set()
        # 自軍の玉以外の着手に対する、敵軍の玉以外の応手の集合（Quaffer；ゴクゴク飲む人。Pの次の文字Qを頭文字にした単語）
        q_move_u_for_p_set = set()

        # 自玉に対する、敵玉の応手の一覧と、敵兵の応手の一覧を作成
        for move_u in k_moves_u:
            move_obj = Move.from_usi(move_u)

            (temp_l_move_u_for_k_set,
             temp_q_move_u_for_k_set) = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

            # 和集合を作成
            l_move_u_for_k_set = l_move_u_for_k_set.union(temp_l_move_u_for_k_set)
            q_move_u_for_k_set = q_move_u_for_k_set.union(temp_q_move_u_for_k_set)

        # 自兵に対する、敵玉の応手の一覧と、敵兵の応手の一覧を作成
        for move_u in p_moves_u:
            move_obj = Move.from_usi(move_u)

            (temp_l_move_u_for_p_set,
             temp_q_move_u_for_p_set) = BoardHelper.create_counter_move_u_set(
                    board=board,
                    move_obj=move_obj)

            # 和集合を作成
            l_move_u_for_p_set = l_move_u_for_p_set.union(temp_l_move_u_for_p_set)
            q_move_u_for_p_set = q_move_u_for_p_set.union(temp_q_move_u_for_p_set)

        print(f"  自玉に対する、敵玉の応手の一覧：")
        for move_u in l_move_u_for_k_set:
            print(f"    KL  turn:{Turn.to_string(board.turn)}  K:*****  L:{move_u}")

        print(f"  自玉に対する、敵兵の応手の一覧：")
        for move_u in q_move_u_for_k_set:
            print(f"    KL  turn:{Turn.to_string(board.turn)}  K:*****  Q:{move_u}")

        print(f"  自兵に対する、敵玉の応手の一覧：")
        for move_u in l_move_u_for_p_set:
            print(f"    PL  turn:{Turn.to_string(board.turn)}  P:*****  L:{move_u}")

        print(f"  自兵に対する、敵兵の応手の一覧：")
        for move_u in q_move_u_for_p_set:
            print(f"    PL  turn:{Turn.to_string(board.turn)}  P:*****  Q:{move_u}")

        #
        # 着手と応手の関係を全部取得
        # -----------------------
        #
        #   辞書。
        #   キーは、着手と応手の２つの通しインデックス。値は　関係が無ければ０，あれば１
        #
        (kl_index_and_relation_bit_dictionary,
         kq_index_and_relation_bit_dictionary,
         pl_index_and_relation_bit_dictionary,
         pq_index_and_relation_bit_dictionary) = EvaluationFacade.select_fo_index_and_relation_bit(
                k_moves_u=k_moves_u,
                l_move_u_for_k_set=l_move_u_for_k_set,
                q_move_u_for_k_set=q_move_u_for_k_set,
                p_moves_u=p_moves_u,
                l_move_u_for_p_set=l_move_u_for_p_set,
                q_move_u_for_p_set=q_move_u_for_p_set,
                turn=board.turn,
                kifuwarabe=kifuwarabe)

        print(f"  自玉の着手と、敵玉の応手の、関係の一覧（キー：ｆｏ＿ｉｎｄｅｘ，　値：関係ビット）：")
        for fo_index, relation_bit in kl_index_and_relation_bit_dictionary.items():
            (k_move_obj,
             l_move_obj) = EvaluationKkTable.destructure_kl_index(
                kl_index=fo_index)
            print(f"    KL  turn:{Turn.to_string(board.turn)}  kl_index:{fo_index:6}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_bit:{relation_bit}")

        print(f"  自玉の着手と、敵兵の応手の、関係の一覧：")
        for fo_index, relation_bit in kq_index_and_relation_bit_dictionary.items():
            print(f"    KQ  turn:{Turn.to_string(board.turn)}  kq_index:{fo_index:6}  relation_bit:{relation_bit}")

        print(f"  自兵の着手と、敵玉の応手の、関係の一覧：")
        for fo_index, relation_bit in pl_index_and_relation_bit_dictionary.items():
            print(f"    PL  turn:{Turn.to_string(board.turn)}  pl_index:{fo_index:6}  relation_bit:{relation_bit}")

        print(f"  自兵の着手と、敵兵の応手の、関係の一覧：")
        for fo_index, relation_bit in pq_index_and_relation_bit_dictionary.items():
            print(f"    PQ  turn:{Turn.to_string(board.turn)}  pq_index:{fo_index:6}  relation_bit:{relation_bit}")

        # 関係のキーをインデックスから着手へ変換
        (k_move_u_and_l_to_relation_number_dictionary,
         k_move_u_and_q_to_relation_number_dictionary,
         p_move_u_and_l_to_relation_number_dictionary,
         p_move_u_and_q_to_relation_number_dictionary) = EvaluationFacade.select_move_u_and_relation_number_group_by_move_u(
                kl_index_and_relation_bit_dictionary,
                kq_index_and_relation_bit_dictionary,
                pl_index_and_relation_bit_dictionary,
                pq_index_and_relation_bit_dictionary)

        print(f"  自玉の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：関係数）：")
        for f_move_u, relation_number in k_move_u_and_l_to_relation_number_dictionary.items():
            print(f"    KL  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  L:*****  relation_number:{relation_number:3}")

        print(f"  自玉の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：関係数）：")
        for f_move_u, relation_number in k_move_u_and_q_to_relation_number_dictionary.items():
            print(f"    KQ  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  Q:*****  relation_number:{relation_number:3}")

        print(f"  自兵の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：関係数）：")
        for f_move_u, relation_number in p_move_u_and_l_to_relation_number_dictionary.items():
            print(f"    PL  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  L:*****  relation_number:{relation_number:3}")

        print(f"  自兵の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：関係数）：")
        for f_move_u, relation_number in p_move_u_and_q_to_relation_number_dictionary.items():
            print(f"    PQ  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  Q:*****  relation_number:{relation_number:3}")

        #
        # 評価値テーブルを参照し、各指し手にポリシー値を付ける
        # ---------------------------------------------
        #
        #   ポリシー値は千分率の４桁の整数
        #
        (k_move_u_for_l_and_policy_dictionary,
         k_move_u_for_q_and_policy_dictionary,
         p_move_u_for_l_and_policy_dictionary,
         p_move_u_for_q_and_policy_dictionary) = EvaluationFacade.select_move_u_and_policy_permille_group_by_move_u(
                k_move_u_and_l_to_relation_number_dictionary=k_move_u_and_l_to_relation_number_dictionary,
                k_move_u_and_q_to_relation_number_dictionary=k_move_u_and_q_to_relation_number_dictionary,
                p_move_u_and_l_to_relation_number_dictionary=p_move_u_and_l_to_relation_number_dictionary,
                p_move_u_and_q_to_relation_number_dictionary=p_move_u_and_q_to_relation_number_dictionary)

        print(f"  自玉の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
        for f_move_u, policy in k_move_u_for_l_and_policy_dictionary.items():
            print(f"    KL  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  L:*****  policy:{policy:3}")

        print(f"  自玉の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
        for f_move_u, policy in k_move_u_for_q_and_policy_dictionary.items():
            print(f"    KQ  turn:{Turn.to_string(board.turn)}  K:{f_move_u:5}  Q:*****  policy:{policy:3}")

        print(f"  自兵の着手と、敵玉の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
        for f_move_u, policy in p_move_u_for_l_and_policy_dictionary.items():
            print(f"    PL  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  L:*****  policy:{policy:3}")

        print(f"  自兵の着手と、敵兵の応手の、関係の一覧（キー：着手，　値：ポリシー値）：")
        for f_move_u, policy in p_move_u_for_q_and_policy_dictionary.items():
            print(f"    PQ  turn:{Turn.to_string(board.turn)}  P:{f_move_u:5}  Q:*****  policy:{policy:3}")

        #
        # FIXME （まだ評価値テーブルができていないので）ダミー値の挿入
        #

        print(f"  ＫＱ　ダミーの自玉の着手を挿入（キー：ダミーの着手，　値：ポリシー値５００‰）：")
        for move_u in k_moves_u:
            print(f"    add  turn:{Turn.to_string(board.turn)}  K:{move_u:5}  Q:*****  policy: 500‰")
            k_move_u_for_q_and_policy_dictionary[move_u] = 500

        print(f"  ＰＬ　ダミーの自兵の着手を挿入（キー：ダミーの着手，　値：ポリシー値５００‰）：")
        for move_u in p_moves_u:
            print(f"    add  turn:{Turn.to_string(board.turn)}  P:{move_u:5}  L:*****  policy: 500‰")
            p_move_u_for_l_and_policy_dictionary[move_u] = 500

        print(f"  ＰＱ　ダミーの自兵の着手を挿入（キー：ダミーの着手，　値：ポリシー値５００‰）：")
        for move_u in p_moves_u:
            print(f"    add  turn:{Turn.to_string(board.turn)}  P:{move_u:5}  Q:*****  policy: 500‰")
            p_move_u_for_q_and_policy_dictionary[move_u] = 500

        # FIXME 同じ 5i4h でも、ＫＬとＫＱの２つあるといった状況になっているが、これでいいか？
        # TODO このあと、 good と bad に分けるときマージするか？

        return (k_move_u_for_l_and_policy_dictionary,
                k_move_u_for_q_and_policy_dictionary,
                p_move_u_for_l_and_policy_dictionary,
                p_move_u_for_q_and_policy_dictionary)


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
