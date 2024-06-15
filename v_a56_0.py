import cshogi
import datetime

#              python v_a56_0.py
from                  v_a56_0_eval.edit import EvaluationEdit
from                  v_a56_0_eval.kk import EvaluationKkTable
from                  v_a56_0_eval.kp import EvaluationKpTable
from                  v_a56_0_eval.pk import EvaluationPkTable
from                  v_a56_0_eval.pp import EvaluationPpTable
from                  v_a56_0_misc.choice_best_move import ChoiceBestMove
from                  v_a56_0_misc.game_result_document import GameResultDocument
from                  v_a56_0_misc.learn import LearnAboutOneGame
from                  v_a56_0_misc.lib import Turn, Move, MoveHelper, BoardHelper
engine_version_str = "v_a56_0"


########################################
# 設定
########################################

"""`engine_version_str` - 将棋エンジン・バージョン文字列。ファイル名などに使用"""

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

        # 対局結果ドキュメント
        self._game_result_document = None

        # 好手・悪手のランキングの階層数
        # TODO 探索部の choice_best_move では使ってるが、学習部の weaken, strongthen では使ってないので、全ての箇所で共通の処理になるようにしたい
        self._ranking_resolution = 10


    @property
    def board(self):
        return self._board


    @property
    def my_turn(self):
        return self._my_turn


    @property
    def game_result_document(self):
        """対局結果ドキュメント"""
        return self._game_result_document


    @property
    def ranking_resolution(self):
        """好手・悪手のランキングの階層数"""
        return self._ranking_resolution


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
            (result_str, reason) = self.playout(
                    is_debug=is_debug)

            position_command = BoardHelper.get_position_command(
                    board=self._board)

            print(f"""\
[{datetime.datetime.now()}] [playout]
{self._board}
    # result:{result_str}
    # reason:{reason}
    # move_number:{self._board.move_number} / max_move_number:{max_move_number}
    # {position_command}
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

        # 連続自己対局モード
        #       code: selfmatch
        elif head == 'selfmatch':
            self.selfmatch(
                    is_debug=is_debug)

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


    def load_eval_all_tables(
            self):
        print(f"[{datetime.datetime.now()}] [kifuwarabe > load eval all tables] start...")

        """評価値テーブル［0:先手, 1:後手］の読込"""
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

        print(f"[{datetime.datetime.now()}] [kifuwarabe > load eval all tables] finished")


    def load_game_result_file(
            self,
            is_debug=False):
        """対局結果ファイルの読込

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？
        """
        # 対局結果ドキュメント（デフォルト）
        self._game_result_document = GameResultDocument(
                file_stem=GameResultDocument.get_file_stem(engine_version_str))


    def usinewgame(
            self,
            is_debug=False):
        """新しい対局

        Parameters
        ----------
        is_debug : bool
            デバッグモードか？
        """

        # 評価値テーブルの読込
        self.load_eval_all_tables()

        # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
        self.save_eval_all_tables(
                is_debug=is_debug)

        # 対局結果ファイルの読込
        self.load_game_result_file(
                is_debug=is_debug)


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
        for move_u in moves_text_as_usi:
            self._board.push_usi(move_u)
            if is_debug:
                print(f"[kifuwarabe > position] done  M:{move_u:5}  board turn:{Turn.to_string(self._board.turn)}")

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
                print(f"[{datetime.datetime.now()}] [kifuwarabe > go] my turn.  board turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")
            else:
                print(f"[{datetime.datetime.now()}] [kifuwarabe > go] opponent turn.  board turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")

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
        best_move_str = ChoiceBestMove.do_it(
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
            コマンドの名前以外。 'draw', 'lose', 'win'
        """

        # 開始ログは出したい
        print(f"[{datetime.datetime.now()}] [gameover] start...")

        if cmd_tail.strip() == '':
            print(f"`do` command must be result.  ex:`gameover lose`  cmd_tail:`{cmd_tail}`")
            return

        # 持将棋
        if cmd_tail == 'draw':
            print(f"持将棋か～（ー＿ー） my turn:{self._my_turn}", flush=True)

            # ［対局結果］　常に記憶する
            self._game_result_document.add_and_save(
                    my_turn=self._my_turn,
                    result_str=cmd_tail,
                    reason='-',
                    board=self._board)

        # 負け
        elif cmd_tail == 'lose':
            print(f"あ～あ、 {self._my_turn} 番で負けたぜ（＞＿＜）", flush=True)

            # ［対局結果］　常に記憶する
            self._game_result_document.add_and_save(
                    my_turn=self._my_turn,
                    result_str=cmd_tail,
                    reason='-',
                    board=self._board)

        # 勝ち
        elif cmd_tail == 'win':
            print(f"やったぜ {self._my_turn} 番で勝ったぜ（＾ｑ＾）", flush=True)

            # ［対局結果］　常に記憶する
            self._game_result_document.add_and_save(
                    my_turn=self._my_turn,
                    result_str=cmd_tail,
                    reason='-',
                    board=self._board)

        # その他
        else:
            print(f"なんだろな（・＿・）？　'{cmd_tail}'  my turn:{self._my_turn}", flush=True)

            # ［対局結果］　常に記憶する
            self._game_result_document.add_and_save(
                    my_turn=self._my_turn,
                    result_str=cmd_tail,
                    reason='-',
                    board=self._board)

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
            print(f"[kifuwarabe > policy] my turn.  board turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")
        else:
            print(f"[kifuwarabe > policy] opponent turn.  board turn:{Turn.to_string(self._board.turn)}  my turn:{Turn.to_string(self._my_turn)}")

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
        # ランク付けされた指し手一覧（好手、悪手）
        # ----------------------------------
        #
        ranked_move_u_set_list = ChoiceBestMove.select_ranked_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self,
                is_debug=is_debug)

        for ranking, ranked_move_u_set in enumerate(ranked_move_u_set_list):
            print(f'  ランク付けされた指し手一覧（ranking:{ranking}）：')
            for ranked_move_u in ranked_move_u_set:
                print(f'    turn:{Turn.to_string(self._board.turn)}  ranking:{ranking}  F:{ranked_move_u:5}  O:*****')


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
        (black_k_black_l_index_to_relation_exists_dictionary,
         black_k_black_q_index_to_relation_exists_dictionary,
         black_p_black_l_index_to_relation_exists_dictionary,
         black_p_black_q_index_to_relation_exists_dictionary) = ChoiceBestMove.select_black_f_black_o_index_to_relation_exists(
                move_obj=Move.from_usi(move_u),
                is_king_move=is_king_move,
                board=self._board,
                kifuwarabe=self._kifuwarabe)

        #
        # 表示
        #
        if is_king_move:
            # ＫＬ
            for black_k_black_l_index, relation_exists in black_k_black_l_index_to_relation_exists_dictionary.items():

                black_k_move_obj, black_l_move_obj = EvaluationKkTable.build_black_k_black_l_moves_by_black_k_black_l_index(
                        black_k_black_l_index=black_k_black_l_index,
                        shall_k_white_to_black=self._board.turn==cshogi.WHITE,
                        shall_l_white_to_black=self._board.turn==cshogi.BLACK)

                print(f"  turn:{Turn.to_string(self._board.turn)}  black_k_black_l_index:{black_k_black_l_index:7}  K:{black_k_move_obj.as_usi:5}  L:{black_l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＫＱ
            for black_k_black_q_index, relation_exists in black_k_black_q_index_to_relation_exists_dictionary.items():

                black_k_move_obj, black_q_move_obj = EvaluationKpTable.build_black_k_black_p_moves_by_black_k_black_p_index(
                        kp_index=black_k_black_q_index,
                        shall_k_white_to_black=self._board.turn==cshogi.WHITE,
                        shall_p_white_to_black=self._board.turn==cshogi.BLACK)

                print(f"  turn:{Turn.to_string(self._board.turn)}  black_k_black_q_index:{black_k_black_q_index:7}  K:{black_k_move_obj.as_usi:5}  Q:{black_q_move_obj.as_usi:5}  relation_exists:{relation_exists}")

        else:
            # ＰＬ
            for black_p_black_l_index, relation_exists in black_p_black_l_index_to_relation_exists_dictionary.items():

                display_black_p_move_obj, display_black_l_move_obj = EvaluationPkTable.build_black_p_black_k_moves_by_black_p_black_k_index(
                        pk_index=black_p_black_l_index,
                        shall_p_white_to_black=self._board.turn==cshogi.WHITE,
                        shall_k_white_to_black=self._board.turn==cshogi.BLACK)

                print(f"  turn:{Turn.to_string(self._board.turn)}  black_p_black_l_index:{black_p_black_l_index:7}  P:{display_black_p_move_obj.as_usi:5}  L:{display_black_l_move_obj.as_usi:5}  relation_exists:{relation_exists}")

            # ＰＱ
            for black_p_black_q_index, relation_exists in black_p_black_q_index_to_relation_exists_dictionary.items():

                display_black_p_move_obj, display_black_q_move_obj = EvaluationPpTable.build_black_p1_black_p2_moves_by_black_p1_black_p2_index(
                        pq_index=black_p_black_q_index,
                        # black_p_black_q_index は両方先手のインデックスなので、これ以上変更しません
                        shall_p1_white_to_black=False,
                        shall_p2_white_to_black=False)

                print(f"  turn:{Turn.to_string(self._board.turn)}  black_p_black_q_index:{black_p_black_q_index:7}  P:{display_black_p_move_obj.as_usi:5}  Q:{display_black_q_move_obj.as_usi:5}  relation_exists:{relation_exists}")


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
        reason : str
            'max_move', 'resign', 'nyugyoku_win', 'max_playout_depth'
        """

        # 学習中以外はログを出したい
        if not is_in_learn:
            print(f'[{datetime.datetime.now()}] [playout] start...')

        if max_playout_depth is None:
            max_playout_depth = max_move_number - self._board.move_number + 1

        def playout_local():
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
                best_move_str = ChoiceBestMove.do_it(
                        legal_moves=list(self._board.legal_moves),
                        board=self._board,
                        kifuwarabe=self)

                if is_debug:
                    print(f"[{datetime.datetime.now()}] [playout] best_move:{best_move_str:5}")

                # 一手指す
                self._board.push_usi(best_move_str)


            # プレイアウト深さ上限
            return 'max_playout_depth'

        reason = playout_local()

        if not self._board.is_game_over():
            return ('draw', reason)

        if self._board.turn == self.my_turn:
            return ('lose', reason)

        return ('win', reason)


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
        LearnAboutOneGame(
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


    def selfmatch(
            self,
            is_debug=False):
        """連続自己対局
        code: selfmatch
        """
        print(f"[{datetime.datetime.now()}] [selfmatch] start...")

        self.usi()

        self.isready()

        # 無限ループ
        while True:

            self.usinewgame()

            self.position(
                    cmd_tail="startpos")

            (result_str, reason) = self.playout(
                    is_debug=is_debug)

            self.gameover(
                    cmd_tail=result_str)

            print(f"[{datetime.datetime.now()}] [selfmatch] repeat")


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
