class Usi():
    """ＵＳＩプロトコル"""


    _rank_th_num_to_alphabet = {
        1:'a',
        2:'b',
        3:'c',
        4:'d',
        5:'e',
        6:'f',
        7:'g',
        8:'h',
        9:'i',
    }
    """1 から始まる段の整数を a から始まる英字に変換"""


    # 使ってない？
    @classmethod
    def get_rank_th_num_to_alphabet(clazz, rank_th):
        return clazz._rank_th_num_to_alphabet[rank_th]


    _srcloc_to_code = None
    """以下のような辞書を srcloc_to_code(...) 関数の初回使用時に自動生成する。
    code は、ＵＳＩ形式の指し手符号の先頭２文字。 '7g' や 'R*' など
    {
        0 : '1a',
        1 : '1b',
        ...
        81 : 'R*',
        ...
        87 : 'P*',
    }
    """


    @classmethod
    def sq_to_code(clazz, sq):
        """マス番号から、ＵＳＩ形式の符号の先頭２文字へ変換します"""
        file_th = sq // 9 + 1
        rank_th = sq % 9 + 1
        return f"{file_th}{clazz._rank_th_num_to_alphabet[rank_th]}"


    _srcdrop_str_list = ['R*', 'B*', 'G*', 'S*', 'N*', 'L*', 'P*']


    @classmethod
    def get_srcdrop_str_list(clazz):
        return clazz._srcdrop_str_list


    @classmethod
    def srcloc_to_code(clazz, srcloc):
        """0 ～ 87 の整数から、ＵＳＩ形式の指し手符号の先頭２文字へ変換"""
        if clazz._srcloc_to_code is None:
            clazz._srcloc_to_code = {}

            # 盤上のマス
            for sq in range(0,81):
                clazz._srcloc_to_code[sq] = clazz.sq_to_code(sq)

            # 打
            drop_num = 81
            for drop_str in clazz._srcdrop_str_list:
                clazz._srcloc_to_code[drop_num] = drop_str
                drop_num += 1

        return clazz._srcloc_to_code[srcloc]


    _code_to_srcloc = None
    """以下のような辞書を code_to_srcloc(...) 関数の初回使用時に自動生成する
    {
        '1a' : 0,
        '1b' : 1,
        ...
        '9i' : 80,
        'R*' : 81,
        ...
        'P*' : 87,
    }
    """


    @classmethod
    def code_to_srcloc(clazz, code):
        """ＵＳＩ形式の指し手符号の先頭２文字から、0 ～ 87 の整数へ変換"""
        if clazz._code_to_srcloc is None:
            clazz._code_to_srcloc = {}

            # 盤上のマス
            for sq in range(0,81):
                code_str = clazz.sq_to_code(sq)
                clazz._code_to_srcloc[code_str] = sq

            # 打
            drop_num = 81
            for drop_str in clazz._srcdrop_str_list:
                clazz._code_to_srcloc[drop_str] = drop_num
                drop_num += 1

        return clazz._code_to_srcloc[code]


    @staticmethod
    def sq_to_file_th_rank_th(sq):
        """盤上のマス番号を渡すと、 1 から始まる筋番号と、 1 から始まる段番号のタプルを返します"""
        return (sq // 9 + 1,
                sq % 9 + 1)


    @classmethod
    def file_th_rank_th_to_code(
            clazz,
            file_th,
            rank_th):
        return f"{file_th}{clazz._rank_th_num_to_alphabet[rank_th]}"


    @staticmethod
    def is_drop_by_srcloc(srcloc):
        """駒を打つ手か？

        Parameters
        ----------
        srcloc : int
            盤上のマス番号 0～80、または打つ駒の種類 81～87
        """
        return 81 <= srcloc and srcloc <= 87


    @staticmethod
    def srcloc_to_file_th_rank_th(srcloc):
        """元位置番号を渡すと、 1 から始まる筋番号と、 1 から始まる段番号のタプルを返します"""
        if Usi.is_drop_by_srcloc(srcloc):
            raise ValueError("[usi > srcloc to file_th rank th] 打はマス番号に変換できません")

        return (srcloc // 9 + 1,
                srcloc % 9 + 1)


    @staticmethod
    def srcloc_to_sq(srcloc):
        """元位置番号を受け取ると、マス番号を返します

        Returns
        -------
        sq : int
            マス番号。 0～80
        """
        if Usi.is_drop_by_srcloc(srcloc):
            raise ValueError("[usi > srcloc to sq] 打はマス番号に変換できません")

        return srcloc


    @staticmethod
    def rotate_srcloc(srcloc):
        # 打はそのまま返す
        if Usi.is_drop_by_srcloc(srcloc):
            return srcloc

        # 盤上の升番号は、盤を１８０°回転したときの位置の番号を返す
        return 80 - srcloc


    @staticmethod
    def promotion_to_code(promoted):
        """成る手"""
        if promoted:
            return '+'
        else:
            return ''


    @staticmethod
    def sq_to_jsa(sq):
        """0 から始まるマスの通し番号は読みずらいので、
        十の位を筋、一の位を段になるよう変換します。
        これは将棋の棋士も棋譜に用いている記法です。
        JSA は日本将棋連盟（Japan Shogi Association）

        Parameters
        ----------
        serial_sq_or_none : int
            0 から始まるマスの通し番号。打のときは None
        """

        (file_th,
         rank_th) = Usi.sq_to_file_th_rank_th(sq)

        return 10 * file_th + rank_th


    _srcloc_to_jsa = None
    """以下のような辞書を srcloc_to_jsa(...) 関数の初回使用時に自動生成する
    {
        0 : '1a',
        1 : '1b',
        ...
        80 : '9i',
        81 : 'R*',
        ...
        87 : 'P*',
    }
    """


    @classmethod
    def srcloc_to_jsa(clazz, srcloc):
        """元位置番号を、日本将棋連盟式のマスの符号へ変換"""
        if clazz._srcloc_to_jsa is None:
            clazz._srcloc_to_jsa = {}

            # 盤上のマス
            for sq in range(0,81):
                jsa_str = Usi.sq_to_jsa(sq)
                clazz._srcloc_to_jsa[sq] = jsa_str

            # 打
            drop_num = 81
            for drop_str in clazz._srcdrop_str_list:
                clazz._code_to_srcloc[drop_num] = drop_str
                drop_num += 1

        return clazz._srcloc_to_jsa[srcloc]


    #get_sq_by_file_rank
    @staticmethod
    def file_rank_to_sq(file, rank):
        """
        Parameters
        ----------
        file : int
            0 から始まる筋の番号
        rank : int
            0 から始まる段の番号
        """
        return file * 9 + rank


    @staticmethod
    def jsa_to_sq(jsa_sq):
        """プロ棋士も使っているマス番号の書き方は
        コンピューターには使いづらいので、
        0 から始まるマスの通し番号に変換します

        豆知識：　十の位を筋、一の位を段とするマス番号は、
                将棋の棋士も棋譜に用いている記法です。
                JSA は日本将棋連盟（Japan Shogi Association）

        Parameters
        ----------
        jsa_sq : int
            筋と段は 1 から始まる整数とし、
            十の位を筋、一の位を段とするマス番号
        """

        file = jsa_sq // 10 - 1
        rank = jsa_sq % 10 - 1

        return Usi.file_rank_to_sq(file, rank)
