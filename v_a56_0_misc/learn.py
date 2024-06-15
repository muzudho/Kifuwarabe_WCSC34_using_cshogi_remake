import datetime
import random

from v_a56_0_debug_plan import DebugPlan
from v_a56_0_misc.choice_best_move import ChoiceBestMove
from v_a56_0_misc.lib import Turn, BoardHelper


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
        attack_extension = 30
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

        # 詰める方の手番
        attacker_turn = self._board.turn
        # 逃げる方の手番
        defender_turn = Turn.flip(attacker_turn)

        # 終局局面までの手数
        self._move_number_to_end = self._move_number_at_end - self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] [learn > 詰める方] move_number_to_end:{self._move_number_to_end} = move_number_at_end:{self._move_number_at_end} - board.move_number:{self._board.move_number}")

        # - アンドゥした局面は、投了局面ではないはず
        # - 入玉宣言局面は、とりあえず考慮から外す
        # - １手詰めはとりあえず、考慮から外す

        #
        # ランク付けされた指し手一覧（好手、悪手）
        # ----------------------------------
        #
        ranked_move_u_set_list = ChoiceBestMove.select_ranked_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        print(f'[{datetime.datetime.now()}] [learn > 詰める方]  mate:{mate}  ランク別着手数：', end='')
        size_list = []
        sum_size = 0
        for ranking, ranked_move_u_set in enumerate(ranked_move_u_set_list):
            set_size = len(ranked_move_u_set)
            size_list.append(set_size)
            sum_size += set_size
            print(f'  [{ranking}]{set_size}', end='')

        print(f'  累計：{sum_size}', flush=True)

        # TODO 好手と悪手の真ん中を設定できるようにしたい
        ranking_resolution_threshold = sum_size // self._kifuwarabe.ranking_resolution


        for ranking, ranked_move_u_set in enumerate(ranked_move_u_set_list):
            choice_num = 0

            if ranking < ranking_resolution_threshold:

                if self._is_debug:
                    print(f'[{datetime.datetime.now()}] [learn > 詰める方]  着手のランキング：{ranking}（好手）')

                for move_u in ranked_move_u_set:

                    # カウンターは事前に進める
                    choice_num += 1

                    # mate が 3 以降なら、検討を間引く
                    if 3 <= mate and not self.is_learn_by_rate():
                        continue

                    is_weak_move = False

                    # ｎ手詰め局面図かチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 詰める方 > 好手] {mate}手詰め局面図エラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
                        raise ValueError(f"[learn > 詰める方 > 好手] {mate}手詰め局面図エラー")

                    # （ｎ手詰め局面図で）とりあえず一手指す
                    self._board.push_usi(move_u)

                    # プレイアウトする
                    (result_str, reason) = self._kifuwarabe.playout(
                            is_in_learn=True,
                            # １手指した分引く
                            max_playout_depth=max_playout_depth - 1)

                    move_number_difference = self._board.move_number - self._move_number_at_end

                    # 進捗ログを出したい
                    def log_progress(comment):
                        if DebugPlan.learn_at_odd_log_progress():
                            print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手] ({choice_num:3}/{sum_size:3})  {move_u:5}  {result_str}  [{self._board.move_number}手（差{move_number_difference}）{Turn.to_kanji(self._board.turn)}]  {reason}  {comment}', flush=True)

                    # どちらかが投了した
                    if reason == 'resign':
                        # 攻め手の負け
                        if attacker_turn == self._board.turn:
                            # すごく悪い手だ。好手の評価を取り下げる
                            is_weak_move = True
                            log_progress(f"[▼DOWN▼] {mate}手詰めを逃して {max_playout_depth} 手以内に負けた")
                        else:
                            # 好手の評価はそのまま
                            log_progress(f"[　] {mate}手詰めは逃したが {max_playout_depth} 手以内には勝ったからセーフ")

                    # どちらかが入玉勝ちした
                    elif reason == 'nyugyoku_win':
                        # 攻め手の勝ち
                        if attacker_turn == self._board.turn:
                            # 好手の評価はそのまま
                            log_progress(f"[　] {mate}手詰めは逃したが {max_playout_depth} 手以内には入玉宣言勝ちしたからセーフ")

                        else:
                            is_weak_move = True
                            # すごく悪い手だ。好手の評価を取り下げる
                            log_progress(f"[▼DOWN▼] {mate}手詰めを逃して、 {max_playout_depth} 手以内に入玉宣言されて負けた")

                    # 手数の上限に達した
                    elif reason == 'max_move':
                        # ノーカウント
                        log_progress(f"[　] 攻めてる間に手数上限で打ち切られた")

                    # プレイアウトの深さの上限に達した
                    elif reason == 'max_playout_depth':
                        # （評価値テーブルを動かしたいので）好手の評価を取り下げる
                        is_weak_move = True
                        log_progress(f"[▼DOWN▼] 攻めてる間にプレイアウトが打ち切られた")

                    else:
                        # 好手の評価はそのまま
                        log_progress("[　] 関心のない結果")

                    # 終局図の内部データに進める
                    self.restore_end_position()

                    # ｎ手詰めの局面まで戻す
                    for _i in range(0, mate):
                        self._board.pop()

                    # 戻せたかチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 詰める方 > 好手] 局面巻き戻しエラー
    {self._board}
        # board move_number:{self._board.move_number}
        # {BoardHelper.get_position_command(board=self._board)}
    """)
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

            else:

                if self._is_debug:
                    print(f'[{datetime.datetime.now()}] [learn > 詰める方]  着手のランキング：{ranking}（悪手）')

                for move_u in ranked_move_u_set:

                    # カウンターは事前に進める
                    choice_num += 1

                    # mate が 4 以降なら、検討を間引く
                    if 4 <= mate and not self.is_learn_by_rate():
                        continue

                    is_strong_move = False

                    # ｎ手詰め局面図かチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] {mate}手詰め局面図エラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
                        raise ValueError(f"[learn > 詰める方 > 悪手] {mate}手詰め局面図エラー")

                    # （ｎ手詰め局面図で）とりあえず一手指す
                    self._board.push_usi(move_u)

                    # プレイアウトする
                    (result_str, reason) = self._kifuwarabe.playout(
                            is_in_learn=True,
                            # １手指しているので、１つ引く
                            max_playout_depth=max_playout_depth - 1)

                    move_number_difference = self._board.move_number - self._move_number_at_end

                    # 進捗ログを出したい
                    def log_progress(comment):
                        if DebugPlan.learn_at_odd_log_progress():
                            print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] ({choice_num:3}/{sum_size:3})  {move_u:5}  {result_str}  [{self._board.move_number}手（差{move_number_difference}）{Turn.to_kanji(self._board.turn)}]  {reason}  {comment}', flush=True)

                    # どちらかが投了した
                    if reason == 'resign':
                        # 逃げてた方の負け
                        if defender_turn == self._board.turn:
                            # かかった手数ｎ手
                            if self._move_number_at_end - self._board.move_number == mate:
                                # 良いことだ。評価を上げよう
                                is_strong_move = True
                                log_progress(f"[▲UP▲] {mate}手詰めの局面で、その通り{mate}手で勝った")
                            else:
                                # 相手がヘボ手を指している可能性もあるから、ヘボ手を好手にするのはよくないが、今は評価値テーブルの値を変化させたいから、好手ということにしておく
                                is_strong_move = True
                                log_progress(f"[▲UP▲] {mate}手詰めの局面で、{mate + 1}手以上かけて {max_playout_depth} 手以内には勝った")

                        else:
                            # 悪手の評価はそのまま
                            log_progress(f"[　] {mate}手詰めの局面で、{mate}手詰めを逃して負けた")

                    # 手数の上限に達した
                    elif reason == 'max_move':
                        # ノーカウント
                        log_progress(f"[　] 攻めてる間に手数上限で打ち切られた")

                    elif reason == 'max_playout_depth':
                        # 悪手の評価はそのまま
                        log_progress(f"[　] 攻めてる間にプレイアウトが打ち切られた")

                    else:
                        # 悪手の評価はそのまま
                        log_progress("[　] 関心のない結果")

                    # 終局図の内部データに進める
                    self.restore_end_position()

                    # ｎ手詰めの局面まで戻す
                    for _i in range(0, mate):
                        self._board.pop()

                    # 戻せたかチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] 局面巻き戻しエラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
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

        # 逃げる方の手番
        defender_turn = self._board.turn
        # 詰める方の手番
        attacker_turn = Turn.flip(defender_turn)

        # 終局局面までの手数
        self._move_number_to_end = self._move_number_at_end - self._board.move_number
        if self._is_debug:
            print(f"[{datetime.datetime.now()}] [learn > 逃げる方] move_number_to_end:{self._move_number_to_end} = move_number_at_end:{self._move_number_at_end} - board.move_number:{self._board.move_number}")

        #
        # ランク付けされた指し手一覧（好手、悪手）
        # ----------------------------------
        #
        ranked_move_u_set_list = ChoiceBestMove.select_ranked_f_move_u_set_facade(
                legal_moves=list(self._board.legal_moves),
                board=self._board,
                kifuwarabe=self._kifuwarabe,
                is_debug=self._is_debug)

        # 作業量はログを出したい
        print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  mate:{mate}  ランク別着手数：', end='')
        size_list = []
        sum_size = 0
        for ranking, ranked_move_u_set in enumerate(ranked_move_u_set_list):
            set_size = len(ranked_move_u_set)
            size_list.append(set_size)
            sum_size += set_size
            print(f'  [{ranking}]{set_size}', end='')

        print(f'  累計：{sum_size}', flush=True)

        # TODO 好手と悪手の真ん中を設定できるようにしたい
        ranking_resolution_threshold = sum_size // self._kifuwarabe.ranking_resolution


        for ranking, ranked_move_u_set in enumerate(ranked_move_u_set_list):
            choice_num = 0

            if ranking < ranking_resolution_threshold:
                if self._is_debug:
                    print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  着手のランキング：{ranking}（好手）')

                for move_u in ranked_move_u_set:

                    # カウンターは事前に進める
                    choice_num += 1

                    # 検討を間引く
                    if not self.is_learn_by_rate():
                        continue

                    is_weak_move = False

                    # ｎ手詰め局面図かチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] {mate}手詰め局面図エラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
                        raise ValueError(f"[learn > 逃げる方 > 好手] {mate}手詰め局面図エラー")

                    # （ｎ手詰め局面図で）とりあえず一手指す
                    self._board.push_usi(move_u)

                    # プレイアウトする
                    (result_str, reason) = self._kifuwarabe.playout(
                            is_in_learn=True,
                            # １手指した分引く
                            max_playout_depth=max_playout_depth - 1)

                    move_number_difference = self._board.move_number - self._move_number_at_end

                    # 進捗ログを出したい
                    def log_progress(comment):
                        if DebugPlan.learn_at_even_log_progress():
                            print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] ({choice_num:3}/{sum_size:3})  {move_u:5}  {result_str}  [{self._board.move_number}手（差{move_number_difference}）{Turn.to_kanji(self._board.turn)}]  {reason}  {comment}', flush=True)

                    # どちらかが投了した
                    if reason == 'resign':
                        # 逃げてる方の負け
                        if defender_turn == self._board.turn:
                            if self._move_number_at_end - self._board.move_number == 2:
                                # 好手の評価を取り下げる
                                is_weak_move = True
                                log_progress(f"[▼DOWN▼] {mate}手詰めが掛けられていて、それを食らった")

                            else:
                                # 好手の評価はそのまま
                                log_progress(f"[　] {mate}手詰めが掛けられていたが、そこから粘った")

                        else:
                            # 好手を維持
                            log_progress(f"[　] 逃げてる方が勝った")


                    # 手数の上限に達した
                    elif reason == 'max_move':
                        # 好手の評価はそのまま
                        log_progress(f"[　] 手数上限で打ち切られるまで逃げ切った")

                    # プレイアウトの深さの上限に達した
                    elif reason == 'max_playout_depth':
                        # 好手の評価はそのまま
                        log_progress(f"[　] プレイアウトが打ち切られるまで逃げ切った")

                    else:
                        # この好手の評価はそのまま
                        log_progress("[　] 関心のない結果")

                    # 終局図の内部データに進める
                    self.restore_end_position()

                    # ｎ手詰めの局面まで戻す
                    for _i in range(0, mate):
                        self._board.pop()

                    # 戻せたかチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] 局面巻き戻しエラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
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

            else:

                if self._is_debug:
                    print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現悪手一覧：')

                for move_u in ranked_move_u_set:

                    # カウンターは事前に進める
                    choice_num += 1

                    # 検討を間引く
                    if not self.is_learn_by_rate():
                        continue

                    is_strong_move = False

                    # ｎ手詰め局面図かチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] {mate}手詰め局面図エラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
                        raise ValueError(f"[learn > 逃げる方 > 悪手] {mate}手詰め局面図エラー")

                    # （ｎ手詰め局面図で）とりあえず一手指す
                    self._board.push_usi(move_u)

                    # プレイアウトする
                    (result_str, reason) = self._kifuwarabe.playout(
                            is_in_learn=True,
                            # １手指しているので、１つ引く
                            max_playout_depth=max_playout_depth - 1)

                    move_number_difference = self._board.move_number - self._move_number_at_end

                    # 進捗ログを出したい
                    def log_progress(comment):
                        if DebugPlan.learn_at_even_log_progress():
                            print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] ({choice_num:3}/{sum_size:3})  {move_u:5}  {result_str}  [{self._board.move_number}手（差{move_number_difference}）{Turn.to_kanji(self._board.turn)}]  {reason}  {comment}', flush=True)

                    # どちらかが投了した
                    if reason == 'resign':
                        # 逃げてる方が負け
                        if defender_turn == self._board.turn:
                            log_progress(f"[　] 逃げようとしたが、逃げ切れなかった")

                        # 逃げてたら勝った
                        else:
                            is_strong_move = True
                            log_progress(f"[▲UP▲] 逃げてたら勝った")

                    # どちらかが入玉勝ちした
                    elif reason == 'nyugyoku_win':
                        if defender_turn == self._board.turn:
                            log_progress(f"[　] 逃げようとしたが、入玉宣言負けしてしまった")

                        # 逃げてたら勝った
                        else:
                            is_strong_move = True
                            log_progress(f"[▲UP▲] 逃げてたら、入玉宣言勝ちした")

                    # 手数の上限に達した
                    elif reason == 'max_move':
                        # （評価値テーブルを動かしたいので）悪手の評価を取り下げる
                        is_strong_move = True
                        log_progress(f"[▲UP▲] 手数上限で打ち切られるまで逃げ切った")

                    # プレイアウトの深さの上限に達した
                    elif reason == 'max_playout_depth':
                        # （評価値テーブルを動かしたいので）悪手の評価を取り下げる
                        is_strong_move = True
                        log_progress(f"[▲UP▲] プレイアウトが打ち切られるまで逃げ切った")

                    else:
                        # この悪手の評価はそのまま
                        log_progress("[　] 関心のない結果")


                    # 終局図の内部データに進める
                    self.restore_end_position()

                    # ｎ手詰めの局面まで戻す
                    for _i in range(0, mate):
                        self._board.pop()

                    # 戻せたかチェック
                    if self._board.sfen() != sfen_at_mate:
                        # エラー時
                        print(f"""[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] 局面巻き戻しエラー
{self._board}
    # board move_number:{self._board.move_number}
    # {BoardHelper.get_position_command(board=self._board)}
""")
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
