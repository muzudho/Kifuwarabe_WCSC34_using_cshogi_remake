import datetime
from v_a41_0_debug_plan import DebugPlan
from v_a41_0_eval import MoveAndPolicyHelper
from v_a41_0_lib import Turn, BoardHelper


class Learn():
    """学習部"""


    def __init__(
            self,
            board,
            kifuwarabe,
            is_debug):
        """初期化

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe:
            きふわらべ
        is_debug : bool
            デバッグモードか？
        """

        self._board = board
        self._kifuwarabe = kifuwarabe
        self._is_debug = is_debug

        self._init_position_sfen = None
        self._principal_history = None
        self._end_position_sfen = None


    def restore_end_position(self):
        """終局図の内部データに戻す"""

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
            print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
            raise ValueError("局面巻き戻しエラー")

        #if is_debug:
        #    print(f"[{datetime.datetime.now()}] [learn] restore_end_position end.")


    def learn_it(self):
        """それを学習する"""

        # 開始ログは出したい
        print(f'[{datetime.datetime.now()}] [learn] start...')

        # 終局図の sfen を取得。巻き戻せたかのチェックに利用
        self._end_position_sfen = self._board.sfen()

        # 終局図とその sfen はログに出したい
        print(f"[{datetime.datetime.now()}] [learn] 終局図：")
        print(self._board)

        # 現局面の position コマンドを表示
        print(f"""[{datetime.datetime.now()}] [learn]
    board.move_number:{self._board.move_number}
    #{BoardHelper.get_position_command(board=self._board)}
""")

        # 戻せたかチェック
        if self._board.sfen() != self._end_position_sfen:
            # 終局図の表示
            print(f"[{datetime.datetime.now()}] [learn] 局面巻き戻しエラー")
            print(self._board)
            print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
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

        # 初期局面と、その sfen はログに出したい
        print(f"[{datetime.datetime.now()}] [learn] 初期局面図：")
        print(self._board)
        print(f"  init_position_sfen:`{self._init_position_sfen}`   board.move_number:{self._board.move_number}")

        # 終局図の内部データに戻す
        self.restore_end_position()

        # 終局局面の手数
        self._move_number_at_end = self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] move_number_at_end:{self._move_number_at_end}")

        mate = 1

        # 全ての着手をさかのぼると時間がかかるので、上限を８手としておく
        max_depth = self._move_number_at_end

        if 8 < max_depth:
            max_depth = 8

        while mate <= max_depth:

            #
            # 奇数：　詰める方
            # --------------
            #
            self.at_odd(
                    mate=mate,
                    # １手詰め局面なのだから、１手指せば充分だが、必至も考えて３手ぐらい余裕を与える
                    max_playout_depth=mate+2)

            mate += 1

            if self._move_number_at_end < mate:
                break

            #
            # 偶数：　逃げる方
            # --------------
            #
            self.at_even(
                    mate=mate,
                    # ２手詰め局面なのだから、２手指せば充分だが、必至も考えて４手ぐらい余裕を与える
                    max_playout_depth=mate+2)

            mate += 1

            # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
            #
            #   そんなに変更が起きないので、２手毎に保存してみる
            #
            self._kifuwarabe.save_eval_all_tables()

        #
        # おわり
        # -----
        #

        # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
        self._kifuwarabe.save_eval_all_tables()

        # 終局図の内部データに戻す
        self.restore_end_position()

        print(f"[{datetime.datetime.now()}] [learn] finished", flush=True)


    def at_odd(
            self,
            mate,
            max_playout_depth):
        """奇数。詰める方

        Parameters
        ----------
        mate : int
            ｎ手詰め
        max_playout_depth : int
            プレイアウト最大深さ
        """
        # 棋譜を巻き戻せないなら、学ぶことはできません
        if self._board.move_number < mate + 1:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方] ignored. you cannot learn. short moves. board.move_number:{self._board.move_number}')
            return

        # 終局図の内部データに戻す
        self.restore_end_position()

        # ｎ手詰めの局面まで戻す
        for _i in range(0, mate):
            self._board.pop()

        # ｎ手詰めの局面図の sfen
        sfen_at_mate = self._board.sfen()

        # 現局面の position コマンドを表示
        print(f"""[{datetime.datetime.now()}] [learn]
    board.move_number:{self._board.move_number}
    #{BoardHelper.get_position_command(board=self._board)}
""")

        # 終局局面までの手数
        self._move_number_to_end = self._move_number_at_end - self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] [learn > 詰める方] move_number_to_end:{self._move_number_to_end} = move_number_at_end:{self._move_number_at_end} - board.move_number:{self._board.move_number}")

        # - アンドゥした局面は、投了局面ではないはず
        # - 入玉宣言局面は、とりあえず考慮から外す
        # - １手詰めはとりあえず、考慮から外す

        #
        # 好手、悪手一覧
        # ------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set_power(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        good_num = len(good_move_u_set)
        bad_num = len(bad_move_u_set)
        total_num = good_num + bad_num
        print(f'[{datetime.datetime.now()}] [learn > 詰める方]　作業量その１  好手数：{good_num}　悪手数：{bad_num}　※プレイアウトに時間がかかることがあります', flush=True)

        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方]  現好手一覧：')

        choice_num = 0

        for move_u in good_move_u_set:
            choice_num += 1
            is_weak_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 好手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError(f"[learn > 詰める方 > 好手] {mate}手詰め局面図エラー")

            # （ｎ手詰め局面図で）とりあえず一手指す
            self._board.push_usi(move_u)

            # プレイアウトする
            result_str = self._kifuwarabe.playout(
                    is_in_learn=True,
                    # １手指した分引く
                    max_playout_depth=max_playout_depth - 1)

            move_number_difference = self._board.move_number - self._move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                if DebugPlan.learn_at_odd_log_progress():
                    print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手]    ({choice_num:3} / {total_num:3}) [{self._board.move_number} moves / {Turn.to_string(self._board.turn)}]  F:{move_u:5}  O:*****  is good.  result:`{result_str}`  move_number_difference:{move_number_difference}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の負け
                if self._kifuwarabe._my_turn == self._board.turn:
                    is_weak_move = True
                    log_progress(f"fumble:{mate}手詰めを逃して {max_playout_depth} 手以内に負けた。すごく悪い手だ。好手の評価を取り下げる")
                else:
                    log_progress(f"ignored:{mate}手詰めは逃したが {max_playout_depth} 手以内には勝ったからセーフとする。好手の評価はそのまま")

            # どちらかが入玉勝ちした
            elif result_str == 'nyugyoku_win':
                if self._kifuwarabe._my_turn == self._board.turn:
                    log_progress(f"ignored:{mate}手詰めは逃したが {max_playout_depth} 手以内には入玉宣言勝ちしたからセーフとする。好手の評価はそのまま")

                else:
                    is_weak_move = True
                    log_progress(f"fumble:{mate}手詰めを逃して、 {max_playout_depth} 手以内に入玉宣言されて負けた。すごく悪い手だ。好手の評価を取り下げる")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            # プレイアウトの深さの上限に達した
            elif result_str == 'max_playout_depth':
                is_weak_move = True
                log_progress(f"fumble:{mate}手詰めを逃して {max_playout_depth} 手以内に終局しなかった。好手の評価を取り下げる")

            else:
                log_progress("ignored:好手の評価はそのまま")

            # 終局図の内部データに戻す
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 終局図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 好手] 局面巻き戻しエラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を下げる
            if is_weak_move:
                result_str = self._kifuwarabe.weaken(
                        cmd_tail=move_u,
                        is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手]        weaken {move_u:5}  result:`{result_str}`')


        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方]  現悪手一覧：')

        for move_u in bad_move_u_set:
            choice_num += 1
            is_strong_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError(f"[learn > 詰める方 > 悪手] {mate}手詰め局面図エラー")

            # （ｎ手詰め局面図で）とりあえず一手指す
            self._board.push_usi(move_u)

            # プレイアウトする
            result_str = self._kifuwarabe.playout(
                    is_in_learn=True,
                    # １手指しているので、１つ引く
                    max_playout_depth=max_playout_depth - 1)

            move_number_difference = self._board.move_number - self._move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                if DebugPlan.learn_at_odd_log_progress():
                    print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手]    ({choice_num:3} / {total_num:3}) [{self._board.move_number} moves / {Turn.to_string(self._board.turn)}]  F:{move_u:5}  O:*****  is bad.  result:`{result_str}`  move_number_difference:{move_number_difference}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の勝ち
                if self._kifuwarabe._my_turn != self._board.turn:
                    # かかった手数ｎ手
                    if self._move_number_at_end - self._board.move_number == mate:
                        is_strong_move = True
                        log_progress(f"nice:{mate}手詰めの局面で、{mate}手で勝ったので、評価を上げよう")
                    else:
                        log_progress(f"ignored:{mate}手詰めの局面で、{mate + 1}手以上かけて {max_playout_depth} 手以内には勝ったが、相手がヘボ手を指した可能性を消せない。悪手の評価はこのまま")

                else:
                    log_progress(f"ignored:{mate}手詰めの局面で、{mate}手詰めを逃して負けたのだから、悪手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            elif result_str == 'max_playout_depth':
                log_progress(f"ignored:{mate}手詰めの局面で、 {max_playout_depth} 手かけて終局しなかったので、悪手の評価はそのまま")

            else:
                log_progress("ignored:悪手の評価はそのまま")

            # 終局図の内部データに戻す
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] 局面巻き戻しエラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を上げる
            if is_strong_move:
                result_str = self._kifuwarabe.strengthen(
                        cmd_tail=move_u,
                        is_debug=True)
                        #is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手]        strengthen {move_u:5}  result:`{result_str}`')


    def at_even(
            self,
            mate,
            max_playout_depth):
        """偶数。逃げる方

        Parameters
        ----------
        mate : int
            ｎ手詰め
        max_playout_depth : int
            プレイアウトの最大深さ
        """

        # 棋譜を巻き戻せないなら、学ぶことはできません
        if self._board.move_number < mate + 1:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方] ignored. you cannot learn. short moves. board.move_number:{self._board.move_number}')
            return

        # 終局図の内部データに戻す
        self.restore_end_position()

        # ｎ手詰めの局面まで戻す
        for _i in range(0, mate):
            self._board.pop()

        # ｎ手詰めの局面図の sfen
        sfen_at_mate = self._board.sfen()

        # 現局面の position コマンドを表示
        print(f"""[{datetime.datetime.now()}] [learn]
    board.move_number:{self._board.move_number}
    #{BoardHelper.get_position_command(board=self._board)}
""")

        # 終局局面までの手数
        self._move_number_to_end = self._move_number_at_end - self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] [learn > 逃げる方] move_number_to_end:{self._move_number_to_end} = move_number_at_end:{self._move_number_at_end} - board.move_number:{self._board.move_number}")

        #
        # 好手、悪手一覧
        # ------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set_power(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        good_num = len(good_move_u_set)
        bad_num = len(bad_move_u_set)
        total_num = good_num + bad_num
        print(f'[{datetime.datetime.now()}] [learn > 逃げる方]　作業量その２  好手数：{good_num}　悪手数：{bad_num}')

        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現好手一覧：')

        choice_num = 0

        for move_u in good_move_u_set:
            choice_num += 1
            is_weak_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError(f"[learn > 逃げる方 > 好手] {mate}手詰め局面図エラー")

            # （ｎ手詰め局面図で）とりあえず一手指す
            self._board.push_usi(move_u)

            # プレイアウトする
            result_str = self._kifuwarabe.playout(
                    is_in_learn=True,
                    # １手指した分引く
                    max_playout_depth=max_playout_depth - 1)

            move_number_difference = self._board.move_number - self._move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                if DebugPlan.learn_at_even_log_progress():
                    print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手]    ({choice_num:3} / {total_num:3})  [{self._board.move_number} moves / {Turn.to_string(self._board.turn)}]  F:{move_u:5}  O:*****  is good.  result:`{result_str}`  move_number_difference:{move_number_difference}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の負け。かかった手数２手。つまり１手詰め
                if self._kifuwarabe._my_turn == self._board.turn and self._move_number_at_end - self._board.move_number == 2:
                    is_weak_move = True
                    log_progress(f"fumble:{mate}手詰めが掛けられていて、{mate}手詰めを避けられなかったから、好手の評価を取り下げる")

                else:
                    log_progress(f"fumble:{mate}手詰めが掛けられていて、{mate}手詰めを避けたから、好手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            else:
                log_progress("ignored:この好手の評価はそのまま")

            # 終局図の内部データに戻す
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] 局面巻き戻しエラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を下げる
            if is_weak_move:
                result_str = self._kifuwarabe.weaken(
                        cmd_tail=move_u,
                        is_debug=True)
                        #is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手]        weaken {move_u:5}  result:`{result_str}`')


        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現悪手一覧：')

        for move_u in bad_move_u_set:
            choice_num += 1
            is_strong_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError(f"[learn > 逃げる方 > 悪手] {mate}手詰め局面図エラー")

            # （ｎ手詰め局面図で）とりあえず一手指す
            self._board.push_usi(move_u)

            # プレイアウトする
            result_str = self._kifuwarabe.playout(
                    is_in_learn=True,
                    # １手指しているので、１つ引く
                    max_playout_depth=max_playout_depth - 1)

            move_number_difference = self._board.move_number - self._move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                if DebugPlan.learn_at_even_log_progress():
                    print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手]    ({choice_num:3} / {total_num:3})  [{self._board.move_number} moves / {Turn.to_string(self._board.turn)}]  F:{move_u:5}  O:*****  is bad.  result:`{result_str}`  move_number_difference:{move_number_difference}  comment:{comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 相手をｎ手詰め
                if self._kifuwarabe._my_turn != self._board.turn and move_number_difference == mate:
                    # 次にｎ手詰めの局面に掛けられるところを、その前に詰めたのだから、すごく良い手だ。この手の評価を上げる
                    is_strong_move = True
                    log_progress(f"nice:{mate}手詰めを掛けられていて、逆に{mate - 1}手で勝ったのだから、この手の評価を上げる")
                else:
                    log_progress(f"nice:{mate}手詰めを掛けられていて、ここで１手で勝てなかったから、この悪手の評価はそのまま")

            # どちらかが入玉勝ちした
            elif result_str == 'nyugyoku_win':
                if move_number_difference != mate:
                    # 次にｎ手詰めの局面に掛けられるところを、その前に入玉宣言勝ちしたのだから、すごく良い手だ。この手の評価を上げる
                    is_strong_move = True
                    log_progress(f"nice:{mate}手詰めを掛けられていて、逆に{mate - 1}手で入玉宣言勝ちしたのだから、この手の評価を上げる")
                else:
                    log_progress(f"nice:{mate}手詰めを掛けられていて、ここで{mate}手以上掛けて入玉したから、この悪手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            else:
                log_progress("ignored:この悪手の評価はそのまま")

            # 終局図の内部データに戻す
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] 局面巻き戻しエラー")
                print(self._board)
                print(f"  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を上げる
            if is_strong_move:
                result_str = self._kifuwarabe.strengthen(
                        cmd_tail=move_u,
                        is_debug=True)
                        #is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手]        strengthen {move_u:5}  result:`{result_str}`')
