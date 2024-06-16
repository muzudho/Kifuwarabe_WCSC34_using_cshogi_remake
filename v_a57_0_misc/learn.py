import cshogi
import datetime
import random

from v_a57_0_debug_plan import DebugPlan
from v_a57_0_misc.choice_best_move import ChoiceBestMove
from v_a57_0_misc.lib import Turn, Move, BoardHelper


class LearnAboutOneGame():
    """学習部

    対局データ１つを与えると、そこから学習する
    """


    def __init__(
            self,
            board,
            kifuwarabe,
            learn_config_document,
            is_debug):
        """初期化

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe:
            きふわらべ
        learn_config_document : LearnConfigDocument
            学習設定ドキュメント
        is_debug : bool
            デバッグモードか？
        """

        self._board = board
        self._kifuwarabe = kifuwarabe
        self._learn_config_document = learn_config_document
        self._is_debug = is_debug

        self._init_position_sfen = None
        self._principal_history = None
        self._end_position_sfen = None

        self._won_player_turn = None
        """勝った方の手番"""

        self._lost_player_turn = None
        """負けた方の手番"""


    def is_learn_by_rate(self):
        """全ての指し手の良し悪しを検討していると、全体を見る時間がなくなるから、
        間引くのに使う"""

        # 次の対局の usinewgame のタイミングで、前の対局の棋譜をトレーニングデータにして機械学習を走らせるから、持ち時間を消費してしまう。
        # 平均合法手が 80 手と仮定して、 80分の1 にすれば、 1 手当たり 1 つの合法手を検討する間隔になって早く終わるだろう
        # 分子
        numerator = self._learn_config_document.learn_rate_numerator #1
        denominator = self._learn_config_document.learn_rate_denominator #80
        return random.randint(0,denominator) <= (numerator - 1)


    def restore_end_position(self):
        """終局図の内部データに進める"""

        #if is_debug:
        #    print(f"[{datetime.datetime.now()}] [learn] restore_end_position start...")
        # 初期局面
        self._board.set_sfen(self._init_position_sfen)

        # 棋譜再生
        for move_id in self._principal_history:
            self._board.push(move_id)

        # 戻せたかチェック
        if self._board.sfen() != self._end_position_sfen:
            # 終局図の表示
            print(f"[{datetime.datetime.now()}] [learn] 局面巻き戻しエラー")
            print(self._board)
            print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
            raise ValueError("局面巻き戻しエラー")

        #if is_debug:
        #    print(f"[{datetime.datetime.now()}] [learn] restore_end_position end.")


    def learn_it(self):
        """それを学習する"""

        # 開始ログは出したい
        print(f'[{datetime.datetime.now()}] [learn > learn_it] start...')

        # 終局図の sfen を取得。巻き戻せたかのチェックに利用
        self._end_position_sfen = self._board.sfen()

        # 負けてた方の手番
        self._lost_player_turn = self._board.turn

        # 勝ってた方の手番
        self._won_player_turn = Turn.flip(self._lost_player_turn)

        ## 終局図とその sfen はログに出したい
        #print(f"[{datetime.datetime.now()}] [learn > learn_it] 終局図：")
        #print(self._board)

        #        # 現局面の position コマンドを表示
        #        print(f"""[{datetime.datetime.now()}] [learn > learn_it]
        #    # board move_number:{self._board.move_number}
        #    # {BoardHelper.get_position_command(board=self._board)}
        #""")

        # 戻せたかチェック
        if self._board.sfen() != self._end_position_sfen:
            # 終局図の表示
            print(f"""[{datetime.datetime.now()}] [learn > learn_it] 局面巻き戻しエラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
            raise ValueError("局面巻き戻しエラー")

        # 本譜の指し手を覚えておく。ログにも出したい
        self._principal_history = self._board.history

        # （あとで元の position の内部状態に戻すために）初期局面まで巻き戻し、初期局面を覚えておく
        while 1 < self._board.move_number:
            # １手戻す
            #if is_debug:
            #    print(f"[{datetime.datetime.now()}] [learn] undo to init  board.move_number:{board.move_number}")

            self._board.pop()

        # （あとで元の position の内部状態に戻すために）初期局面を覚えておく
        self._init_position_sfen = self._board.sfen()

        # 初期局面をログに出したい。 position は文字量が多くなるので出さない
        print(f"""[{datetime.datetime.now()}] [learn] 初期局面図：
{self._board}
    # board.move_number:{self._board.move_number}
""")

        # 終局図の内部データに進める
        self.restore_end_position()

        # 終局局面の手数
        self._move_number_at_end = self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] move_number_at_end:{self._move_number_at_end}")

        mate = 1

        max_depth = self._move_number_at_end

        # プレイアウトが遅いので仕方なく、全ての着手をさかのぼると時間がかかるので、上限を決めておく
        #if 16 < max_depth:
        #    max_depth = 16

        # ３手詰めを３手で詰める必要はなく、５手必至でも良い手と言えるので（ただの詰み逃しかもしれないが）、そのような場合 5-3 で、 attack_extension=2 とします
        attack_extension = 10
        # ２手詰めを４手詰めまで引き延ばせれば、逃げるのが上手くなったと言えるので、そのような場合 4-2 で、 escape_extension=2 とします
        escape_extension = 30

        while mate <= max_depth:

            #
            # 奇数：　詰める方
            # --------------
            #
            (result_str,
             changed_count) = self.at_position(
                    mate=mate,
                    playout_extension_depth=mate+attack_extension)

            mate += 1

            if self._move_number_at_end < mate or result_str == 'can not rewind':
                break

            #
            # 偶数：　逃げる方
            # --------------
            #
            (result_str,
             changed_count) = self.at_position(
                    mate=mate,
                    playout_extension_depth=mate+escape_extension)

            mate += 1

            if self._move_number_at_end < mate or result_str == 'can not rewind':
                break

            #
            # ２０手毎にコマメに保存する
            #
            #   mate = 1 から始まることに注意
            #
            if mate % 20 == 1:
                # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
                self._kifuwarabe.save_eval_all_tables(
                        is_debug=self._is_debug)

        #
        # おわり
        # -----
        #

        # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
        self._kifuwarabe.save_eval_all_tables(
                is_debug=self._is_debug)

        # 終局図の内部データに進める
        self.restore_end_position()

        print(f"[{datetime.datetime.now()}] [learn] finished", flush=True)


    def at_position(
            self,
            mate,
            playout_extension_depth):
        """奇数。詰める方

        Parameters
        ----------
        mate : int
            ｎ手詰め
        playout_extension_depth : int
            プレイアウトでの延長手数
        """

        changed_count = 0

        # 棋譜を巻き戻せないなら、学ぶことはできません
        if self._board.move_number < mate + 1:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方] ignored. you cannot learn. short moves. board.move_number:{self._board.move_number}')
            return ('can not rewind', changed_count)

        # 終局図の内部データに進める
        self.restore_end_position()

        # ｎ手詰めの局面まで戻す
        last_move_id = None
        for _i in range(0, mate):
            last_move_id = self._board.pop()

        last_move_u = cshogi.move_to_usi(last_move_id)
        #last_move_obj = Move.from_usi(last_move_u)

        # ｎ手詰めの局面図の sfen
        sfen_at_mate = self._board.sfen()
        turn_at_problem = self._board.turn
        move_number_at_problem = self._board.move_number
        move_number_between_end_and_problem = self._move_number_at_end - move_number_at_problem

        # 終局局面までの手数
        self._move_number_to_end = self._move_number_at_end - self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] [learn > at position] move_number_to_end:{self._move_number_to_end} = move_number_at_end:{self._move_number_at_end} - board.move_number:{self._board.move_number}")

        #
        # 階位（ｔｉｅｒ）付けされた指し手一覧
        # -------------------------------
        #
        tiered_move_u_set_list = ChoiceBestMove.select_ranked_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        print(f'[{datetime.datetime.now()}] [learn > at position]  mate:{mate}  ランク別着手数：', end='')
        size_list = []
        sum_size = 0
        for tier, ranked_move_u_set in enumerate(tiered_move_u_set_list):
            set_size = len(ranked_move_u_set)
            size_list.append(set_size)
            sum_size += set_size
            print(f'    [{tier:2}位 {set_size}]', end='')

        print(f'  累計：{sum_size}', flush=True)

        for tier, ranked_move_u_set in enumerate(tiered_move_u_set_list):
            choice_num = 0

            if self._is_debug:
                print(f'[{datetime.datetime.now()}] [learn > at position]  着手{tier:2}位一覧')

            for move_u in ranked_move_u_set:

                # カウンターは事前に進める
                choice_num += 1

                # 本譜の指し手は必ず学習する
                if move_u == last_move_u:
                    pass

                # mate が 4 以上の局面は、学習率くじで当たった指し手だけ学習する
                elif 4 <= mate and not self.is_learn_by_rate():
                    continue

                # 弱化・強化するフラグ
                shall_1_weaken_2_strongthen = 0

                # ｎ手詰め局面図かチェック
                if self._board.sfen() != sfen_at_mate:
                    # エラー時
                    print(f"""[{datetime.datetime.now()}] [learn > at position] {tier:2}位  {mate}手詰め局面図エラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
                    raise ValueError(f"[learn > at position] {tier:2}位  {mate}手詰め局面図エラー")

                # （ｎ手詰め局面図で）とりあえず一手指す
                self._board.push_usi(move_u)

                # 指し継ぎ手数           = (投了局面手数　－　学習局面手数       ) + プレイアウトでの延長手数    - 指した１手分
                move_number_difference = move_number_between_end_and_problem + playout_extension_depth - 1

                # プレイアウトする
                (result_str, reason) = self._kifuwarabe.playout(
                        is_in_learn=True,
                        # １手指した分引く
                        max_playout_depth=move_number_difference)

                # 進捗ログを出したい
                def log_progress(comment):
                    if DebugPlan.learn_at_position_log_progress():
                        print(f'[{datetime.datetime.now()}] [learn > at position] {tier:2}位  ({choice_num:3}/{sum_size:3})  {move_u:5}  {result_str}  [(投了{self._move_number_at_end:3}手目) (巻戻し:{move_number_between_end_and_problem:3}) (学習局面:{move_number_at_problem:3}手目) (指継:{move_number_difference:3}手) (再投了:{self._board.move_number:3}手目 {Turn.to_kanji(self._board.turn)})]  {reason}  {comment}', flush=True)

                # どちらかが投了した
                if reason == 'resign':
                    # 負けた（問題局面と投了局面の手番が同じ）
                    if turn_at_problem == self._board.turn:
                        shall_1_weaken_2_strongthen = 1
                        log_progress(f"[▼DOWN▼] 指し継いだら、負けた")

                    # 勝った（問題局面と投了局面の手番が異なる）
                    else:
                        shall_1_weaken_2_strongthen = 2
                        log_progress(f"[▲UP▲] 指し継いだら、勝った")

                # どちらかが入玉宣言勝ちした
                elif reason == 'nyugyoku_win':
                    # 勝った（問題局面と入玉宣言勝ち局面の手番が同じ）
                    if turn_at_problem == self._board.turn:
                        shall_1_weaken_2_strongthen = 2
                        log_progress(f"[▲UP▲] 指し継いだら、入玉宣言して、勝った")

                    # 負けた（問題局面と入玉宣言勝ち局面の手番が異なる）
                    else:
                        shall_1_weaken_2_strongthen = 1
                        log_progress(f"[▼DOWN▼] 指し継いだら、入玉宣言されて、負けた")

                # 手数の上限に達した
                elif reason == 'max_move':
                    # ノーカウント
                    log_progress(f"[　] 手数上限で打ち切られた")

                # プレイアウトの深さの上限に達した
                elif reason == 'max_playout_depth':
                    # ノーカウント
                    log_progress(f"[ ] プレイアウト用の手数上限で打ち切られた")

                else:
                    # ノーカウント
                    log_progress("[　] 関心のない結果")

                # 終局図の内部データに進める
                self.restore_end_position()

                # ｎ手詰めの局面まで戻す
                for _i in range(0, mate):
                    self._board.pop()

                # 戻せたかチェック
                if self._board.sfen() != sfen_at_mate:
                    # エラー時
                    print(f"""[{datetime.datetime.now()}] [learn > at position] {tier:2}位  局面巻き戻しエラー
    {self._board}
        # board move_number:{self._board.move_number}
        # {BoardHelper.get_position_command(board=self._board)}
    """)
                    raise ValueError("局面巻き戻しエラー")

                # ｎ手詰めの局面にしてから、評価値を下げる
                if shall_1_weaken_2_strongthen == 1:
                    result_str = self._kifuwarabe.weaken(
                            cmd_tail=move_u,
                            is_debug=True)
                            #is_debug=self._is_debug)

                    # 変更はログに出したい
                    print(f'[{datetime.datetime.now()}] [learn > at position] {tier:2}位       weaken {move_u:5}  result:`{result_str}`')

                    if result_str == 'changed':
                        changed_count += 1

                # ｎ手詰めの局面にしてから、評価値を上げる
                elif shall_1_weaken_2_strongthen == 2:
                    result_str = self._kifuwarabe.strengthen(
                            cmd_tail=move_u,
                            is_debug=True)
                            #is_debug=self._is_debug)

                    # 変更はログに出したい
                    print(f'[{datetime.datetime.now()}] [learn > at position] {tier:2}位        strengthen {move_u:5}  result:`{result_str}`')

                    if result_str == 'changed':
                        changed_count += 1


        return ('ok', changed_count)
