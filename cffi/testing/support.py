import sys

if sys.version_info < (3,):
    __all__ = ['u']

    class U(object):
        def __add__(self, other):
            return eval('u'+repr(other).replace(r'\\u', r'\u')
                                       .replace(r'\\U', r'\U'))
    u = U()
    assert u+'a\x00b' == eval(r"u'a\x00b'")
    assert u+'a\u1234b' == eval(r"u'a\u1234b'")
    assert u+'a\U00012345b' == eval(r"u'a\U00012345b'")

else:
    __all__ = ['u', 'unicode', 'long']
    u = ""
    unicode = str
    long = int
