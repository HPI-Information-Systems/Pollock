"""This file is used to fix project specific constant values, also enums and such
"""
from enum import Enum

RAND_SEED = 27


class Position(Enum):
    RANDOM = 1


class Distribution(Enum):
    FIRST = 1
    RANDOM = 2
    NO_DELIM = 3
    ALL_CELLS = 4


class NumberCells(Enum):
    ONE = 1
    RANDOM = 2
    OVERFLOW = 3


class Encoding(Enum):
    ASCII = 'ascii'
    BIG5 = 'big5'
    BIG5HKSCS = 'big5hkscs'
    CP037 = 'cp037'
    CP273 = 'cp273'
    CP424 = 'cp424'
    CP437 = 'cp437'
    CP500 = 'cp500'
    CP720 = 'cp720'
    CP737 = 'cp737'
    CP775 = 'cp775'
    CP850 = 'cp850'
    CP852 = 'cp852'
    CP855 = 'cp855'
    CP856 = 'cp856'
    CP857 = 'cp857'
    CP858 = 'cp858'
    CP860 = 'cp860'
    CP861 = 'cp861'
    CP862 = 'cp862'
    CP863 = 'cp863'
    CP864 = 'cp864'
    CP865 = 'cp865'
    CP866 = 'cp866'
    CP869 = 'cp869'
    CP874 = 'cp874'
    CP875 = 'cp875'
    CP932 = 'cp932'
    CP949 = 'cp949'
    CP950 = 'cp950'
    CP1006 = 'cp1006'
    CP1026 = 'cp1026'
    CP1125 = 'cp1125'
    CP1140 = 'cp1140'
    CP1250 = 'cp1250'
    CP1251 = 'cp1251'
    CP1252 = 'cp1252'
    CP1253 = 'cp1253'
    CP1254 = 'cp1254'
    CP1255 = 'cp1255'
    CP1256 = 'cp1256'
    CP1257 = 'cp1257'
    CP1258 = 'cp1258'
    CP65001 = 'cp65001'
    euc_jp = 'euc_jp'
    EUC_JIS_2004 = 'euc_jis_2004'
    EUC_JISX0213 = 'euc_jisx0213'
    EUC_KR = 'euc_kr'
    GB2312 = 'gb2312'
    GBK = 'gbk'
    GB18030 = 'gb18030'
    HZ = 'hz'
    ISO2022_JP = 'iso2022_jp'
    ISO2022_JP_1 = 'iso2022_jp_1'
    ISO2022_JP_2 = 'iso2022_jp_2'
    ISO2022_JP_2004 = 'iso2022_jp_2004'
    ISO2022_JP_3 = 'iso2022_jp_3'
    ISO2022_JP_EXT = 'iso2022_jp_ext'
    ISO2022_KR = 'iso2022_kr'
    LATIN_1 = 'latin_1'
    ISO8859_2 = 'iso8859_2'
    ISO8859_3 = 'iso8859_3'
    ISO8859_4 = 'iso8859_4'
    ISO8859_5 = 'iso8859_5'
    ISO8859_6 = 'iso8859_6'
    ISO8859_7 = 'iso8859_7'
    ISO8859_8 = 'iso8859_8'
    ISO8859_9 = 'iso8859_9'
    ISO8859_10 = 'iso8859_10'
    ISO8859_11 = 'iso8859_11'
    ISO8859_13 = 'iso8859_13'
    ISO8859_14 = 'iso8859_14'
    ISO8859_15 = 'iso8859_15'
    ISO8859_16 = 'iso8859_16'
    JOHAB = 'johab'
    KOI8_R = 'koi8_r'
    KOI8_T = 'koi8_t'
    KOI8_U = 'koi8_u'
    KZ1048 = 'kz1048'
    MAC_CYRILLIC = 'mac_cyrillic'
    MAC_GREEK = 'mac_greek'
    MAC_ICELAND = 'mac_iceland'
    MAC_LATIN2 = 'mac_latin2'
    MAC_ROMAN = 'mac_roman'
    MAC_TURKISH = 'mac_turkish'
    PTCP154 = 'ptcp154'
    SHIFT_JIS = 'shift_jis'
    SHIFT_JIS_2004 = 'shift_jis_2004'
    SHIFT_JISX0213 = 'shift_jisx0213'
    UTF_32 = 'utf_32'
    UTF_32_BE = 'utf_32_be'
    UTF_32_LE = 'utf_32_le'
    UTF_16 = 'utf_16'
    UTF_16_BE = 'utf_16_be'
    UTF_16_LE = 'utf_16_le'
    UTF_7 = 'utf_7'
    UTF_8 = 'utf_8'
    UT_8_SIG = 'utf_8_sig'

    supported_encodings = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737',
                           'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862',
                           'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950',
                           'cp1006', 'cp1026', 'cp1125', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254',
                           'cp1255', 'cp1256', 'cp1257', 'cp1258', 'cp65001', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
                           'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                           'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 'iso8859_2',
                           'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9',
                           'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab',
                           'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland',
                           'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004',
                           'shift_jisx0213', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be',
                           'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig']
