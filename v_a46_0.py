# python v_a46_0.py
import cshogi
import datetime
import random
from v_a46_0_eval.facade import EvaluationFacade
from v_a46_0_eval.edit import EvaluationEdit
from v_a46_0_eval.kk import EvaluationKkTable
from v_a46_0_eval.kp import EvaluationKpTable
from v_a46_0_eval.pk import EvaluationPkTable
from v_a46_0_eval.pp import EvaluationPpTable
from v_a46_0_learn import Learn
from v_a46_0_lib import Turn, Move, MoveHelper, BoardHelper, GameResultFile


########################################
# 設定
########################################

engine_version_str = "v_a46_0"
"""将棋エンジン・バージョン文字列。ファイル名などに使用"""

max_move_number = 512
"""手数上限"""


########################################
# 有名な定数
########################################

# [コンピュータ将棋基礎情報研究所 > 一局面の合法手の最大数が593手であることの証明](http://lfics81.techblog.jp/archives/2041940.html)
#max_legal_move_number = 593


########################################
# USI ループ
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

        # ＫＱ評価値テーブル　[0:先手, 1:後手]
        self._evaluation_kq_table_obj_array = [
            EvaluationKpTable(
                    engine_version_str=engine_version_str),
            EvaluationKpTable(
                    engine_version_str=engine_version_str),
        ]

        # ＰＬ評価値テーブル　[0:先手, 1:後手]
        self._evaluation_pl_table_obj_array = [
            EvaluationPkTable(
                    engine_version_str=engine_version_str),
            EvaluationPkTable(
                    engine_version_str=engine_version_str),
        ]

        # ＰＱ評価値テーブル　[0:先手, 1:後手]
        self._evaluation_pq_table_obj_array = [
            EvaluationPpTable(
                    engine_version_str=engine_version_str),
            EvaluationPpTable(
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


    @property
    def evaluation_kq_table_obj_array(self):
        """ＫＱ評価値テーブル　[0:先手, 1:後手]"""
        return self._evaluation_kq_table_obj_array


    @property
    def evaluation_pl_table_obj_array(self):
        """ＰＬ評価値テーブル　[0:先手, 1:後手]"""
        return self._evaluation_pl_table_obj_array


    @property
    def evaluation_pq_table_obj_array(self):
        """ＰＰ評価値テーブル　[0:先手, 1:後手]"""
        return self._evaluation_pq_table_obj_array


    def usi_loop(self):
        """ＵＳＩループ"""

        while True:
            result_str = self.usi_sequence(
                    command_str=input())

            if result_str == 'quit':
                break

        print(f"[{datetime.datetime.now()}] end of USI loop")


    def usi_sequence(
            self,
            command_str,
            is_debug=False):
        """ＵＳＩシーケンス

        Parameters
        ----------
        command_str : str
            コマンド
        is_debug : bool
            デバッグモード
        """

        #
        # 入力
        #
        #   全部バラバラにすると position コマンドとか解析しにくいので、コマンド名とそれ以外で分ける
        #
        head_tail = command_str.split(' ', 1)
        if is_debug:
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
            self.usinewgame(
                    is_debug=is_debug)

        # 局面データ解析
        elif head == 'position':
            self.position(
                    cmd_tail=tail)

        # 思考開始～最善手返却
        elif head == 'go':
            self.go(
                    is_debug=is_debug)

        # 中断
        elif head == 'stop':
            self.stop()

        # 対局終了
        elif head == 'gameover':
            self.gameover(
                    cmd_tail=tail,
                    is_debug=is_debug)

        # アプリケーション終了
        elif head == 'quit':
            return 'quit'

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
            self.policy(
                    is_debug=is_debug)

        # 指定の手の評価値テーブルの関係を全て表示する
        #       code: relation 7g7f
        elif head == 'relation':
            self.relation(
                    cmd_tail=tail)

        # 指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が無いようにする。
        # これによって、その着手のポリシー値は下がる
        #       code: weaken 5i5h
        elif head == 'weaken':
            result_str = self.weaken(
                    cmd_tail=tail,
                    is_debug=is_debug)

            print(f"[weaken] result=`{result_str}`")

        # 指定の着手の評価値テーブルについて、関連がある箇所を（適当に選んで）、それを関連が有るようにする。
        # これによって、その着手のポリシー値は上がる
        #       code: strengthen 5i5h
        elif head == 'strengthen':
            result_str = self.strengthen(
                    cmd_tail=tail,
                    is_debug=is_debug)

            print(f"[strengthen] result=`{result_str}`")

        # プレイアウト
        #       code: playout
        elif head == 'playout':
            result_str = self.playout(
                    is_debug=is_debug)

            position_command = BoardHelper.get_position_command(
                    board=self._board)

            print(f"""\
[{datetime.datetime.now()}] [playout] result:`{result_str}`
{self._board}
#move_number:{self._board.move_number} / max_move_number:{max_move_number}
#{position_command}
""",
                    flush=True)

        # 学習
        elif head == 'learn':
            self.learn(
                    is_debug=is_debug)

        # 局面表示
        #       code: board
        elif head == 'board':
            self.print_board()

        # sfen 表示
        #       code: sfen
        elif head == 'sfen':
            self.print_sfen()

        # デバッグモード
        #       code: debug position startpos
        elif head == 'debug':
            self.debug(
                    cmd_tail=tail)

        return ''


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


    def save_eval_all_tables(
            self,
            is_debug=False):
        """（変更があれば）ＫＬ評価値テーブル［0:先手, 1:後手］の保存

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？
        """
        for turn in [cshogi.BLACK, cshogi.WHITE]:
            turn_index = Turn.to_index(turn)

            # ＫＬ
            if self._evaluation_kl_table_obj_array[turn_index].mm_table_obj.is_file_modified:
                print(f"[{datetime.datetime.now()}] kl file save...  turn:{Turn.to_string(turn)}", flush=True)
                self._evaluation_kl_table_obj_array[turn_index].save_kk_evaluation_table_file(
                        is_debug=is_debug)

            else:
                print(f"[{datetime.datetime.now()}] kl file not changed.  turn:{Turn.to_string(turn)}", flush=True)

            # ＫＱ
            if self._evaluation_kq_table_obj_array[turn_index].mm_table_obj.is_file_modified:
                print(f"[{datetime.datetime.now()}] kq file save...  turn:{Turn.to_string(turn)}", flush=True)
                self._evaluation_kq_table_obj_array[turn_index].save_kp_evaluation_table_file(
                        is_debug=is_debug)

            else:
                print(f"[{datetime.datetime.now()}] kq file not changed.  turn:{Turn.to_string(turn)}", flush=True)

            # ＰＬ
            if self._evaluation_pl_table_obj_array[turn_index].mm_table_obj.is_file_modified:
                print(f"[{datetime.datetime.now()}] pl file save...  turn:{Turn.to_string(turn)}", flush=True)
                self._evaluation_pl_table_obj_array[turn_index].save_pk_evaluation_table_file(
                        is_debug=is_debug)

            else:
                print(f"[{datetime.datetime.now()}] pl file not changed.  turn:{Turn.to_string(turn)}", flush=True)

            # ＰＱ
            if self._evaluation_pq_table_obj_array[turn_index].mm_table_obj.is_file_modified:
                print(f"[{datetime.datetime.now()}] pp file save...  turn:{Turn.to_string(turn)}", flush=True)
                self._evaluation_pq_table_obj_array[turn_index].save_pp_evaluation_table_file(
                        is_debug=is_debug)

            else:
                print(f"[{datetime.datetime.now()}] pp file not changed.  turn:{Turn.to_string(turn)}", flush=True)


    def usinewgame(
            self,
            is_debug=False):
        """新しい対局

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？
        """

        # 評価値テーブル［0:先手, 1:後手］の読込
        for turn in [cshogi.BLACK, cshogi.WHITE]:
            turn_index = Turn.to_index(turn)

            # ＫＬ
            self._evaluation_kl_table_obj_array[turn_index].load_on_usinewgame(
                    turn=turn)

            # ＫＱ
            self._evaluation_kq_table_obj_array[turn_index].load_on_usinewgame(
                    turn=turn)

            # ＰＬ
            self._evaluation_pl_table_obj_array[turn_index].load_on_usinewgame(
                    turn=turn)

            # ＰＰ
            self._evaluation_pq_table_obj_array[turn_index].load_on_usinewgame(
                    turn=turn)

        # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
        self.save_eval_all_tables(
                is_debug=is_debug)

        # 対局結果ファイル（デフォルト）
        self._game_result_file = GameResultFile(
                engine_version_str=engine_version_str)

        # 読取
        game_result_lines = self._game_result_file.read_lines()

        if is_debug:
            for line in game_result_lines:
                print(f"[{datetime.datetime.now()}] [usinewgame] game result line:[{line}]")

        if 2 <= len(game_result_lines):
            #(win_lose_etc, result_turn) = game_result_lines[0].split(' ')
            position_command = game_result_lines[1]
            head_tail = position_command.split(' ', 1)

            self.position(
                    cmd_tail=head_tail[1],
                    is_debug=is_debug)

            # 学習する。
            # 開始ログは出したい
            print(f"[{datetime.datetime.now()}] [usinewgame] learn start...", flush=True)

            self.learn(
                    is_debug=is_debug)

            # 終了ログは出したい
            print(f"[{datetime.datetime.now()}] [usinewgame] learn end", flush=True)


    def position(
            self,
            cmd_tail,
            is_debug=False):
        """局面データ解析

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        is_debug : bool
            デバッグモードか？
        """

        board_and_moves = cmd_tail.split('moves')
        board_str = board_and_moves[0].strip()

        # `moves` で分割できたなら
        if len(board_and_moves) > 1:
            moves_str = board_and_moves[1].strip()
            if is_debug:
                print(f"[kifuwarabe > position] moves:`{moves_str}`")

            # 区切りは半角空白１文字とします
            moves_text_as_usi = moves_str.split(' ')
        else:
            moves_text_as_usi = []

        if is_debug:
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
            if is_debug:
                print(f"[kifuwarabe > position] done  M:{move_as_usi:5}  board turn:{Turn.to_string(self._board.turn)}")

        # 現局面の手番を、自分の手番とする
        self._my_turn = self._board.turn
        if is_debug:
            print(f"[kifuwarabe > position] my turn is {Turn.to_string(self._my_turn)}")


    def go(
            self,
            is_debug=False):
        """思考開始～最善手返却

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？
        """

        if is_debug:
            # 自分の手番と、局面の手番が一致なら自分のターン
            if self._board.turn == self._my_turn:
                print(f"[{datetime.datetime.now()}] [kifuwarabe > go] my turn.  board.turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")
            else:
                print(f"[{datetime.datetime.now()}] [kifuwarabe > go] opponent turn.  board.turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")

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

        # １手詰めを詰める
        if not self._board.is_check():
            """自玉に王手がかかっていない時で"""

            if (matemove := self._board.mate_move_in_1ply()):
                """１手詰めの指し手があれば、それを取得"""

                best_move = cshogi.move_to_usi(matemove)
                print('info score mate 1 pv {}'.format(best_move), flush=True)
                print(f'bestmove {best_move}', flush=True)
                return

        # くじを引く（投了のケースは対応済みなので、ここで対応しなくていい）
        best_move_str = Lottery.choice_best(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self,
                is_debug=is_debug)

        print(f"info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move")
        print(f'bestmove {best_move_str}', flush=True)


    def stop(self):
        """中断"""
        print('bestmove resign', flush=True)


    def gameover(
            self,
            cmd_tail,
            is_debug=False):
        """対局終了

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外
        """

        # 開始ログは出したい
        print(f"[{datetime.datetime.now()}] [gameover] start...")

        if cmd_tail.strip() == '':
            print(f"`do` command must be result.  ex:`gameover lose`  cmd_tail:`{cmd_tail}`")
            return

        # 負け
        if cmd_tail == 'lose':
            if self._my_turn is None:
                raise ValueError(f'unexpected my turn:{Turn.to_string(self._my_turn)}')

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

        # 終了ログは出したい
        print(f"[{datetime.datetime.now()}] [gameover] end", flush=True)


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


    def policy(
            self,
            is_debug=False):
        """現局面のポリシー値を確認する
            code: policy

        Parameters
        ----------
        is_debug : bool
            デバッグか？
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

        # １手詰めを詰める
        #
        #   自玉に王手がかかっていない時で
        #
        if not self._board.is_check():

            # １手詰めの指し手があれば、それを取得
            if (matemove := self._board.mate_move_in_1ply()):

                best_move = cshogi.move_to_usi(matemove)
                print(f'  # bestmove {best_move} (mate)', flush=True)
                return

        #
        # 好手、悪手一覧
        # ------------
        #
        (good_move_u_set,
         bad_move_u_set) = EvaluationFacade.select_good_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self,
                is_debug=is_debug)

        print(f'  好手一覧：')
        for move_u in good_move_u_set:
            print(f'    turn:{Turn.to_string(self._board.turn)}  F:{move_u:5}  O:*****  is good')

        print(f'  悪手一覧：')
        for move_u in bad_move_u_set:
            print(f'    turn:{Turn.to_string(self._board.turn)}  F:{move_u:5}  O:*****  is bad')


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

        move_obj = Move.from_usi(move_u)

        k_sq = BoardHelper.get_king_square(self._board)

        # 自玉の指し手か？
        is_king_move = MoveHelper.is_king(k_sq, move_obj)

        # 着手と応手をキー、関係の有無を値とする辞書を作成します
        (kl_index_to_relation_exists_dictionary,
         kq_index_to_relation_exists_dictionary,
         pl_index_to_relation_exists_dictionary,
         pq_index_to_relation_exists_dictionary) = EvaluationFacade.select_fo_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                is_king_move=is_king_move,
                board=self._board,
                kifuwarabe=self._kifuwarabe)

        #
        # 表示
        #
        if is_king_move:
            # ＫＬ
            for kl_index, relation_exists in kl_index_to_relation_exists_dictionary.items():

                k_move_obj, l_move_obj = EvaluationKkTable.destructure_kl_index(
                        kl_index=kl_index,
                        k_turn=self._board.turn)

                print(f"  turn:{Turn.to_string(self._board.turn)}  kl_index:{kl_index:7}  K:{k_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＫＱ
            for kq_index, relation_exists in kq_index_to_relation_exists_dictionary.items():

                k_move_obj, q_move_obj = EvaluationKpTable.destructure_kp_index(
                        kp_index=kq_index,
                        k_turn=self._board.turn)

                print(f"  turn:{Turn.to_string(self._board.turn)}  kq_index:{kq_index:7}  K:{k_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        else:
            # ＰＬ
            for pl_index, relation_exists in pl_index_to_relation_exists_dictionary.items():

                p_move_obj, l_move_obj = EvaluationPkTable.destructure_pk_index(
                        pk_index=pl_index,
                        p_turn=self._board.turn)

                print(f"  turn:{Turn.to_string(self._board.turn)}  pl_index:{pl_index:7}  P:{p_move_obj.as_usi:5}  L:{l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＰＱ
            for pq_index, relation_exists in pq_index_to_relation_exists_dictionary.items():

                p_move_obj, q_move_obj = EvaluationPpTable.destructure_pp_index(
                        pq_index=pq_index,
                        p1_turn=self._board.turn)

                print(f"  turn:{Turn.to_string(self._board.turn)}  pq_index:{pq_index:7}  P:{p_move_obj.as_usi:5}  Q:{q_move_obj.as_usi:5}  relation_exists:{relation_exists}")


    def weaken(
            self,
            cmd_tail,
            is_debug=False):
        """評価値テーブルの調整。
        指定の着手のポリシー値が 0.5 未満になるよう価値値テーブルを調整する。
        code: weaken 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外

        Returns
        -------
        result_str : str
            'failed', 'changed', 'keep'
        """

        if cmd_tail.strip() == '':
            if is_debug:
                print(f"[{datetime.datetime.now()}] [weaken] weaken command must be 1 move.  ex:`weaken 5i5h`  cmd_tail:`{cmd_tail}`")
            return 'failed'

        return EvaluationEdit(
                board=self._board,
                kifuwarabe=self
        ).weaken(
                move_u=cmd_tail,
                is_debug=is_debug)


    def strengthen(
            self,
            cmd_tail,
            is_debug=False):
        """評価値テーブルの調整。
        指定の着手のポリシー値が 0.5 以上になるよう評価値テーブルを調整する。
        code: strengthen 5i5h

        Parameters
        ----------
        cmd_tail : str
            コマンドの名前以外

        Returns
        -------
        result_str : str
            'failed', 'changed', 'keep'
        """

        if cmd_tail.strip() == '':
            if is_debug:
                print(f"[{datetime.datetime.now()}] [strengthen] strengthen command must be 1 move.  ex:`strengthen 5i5h`  cmd_tail:`{cmd_tail}`")
            return 'failed'

        return EvaluationEdit(
                board=self._board,
                kifuwarabe=self
        ).strengthen(
                move_u=cmd_tail,
                is_debug=is_debug)


    def playout(
            self,
            is_in_learn=False,
            max_playout_depth=None,
            is_debug=False):
        """プレイアウト
        現局面から、投了局面になるまで、適当に指します

        Parameters
        ----------
        is_in_learn : bool
            学習中
        max_playout_depth : int
            プレイアウトする手数。無制限なら None
        is_debug : bool
            デバッグ中

        Returns
        -------
        result : str
            'max_move', 'resign', 'nyugyoku_win', 'max_playout_depth'
        """

        # 学習中以外はログを出したい
        if not is_in_learn:
            print(f'[{datetime.datetime.now()}] [playout] start...')

        if max_playout_depth is None:
            max_playout_depth = max_move_number - self._board.move_number + 1

        for _playout_depth in range(0, max_playout_depth):

            # 手数上限
            if max_move_number <= self._board.move_number:
                return 'max_move'

            # 投了局面時
            if self._board.is_game_over():
                return 'resign'

            # 入玉勝利宣言局面時
            if self._board.is_nyugyoku():
                return 'nyugyoku_win'

            # （評価値テーブルの内容だけで対局したい用途で使う想定なので）プレイアウト中は１手詰めルーチンを使わない

            # くじを引く（投了のケースは対応済みなので、ここで対応しなくていい）
            best_move_str = Lottery.choice_best(
                    legal_moves=list(self._board.legal_moves),
                    board=self._board,
                    kifuwarabe=self)

            if is_debug:
                print(f"[{datetime.datetime.now()}] [playout] best_move:{best_move_str:5}")

            # 一手指す
            self._board.push_usi(best_move_str)


        # プレイアウト深さ上限
        return 'max_playout_depth'


    def learn(
            self,
            is_debug=False):
        """学習

        `playout` してから `learn ` する想定です

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？
        """

        # 学習する
        Learn(
                board=self._board,
                kifuwarabe=self,
                is_debug=is_debug).learn_it()


    def print_board(self):
        """局面表示"""
        print(self._board)


    def print_sfen(self):
        """sfen 表示"""
        print(self._board.sfen())


    def debug(self, cmd_tail):
        """デバッグモード
        code: debug position startpos

        `debug quit` では quit しないので注意

        Parameters
        ----------
        cmd_tail : str
            残りのコマンド文字列
        """
        result_str = self.usi_sequence(
                command_str=cmd_tail,
                is_debug=True)


########################################
# くじ引き階層
########################################

class Lottery():


    @staticmethod
    def choice_best(
            legal_moves,
            board,
            kifuwarabe,
            is_debug=False):
        """くじを引く

        Parameters
        ----------
        legal_moves : list<int>
            合法手のリスト : cshogi の指し手整数
        board : Board
            局面
        kifuwarabe : Kifuwarabe
            評価値テーブルを持っている
        is_debug : bool
            デバッグモードか？
        """

        (good_move_u_set,
         bad_move_u_set) = EvaluationFacade.select_good_f_move_u_set_facade(
                legal_moves=legal_moves,
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        # 候補手の中からランダムに選ぶ。USIの指し手の記法で返却
        if 0 < len(good_move_u_set):
            return random.choice(list(good_move_u_set))

        # 何も指さないよりは、悪手を指した方がマシ
        else:
            return random.choice(list(bad_move_u_set))


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
