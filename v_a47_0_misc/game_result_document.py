import os
import datetime
from v_a47_0_misc.lib import FileName, Turn, BoardHelper


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
        """
        (result, tail) = line.split(' ', 1)
        (result_turn, position_command) = tail.split(' ', 1)

        return GameResultRecord(
                result=result,
                result_turn=Turn.str_to_int(result_turn),
                position_command=position_command)


    def __init__(
            self,
            result,
            result_turn,
            position_command):
        """初期化

        Parameters
        ----------
        result : str
            'win', 'lose', 'draw'
        result_turn : int
            結果がどちらの手番のものか
        position_command : str
            USI の position コマンド形式
        """
        self._result = result
        self._result_turn = result_turn
        self._position_command = position_command


    @property
    def result(self):
        return self._result


    @property
    def result_turn(self):
        return self._result_turn


    @property
    def position_command(self):
        return self._position_command


    def to_string_line(self):
        return f"{self.result} {self.result_turn} {self.position_command}\n"


class GameResultDocument():
    """対局結果ドキュメント"""


    def __init__(
            self,
            engine_version_str):
        """初期化

        Parameters
        ----------
        engine_version_str : str
            将棋エンジンのバージョン
        """
        self._file_name_obj = FileName(
            file_stem = f'data[{engine_version_str}]_n1_game_result',
            file_extension = '.txt')


    @property
    def file_name_obj(self):
        """ファイル名オブジェクト"""
        return self._file_name_obj


    def exists(self):
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
        """結果の読込

        Returns
        -------
        record_list : list<GameResultRecord>
            各行。１行は１対局分
        """

        print(f"[{datetime.datetime.now()}] read `{self.file_name_obj.base_name}` file...", flush=True)

        try:

            with open(self.file_name_obj.base_name, 'r+', encoding="utf-8") as f:
                text = f.read()

            # 改行で分割
            lines = text.splitlines()
            record_list = []
            for line in lines:
                record_list.append(GameResultRecord.parse_line(line))
            print(f"[{datetime.datetime.now()}] read `{self.file_name_obj.base_name}` file", flush=True)

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



    def add_loss_and_save(self, my_turn, board):
        """負け

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        result_turn = Turn.to_string(my_turn)

        print(f"あ～あ、 {result_turn} 番で負けたぜ（＞＿＜）", flush=True)

        position_command = BoardHelper.get_position_command(
                board=board)
        game_result_record = GameResultRecord(
                result='lose',
                result_turn=result_turn,
                position_command=position_command)

        # ファイルに出力する
        GameResultDocument.append_to_file_and_save(
                base_name=self.file_name_obj.base_name,
                game_result_record=game_result_record)


    def add_win_and_save(self, my_turn, board):
        """勝ち

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        result_turn = Turn.to_string(my_turn)

        print(f"やったぜ {result_turn} 番で勝ったぜ（＾ｑ＾）", flush=True)

        position_command = BoardHelper.get_position_command(
                board=board)
        game_result_record = GameResultRecord(
                result='win',
                result_turn=result_turn,
                position_command=position_command)

        # ファイルに出力する
        GameResultDocument.append_to_file_and_save(
                game_result_record=game_result_record)


    def add_draw_and_save(self, my_turn, board):
        """持将棋

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        result_turn = Turn.to_string(my_turn)

        print(f"持将棋か～（ー＿ー） turn: {result_turn}", flush=True)

        position_command = BoardHelper.get_position_command(
                board=board)
        game_result_record = GameResultRecord(
                result='draw',
                result_turn=result_turn,
                position_command=position_command)

        # ファイルに出力する
        GameResultDocument.append_to_file_and_save(
                base_name=self.file_name_obj.base_name,
                game_result_record=game_result_record)


    def add_otherwise_and_save(self, result_text, my_turn, board):
        """予期しない結果を追加して保存

        Parameters
        ----------
        result_text : str
            結果文字列。半角空白を含めないでください
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        result_turn = Turn.to_string(my_turn)

        print(f"なんだろな（・＿・）？　'{result_text}', turn: '{result_turn}'", flush=True)

        position_command = BoardHelper.get_position_command(
                board=board)
                # 半角空白が混ざっていると構文が崩れるので、アンダースコアで強制的に置き換えます
        game_result_record = GameResultRecord(
                result=result_text.replace(" ", "_"),
                result_turn=result_turn,
                position_command=position_command)

        # ファイルに出力する
        GameResultDocument.append_to_file_and_save(
                base_name=self.file_name_obj.base_name,
                game_result_record=game_result_record)
