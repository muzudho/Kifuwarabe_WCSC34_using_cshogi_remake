import os
import datetime
import random
import time


class EvaluationLib():
    """評価関数テーブル用ライブラリー"""


    @staticmethod
    def read_evaluation_table_as_array_from_file(
            file_name_obj):
        """評価値テーブル・ファイルの読込

        Parameters
        ----------
        file_name_obj : FileName
            ファイル名オブジェクト
        """

        # ロードする。数分ほどかかる
        print(f"[{datetime.datetime.now()}] read   `{file_name_obj.base_name}` file ...", flush=True)

        table_as_array = []

        # 読込失敗時は、リトライを１０回は行いたい
        max_try = 10
        for retry in range(0,max_try):

            try:
                with open(file_name_obj.base_name, 'rb') as f:

                    one_byte_binary = f.read(1)

                    while one_byte_binary:
                        one_byte_num = int.from_bytes(one_byte_binary, signed=False)

                        # 大きな桁から、リストに追加していきます
                        table_as_array.append(one_byte_num//128 % 2)
                        table_as_array.append(one_byte_num// 64 % 2)
                        table_as_array.append(one_byte_num// 32 % 2)
                        table_as_array.append(one_byte_num// 16 % 2)
                        table_as_array.append(one_byte_num//  8 % 2)
                        table_as_array.append(one_byte_num//  4 % 2)
                        table_as_array.append(one_byte_num//  2 % 2)
                        table_as_array.append(one_byte_num//      2)

                        one_byte_binary = f.read(1)

                print(f"[{datetime.datetime.now()}] loaded `{file_name_obj.base_name}` file. evaluation table size: {len(table_as_array)}", flush=True)

                # リトライのループを抜ける
                break

            # （機械学習の実行中にアクセスすると）評価値ファイルが存在しない瞬間はある
            #FileNotFoundError
            except Exception as ex:

                # 次にループを抜けるタイミングなら、例外を投げ上げる
                if max_try <= retry + 1:
                    raise

                # ３０～５９秒後にリトライする
                else:
                    seconds = random.randint(30,60)
                    print(f"[{datetime.datetime.now()}] [evaluation lib > read evaluation table as array from file] failed to read `{file_name_obj.base_name}` file. wait for {seconds} seconds before retrying. ex:{ex}")
                    time.sleep(seconds)
                    continue

        return table_as_array


    @staticmethod
    def create_random_evaluation_table_as_array(
            a_move_size,
            b_move_size):
        """ランダム値の入った評価値テーブルの配列を新規作成する

        Parameters
        ----------
        a_move_size : int
            指し手Ａのサイズ
        b_move_size : int
            指し手Ｂのサイズ
        """

        # ダミーデータを入れる。１分ほどかかる
        print(f"[{datetime.datetime.now()}] make random evaluation table in memory... (a_move_size:{a_move_size} b_move_size:{b_move_size})", flush=True)

        new_table_as_array = []

        for _index in range(0, a_move_size * b_move_size):
            # 値は 0, 1 の２値
            new_table_as_array.append(random.randint(0,1))

        print(f"[{datetime.datetime.now()}] random evaluation table maked in memory. (size:{len(new_table_as_array)})", flush=True)
        return new_table_as_array


    @staticmethod
    def save_evaluation_table_file(
            file_name_obj,
            table_as_array,
            is_debug=False):
        """ファイルへ保存します

        保存するかどうかは先に判定しておくこと

        Parameters
        ----------
        file_name_obj : FileName
            ファイル名オブジェクト
        table_as_array : []
            配列
        is_debug : bool
            デバッグモードか？
        """

        if is_debug:
            print(f"[{datetime.datetime.now()}] save {file_name_obj.temporary_base_name} file ...", flush=True)

        # ファイルにバイナリ形式で出力する
        with open(file_name_obj.temporary_base_name, 'wb') as f:

            length = 0
            sum = 0

            for bit in table_as_array:
                if bit==0:
                    # byte型配列に変換して書き込む
                    # 1 byte の数 0
                    sum *= 2
                    sum += 0
                    length += 1
                else:
                    # 1 byte の数 1
                    sum *= 2
                    sum += 1
                    length += 1

                if 8 <= length:
                    # 整数型を、１バイトのバイナリーに変更
                    f.write(sum.to_bytes(1))
                    sum = 0
                    length = 0

            # 末端にはみ出た１バイト
            if 0 < length and length < 8:
                while length < 8:
                    sum *= 2
                    length += 1

                f.write(sum.to_bytes(1))

        # 読込失敗時は、リトライを１０回は行いたい
        max_try = 10
        for retry in range(0,max_try):

            try:
                if is_debug:
                    print(f"[{datetime.datetime.now()}] remove ./{file_name_obj.base_name} file...", flush=True)

                os.remove(
                        path=f'./{file_name_obj.base_name}')

            # ファイルが見つからないのは好都合なので無視します
            except FileNotFoundError:
                pass

            # ファイルが使用中かも。削除できないならリネームできないので困る
            except PermissionError as ex:

                # 次にループを抜けるタイミングなら、例外を投げ上げる
                if max_try <= retry + 1:
                    raise

                # ３０～５９秒後にリトライする
                else:
                    seconds = random.randint(30,60)
                    print(f"[{datetime.datetime.now()}] [evaluation lib > save evaluation table file] failed to remove `{file_name_obj.base_name}` file. wait for {seconds} seconds before retrying. ex:{ex}")
                    time.sleep(seconds)
                    continue

        if is_debug:
            print(f"[{datetime.datetime.now()}] rename {file_name_obj.temporary_base_name} file to {file_name_obj.base_name}...", flush=True)

        os.rename(
                src=file_name_obj.temporary_base_name,
                dst=file_name_obj.base_name)
