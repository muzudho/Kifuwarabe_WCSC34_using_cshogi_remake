import os
import datetime
from v_a46_0_misc.lib import FileName, Turn, BoardHelper


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
            print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file delete...", flush=True)
            os.remove(self.file_name_obj.base_name)
            print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file deleted", flush=True)

        except FileNotFoundError:
            # ファイルが無いのなら、削除に失敗しても問題ない
            pass


    def read_lines(self):
        """結果の読込"""
        try:
            print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file read ...", flush=True)

            with open(self.file_name_obj.base_name, 'r', encoding="utf-8") as f:
                text = f.read()

            # 改行で分割
            lines = text.splitlines()
            print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file read", flush=True)

            return lines

        # ファイルの読込に失敗
        except:
            return []


    def save_lose(self, my_turn, board):
        """負け

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        position_command = BoardHelper.get_position_command(
                board=board)

        print(f"あ～あ、 {turn_text} 番で負けたぜ（＞＿＜）", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file save ...", flush=True)

        with open(self.file_name_obj.base_name, 'w', encoding="utf-8") as f:
            f.write(f"""lose {turn_text}
{position_command}""")

        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file saved", flush=True)


    def save_win(self, my_turn, board):
        """勝ち

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        position_command = BoardHelper.get_position_command(
                board=board)

        print(f"やったぜ {turn_text} 番で勝ったぜ（＾ｑ＾）", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file save ...", flush=True)
        with open(self.file_name_obj.base_name, 'w', encoding="utf-8") as f:
            f.write(f"""win {turn_text}
{position_command}""")

        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file saved", flush=True)


    def save_draw(self, my_turn, board):
        """持将棋

        Parameters
        ----------
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        position_command = BoardHelper.get_position_command(
                board=board)

        print(f"持将棋か～（ー＿ー） turn: {turn_text}", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file save ...", flush=True)
        with open(self.file_name_obj.base_name, 'w', encoding="utf-8") as f:
            f.write(f"""draw {turn_text}
{position_command}""")

        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file saved", flush=True)


    def save_otherwise(self, result_text, my_turn, board):
        """予期しない結果

        Parameters
        ----------
        result_text : str
            結果文字列
        my_turn : Turn
            自分の手番
        board : Board
            将棋盤
        """

        turn_text = Turn.to_string(my_turn)
        position_command = BoardHelper.get_position_command(
                board=board)

        print(f"なんだろな（・＿・）？　'{result_text}', turn: '{turn_text}'", flush=True)

        # ファイルに出力する
        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file save ...", flush=True)
        with open(self.file_name_obj.base_name, 'w', encoding="utf-8") as f:
            f.write(f"""{result_text} {turn_text}
{position_command}""")

        print(f"[{datetime.datetime.now()}] {self.file_name_obj.base_name} file saved", flush=True)
