# 📖 [Python 3.11から新たに仲間に加わったTOMLパーサー](https://gihyo.jp/article/2022/11/monthly-python-2211)
# 📖 [tomllib --- TOML ファイルの解析](https://docs.python.org/ja/3.12/library/tomllib.html)
import tomllib
import datetime
from pprint import pprint


class LearnConfigDocument():
    """学習設定ドキュメント"""


    @staticmethod
    def get_base_name(
            engine_version_str):
        return f"{engine_version_str}_n1_learn_config.toml"


    @staticmethod
    def load_toml(
            base_name,
            engine_version_str):
        """設定ファイル読込"""

        print(f"[{datetime.datetime.now()}] [learn config document > load toml] read `{base_name}` file start...")

        try:
            with open(base_name, "rb") as f:
                document = tomllib.load(f)

            print(f"[{datetime.datetime.now()}] [learn config document > load toml] finished")

            return LearnConfigDocument(
                    document=document)

        except FileNotFoundError as ex:
            print(f"[{datetime.datetime.now()}] [learn config document > load toml] failed to read `{base_name}` file")
            return None


    def __init__(
            self,
            document):
        self._document = document


    @property
    def learn_rate_numerator(self):
        """学習率の分子"""
        return self._document['learn_rate']['numerator']


    @property
    def learn_rate_denominator(self):
        """学習率の分母"""
        return self._document['learn_rate']['denominator']


    @property
    def short_mate_mode_relay_move_number(self):
        """短手数の詰めチェックモードでの指し継ぎ手数"""
        return self._document['short_mate_mode']['relay_move_number']
