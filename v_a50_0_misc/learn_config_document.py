# 📖 [Python 3.11から新たに仲間に加わったTOMLパーサー](https://gihyo.jp/article/2022/11/monthly-python-2211)
# 📖 [tomllib --- TOML ファイルの解析](https://docs.python.org/ja/3.12/library/tomllib.html)
import tomllib
from pprint import pprint


class LearnConfigDocument():
    """学習設定ドキュメント"""


    @staticmethod
    def load_toml(
            engine_version_str):

        with open(f"data[{engine_version_str}]_n1_learn.config.toml", "rb") as f:
            document = tomllib.load(f)


    def __init__(
            self,
            document):
        self._document = document


    @property
    def learn_rate_numerator(self):
        """学習率の分子"""
        return self._document['learn_rate']['numerator']


    @property
    def learn_rate_numerator(self):
        """学習率の分母"""
        return self._document['learn_rate']['denominator']
