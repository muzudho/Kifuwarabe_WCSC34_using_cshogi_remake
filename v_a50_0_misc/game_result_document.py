import os
import datetime
from v_a50_0_misc.lib import FileName, Turn, BoardHelper


class GameResultRecord():
    """１対局の結果"""

    @staticmethod
    def parse_line(
            line):
        """解析

        Parameters
        ----------
        line : str
            対局１つ分の１行
            {手番} {勝敗の結果} {理由} {対局コマンド}
        """
        tail = line
        (result_turn, tail) = tail.split(' ', 1)
        (result, tail) = tail.split(' ', 1)
        (reason, position_command) = tail.split(' ', 1)

        return GameResultRecord(
                result_turn=Turn.str_to_int(result_turn),
                result=result,
                reason=reason,
                position_command=position_command)


    def __init__(
            self,
            result_turn,
            result,
            reason,
            position_command):
        """初期化

        Parameters
        ----------
        result_turn : int
            勝敗の結果がどちらの手番について書かれているか。
            自分の対局の場合、自分の手番、それ以外は任意
        result : str
            勝敗の結果。 'win', 'lose', 'draw'
        reason : str
            勝敗の理由。 'max_move' とか色々
        position_command : str
            USI の position コマンド形式
        """
        self._result_turn = result_turn
        self._result = result
        self._reason = reason
        self._position_command = position_command


    @property
    def result_turn(self):
        return self._result_turn


    @property
    def result(self):
        return self._result


    @property
    def reason(self):
        return self._reason


    @property
    def position_command(self):
        return self._position_command


    def to_string_line(self):
        return f"{self.result_turn} {self.result}  {self.reason} {self.position_command}\n"


class GameResultDocument():
    """対局結果ドキュメント"""


    @staticmethod
    def get_file_stem(
            engine_version_str):
        """ファイル名の幹を作成

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        return f'data[{engine_version_str}]_n1_game_result'


    @staticmethod
    def get_file_extension():
        """ファイル拡張子を取得"""
        return '.txt'


    @staticmethod
    def get_file_name(
            engine_version_str):
        """ファイル名を作成

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        return f'{GameResultDocument.get_file_stem(engine_version_str)}{GameResultDocument.get_file_extension()}'


    @staticmethod
    def get_file_stem_for_learning(
            engine_version_str):
        """学習用の一時ファイル名の幹を作成

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        return f'data[{engine_version_str}]_n1_game_result_for_learn'


    @staticmethod
    def get_file_name_for_learning(
            engine_version_str):
        """ファイル名を作成

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        return f'{GameResultDocument.get_file_stem_for_learning(engine_version_str)}{GameResultDocument.get_file_extension()}'


    def __init__(
            self,
            file_stem):
        """初期化

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        self._file_name_obj = FileName(
            file_stem = file_stem,
            file_extension = '.txt')


    @property
    def file_name_obj(self):
        """ファイル名オブジェクト"""
        return self._file_name_obj


    def exists_file(self):
        """ファイルの存在確認"""
        return os.path.isfile(self.file_name_obj.base_name)


    def delete(self):
        """ファイルの削除"""

        try:
            print(f"[{datetime.datetime.now()}] delete `{self.file_name_obj.base_name}` file...", flush=True)
            os.remove(self.file_name_obj.base_name)
            print(f"[{datetime.datetime.now()}] deleted `{self.file_name_obj.base_name}` file", flush=True)

        except FileNotFoundError:
            # ファイルが無いのなら、削除に失敗しても問題ない
            pass


    #read_lines
    def read_record_list(self):
        """結果ファイルの読込

        Returns
        -------
        record_list : list<GameResultRecord>
            各行。１行は１対局分
        """

        print(f"[{datetime.datetime.now()}] read   `{self.file_name_obj.base_name}` file...", flush=True)

        try:

            with open(self.file_name_obj.base_name, 'r+', encoding="utf-8") as f:
                text = f.read()

            # 改行で分割
            lines = text.splitlines()
            record_list = []
            for line in lines:
                record_list.append(GameResultRecord.parse_line(line))
            print(f"[{datetime.datetime.now()}] read   `{self.file_name_obj.base_name}` file", flush=True)

            return record_list

        # ファイルの読込に失敗したら残念ですが、無視して続行します
        except Exception as ex:
            print(f'[{datetime.datetime.now()}] [read_record_list] failed to read `{self.file_name_obj.base_name}` file. ex:{ex}')
            return []


    @staticmethod
    def append_to_file_and_save(
            base_name,
            game_result_record):
        """ファイルに対局結果を追加して保存する

        Parameters
        ----------
        base_name : str
            ファイル名
        result : str
            'win', 'lose', 'draw'
        position_command : str
            USI の position コマンド
        """
        print(f"[{datetime.datetime.now()}] save `{base_name}` file...", flush=True)

        # サイズが膨大になるのを防ぎます
        try:
            byte_size = os.path.getsize(base_name)

        # ファイルが無いのならＯｋ
        except FileNotFoundError:
            byte_size = 0

        # 1 giga 超えたら保存やめとくか
        #      mega       kilo       bytes
        if 1024     * 1024     * 1024      < byte_size:
            print(f"[{datetime.datetime.now()}] failed to save `{base_name}` file. size is huge. {byte_size} bytes", flush=True)
            return

        try:
            # `a` - 追加モードでファイルを開く
            # `+` - ファイルが無ければ新規作成する
            with open(base_name, 'a+', encoding="utf-8") as f:
                f.write(game_result_record.to_string_line())

            print(f"[{datetime.datetime.now()}] saved `{base_name}` file", flush=True)

        except Exception as ex:
            # 保存に失敗したら残念ですが、無視して続行します
            print(f'[{datetime.datetime.now()}] [append_to_file_and_save] failed to save `{base_name}` file. ex:{ex}')


    def add_and_save(
            self,
            my_turn,
            result_str,
            reason,
            board):
        """結果を追加して保存

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        result_str : str
            勝敗の結果。半角空白を含めないでください
        reason : str
            勝敗の結果の理由
        board : Board
            将棋盤
        """

        result_turn = Turn.to_string(my_turn)

        position_command = BoardHelper.get_position_command(
                board=board)

        game_result_record = GameResultRecord(
                result_turn=result_turn,
                # 半角空白が混ざっていると構文が崩れるので、アンダースコアで強制的に置き換えます
                result=result_str.replace(" ", "_"),
                reason=reason,
                position_command=position_command)

        # ファイルに出力する
        GameResultDocument.append_to_file_and_save(
                base_name=self.file_name_obj.base_name,
                game_result_record=game_result_record)
