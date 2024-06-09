import os
import datetime
import time

# python v_a51_0_main_learn.py
from     v_a51_0 import Kifuwarabe, max_move_number, engine_version_str
from     v_a51_0_misc.game_result_document import GameResultDocument
from     v_a51_0_misc.learn import LearnAboutOneGame
from     v_a51_0_misc.learn_config_document import LearnConfigDocument
from     v_a51_0_misc.lib import BoardHelper


class LearningFramework():
    """学習フレームワーク"""


    def __init__(self):
        pass


    def start_it(
            self,
            board,
            kifuwarabe,
            is_debug):
        """学習フレームワークを始める

        Parameters
        ----------
        board : cshogi.Board
            現局面
        kifuwarabe : Kifuwarabe
            きふわらべ
        is_debug : bool
            デバッグモードか？
        """

        if is_debug:
            print(f"[{datetime.datetime.now()}] [learning framework > start it] start")

        # 強制終了するまで、ずっと繰り返す
        while True:
            # 学習設定ファイルの読込
            learn_config_file_base_name = LearnConfigDocument.get_base_name(engine_version_str)

            learn_config_document = LearnConfigDocument.load_toml(
                    base_name=learn_config_file_base_name,
                    engine_version_str=engine_version_str)

            if learn_config_document == None:
                # １分後にループをやり直し
                seconds = 60.0
                print(f"[{datetime.datetime.now()}] [learning framework > start it] failed to read `{learn_config_file_base_name}` file. wait for {seconds} seconds before retrying")
                time.sleep(seconds)
                continue


            # 評価値テーブルの読込
            kifuwarabe.load_eval_all_tables()

            original_file_name = GameResultDocument.get_file_name(engine_version_str)
            file_name_for_learning = GameResultDocument.get_file_name_for_learning(engine_version_str)

            if not os.path.isfile(original_file_name):
                # １分後にループをやり直し
                seconds = 60.0
                print(f"[{datetime.datetime.now()}] [learning framework > start it] `{original_file_name}` file not found. wait for {seconds} seconds before retrying")
                time.sleep(seconds)
                continue

            # （既存なら）学習用の一時ファイルを削除したい
            try:
                if is_debug:
                    print(f"[{datetime.datetime.now()}] [learning framework > start it] remove `{file_name_for_learning}` file...")

                os.remove(file_name_for_learning)

            # ファイルが存在しないなら無視する
            except FileNotFoundError:
                pass

            try:
                # 対局結果ファイルを、学習用にリネーム（対局結果ファイルは、学習を回したあと削除する）
                os.rename(
                        src=original_file_name,
                        dst=file_name_for_learning)

            except Exception as ex:
                # １分後にループをやり直し
                seconds = 60.0
                print(f"[{datetime.datetime.now()}] [learning framework > start it] failed to rename file. wait for {seconds} seconds before retrying. ex:{ex}")
                time.sleep(seconds)
                continue

            # 対局結果の学習用の一時ファイルのオブジェクト生成（ファイル読込はあとでする）
            game_result_document = GameResultDocument(
                    # ファイル名の幹だけ
                    file_stem=GameResultDocument.get_file_stem_for_learning(engine_version_str))

            # 対局結果ファイルの読込、各行取得
            game_result_record_list = game_result_document.read_record_list()

            # サイズ
            max_game = len(list(game_result_record_list))

            if is_debug:
                print(f"[{datetime.datetime.now()}] [learning framework > start it] length of game result record list:{max_game}")

            for game_index, game_result_record in enumerate(game_result_record_list):

                # position コマンドの読取
                kifuwarabe.position(
                        # position コマンドの position 抜き
                        cmd_tail=game_result_record.position_command.split(' ', 1)[1],
                        is_debug=is_debug)

                # 開始ログは出したい
                print(f"[{datetime.datetime.now()}] [learning framework > start it] ({game_index + 1:4}/{max_game}) start...", flush=True)

                # 学習する
                LearnAboutOneGame(
                        board=board,
                        kifuwarabe=kifuwarabe,
                        learn_config_document=learn_config_document,
                        is_debug=is_debug).learn_it()

                # 終了ログは出したい
                print(f"[{datetime.datetime.now()}] [learning framework > start it] ({game_index + 1:4}/{max_game}) finished, flush=True")

            # 学習用の一時ファイルを削除したい
            try:
                if is_debug:
                    print(f"[{datetime.datetime.now()}] [learning framework > start it] remove `{file_name_for_learning}` file...")

                os.remove(file_name_for_learning)

            except Exception as ex:
                print(f"[{datetime.datetime.now()}] [learning framework > start it] failed to remove `{file_name_for_learning}` file. ex:{ex}")
                # 学習用の一時ファイルを削除できなければ、結局次の学習のためのリネームで失敗するので、ここで強制終了しておく
                raise

            # 繰り返すので終わりではない
            if is_debug:
                print(f"[{datetime.datetime.now()}] [learning framework > start it] repeat")


########################################
# スクリプト実行時
########################################

if __name__ == '__main__':
    """スクリプト実行時"""

    #print(f"cshogi.BLACK:{cshogi.BLACK}  cshogi.WHITE:{cshogi.WHITE}")

    try:
        kifuwarabe = Kifuwarabe()
        print(kifuwarabe.board)

        learning_framework = LearningFramework()
        learning_framework.start_it(
                board=kifuwarabe.board,
                kifuwarabe=kifuwarabe,
                is_debug=False)

    except Exception as err:
        print(f"[{datetime.datetime.now()}] [learning framework > unexpected error] {err=}, {type(err)=}")
        raise
