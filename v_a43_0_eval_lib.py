import os
import datetime
import random


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
        print(f"[{datetime.datetime.now()}] read {file_name_obj.base_name} file ...", flush=True)

        table_as_array = []

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

            print(f"[{datetime.datetime.now()}] '{file_name_obj.base_name}' file loaded. evaluation table size: {len(table_as_array)}", flush=True)

        except FileNotFoundError as ex:
            print(f"[evaluation table / load from file] [{file_name_obj.base_name}] file error. {ex}")
            raise

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
            table_as_array):
        """ファイルへ保存します

        Parameters
        ----------
        file_name_obj : FileName
            ファイル名オブジェクト
        """

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

        try:
            print(f"[{datetime.datetime.now()}] remove ./{file_name_obj.base_name} file...", flush=True)

            os.remove(
                    path=f'./{file_name_obj.base_name}')

        # ファイルが見つからないのは好都合なので無視します
        except FileNotFoundError:
            pass

        print(f"[{datetime.datetime.now()}] rename {file_name_obj.temporary_base_name} file to {file_name_obj.base_name}...", flush=True)

        os.rename(
                src=file_name_obj.temporary_base_name,
                dst=file_name_obj.base_name)
