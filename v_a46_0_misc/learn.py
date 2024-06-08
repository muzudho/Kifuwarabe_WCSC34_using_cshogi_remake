import datetime
import random
from v_a46_0_debug_plan import DebugPlan
from v_a46_0_eval.facade import EvaluationFacade
from v_a46_0_misc.lib import Turn, BoardHelper


class Learn():
    """学習部"""


    @staticmethod
    def is_learn_by_rate():
        """全ての指し手の良し悪しを検討していると、全体を見る時間がなくなるから、
        間引くのに使う"""

        ## 平均合法手が 80 手と仮定して、 20分の1 にすれば、１手当たり 4 つの合法手を検討するだろう
        #return random.randint(0,20) == 0

        # 次の対局の usinewgame のタイミングで、前の対局の棋譜をトレーニングデータにして機械学習を走らせるから、持ち時間を消費してしまう。
        # 平均合法手が 80 手と仮定して、 80分の1 にすれば、 1 手当たり 1 つの合法手を検討する間隔になって早く終わるだろう
        return random.randint(0,80) == 0


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
        print(f'[{datetime.datetime.now()}] [learn] start...')

        # 終局図の sfen を取得。巻き戻せたかのチェックに利用
        self._end_position_sfen = self._board.sfen()

        # 終局図とその sfen はログに出したい
        print(f"[{datetime.datetime.now()}] [learn] 終局図：")
        print(self._board)

        # 現局面の position コマンドを表示
        print(f"""[{datetime.datetime.now()}] [learn]
    #board.move_number:{self._board.move_number}
    #{BoardHelper.get_position_command(board=self._board)}
""")

        # 戻せたかチェック
        if self._board.sfen() != self._end_position_sfen:
            # 終局図の表示
            print(f"[{datetime.datetime.now()}] [learn] 局面巻き戻しエラー")
            print(self._board)
            print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
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
        print(f"#  init_position_sfen:`{self._init_position_sfen}`   board.move_number:{self._board.move_number}")

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

        # ３手詰めを３手で詰める必要はなく、５手必至でも良い手と言えるので、そのような場合 5-3 で、 attack_extension=2 とします
        attack_extension = 10
        # ２手詰めを４手詰めまで引き延ばせれば、逃げるのが上手くなったと言えるので、そのような場合 4-2 で、 escape_extension=2 とします
        escape_extension = 100

        while mate <= max_depth:

            #
            # 奇数：　詰める方
            # --------------
            #
            (result_str,
             changed_count) = self.at_odd(
                    mate=mate,
                    max_playout_depth=mate+attack_extension)

            mate += 1

            if self._move_number_at_end < mate or result_str == 'can not rewind' or 30 <= changed_count:
                break

            #
            # 偶数：　逃げる方
            # --------------
            #
            (result_str,
             changed_count) = self.at_even(
                    mate=mate,
                    max_playout_depth=mate+escape_extension)

            mate += 1

            if self._move_number_at_end < mate or result_str == 'can not rewind' or 30 <= changed_count:
                break

            ##
            ## ２０手毎にコマメに保存する
            ##
            #if mate % 20 == 0:
            #    # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
            #    self._kifuwarabe.save_eval_all_tables(
            #            is_debug=self._is_debug)

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

        changed_count = 0

        # 棋譜を巻き戻せないなら、学ぶことはできません
        if self._board.move_number < mate + 1:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方] ignored. you cannot learn. short moves. board.move_number:{self._board.move_number}')
            return ('can not rewind', changed_count)

        # 終局図の内部データに進める
        self.restore_end_position()

        # ｎ手詰めの局面まで戻す
        for _i in range(0, mate):
            self._board.pop()

        # ｎ手詰めの局面図の sfen
        sfen_at_mate = self._board.sfen()

        # 現局面の position コマンドを表示
        print(f"""[{datetime.datetime.now()}] [learn]
    #board.move_number:{self._board.move_number}
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
         bad_move_u_set) = EvaluationFacade.select_good_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        good_num = len(good_move_u_set)
        bad_num = len(bad_move_u_set)
        total_num = good_num + bad_num
        print(f'[{datetime.datetime.now()}] [learn > 詰める方]  mate:{mate}  好手数：{good_num}  悪手数：{bad_num}', flush=True)

        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方]  現好手一覧：')

        choice_num = 0

        for move_u in good_move_u_set:

            # カウンターは事前に進める
            choice_num += 1

            # 検討を間引く
            if not Learn.is_learn_by_rate():
                continue

            is_weak_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 好手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
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
                    print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手] ({choice_num:3}/{total_num:3})  {move_u:5}  [{self._board.move_number}手（差{move_number_difference}） {Turn.to_symbol(self._board.turn)}]  {result_str}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の負け
                if self._kifuwarabe._my_turn == self._board.turn:
                    is_weak_move = True
                    log_progress(f"[↓] {mate}手詰めを逃して {max_playout_depth} 手以内に負けた。すごく悪い手だ。好手の評価を取り下げる")
                else:
                    log_progress(f"[　] {mate}手詰めは逃したが {max_playout_depth} 手以内には勝ったからセーフとする。好手の評価はそのまま")

            # どちらかが入玉勝ちした
            elif result_str == 'nyugyoku_win':
                if self._kifuwarabe._my_turn == self._board.turn:
                    log_progress(f"[　] {mate}手詰めは逃したが {max_playout_depth} 手以内には入玉宣言勝ちしたからセーフとする。好手の評価はそのまま")

                else:
                    is_weak_move = True
                    log_progress(f"[↓] {mate}手詰めを逃して、 {max_playout_depth} 手以内に入玉宣言されて負けた。すごく悪い手だ。好手の評価を取り下げる")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"[　] この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            # プレイアウトの深さの上限に達した
            elif result_str == 'max_playout_depth':
                is_weak_move = True
                log_progress(f"[↓] 攻めてる間にプレイアウトが打ち切られた。（評価値テーブルを動かしたいので）好手の評価を取り下げる")

            else:
                log_progress("[　] 好手の評価はそのまま")

            # 終局図の内部データに進める
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 終局図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 好手] 局面巻き戻しエラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を下げる
            if is_weak_move:
                result_str = self._kifuwarabe.weaken(
                        cmd_tail=move_u,
                        is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手]        weaken {move_u:5}  result:`{result_str}`')

                if result_str == 'changed':
                    changed_count += 1


        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方]  現悪手一覧：')

        for move_u in bad_move_u_set:

            # カウンターは事前に進める
            choice_num += 1

            # 検討を間引く
            if not Learn.is_learn_by_rate():
                continue

            is_strong_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
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
                    print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] ({choice_num:3}/{total_num:3})  {move_u:5}  [{self._board.move_number}手（差{move_number_difference}） {Turn.to_symbol(self._board.turn)}]  {result_str}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の勝ち
                if self._kifuwarabe._my_turn != self._board.turn:
                    # かかった手数ｎ手
                    if self._move_number_at_end - self._board.move_number == mate:
                        is_strong_move = True
                        log_progress(f"[↑] {mate}手詰めの局面で、{mate}手で勝ったので、評価を上げよう")
                    else:
                        log_progress(f"[　] {mate}手詰めの局面で、{mate + 1}手以上かけて {max_playout_depth} 手以内には勝ったが、相手がヘボ手を指した可能性を消せない。悪手の評価はこのまま")

                else:
                    log_progress(f"[　] {mate}手詰めの局面で、{mate}手詰めを逃して負けたのだから、悪手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"[　] この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            elif result_str == 'max_playout_depth':
                log_progress(f"[　] 攻めてる間にプレイアウトが打ち切られた。悪手の評価はそのまま")

            else:
                log_progress("[　] 悪手の評価はそのまま")

            # 終局図の内部データに進める
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] 局面巻き戻しエラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を上げる
            if is_strong_move:
                result_str = self._kifuwarabe.strengthen(
                        cmd_tail=move_u,
                        is_debug=True)
                        #is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手]        strengthen {move_u:5}  result:`{result_str}`')

                if result_str == 'changed':
                    changed_count += 1


        return ('ok', changed_count)


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

        changed_count = 0

        # 棋譜を巻き戻せないなら、学ぶことはできません
        if self._board.move_number < mate + 1:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方] ignored. you cannot learn. short moves. board.move_number:{self._board.move_number}')
            return ('can not rewind', changed_count)

        # 終局図の内部データに進める
        self.restore_end_position()

        # ｎ手詰めの局面まで戻す
        for _i in range(0, mate):
            self._board.pop()

        # ｎ手詰めの局面図の sfen
        sfen_at_mate = self._board.sfen()

        # 現局面の position コマンドを表示
        print(f"""[{datetime.datetime.now()}] [learn]
    #board.move_number:{self._board.move_number}
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
         bad_move_u_set) = EvaluationFacade.select_good_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        good_num = len(good_move_u_set)
        bad_num = len(bad_move_u_set)
        total_num = good_num + bad_num
        print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  mate:{mate}  好手数：{good_num}  悪手数：{bad_num}')

        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現好手一覧：')

        choice_num = 0

        for move_u in good_move_u_set:

            # カウンターは事前に進める
            choice_num += 1

            # 検討を間引く
            if not Learn.is_learn_by_rate():
                continue

            is_weak_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
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
                    print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] ({choice_num:3}/{total_num:3})  {move_u:5}  [{self._board.move_number}手（差{move_number_difference}） {Turn.to_symbol(self._board.turn)}]  {result_str}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の負け。かかった手数２手。つまり１手詰め
                if self._kifuwarabe._my_turn == self._board.turn and self._move_number_at_end - self._board.move_number == 2:
                    is_weak_move = True
                    log_progress(f"[↓] {mate}手詰めが掛けられていて、{mate}手詰めを避けられなかったから、好手の評価を取り下げる")

                else:
                    log_progress(f"[　] {mate}手詰めが掛けられていて、{mate}手詰めを避けたから、好手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"[　] この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            # プレイアウトの深さの上限に達した
            elif result_str == 'max_playout_depth':
                log_progress(f"[　] プレイアウトが打ち切られるまで逃げ切った。好手の評価はそのまま")

            else:
                log_progress("[　] この好手の評価はそのまま")

            # 終局図の内部データに進める
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] 局面巻き戻しエラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を下げる
            if is_weak_move:
                result_str = self._kifuwarabe.weaken(
                        cmd_tail=move_u,
                        is_debug=True)
                        #is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手]        weaken {move_u:5}  result:`{result_str}`')

                if result_str == 'changed':
                    changed_count += 1


        if self._is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現悪手一覧：')

        for move_u in bad_move_u_set:

            # カウンターは事前に進める
            choice_num += 1

            # 検討を間引く
            if not Learn.is_learn_by_rate():
                continue

            is_strong_move = False

            # ｎ手詰め局面図かチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] {mate}手詰め局面図エラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
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
                    print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] ({choice_num:3}/{total_num:3})  {move_u:5}  [{self._board.move_number}手（差{move_number_difference}） {Turn.to_symbol(self._board.turn)}]  {result_str}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 相手をｎ手詰め
                if self._kifuwarabe._my_turn != self._board.turn and move_number_difference == mate:
                    # 次にｎ手詰めの局面に掛けられるところを、その前に詰めたのだから、すごく良い手だ。この手の評価を上げる
                    is_strong_move = True
                    log_progress(f"[↑] {mate}手詰めを掛けられていて、逆に{mate - 1}手で勝ったのだから、この手の評価を上げる")
                else:
                    log_progress(f"[　] {mate}手詰めを掛けられていて、ここで１手で勝てなかったから、この悪手の評価はそのまま")

            # どちらかが入玉勝ちした
            elif result_str == 'nyugyoku_win':
                if move_number_difference != mate:
                    # 次にｎ手詰めの局面に掛けられるところを、その前に入玉宣言勝ちしたのだから、すごく良い手だ。この手の評価を上げる
                    is_strong_move = True
                    log_progress(f"[↑] {mate}手詰めを掛けられていて、逆に{mate - 1}手で入玉宣言勝ちしたのだから、この手の評価を上げる")
                else:
                    log_progress(f"[　] {mate}手詰めを掛けられていて、ここで{mate}手以上掛けて入玉したから、この悪手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"[　] この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            # プレイアウトの深さの上限に達した
            elif result_str == 'max_playout_depth':
                is_strong_move = True
                log_progress(f"[↑] プレイアウトが打ち切られるまで逃げ切った。（評価値テーブルを動かしたいので）悪手の評価を取り下げる")

            else:
                log_progress("[　] この悪手の評価はそのまま")


            # 終局図の内部データに進める
            self.restore_end_position()

            # ｎ手詰めの局面まで戻す
            for _i in range(0, mate):
                self._board.pop()

            # 戻せたかチェック
            if self._board.sfen() != sfen_at_mate:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] 局面巻き戻しエラー")
                print(self._board)
                print(f"#  sfen:`{self._board.sfen()}`  board.move_number:{self._board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # ｎ手詰めの局面にしてから、評価値を上げる
            if is_strong_move:
                result_str = self._kifuwarabe.strengthen(
                        cmd_tail=move_u,
                        is_debug=True)
                        #is_debug=self._is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手]        strengthen {move_u:5}  result:`{result_str}`')

                if result_str == 'changed':
                    changed_count += 1


        return ('ok', changed_count)
