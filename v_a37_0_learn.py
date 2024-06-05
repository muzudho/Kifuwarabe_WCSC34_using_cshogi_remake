import datetime
from v_a37_0_eval import MoveAndPolicyHelper
from v_a37_0_lib import Turn, BoardHelper


class Learn():
    """学習部"""


    @staticmethod
    def learn_it(
            board,
            kifuwarabe,
            is_debug=False):
        """それを学習する

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe:
            きふわらべ
        is_debug : bool
            デバッグモードか？
        """

        # 開始ログは出したい
        print(f'[{datetime.datetime.now()}] [learn] start...')

        # 終局図の sfen を取得。巻き戻せたかのチェックに利用
        end_position_sfen = board.sfen()

        # 終局図とその sfen はログに出したい
        print(f"[{datetime.datetime.now()}] [learn] 終局図：")
        print(board)

        # 現局面の position コマンドを取得
        position_command = BoardHelper.get_position_command(
                board=board)
        print(f"""[{datetime.datetime.now()}] [learn]
    board.move_number:{board.move_number}
    #{position_command}
""")

        # 戻せたかチェック
        if board.sfen() != end_position_sfen:
            # 終局図の表示
            print(f"[{datetime.datetime.now()}] [learn] 局面巻き戻しエラー")
            print(board)
            print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
            raise ValueError("局面巻き戻しエラー")

        # 本譜の指し手を覚えておく。ログにも出したい
        principal_history = board.history

        # （あとで元の position の内部状態に戻すために）初期局面まで巻き戻し、初期局面を覚えておく
        while 1 < board.move_number:
            # １手戻す
            #if is_debug:
            #    print(f"[{datetime.datetime.now()}] [learn] undo to init  board.move_number:{board.move_number}")

            board.pop()

        # （あとで元の position の内部状態に戻すために）初期局面を覚えておく
        init_position_sfen = board.sfen()

        # 初期局面と、その sfen はログに出したい
        print(f"[{datetime.datetime.now()}] [learn] 初期局面図：")
        print(board)
        print(f"  init_position_sfen:`{init_position_sfen}`   board.move_number:{board.move_number}")


        def restore_end_position():
            """終局図の内部データに戻す"""
            #if is_debug:
            #    print(f"[{datetime.datetime.now()}] [learn] restore_end_position start...")
            # 初期局面
            board.set_sfen(init_position_sfen)

            # 棋譜再生
            for move_id in principal_history:
                board.push(move_id)

            # 戻せたかチェック
            if board.sfen() != end_position_sfen:
                # 終局図の表示
                print(f"[{datetime.datetime.now()}] [learn] 局面巻き戻しエラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            #if is_debug:
            #    print(f"[{datetime.datetime.now()}] [learn] restore_end_position end.")

        # 終局図の内部データに戻す
        restore_end_position()

        # 終局局面の手数
        move_number_at_end = board.move_number
        if is_debug:
            print(f"[{datetime.datetime.now()}] move_number_at_end:{move_number_at_end}")

        #
        # 詰める方
        # -------
        #

        # 棋譜の初手から学ぶことはできません
        if board.move_number < 2:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方] You cannot learn from the first move of the game record.')
            return

        # 終局図の内部データに戻っている
        # １手戻す（１手詰めの局面に戻るはず）
        board.pop()

        # １手前局面図と、その sfen は表示したい
        sfen_1_previous = board.sfen()
        print(f"[{datetime.datetime.now()}] [learn > 詰める方] １手前局面図：")
        print(board)
        print(f"  sfen:`{sfen_1_previous}`  board.move_number:{board.move_number}")

        # 終局局面までの手数
        move_number_to_end = move_number_at_end - board.move_number
        if is_debug:
            print(f"[{datetime.datetime.now()}] [learn > 詰める方] move_number_to_end:{move_number_to_end} = move_number_at_end:{move_number_at_end} - board.move_number:{board.move_number}")

        # - アンドゥした局面は、投了局面ではないはず
        # - 入玉宣言局面は、とりあえず考慮から外す
        # - １手詰めはとりあえず、考慮から外す

        #
        # 好手、悪手一覧
        # ------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set_power(
                legal_moves=list(board.legal_moves),
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        # 作業量はログを出したい
        good_num = len(good_move_u_set)
        bad_num = len(bad_move_u_set)
        total_num = good_num + bad_num
        print(f'[{datetime.datetime.now()}] [learn > 詰める方]　作業量その１  好手数：{good_num}　悪手数：{bad_num}　※プレイアウトに時間がかかることがあります', flush=True)

        if is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方]  現好手一覧：')

        choice_num = 0

        # プレイアウトの深さ
        #
        #   １手詰め局面なのだから、１手指せば充分だが、必至も考えて３手ぐらい余裕を与える
        #
        max_playout_depth = 3

        for move_u in good_move_u_set:
            choice_num += 1
            is_weak_move = False

            # １手前局面図かチェック
            if board.sfen() != sfen_1_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 好手] １手前局面図エラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("[learn > 詰める方 > 好手] １手前局面図エラー")

            # （１手前局面図で）とりあえず一手指す
            board.push_usi(move_u)

            # プレイアウトする
            result_str = kifuwarabe.playout(
                    is_in_learn=True,
                    max_playout_depth=max_playout_depth)

            move_number_difference = board.move_number - move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手]    ({choice_num:3} / {total_num:3}) [{board.move_number} moves / {Turn.to_string(board.turn)}]  F:{move_u:5}  O:*****  is good.  result:`{result_str}`  move_number_difference:{move_number_difference}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の負け
                if kifuwarabe._my_turn == board.turn:
                    is_weak_move = True
                    log_progress(f"fumble:１手詰めを逃して {max_playout_depth} 手以内に負けた。すごく悪い手だ。好手の評価を取り下げる")
                else:
                    log_progress(f"ignored:１手詰めは逃したが {max_playout_depth} 手以内には勝ったからセーフとする。好手の評価はそのまま")

            # どちらかが入玉勝ちした
            elif result_str == 'nyugyoku_win':
                if kifuwarabe._my_turn == board.turn:
                    log_progress(f"ignored:１手詰めは逃したが {max_playout_depth} 手以内には入玉宣言勝ちしたからセーフとする。好手の評価はそのまま")

                else:
                    is_weak_move = True
                    log_progress(f"fumble:１手詰めを逃して、 {max_playout_depth} 手以内に入玉宣言されて負けた。すごく悪い手だ。好手の評価を取り下げる")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            # プレイアウトの深さの上限に達した
            elif result_str == 'max_playout_depth':
                is_weak_move = True
                log_progress(f"fumble:１手詰めを逃して {max_playout_depth} 手以内に終局しなかった。好手の評価を取り下げる")

            else:
                log_progress("ignored:好手の評価はそのまま")

            # 終局図の内部データに戻す
            restore_end_position()
            # １手戻す（一手前局面図に戻るはず）
            board.pop()
            # 戻せたかチェック
            if board.sfen() != sfen_1_previous:
                # 終局図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 好手] 局面巻き戻しエラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # 元の局面に戻してから weaken する
            if is_weak_move:
                weaken_result_str = kifuwarabe.weaken(
                        cmd_tail=move_u,
                        is_debug=is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 好手]        weaken {move_u:5}  result:`{weaken_result_str}`')


        if is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 詰める方]  現悪手一覧：')

        for move_u in bad_move_u_set:
            choice_num += 1
            is_strong_move = False

            # １手前局面図かチェック
            if board.sfen() != sfen_1_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] １手前局面図エラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("１手前局面図エラー")

            # （１手前局面図で）とりあえず一手指す
            board.push_usi(move_u)

            # プレイアウトする
            result_str = kifuwarabe.playout(
                    is_in_learn=True,
                    max_playout_depth=max_playout_depth)

            move_number_difference = board.move_number - move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手]    ({choice_num:3} / {total_num:3}) [{board.move_number} moves / {Turn.to_string(board.turn)}]  F:{move_u:5}  O:*****  is bad.  result:`{result_str}`  move_number_difference:{move_number_difference}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の勝ち
                if kifuwarabe._my_turn != board.turn:
                    # かかった手数１手
                    if move_number_at_end - board.move_number == 1:
                        is_strong_move = True
                        log_progress(f"nice:１手詰めの局面で、１手で勝ったので、評価を上げよう")
                    else:
                        log_progress(f"ignored:１手詰めの局面で、２手以上かけて {max_playout_depth} 手以内には勝ったが、相手がヘボ手を指した可能性を消せない。悪手の評価はこのまま")

                else:
                    log_progress("ignored:１手詰めの局面で、１手詰めを逃して負けたのだから、悪手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            elif result_str == 'max_playout_depth':
                log_progress(f"ignored:１手詰めの局面で、 {max_playout_depth} 手かけて終局しなかったので、悪手の評価はそのまま")

            else:
                log_progress("ignored:悪手の評価はそのまま")

            # 終局図の内部データに戻す
            restore_end_position()
            # １手戻す（一手前局面図に戻るはず）
            board.pop()
            # 戻せたかチェック
            if board.sfen() != sfen_1_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 詰める方 > 悪手] 局面巻き戻しエラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # 元の局面に戻してから strengthen する
            if is_strong_move:
                strengthen_result_str = kifuwarabe.strengthen(
                        cmd_tail=move_u,
                        is_debug=is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 詰める方 > 悪手]        strengthen {move_u:5}  result:`{strengthen_result_str}`')

        #
        # 逃げる方
        # -------
        #

        # ２手戻せない場合
        if board.move_number < 3:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方] igonred.  board.move_number:{board.move_number}')
            return

        # 終局図の内部データに戻す
        restore_end_position()
        # ２手戻す（このあと１手詰めされる側の局面に戻るはず）
        board.pop()
        board.pop()

        # ２手前局面図と、その sfen は表示したい
        sfen_2_previous = board.sfen()
        print(f"[{datetime.datetime.now()}] [learn > 逃げる方] ２手前局面図：")
        print(board)
        print(f"  sfen:`{sfen_2_previous}`  board.move_number:{board.move_number}")

        # 終局局面までの手数
        move_number_to_end = move_number_at_end - board.move_number
        if is_debug:
            print(f"[{datetime.datetime.now()}] [learn > 逃げる方] move_number_to_end:{move_number_to_end} = move_number_at_end:{move_number_at_end} - board.move_number:{board.move_number}")

        #
        # 好手、悪手一覧
        # ------------
        #
        (good_move_u_set,
         bad_move_u_set) = MoveAndPolicyHelper.select_good_f_move_u_set_power(
                legal_moves=list(board.legal_moves),
                board=board,
                kifuwarabe=kifuwarabe,
                is_debug=is_debug)

        # 作業量はログを出したい
        good_num = len(good_move_u_set)
        bad_num = len(bad_move_u_set)
        total_num = good_num + bad_num
        print(f'[{datetime.datetime.now()}] [learn > 逃げる方]　作業量その２  好手数：{good_num}　悪手数：{bad_num}')

        if is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現好手一覧：')

        choice_num = 0

        for move_u in good_move_u_set:
            choice_num += 1
            is_weak_move = False

            # ２手前局面図かチェック
            if board.sfen() != sfen_2_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] ２手前局面図エラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("[learn > 逃げる方 > 好手] ２手前局面図エラー")

            # （２手前局面図で）とりあえず一手指す
            board.push_usi(move_u)

            # プレイアウトする
            result_str = kifuwarabe.playout(
                    is_in_learn=True,
                    max_playout_depth=max_playout_depth)

            move_number_difference = board.move_number - move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手]    ({choice_num:3} / {total_num:3})  [{board.move_number} moves / {Turn.to_string(board.turn)}]  F:{move_u:5}  O:*****  is good.  result:`{result_str}`  move_number_difference:{move_number_difference}  {comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 自分の負け。かかった手数２手。つまり１手詰め
                if kifuwarabe._my_turn == board.turn and move_number_at_end - board.move_number == 2:
                    is_weak_move = True
                    log_progress("fumble:２手詰めが掛けられていて、２手詰めを避けられなかったから、好手の評価を取り下げる")

                else:
                    log_progress("fumble:２手詰めが掛けられていて、２手詰めを避けたから、好手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            else:
                log_progress("ignored:この好手の評価はそのまま")

            # 終局図の内部データに戻す
            restore_end_position()
            # ２手戻す（このあと１手詰めされる側の局面に戻るはず）
            board.pop()
            board.pop()
            # 戻せたかチェック
            if board.sfen() != sfen_2_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 好手] 局面巻き戻しエラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # 元の局面に戻してから strengthen する
            if is_weak_move:
                weaken_result_str = kifuwarabe.weaken(
                        cmd_tail=move_u,
                        is_debug=is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 好手]        weaken {move_u:5}  result:`{weaken_result_str}`')


        if is_debug:
            print(f'[{datetime.datetime.now()}] [learn > 逃げる方]  現悪手一覧：')

        for move_u in bad_move_u_set:
            choice_num += 1
            is_strong_move = False

            # ２手前局面図かチェック
            if board.sfen() != sfen_2_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] ２手前局面図エラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("[learn > 逃げる方 > 悪手] ２手前局面図エラー")

            # （２手前局面図で）とりあえず一手指す
            board.push_usi(move_u)

            # プレイアウトする
            result_str = kifuwarabe.playout(
                    is_in_learn=True)

            move_number_difference = board.move_number - move_number_at_end

            # 進捗ログを出したい
            def log_progress(comment):
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手]    ({choice_num:3} / {total_num:3})  [{board.move_number} moves / {Turn.to_string(board.turn)}]  F:{move_u:5}  O:*****  is bad.  result:`{result_str}`  move_number_difference:{move_number_difference}  comment:{comment}', flush=True)

            # どちらかが投了した
            if result_str == 'resign':
                # 相手を１手詰め
                if kifuwarabe._my_turn != board.turn and move_number_difference == 1:
                    # 次に１手詰めの局面に掛けられるところを、その前に詰めたのだから、すごく良い手だ。この手の評価を上げる
                    is_strong_move = True
                    log_progress("nice:２手詰めを掛けられていて、逆に１手で勝ったのだから、この手の評価を上げる")
                else:
                    log_progress("nice:２手詰めを掛けられていて、ここで１手で勝てなかったから、この悪手の評価はそのまま")

            # どちらかが入玉勝ちした
            elif result_str == 'nyugyoku_win':
                if move_number_difference != 2:
                    # 次に１手詰めの局面に掛けられるところを、その前に入玉宣言勝ちしたのだから、すごく良い手だ。この手の評価を上げる
                    is_strong_move = True
                    log_progress("nice:２手詰めを掛けられていて、逆に１手で入玉宣言勝ちしたのだから、この手の評価を上げる")
                else:
                    log_progress("nice:２手詰めを掛けられていて、ここで２手以上掛けて入玉したから、この悪手の評価はそのまま")

            # 手数の上限に達した
            elif result_str == 'max_move':
                log_progress(f"ignored:この学習では、手数の上限で終わった対局は、評価値を変動させないものとする")

            else:
                log_progress("ignored:この悪手の評価はそのまま")

            # 終局図の内部データに戻す
            restore_end_position()
            # ２手戻す（このあと１手詰めされる側の局面に戻るはず）
            board.pop()
            board.pop()
            # 戻せたかチェック
            if board.sfen() != sfen_2_previous:
                # 局面図の表示
                print(f"[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手] 局面巻き戻しエラー")
                print(board)
                print(f"  sfen:`{board.sfen()}`  board.move_number:{board.move_number}")
                raise ValueError("局面巻き戻しエラー")

            # 元の局面に戻してから strengthen する
            if is_strong_move:
                strengthen_result_str = kifuwarabe.strengthen(
                        cmd_tail=move_u,
                        is_debug=is_debug)

                # 変更はログに出したい
                print(f'[{datetime.datetime.now()}] [learn > 逃げる方 > 悪手]        strengthen {move_u:5}  result:`{strengthen_result_str}`')


        #
        # おわり
        # -----
        #

        # 終局図の内部データに戻す
        restore_end_position()

        # 全ての評価値テーブル［0:先手, 1:後手］の（変更があれば）保存
        kifuwarabe.save_eval_all_tables()

        print(f"[{datetime.datetime.now()}] [learn] finished", flush=True)
