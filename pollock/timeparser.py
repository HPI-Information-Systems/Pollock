"""Code from https://github.com/thomst/timeparser/"""
"""
Parse strings to objects of :mod:`datetime`.

This module intends to make string-parsing to :mod:`datetime`-objects as
easy as possible while allowing a fine configuration about which kind of formats
are supported:

Parsing any kind of string is as easy as:

    >>> date = parsedate('3 Jan 2013')
    datetime.date(2013, 1, 3)

Now suppose you don't want to allow parsing strings with literal month-names:

    >>> DateFormats.config(allow_month_name=False)
    >>> date = parsedate('3 Jan 2013')
    ValueError: couldn't parse '3 Jan 2013' as date

Most of the time you will use `format-classes`_ only to alter their configuration.
The `parser-functions`_ (except :func:`parsetimedelta`) use the `format-classes`_
to recieve a list of format-strings and try to parse the string with them using
:meth:`datetime.datetime.strptime`.

:func:`parsetimedelta` breaks with that concept. It don't need format-strings at
all and has his own :func:`logic <parsetimedelta>`.

A closer look at `format-classes`_
----------------------------------

`Format-classes`_ are actual :obj:`list`-types that provides two main-features:
    * They produce themselves as lists of format-strings accordingly to a set of
      parameters,
    * and they are configurable in regard to these parameters.

To create a list with an altered configuration you can either pass keyword-
arguments to the constructor:

    >>> formats = TimeFormats(seps=['-', ':', ';'], allow_microsec=True)

or change the default-configuration on class-level:

    >>> TimeFormats.config(seps=['-', ':', ';'], allow_microsec=True)
    >>> formats = TimeFormats()

Both will result in the same list of formats, but the former way doesn't touch
the default-configuration.

If you just call the constructor the format-class will produce a list of all
formats for the actual configuration:

    >>> formats = DateFormats()
    >>> len(formats)
    77

But if you look for formats for a specific string you can pass the string to the
constructor:

    >>> DateFormats('3 Jan 2013')
    ['%d %b %Y']

That is what the `parser-functions`_ do to minimize the amount of formats they
have to try to parse the string with.

Producing formats for a specific string also respects the current setting:

    >>> set(DateFormats('3 Jan 2013')) < set(DateFormats())
    True
    >>> DateFormats.config(allow_month_name=False)
    >>> DateFormats('3 jan 2013')
    ValueError: no proper format for '3 jan 2013'
"""

import datetime
import re
import subprocess
import shlex

import warnings

warnings.simplefilter('default')

__version__ = '0.7.4'


class Today:
    """
    Today emulates a :class:`datetime.date`-object that could be changed through
    :meth:`set`.

    On creation Today will be set to :meth:`datetime.date.today`.

    Because :obj:`datetime.date`-objects are not mutable (but Today-instance has
    to be), Today imitates a :obj:`datetime.date` just saving one as
    :attr:`Today.dateobj` and let :attr:`Today.year`, :attr:`Today.month` and
    :attr:`Today.day` returning its values.
    """

    def __init__(self):
        self.set()

    def set(self, *args, **kwargs):
        """
        Change TODAY.

        :arg int year:      year
        :arg int month:     month
        :arg int day:       day
        """
        if args or kwargs:
            self._dateobj = datetime.date(*args, **kwargs)
        else:
            self._dateobj = datetime.date.today()
        for a in ('month', 'year', 'day', 'replace', '__repr__', '__eq__'):
            setattr(self, a, getattr(self._dateobj, a))


TODAY = Today()
"""
TODAY is an instance of :class:`Today` and is used to complement dates that were
parsed with an incomplete format-string:

    >>> TODAY
    TODAY(2013, 5, 9)
    >>> parsedate('20 Apr')
    datetime.date(2013, 4, 20)

or even:

    >>> TODAY
    TODAY(2013, 5, 9)
    >>> parsedate('20')
    datetime.date(2013, 5, 20)

TODAY defaults to :meth:`datetime.date.today`, but can be changed through
:meth:`Today.set`:

    >>> TODAY.set(2000, 1, 1)
    >>> parsedate('20')
    datetime.date(2000, 1, 20)
"""


class Endian:
    """
    Endian emulates a tuple, which represents the order of a date.

    Dates can be ordered in three different ways:

        * little-endian:    ``('day', 'month', 'year')``
        * big-endian:       ``('year', 'month', 'day')``
        * middle-endian:    ``('month', 'day', 'year')``

    On creation a local default-order is guessed (either little- or big-endian).
    To change it use :meth:`set`.
    """
    OPTIONS = dict(
        little=('day', 'month', 'year'),
        big=('year', 'month', 'day'),
        middle=('month', 'day', 'year')
    )

    # TODO: in try_hard-mode all endian-modes should be checked.
    @property
    def options(self):
        """
        List of endian-options leaded by the set endian-mode.
        """
        eithor = ('little', 'big')
        keys = (self._key, eithor[(eithor.index(self._key) + 1) % 2], 'middle')
        return [self.OPTIONS[k] for k in keys]

    def __init__(self):
        self.set()

    def set(self, key=None):
        """
        Set ENDIAN to little-, big- or middle-endian.

        :arg key:       A string matching 'little', 'big' or 'middle'.
        :type key:      str or None

        If key is None the local-default-order is guessed.
        """
        self._key = self._check_key(key) or self._guess()
        for m in ('__iter__', '__getitem__', '__repr__', 'index'):
            setattr(self, m, getattr(self.OPTIONS[self._key], m))

    def get(self, no_year=False, key=None):
        key = self._check_key(key) or self._key
        if no_year:
            if key in ['little', 'middle']:
                return self.OPTIONS[key][:-1]
            else:
                return self.OPTIONS[key][1:]
        endian = self.__class__()
        endian.set(self._check_key(key) or self._key)
        return endian

    @classmethod
    def _check_key(cls, key):
        if not key: return None
        for k in cls.OPTIONS.keys():
            if re.match(key, k): return k
        else:
            raise ValueError("'%s' is an invalid key" % key)

    @staticmethod
    def _guess():
        # today.strftime('%x') returns a middle-endian-date. Therefore I use the
        # unix's date-command.
        # (Mind that this won't work if date +%x returns a datestring with a
        # two-digit-year.)
        # TODO: find a more solid way (which could also regard 'middle')
        popen = subprocess.Popen(
            shlex.split('date +%x'),
            stdout=subprocess.PIPE)
        datestring = popen.communicate()[0]
        one, two, three = re.findall(rb'[-+]?\d+', datestring)
        if int(one) == datetime.date.today().year:
            return 'big'
        else:
            return 'little'


ENDIAN = Endian()
"""
In generell dates could have one of three orders:
    * little-endian:    *day, month, year*
    * big-endian:       *year, month, day*
    * middle-endian:    *month, day, year*

ENDIAN is an instance of :class:`Endian` and defines the order that should be
applied:

    >>> ENDIAN
    ('day', 'month', 'year')
    >>> parsedate('26/4/13')
    datetime.date(2013, 4, 26)

On creation a local-default-order is guessed, but could be changed through
:meth:`Endian.set`:

    >>> ENDIAN.set('big')
    >>> ENDIAN
    ('year', 'month', 'day')
    >>> parsedate('26/4/13')
    datetime.date(2026, 4, 13)

.. warning::

    Guessing the local default is in a provisional state and a middle-endian-
    order is not regarded at all.
"""


class BaseFormats(list):
    """
    Base-class for format-classes; inherit from :class:`list`.

    :keyword string:            Pre-select formats for string.
    :keyword seps:              Allowed separators for formats.
    :keyword allow_no_sep:      Allows formats without any separator.
    :keyword try_hard:          Regardless of any configuration try hard to
                                build formats for the given string.
    :keyword figures:           List of three booleans that predicts how many
                                digits formats are allowed to have.

                                * figures[0]: allows a one-digit format ('%H')
                                * figures[1]: allows two-digit-fmts (e.g. '%H:%M')
                                * figures[2]: allows three-digit-fmts (e.g. '%H:%M:%S')

    :type seps:                 list
    :type allow_no_sep:         bool
    :type figures:              list

    :raises:                    ValueError if no format could be produced for
                                *string*.
    """
    ALLOW_NO_SEP = True
    """Allows formats without any separator ('%H%M%S')."""
    FIGURES = [True, True, True]
    """
    List of three booleans that predicts how many digits formats are allowed
    to have:

    * figures[0]: Allows the one-digit format '%H'.
    * figures[1]: Allows two-digit-formats like '%H:%M'.
    * figures[2]: Allows three-digit-formats like '%H:%M:%S'.
    """
    SFORMATS = list()
    ERR_MSG = "no proper format for '%s'"

    USE_FORMATS = True
    USE_SFORMATS = True

    TRY_HARD = False
    """
    Regardless of any configuration try hard to build formats for the given string.
    """

    @staticmethod
    def isnone(v):
        return type(v) == type(None)

    def __init__(self, string=None, seps=None, allow_no_sep=None, figures=None, \
                 try_hard=None, use_formats=None, use_sformats=None):
        super(BaseFormats, self).__init__()

        self._figures = figures or self.FIGURES[:]
        if self.isnone(seps):
            self._seps = self.SEPS[:]
        else:
            self._seps = seps[:]
        if self.isnone(allow_no_sep):
            self._allow_no_sep = self.ALLOW_NO_SEP
        else:
            self._allow_no_sep = allow_no_sep
        if self.isnone(use_formats):
            self._use_formats = self.USE_FORMATS
        else:
            self._use_formats = use_formats
        if self.isnone(use_sformats):
            self._use_sformats = self.USE_SFORMATS
        else:
            self._use_sformats = use_sformats
        if self.isnone(try_hard):
            self._try_hard = self.TRY_HARD
        else:
            self._try_hard = try_hard

        self._sformats = self.SFORMATS

        self._check_config()

        if string and self._try_hard:
            self._set_any_formats_for_string(string)
        elif string:
            self._set_allowed_formats_for_string(string)
        else:
            self._set_all(string)

    def _check_config(self):
        if not self._use_formats and not self._use_sformats:
            raise Exception('invalid configuration')
        if not any(self._figures):
            raise Exception('invalid configuration')

    @classmethod
    def config(cls, seps=None, allow_no_sep=None, figures=None, try_hard=None,
               use_formats=None, use_sformats=None):
        """
        Modify class-configuration.

        :keyword seps:              Allowed separators for formats.
        :keyword allow_no_sep:      Allows formats without any separator.
        :keyword try_hard:          Regardless of any configuration try hard to
                                    build formats for the given string.
        :keyword figures:           List of three booleans that predicts how many
                                    digits formats are allowed to have.

        :type seps:                 list
        :type allow_no_sep:         bool
        :type figures:              list
        """
        # TODO: overwork the concept of config: use **kwargs and check the dict
        if seps: cls.SEPS = seps
        if not cls.isnone(allow_no_sep): cls.ALLOW_NO_SEP = allow_no_sep
        if not cls.isnone(use_formats): cls.USE_FORMATS = use_formats
        if not cls.isnone(use_sformats): cls.USE_SFORMATS = use_sformats
        if not cls.isnone(try_hard): cls.TRY_HARD = try_hard
        if figures: cls.FIGURES = figures
        if not any(cls.FIGURES): raise Exception('invalid configuration')

    def _eval_ingredients(self, string):

        self._alternation = re.findall('[^\W_]+|[\W_]+', string)
        self._values = re.findall('[^\W_]+', string)
        self._nonvalues = re.findall('[\W_]+', string)

    def _eval_figures(self):
        """
        Evaluate the figures of the string.
        """

    def _eval_seps_and_formats(self):

        if len(self._values) == 4:
            self._use_formats = False
        elif not self._nonvalues and self._allow_no_sep:
            self._seps = list()
            self._use_sformats = False
        elif len(set(self._nonvalues)) == 1 and self._nonvalues[0] in self._seps:
            self._seps = [self._nonvalues[0]]
            self._allow_no_sep = False
            self._use_sformats = False
        else:
            self._use_formats = False

    def _get_code_list(self):
        """
        Builds and returns a list of code-lists (like ['%d', '%b', '%Y']).
        These code-lists will be joined to format-strings by self._all().
        """

    def _get_sformats(self):
        # TODO: rework this...
        formats = list()
        for l in self._sformats:
            l += [[str()] for x in range(7 - len(l))]
            formats.extend([
                a + b + c + d + e + f + g
                for a in l[0]
                for b in l[1]
                for c in l[2]
                for d in l[3]
                for e in l[4]
                for f in l[5]
                for g in l[6]
            ])
        return formats

    def _get_formats(self):
        code_list = self._get_code_list()
        formats = list()
        if self._allow_no_sep: self._seps.append(str())
        for s in self._seps:
            for codes in code_list:
                formats.append(s.join(codes))
        return formats

    def _get_all(self):
        formats = list()
        if self._use_formats: formats.extend(self._get_formats())
        if self._use_sformats: formats.extend(self._get_sformats())
        return [f for i, f in enumerate(formats) if not f in formats[:i]]

    def _analyse(self, string):

        self._eval_ingredients(string)
        self._eval_figures()
        self._eval_seps_and_formats()

    def _set_any_formats_for_string(self, string):

        self._figures = [True for b in self._figures]
        self._analyse(string)

        self.extend(self._get_formats_for_string())

    def _set_allowed_formats_for_string(self, string):

        self._analyse(string)

        # don't use set to keep the order
        str_fmts = self._get_formats_for_string()
        all_fmts = self._get_all()
        self.extend([f for f in str_fmts if f in all_fmts])

    def _set_all(self, string):

        self.extend(self._get_all())


class TimeFormats(BaseFormats):
    """
    A list of time-string-formats that generates himself.

    :keyword string:            Pre-select formats for string.
    :keyword seps:              Allowed separators for formats.
    :keyword allow_no_sep:      Allows formats without any separator.
    :keyword figures:           List of four booleans (s. :attr:`FIGURES`).
    :keyword try_hard:          Regardless of any configuration try hard to
                                build formats for the given string.

    :type string:               str
    :type seps:                 list
    :type allow_no_sep:         bool
    :type figures:              list
    :type allow_microsec:       bool

    :raises:                    ValueError if no format could be produced for
                                *string*.
    """
    CODES = ['%H', '%M', '%S', '%f']
    SEPS = [':', ' ']
    """A list of separators, formats are produced with."""
    ALLOW_NO_SEP = True
    """Allows formats without any separator ('%H%M%S')."""
    FIGURES = [True, True, True, False]
    """
    List of four booleans that predicts how many digits formats are allowed
    to have:

    * figures[0]: Allows the one-digit format '%H'.
    * figures[1]: Allows two-digit-formats like '%H:%M'.
    * figures[2]: Allows three-digit-formats like '%H:%M:%S'.
    * figures[3]: Allows four-digit-formats like '%H:%M:%S.%f'.
    """
    SFORMATS = [
        [['%H'], [':'], ['%M'], [':'], ['%S'], ['h', ' h']],
        [['%H'], [':', ''], ['%M'], ['h', ' h']],
        [['%H'], ['h', ' h']],
    ]
    MFORMATS = [
        [['%H'], [':'], ['%M'], [':'], ['%S'], ['.'], ['%f']],
        [['%H'], [''], ['%M'], [''], ['%S'], ['.'], ['%f']],
    ]

    def _eval_ingredients(self, string):

        self._values = re.findall('[\d]+', string)
        self._nonvalues = re.findall('[\D]+', string)
        self._alternation = re.findall('[\d]+|[\D]+', string)

    def _eval_figures(self):

        fmask = lambda f: map(lambda x, y: y if x else x, self._figures, f)

        d = self._values
        if len(d) == 4:
            self._figures = list(fmask([False, False, False, True]))
        elif len(d) == 3:
            self._figures = list(fmask([False, False, True, False]))
        elif len(d) == 2:
            self._figures = list(fmask([False, True, False, False]))
        elif len(d) == 1:
            if self._allow_no_sep:
                v = d[0]
                if len(v) > 6:
                    self._figures = list(fmask([False, False, False, True]))
                elif len(v) >= 5:
                    self._figures = list(fmask([False, False, True, True]))  # also figures[3]?
                elif len(v) >= 3:
                    self._figures = list(fmask([False, True, True, False]))
                elif len(v) == 2:
                    self._figures = list(fmask([True, True, False, False]))
                elif len(v) == 1:
                    self._figures = list(fmask([True, False, False, False]))
            else:
                self._figures = list(fmask([True, False, False, False]))
        else:
            self._figures = [False, False, False, False]

    def _get_formats_for_string(self):

        clist = self._get_code_list()
        formats = list()

        for l in clist:
            if len(self._values) == 1:
                c_or_v = lambda v: v if not v.isdigit() else ''.join(l)
            elif 1 < len(self._values) <= 4:
                iterator = iter(l)
                c_or_v = lambda v: v if not v.isdigit() else iterator.__next__()
            formats.append(str().join([c_or_v(v) for v in self._alternation]))

        return formats

    def _get_code_list(self):
        code_list = list()
        if self._figures[0]: code_list.append(self.CODES[:1])
        if self._figures[1]: code_list.append(self.CODES[:2])
        if self._figures[2]: code_list.append(self.CODES[:3])
        if self._figures[3]: code_list.append(self.CODES[:4])
        return code_list

    def _get_sformats(self):
        if self._figures[3]: self._sformats += self.MFORMATS
        return super(TimeFormats, self)._get_sformats()


class DateFormats(BaseFormats):
    """
    A list of date-string-formats that generates himself.

    :keyword string:            Pre-select formats for string.
    :keyword seps:              Allowed separators for formats.
    :keyword allow_no_sep:      Allows formats without any separator.
    :keyword figures:           List of three booleans (s. :attr:`FIGURES`).
    :keyword allow_month_name:  Allows formats with month-names (%b or %B)
    :keyword try_hard:          Regardless of any configuration try hard to
                                build formats for the given string.

    :type string:               str
    :type seps:                 list
    :type allow_no_sep:         bool
    :type figures:              list
    :type allow_month_name:     bool

    :raises:                    ValueError if no format could be produced for
                                *string*.
    """
    CODES = ['%d', '%m', '%y']
    CODE_DICT = {
        'year': ['%y', '%Y'],
        'month': ['%m', '%b', '%B'],
        'day': ['%d']
    }
    SEPS = ['.', '-', '/', ' ', '. ']
    """A list of separators, formats are produced with."""
    ALLOW_NO_SEP = True
    """Allows formats without any separator ('%d%m%y')."""
    FIGURES = [True, True, True]
    """
    List of three booleans that predicts how many digits formats are allowed
    to have:

    * figures[0]: Allows the one-digit format '%d'.
    * figures[1]: Allows two-digit-formats like '%d/%m'.
    * figures[2]: Allows three-digit-formats like '%d/%m/%y'.
    """
    MONTH_CODE = [True, True, True]
    YEAR_CODE = [True, True]

    SFORMATS_OPTIONS = {
        'little': [
            [['%d'], ['.', '. '], ['%m', '%b'], ['.']],
            [['%d'], ['.'], ['%m', '%b'], ['. '], ['%y', '%Y']],
            [['%d'], ['.', '. '], ['%b', '%B'], [' '], ['%y', '%Y']],
        ],
        'big': [
            [['%m', '%b'], ['.', '. '], ['%d'], ['.']],
            [['%b', '%B'], [' '], ['%d'], ['.']],
            [['%y', '%Y'], [' '], ['%m', '%b'], ['.', '. '], ['%d'], ['.']],
            [['%y', '%Y'], [' '], ['%b', '%B'], [' '], ['%d'], ['.']],
        ],
        'middle': [
        ]
    }

    SFORMATS = list()

    def __init__(self, *args, **kwargs):

        allow_month_name = kwargs.pop('allow_month_name', None)
        if self.isnone(allow_month_name):
            self._month_code = self.MONTH_CODE
        elif allow_month_name:
            self._month_code = [True, True, True]
        elif not allow_month_name:
            self._month_code = [True, False, False]

        self._year_code = self.YEAR_CODE
        self.SFORMATS = self.SFORMATS_OPTIONS[ENDIAN._key]

        super(DateFormats, self).__init__(*args, **kwargs)

    @classmethod
    def config(cls, *args, **kwargs):
        """
        Modify class-configuration.

        :keyword seps:              Allowed separators for formats.
        :keyword allow_no_sep:      Allows formats without any separator.
        :keyword figures:           List of three booleans (s. :attr:`FIGURES`).
        :keyword allow_month_name:  Allows formats with month-names (%b or %B)
        :keyword try_hard:          Regardless of any configuration try hard to
                                    build formats for the given string.

        :type seps:                 list
        :type allow_no_sep:         bool
        :type figures:              list
        :type allow_month_name:     bool
        """
        allow_month_name = kwargs.pop('allow_month_name', None)
        if cls.isnone(allow_month_name):
            pass
        elif allow_month_name:
            cls.MONTH_CODE = [True, True, True]
        elif not allow_month_name:
            cls.MONTH_CODE = [True, False, False]

        super(DateFormats, cls).config(*args, **kwargs)
        for c in [cls.MONTH_CODE, cls.YEAR_CODE]:
            if not any(c): raise Exception('invalid configuration')

    def _check_config(self):
        for c in [self._month_code, self._year_code, self._figures]:
            if not any(c): raise Exception('invalid configuration')

    def _analyse(self, string):

        self._eval_ingredients(string)
        self._eval_monthname(string)
        self._eval_figures()
        self._eval_seps_and_formats()

    def _eval_monthname(self, string):

        mmask = lambda m: map(lambda x, y: y if x else x, self._month_code, m)

        if re.search('(?<![a-zA-Z])[a-zA-Z]{3}(?![a-zA-Z])', string):
            self._month_code = mmask([False, True, False])
        elif re.search('(?<![a-zA-Z])[a-zA-Z]{4,9}(?![a-zA-Z])', string):
            self._month_code = mmask([False, False, True])
        elif not re.search('[a-zA-Z]+', string):
            self._month_code = mmask([True, False, False])
        else:
            self._figures = [False, False, False]

    def _eval_figures(self):

        fmask = lambda f: map(lambda x, y: y if x else x, self._figures, f)
        ymask = lambda y: map(lambda x, y: y if x else x, self._year_code, y)

        if len(self._values) == 3:
            if len(self._values[ENDIAN.index('year')]) == 2:
                self._year_code = ymask([True, False])
            else:
                self._year_code = ymask([False, True])
            self._figures = fmask([False, False, True])
        elif len(self._values) == 2:
            self._figures = fmask([False, True, False])
        elif len(self._values) == 1:
            value = self._values[0]
            if self._nonvalues:
                self._figures = fmask([True, False, False])
            elif not self._nonvalues and self._allow_no_sep:
                if any(self._month_code[1:]):
                    if value[-1].isalpha():
                        self._figures = fmask([False, True, False])
                    else:
                        self._figures = fmask([False, False, True])
                elif len(value) == 1:
                    self._figures = fmask([True, False, False])
                elif len(value) <= 3:
                    self._figures = fmask([True, True, False])
                else:
                    if len(value) <= 4:
                        self._figures = fmask([False, True, True])
                    else:
                        self._figures = fmask([False, False, True])
                    if len(value) <= 5:
                        self._year_code = ymask([True, False])
                    elif len(value) >= 7:
                        self._year_code = ymask([False, True])
            else:
                self._figures = [False, False, False]
        else:
            self._figures = [False, False, False]

    def _get_formats_for_string(self):

        clist = self._get_code_list()
        formats = list()

        for l in clist:
            if len(self._values) == 1:
                c_or_v = lambda v: v if not v.isalnum() else ''.join(l)
            elif 1 < len(self._values) <= 4:
                iterator = iter(l)
                c_or_v = lambda v: v if not v.isalnum() else iterator.__next__()
            formats.append(str().join([c_or_v(v) for v in self._alternation]))

        return formats

    def _get_code_list(self):
        def get_code(key):
            if key == 'month':
                mcodes = self.CODE_DICT['month']
                return filter(lambda c: self._month_code[mcodes.index(c)], mcodes)
            elif key == 'year':
                ycodes = self.CODE_DICT['year']
                return filter(lambda c: self._year_code[ycodes.index(c)], ycodes)
            elif key == 'day':
                return ['%d']

        code_list = list()
        if self._figures[0]: code_list.append(get_code('day'))
        if self._figures[1]:
            cc = map(get_code, ENDIAN.get(no_year=True))
            code_list.extend([(x, y) for x in cc[0] for y in cc[1]])
        if self._figures[2]:
            cc = map(get_code, ENDIAN)
            code_list.extend([(x, y, z) for x in cc[0] for y in cc[1] for z in cc[2]])

        return code_list

    def _get_formats(self):
        code_list = self._get_code_list()
        formats = list()
        if self._allow_no_sep: self._seps.append(str())
        for s in self._seps:
            for codes in code_list:
                formats.append(s.join(codes))
                if s == '.' and codes[-1] in ['%m', '%d']:
                    codes = list(codes)
                    codes.append(str())
                    formats.append(s.join(codes))
        return formats

    def _set_any_formats_for_string(self, string):
        self._month_code = [True, True, True]
        self._year_code = [True, True]
        super(DateFormats, self)._set_any_formats_for_string(string)


class DatetimeFormats(BaseFormats):
    """
    A list of datetime-string-formats that generates himself.

    :keyword string:            Pre-select formats for string.
    :keyword seps:              Allowed separators for formats.
    :keyword allow_no_sep:      Allows formats without any separator.
    :keyword date_config:       kwargs :class:`DateFormats` are initialized with
    :keyword time_config:       kwargs :class:`TimeFormats` are initialized with
    :keyword try_hard:          Regardless of any configuration try hard to
                                build formats for the given string.

    :type string:               str
    :type seps:                 list
    :type allow_no_sep:         bool
    :type date_config:          dict
    :type time_config:          dict

    :raises:                    ValueError if no format could be produced for
                                *string*.
    """
    SEPS = [' ', ',', '_', ';']
    """A list of separators, formats are produced with."""
    ALLOW_NO_SEP = True
    """Allows formats without any separator ('%H%M%S')."""

    def __init__(self, *args, **kwargs):
        date_config = kwargs.pop('date_config', dict())
        time_config = kwargs.pop('time_config', dict())
        self._date_config = dict(
            seps=DateFormats.SEPS,
            allow_no_sep=DateFormats.ALLOW_NO_SEP,
            figures=DateFormats.FIGURES,
            allow_month_name=DateFormats.MONTH_CODE[-1],
        )
        self._time_config = dict(
            seps=TimeFormats.SEPS,
            allow_no_sep=TimeFormats.ALLOW_NO_SEP,
            figures=TimeFormats.FIGURES,
        )
        self._date_config.update(date_config)
        self._time_config.update(time_config)
        super(DatetimeFormats, self).__init__(*args, **kwargs)

    @classmethod
    def config(self, *args, **kwargs):
        """
        Modify class-configuration.

        :keyword seps:              Allowed separators for formats.
        :keyword allow_no_sep:      Allows formats without any separator.
        :keyword date_config:       kwargs :class:`DateFormats` are initialized with
        :keyword time_config:       kwargs :class:`TimeFormats` are initialized with
        :keyword try_hard:          Regardless of any configuration try hard to
                                    build formats for the given string.

        :type seps:                 list
        :type allow_no_sep:         bool
        :type date_config:          dict
        :type time_config:          dict
        """
        super(DatetimeFormats, self).config(*args, **kwargs)

    def _check_config(self):
        pass

    def _analyse(self, string):

        self._eval_ingredients(string)
        self._seperate_string(string)

    def _seperate_string(self, string):
        """
        Try to reduce the amount of seps for all three format-classes.
        time-seps and date-seps will be passed to the respective constructor.
        """

        self._pairs = list()
        a = self._alternation

        if len(self._values) == 1 and self._allow_no_sep:
            i = len(string)
            while i > 1:
                i -= 1
                self._pairs.append((string[:i], str(), string[i:]))

        elif len(self._values) == 2:
            i = a.index(self._values[0]) + 1
            self._pairs.append((''.join(a[:i]), a[i], ''.join(a[i + 1:])))

        else:
            nvl = self._nonvalues[:]
            nvl.reverse()

            # prefer space-seperators
            spl = [nvl.pop(nvl.index(v)) for v in nvl[:] if ' ' in v]
            for nv in spl:
                i = a.index(nv)
                if i == 0 or i == a.index(a[-1]): continue
                self._pairs.append((''.join(a[:i]), a[i], ''.join(a[i + 1:])))

            for nv in nvl:
                i = a.index(nv)
                if i == 0 or i == a.index(a[-1]): continue
                self._pairs.append((''.join(a[:i]), a[i], ''.join(a[i + 1:])))

    def _get_formats_for_string(self):

        formats = list()

        for d, s, t in self._pairs:
            try:
                # TODO: make the order of date and time configurable
                df = DateFormats(d)
                tf = TimeFormats(t)
            except ValueError:
                continue
            else:
                fmts = [d + s + t for d in df for t in tf]
                formats.extend(fmts)

        # make sure the formats-list is unique (using set would destroy the order)
        return [f for i, f in enumerate(formats) if not f in formats[:i]]

    def _get_all(self):
        """
        Generate datetime-formats by combining date- and time-formats.
        """
        formats = list()
        date_fmt = DateFormats(**self._date_config)
        time_fmt = TimeFormats(**self._time_config)
        for s in self._seps:
            formats += [s.join((d, t)) for d in date_fmt for t in time_fmt]
        if self._allow_no_sep:
            # TODO: warrant that no sformats are included
            self._date_config['allow_no_sep'] = True
            self._time_config['allow_no_sep'] = True
            self._date_config['seps'] = list()
            self._time_config['seps'] = list()
            self._date_config['use_sformats'] = False
            self._time_config['use_sformats'] = False
            date_fmt = DateFormats(**self._date_config)
            time_fmt = TimeFormats(**self._time_config)
            formats += [str().join((d, t)) for d in date_fmt for t in time_fmt]

        return formats


def parsetime(string, formats=list()):
    """
    Parse a string to a :class:`datetime.time` -object.

    :arg str string:        String to be parsed.
    :keyword list formats:  Optional list of formats-string.

    :rtype:                 :class:`datetime.time`
    :raises:                ValueError, if string couldn't been parsed

    The string is tried to be parsed with every format of *formats*.
    If *formats* not given :class:`TimeFormats`\ (string) is used.
    """
    formats = formats or TimeFormats(string=string)
    for f in formats:
        try:
            return datetime.datetime.strptime(string, f).time()
        except ValueError:
            continue
    raise ValueError("couldn't parse '%s' as time" % string)


def parsedate(string, formats=list(), today=None):
    """
    Parse a string to a :class:`datetime.date`-object.

    :arg str string:        String to be parsed.
    :keyword list formats:  Optional list of formats-string.
    :keyword today:         optional date
    :type today:            datetime.date

    :rtype:                 :class:`datetime.date`
    :raises:                ValueError, if string couldn't been parsed

    *string* is tried to be parsed with every format of *formats*.
    If *formats* not given :class:`DateFormats`\ (string) is used.

    If *string* is parsed with an incomplete format (missing year or year and
    month), the date will be completed by *today* or :attr:`timeparser.TODAY`.
    """
    formats = formats or DateFormats(string=string)
    today = today or TODAY
    for f in formats:
        try:
            date = datetime.datetime.strptime(string, f).date()
        except ValueError:
            continue
        else:
            if '%y' not in f.lower():
                date = date.replace(year=today.year)
            if '%m' not in f and '%b' not in f.lower():
                date = date.replace(month=today.month)
            return date
    raise ValueError("couldn't parse '%s' as date" % string)


def parsedatetime(string, formats=list(), today=None):
    """
    Parse a string to a :class:`datetime.datetime`-object.

    :arg str string:        String to be parsed.
    :keyword list formats:  Optional list of formats-string.
    :keyword today:         Optional date
    :type today:            datetime.datetime

    :rtype:                 :class:`datetime.datetime`
    :raises:                ValueError, if string couldn't been parsed

    *string* is tried to be parsed with every format of *formats*.
    If *formats* not given :class:`DatetimeFormats`\ (string) is used.

    If *string* is parsed with an incomplete format (missing year or year and
    month), the date will be completed by *today* or :attr:`timeparser.TODAY`.
    """
    formats = formats or DatetimeFormats(string=string)
    today = today or TODAY
    for f in formats:
        try:
            dtime = datetime.datetime.strptime(string, f)
        except ValueError:
            continue
        else:
            if '%y' not in f.lower():
                dtime = dtime.replace(year=today.year)
            if '%m' not in f and '%b' not in f.lower():
                dtime = dtime.replace(month=today.month)
            return dtime
    raise ValueError("couldn't parse '%s' as datetime" % string)


def parsetimedelta(string, key='weeks'):
    # TODO: rework the key-word-docstring-part.
    """
    Parse a string to a :class:`datetime.timedelta`-object.

    :arg str string:    String to be parsed.
    :keyword str key:   String that contains or matches a timedelta-keyword
                        (defaults to 'weeks').

    :rtype:             :class:`datetime.timedelta`
    :raises:            ValueError, if string couldn't been parsed

    parsetimedelta looks for digits in *string*, that could be seperated. These
    digits will be the arguments for :class:`datetime.timedelta`. Thereby *key*
    is used to determine the *unit* of the first argument, which could be one of
    the keywords for :class:`datetime.timedelta` ('weeks', 'days', 'hours',
    'minutes', 'seconds'). The following arguments get each the next lesser
    *unit*:

    >>> parsetimedelta('1, 2, 3', 'h') == datetime.timedelta(hours=1, minutes=2, seconds=3)
    True

    Another way is to just place keyword-matching literals within the string:

    >>> parsetimedelta('1h 2m 3s') == datetime.timedelta(hours=1, minutes=2, seconds=3)
    True
    """
    kws = ('weeks', 'days', 'hours', 'minutes', 'seconds')
    msg = "couldn't parse '%s' as timedelta"
    key_msg = "couldn't find a timedelta-key for '%s'"

    rkey = key.lower()

    values = [int(x) for x in re.findall('[-+]?\d+', string)]
    rkeys = re.findall('[a-zA-Z]+', string)

    try:
        key = [k for k in kws if re.match(rkey, k)][0]
    except IndexError:
        raise ValueError(key_msg % key)
    try:
        keys = map(lambda r: [k for k in kws if re.match(r, k)][0], rkeys)
    except IndexError:
        raise ValueError(msg % string)

    if len(keys) == len(values):
        kwargs = dict(zip(keys, values))
    elif keys:
        raise ValueError(msg % string)
    else:
        kwargs = dict(zip(kws[kws.index(key):], values))

    try:
        timedelta = datetime.timedelta(**kwargs)
    except:
        raise ValueError(msg % string)
    else:
        return timedelta
