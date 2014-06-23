import py, re
import sys, os, math, weakref
from cffi import FFI, VerificationError, VerificationMissing, model
from testing.support import *


lib_m = ['m']
if sys.platform == 'win32':
    #there is a small chance this fails on Mingw via environ $CC
    import distutils.ccompiler
    if distutils.ccompiler.get_default_compiler() == 'msvc':
        lib_m = ['msvcrt']
    pass      # no obvious -Werror equivalent on MSVC
else:
    if (sys.platform == 'darwin' and
          [int(x) for x in os.uname()[2].split('.')] >= [11, 0, 0]):
        # special things for clang
        extra_compile_args = [
            '-Werror', '-Qunused-arguments', '-Wno-error=shorten-64-to-32']
    else:
        # assume a standard gcc
        extra_compile_args = ['-Werror']

    class FFI(FFI):
        def verify(self, *args, **kwds):
            return super(FFI, self).verify(
                *args, extra_compile_args=extra_compile_args, **kwds)

def setup_module():
    import cffi.verifier
    cffi.verifier.cleanup_tmpdir()
    #
    # check that no $ sign is produced in the C file; it used to be the
    # case that anonymous enums would produce '$enum_$1', which was
    # used as part of a function name.  GCC accepts such names, but it's
    # apparently non-standard.
    _r_comment = re.compile(r"/\*.*?\*/|//.*?$", re.DOTALL | re.MULTILINE)
    _r_string = re.compile(r'\".*?\"')
    def _write_source_and_check(self, file=None):
        base_write_source(self, file)
        if file is None:
            f = open(self.sourcefilename)
            data = f.read()
            f.close()
            data = _r_comment.sub(' ', data)
            data = _r_string.sub('"skipped"', data)
            assert '$' not in data
    base_write_source = cffi.verifier.Verifier._write_source
    cffi.verifier.Verifier._write_source = _write_source_and_check


def test_module_type():
    import cffi.verifier
    ffi = FFI()
    lib = ffi.verify()
    if hasattr(lib, '_cffi_python_module'):
        print('verify got a PYTHON module')
    if hasattr(lib, '_cffi_generic_module'):
        print('verify got a GENERIC module')
    expected_generic = (cffi.verifier._FORCE_GENERIC_ENGINE or
                        '__pypy__' in sys.builtin_module_names)
    assert hasattr(lib, '_cffi_python_module') == (not expected_generic)
    assert hasattr(lib, '_cffi_generic_module') == expected_generic

def test_missing_function(ffi=None):
    # uses the FFI hacked above with '-Werror'
    if ffi is None:
        ffi = FFI()
    ffi.cdef("void some_completely_unknown_function();")
    try:
        lib = ffi.verify()
    except (VerificationError, OSError):
        pass     # expected case: we get a VerificationError
    else:
        # but depending on compiler and loader details, maybe
        # 'lib' could actually be imported but will fail if we
        # actually try to call the unknown function...  Hard
        # to test anything more.
        pass

def test_missing_function_import_error():
    # uses the original FFI that just gives a warning during compilation
    import cffi
    test_missing_function(ffi=cffi.FFI())

def test_simple_case():
    ffi = FFI()
    ffi.cdef("double sin(double x);")
    lib = ffi.verify('#include <math.h>', libraries=lib_m)
    assert lib.sin(1.23) == math.sin(1.23)

def test_rounding_1():
    ffi = FFI()
    ffi.cdef("float sin(double x);")
    lib = ffi.verify('#include <math.h>', libraries=lib_m)
    res = lib.sin(1.23)
    assert res != math.sin(1.23)     # not exact, because of double->float
    assert abs(res - math.sin(1.23)) < 1E-5

def test_rounding_2():
    ffi = FFI()
    ffi.cdef("double sin(float x);")
    lib = ffi.verify('#include <math.h>', libraries=lib_m)
    res = lib.sin(1.23)
    assert res != math.sin(1.23)     # not exact, because of double->float
    assert abs(res - math.sin(1.23)) < 1E-5

def test_strlen_exact():
    ffi = FFI()
    ffi.cdef("size_t strlen(const char *s);")
    lib = ffi.verify("#include <string.h>")
    assert lib.strlen(b"hi there!") == 9

def test_strlen_approximate():
    ffi = FFI()
    ffi.cdef("int strlen(char *s);")
    lib = ffi.verify("#include <string.h>")
    assert lib.strlen(b"hi there!") == 9

def test_strlen_array_of_char():
    ffi = FFI()
    ffi.cdef("int strlen(char[]);")
    lib = ffi.verify("#include <string.h>")
    assert lib.strlen(b"hello") == 5

def test_longdouble():
    ffi = FFI()
    ffi.cdef("long double sinl(long double x);")
    lib = ffi.verify('#include <math.h>', libraries=lib_m)
    for input in [1.23,
                  ffi.cast("double", 1.23),
                  ffi.cast("long double", 1.23)]:
        x = lib.sinl(input)
        assert repr(x).startswith("<cdata 'long double'")
        assert (float(x) - math.sin(1.23)) < 1E-10

def test_longdouble_precision():
    # Test that we don't loose any precision of 'long double' when
    # passing through Python and CFFI.
    ffi = FFI()
    ffi.cdef("long double step1(long double x);")
    SAME_SIZE = ffi.sizeof("long double") == ffi.sizeof("double")
    lib = ffi.verify("""
        long double step1(long double x)
        {
            return 4*x-x*x;
        }
    """)
    def do(cast_to_double):
        x = 0.9789
        for i in range(10000):
            x = lib.step1(x)
            if cast_to_double:
                x = float(x)
        return float(x)

    more_precise = do(False)
    less_precise = do(True)
    if SAME_SIZE:
        assert more_precise == less_precise
    else:
        assert abs(more_precise - less_precise) > 0.1
        # Check the particular results on Intel
        import platform
        if (platform.machine().startswith('i386') or
            platform.machine().startswith('x86')):
            assert abs(more_precise - 0.656769) < 0.001
            assert abs(less_precise - 3.99091) < 0.001
        else:
            py.test.skip("don't know the very exact precision of 'long double'")


all_primitive_types = model.PrimitiveType.ALL_PRIMITIVE_TYPES
all_integer_types = sorted(tp for tp in all_primitive_types
                           if all_primitive_types[tp] == 'i')
all_float_types = sorted(tp for tp in all_primitive_types
                            if all_primitive_types[tp] == 'f')

def all_signed_integer_types(ffi):
    return [x for x in all_integer_types if int(ffi.cast(x, -1)) < 0]

def all_unsigned_integer_types(ffi):
    return [x for x in all_integer_types if int(ffi.cast(x, -1)) > 0]


def test_primitive_category():
    for typename in all_primitive_types:
        tp = model.PrimitiveType(typename)
        C = tp.is_char_type()
        F = tp.is_float_type()
        I = tp.is_integer_type()
        assert C == (typename in ('char', 'wchar_t'))
        assert F == (typename in ('float', 'double', 'long double'))
        assert I + F + C == 1      # one and only one of them is true

def test_all_integer_and_float_types():
    typenames = []
    for typename in all_primitive_types:
        if (all_primitive_types[typename] == 'c' or
            typename == '_Bool' or typename == 'long double'):
            pass
        else:
            typenames.append(typename)
    #
    ffi = FFI()
    ffi.cdef('\n'.join(["%s foo_%s(%s);" % (tp, tp.replace(' ', '_'), tp)
                       for tp in typenames]))
    lib = ffi.verify('\n'.join(["%s foo_%s(%s x) { return x+1; }" %
                                (tp, tp.replace(' ', '_'), tp)
                                for tp in typenames]))
    for typename in typenames:
        foo = getattr(lib, 'foo_%s' % typename.replace(' ', '_'))
        assert foo(42) == 43
        if sys.version < '3':
            assert foo(long(44)) == 45
        assert foo(ffi.cast(typename, 46)) == 47
        py.test.raises(TypeError, foo, ffi.NULL)
        #
        # check for overflow cases
        if all_primitive_types[typename] == 'f':
            continue
        for value in [-2**80, -2**40, -2**20, -2**10, -2**5, -1,
                      2**5, 2**10, 2**20, 2**40, 2**80]:
            overflows = int(ffi.cast(typename, value)) != value
            if overflows:
                py.test.raises(OverflowError, foo, value)
            else:
                assert foo(value) == value + 1

def test_var_signed_integer_types():
    ffi = FFI()
    lst = all_signed_integer_types(ffi)
    csource = "\n".join(["%s somevar_%s;" % (tp, tp.replace(' ', '_'))
                         for tp in lst])
    ffi.cdef(csource)
    lib = ffi.verify(csource)
    for tp in lst:
        varname = 'somevar_%s' % tp.replace(' ', '_')
        sz = ffi.sizeof(tp)
        max = (1 << (8*sz-1)) - 1
        min = -(1 << (8*sz-1))
        setattr(lib, varname, max)
        assert getattr(lib, varname) == max
        setattr(lib, varname, min)
        assert getattr(lib, varname) == min
        py.test.raises(OverflowError, setattr, lib, varname, max+1)
        py.test.raises(OverflowError, setattr, lib, varname, min-1)

def test_var_unsigned_integer_types():
    ffi = FFI()
    lst = all_unsigned_integer_types(ffi)
    csource = "\n".join(["%s somevar_%s;" % (tp, tp.replace(' ', '_'))
                         for tp in lst])
    ffi.cdef(csource)
    lib = ffi.verify(csource)
    for tp in lst:
        varname = 'somevar_%s' % tp.replace(' ', '_')
        sz = ffi.sizeof(tp)
        if tp != '_Bool':
            max = (1 << (8*sz)) - 1
        else:
            max = 1
        setattr(lib, varname, max)
        assert getattr(lib, varname) == max
        setattr(lib, varname, 0)
        assert getattr(lib, varname) == 0
        py.test.raises(OverflowError, setattr, lib, varname, max+1)
        py.test.raises(OverflowError, setattr, lib, varname, -1)

def test_fn_signed_integer_types():
    ffi = FFI()
    lst = all_signed_integer_types(ffi)
    cdefsrc = "\n".join(["%s somefn_%s(%s);" % (tp, tp.replace(' ', '_'), tp)
                         for tp in lst])
    ffi.cdef(cdefsrc)
    verifysrc = "\n".join(["%s somefn_%s(%s x) { return x; }" %
                           (tp, tp.replace(' ', '_'), tp) for tp in lst])
    lib = ffi.verify(verifysrc)
    for tp in lst:
        fnname = 'somefn_%s' % tp.replace(' ', '_')
        sz = ffi.sizeof(tp)
        max = (1 << (8*sz-1)) - 1
        min = -(1 << (8*sz-1))
        fn = getattr(lib, fnname)
        assert fn(max) == max
        assert fn(min) == min
        py.test.raises(OverflowError, fn, max + 1)
        py.test.raises(OverflowError, fn, min - 1)

def test_fn_unsigned_integer_types():
    ffi = FFI()
    lst = all_unsigned_integer_types(ffi)
    cdefsrc = "\n".join(["%s somefn_%s(%s);" % (tp, tp.replace(' ', '_'), tp)
                         for tp in lst])
    ffi.cdef(cdefsrc)
    verifysrc = "\n".join(["%s somefn_%s(%s x) { return x; }" %
                           (tp, tp.replace(' ', '_'), tp) for tp in lst])
    lib = ffi.verify(verifysrc)
    for tp in lst:
        fnname = 'somefn_%s' % tp.replace(' ', '_')
        sz = ffi.sizeof(tp)
        if tp != '_Bool':
            max = (1 << (8*sz)) - 1
        else:
            max = 1
        fn = getattr(lib, fnname)
        assert fn(max) == max
        assert fn(0) == 0
        py.test.raises(OverflowError, fn, max + 1)
        py.test.raises(OverflowError, fn, -1)

def test_char_type():
    ffi = FFI()
    ffi.cdef("char foo(char);")
    lib = ffi.verify("char foo(char x) { return x+1; }")
    assert lib.foo(b"A") == b"B"
    py.test.raises(TypeError, lib.foo, b"bar")
    py.test.raises(TypeError, lib.foo, "bar")

def test_wchar_type():
    ffi = FFI()
    if ffi.sizeof('wchar_t') == 2:
        uniexample1 = u+'\u1234'
        uniexample2 = u+'\u1235'
    else:
        uniexample1 = u+'\U00012345'
        uniexample2 = u+'\U00012346'
    #
    ffi.cdef("wchar_t foo(wchar_t);")
    lib = ffi.verify("wchar_t foo(wchar_t x) { return x+1; }")
    assert lib.foo(uniexample1) == uniexample2

def test_no_argument():
    ffi = FFI()
    ffi.cdef("int foo(void);")
    lib = ffi.verify("int foo(void) { return 42; }")
    assert lib.foo() == 42

def test_two_arguments():
    ffi = FFI()
    ffi.cdef("int foo(int, int);")
    lib = ffi.verify("int foo(int a, int b) { return a - b; }")
    assert lib.foo(40, -2) == 42

def test_macro():
    ffi = FFI()
    ffi.cdef("int foo(int, int);")
    lib = ffi.verify("#define foo(a, b) ((a) * (b))")
    assert lib.foo(-6, -7) == 42

def test_ptr():
    ffi = FFI()
    ffi.cdef("int *foo(int *);")
    lib = ffi.verify("int *foo(int *a) { return a; }")
    assert lib.foo(ffi.NULL) == ffi.NULL
    p = ffi.new("int *", 42)
    q = ffi.new("int *", 42)
    assert lib.foo(p) == p
    assert lib.foo(q) != p

def test_bogus_ptr():
    ffi = FFI()
    ffi.cdef("int *foo(int *);")
    lib = ffi.verify("int *foo(int *a) { return a; }")
    py.test.raises(TypeError, lib.foo, ffi.new("short *", 42))


def test_verify_typedefs():
    py.test.skip("ignored so far")
    types = ['signed char', 'unsigned char', 'int', 'long']
    for cdefed in types:
        for real in types:
            ffi = FFI()
            ffi.cdef("typedef %s foo_t;" % cdefed)
            if cdefed == real:
                ffi.verify("typedef %s foo_t;" % real)
            else:
                py.test.raises(VerificationError, ffi.verify,
                               "typedef %s foo_t;" % real)

def test_nondecl_struct():
    ffi = FFI()
    ffi.cdef("typedef struct foo_s foo_t; int bar(foo_t *);")
    lib = ffi.verify("typedef struct foo_s foo_t;\n"
                     "int bar(foo_t *f) { return 42; }\n")
    assert lib.bar(ffi.NULL) == 42

def test_ffi_full_struct():
    ffi = FFI()
    ffi.cdef("struct foo_s { char x; int y; long *z; };")
    ffi.verify("struct foo_s { char x; int y; long *z; };")
    #
    if sys.platform != 'win32':  # XXX fixme: only gives warnings
        py.test.raises(VerificationError, ffi.verify,
            "struct foo_s { char x; int y; int *z; };")
    #
    py.test.raises(VerificationError, ffi.verify,
        "struct foo_s { int y; long *z; };")
    #
    e = py.test.raises(VerificationError, ffi.verify,
        "struct foo_s { int y; char x; long *z; };")
    assert str(e.value) == (
        "struct foo_s: wrong offset for field 'x'"
        " (we have 0, but C compiler says 4)")
    #
    e = py.test.raises(VerificationError, ffi.verify,
        "struct foo_s { char x; int y; long *z; char extra; };")
    assert str(e.value) == (
        "struct foo_s: wrong total size"
        " (we have %d, but C compiler says %d)" % (
            ffi.sizeof("struct foo_s"),
            ffi.sizeof("struct foo_s") + ffi.sizeof("long*")))
    #
    # a corner case that we cannot really detect, but where it has no
    # bad consequences: the size is the same, but there is an extra field
    # that replaces what is just padding in our declaration above
    ffi.verify("struct foo_s { char x, extra; int y; long *z; };")
    #
    e = py.test.raises(VerificationError, ffi.verify,
        "struct foo_s { char x; short pad; short y; long *z; };")
    assert str(e.value) == (
        "struct foo_s: wrong size for field 'y'"
        " (we have 4, but C compiler says 2)")

def test_ffi_nonfull_struct():
    ffi = FFI()
    ffi.cdef("""
    struct foo_s {
       int x;
       ...;
    };
    """)
    py.test.raises(VerificationMissing, ffi.sizeof, 'struct foo_s')
    py.test.raises(VerificationMissing, ffi.offsetof, 'struct foo_s', 'x')
    py.test.raises(VerificationMissing, ffi.new, 'struct foo_s *')
    ffi.verify("""
    struct foo_s {
       int a, b, x, c, d, e;
    };
    """)
    assert ffi.sizeof('struct foo_s') == 6 * ffi.sizeof('int')
    assert ffi.offsetof('struct foo_s', 'x') == 2 * ffi.sizeof('int')

def test_ffi_nonfull_alignment():
    ffi = FFI()
    ffi.cdef("struct foo_s { char x; ...; };")
    ffi.verify("struct foo_s { int a, b; char x; };")
    assert ffi.sizeof('struct foo_s') == 3 * ffi.sizeof('int')
    assert ffi.alignof('struct foo_s') == ffi.sizeof('int')

def _check_field_match(typename, real, expect_mismatch):
    ffi = FFI()
    testing_by_size = (expect_mismatch == 'by_size')
    if testing_by_size:
        expect_mismatch = ffi.sizeof(typename) != ffi.sizeof(real)
    ffi.cdef("struct foo_s { %s x; ...; };" % typename)
    try:
        ffi.verify("struct foo_s { %s x; };" % real)
    except VerificationError:
        if not expect_mismatch:
            if testing_by_size and typename != real:
                print("ignoring mismatch between %s* and %s* even though "
                      "they have the same size" % (typename, real))
                return
            raise AssertionError("unexpected mismatch: %s should be accepted "
                                 "as equal to %s" % (typename, real))
    else:
        if expect_mismatch:
            raise AssertionError("mismatch not detected: "
                                 "%s != %s" % (typename, real))

def test_struct_bad_sized_integer():
    for typename in ['int8_t', 'int16_t', 'int32_t', 'int64_t']:
        for real in ['int8_t', 'int16_t', 'int32_t', 'int64_t']:
            _check_field_match(typename, real, "by_size")

def test_struct_bad_sized_float():
    for typename in all_float_types:
        for real in all_float_types:
            _check_field_match(typename, real, "by_size")

def test_struct_signedness_ignored():
    _check_field_match("int", "unsigned int", expect_mismatch=False)
    _check_field_match("unsigned short", "signed short", expect_mismatch=False)

def test_struct_float_vs_int():
    if sys.platform == 'win32':
        py.test.skip("XXX fixme: only gives warnings")
    ffi = FFI()
    for typename in all_signed_integer_types(ffi):
        for real in all_float_types:
            _check_field_match(typename, real, expect_mismatch=True)
    for typename in all_float_types:
        for real in all_signed_integer_types(ffi):
            _check_field_match(typename, real, expect_mismatch=True)

def test_struct_array_field():
    ffi = FFI()
    ffi.cdef("struct foo_s { int a[17]; ...; };")
    ffi.verify("struct foo_s { int x; int a[17]; int y; };")
    assert ffi.sizeof('struct foo_s') == 19 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *")
    assert ffi.sizeof(s.a) == 17 * ffi.sizeof('int')

def test_struct_array_no_length():
    ffi = FFI()
    ffi.cdef("struct foo_s { int a[]; int y; ...; };\n"
             "int bar(struct foo_s *);\n")
    lib = ffi.verify("struct foo_s { int x; int a[17]; int y; };\n"
                     "int bar(struct foo_s *f) { return f->a[14]; }\n")
    assert ffi.sizeof('struct foo_s') == 19 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *")
    assert ffi.typeof(s.a) is ffi.typeof('int *')   # because no length
    s.a[14] = 4242
    assert lib.bar(s) == 4242
    # with no declared length, out-of-bound accesses are not detected
    s.a[17] = -521
    assert s.y == s.a[17] == -521
    #
    s = ffi.new("struct foo_s *", {'a': list(range(17))})
    assert s.a[16] == 16
    # overflows at construction time not detected either
    s = ffi.new("struct foo_s *", {'a': list(range(18))})
    assert s.y == s.a[17] == 17

def test_struct_array_guess_length():
    ffi = FFI()
    ffi.cdef("struct foo_s { int a[...]; };")
    ffi.verify("struct foo_s { int x; int a[17]; int y; };")
    assert ffi.sizeof('struct foo_s') == 19 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *")
    assert ffi.sizeof(s.a) == 17 * ffi.sizeof('int')
    py.test.raises(IndexError, 's.a[17]')

def test_struct_array_c99_1():
    if sys.platform == 'win32':
        py.test.skip("requires C99")
    ffi = FFI()
    ffi.cdef("struct foo_s { int x; int a[]; };")
    ffi.verify("struct foo_s { int x; int a[]; };")
    assert ffi.sizeof('struct foo_s') == 1 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *", [424242, 4])
    assert ffi.sizeof(s[0]) == 1 * ffi.sizeof('int')   # the same in C
    assert s.a[3] == 0
    s = ffi.new("struct foo_s *", [424242, [-40, -30, -20, -10]])
    assert ffi.sizeof(s[0]) == 1 * ffi.sizeof('int')
    assert s.a[3] == -10
    s = ffi.new("struct foo_s *")
    assert ffi.sizeof(s[0]) == 1 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *", [424242])
    assert ffi.sizeof(s[0]) == 1 * ffi.sizeof('int')

def test_struct_array_c99_2():
    if sys.platform == 'win32':
        py.test.skip("requires C99")
    ffi = FFI()
    ffi.cdef("struct foo_s { int x; int a[]; ...; };")
    ffi.verify("struct foo_s { int x, y; int a[]; };")
    assert ffi.sizeof('struct foo_s') == 2 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *", [424242, 4])
    assert ffi.sizeof(s[0]) == 2 * ffi.sizeof('int')
    assert s.a[3] == 0
    s = ffi.new("struct foo_s *", [424242, [-40, -30, -20, -10]])
    assert ffi.sizeof(s[0]) == 2 * ffi.sizeof('int')
    assert s.a[3] == -10
    s = ffi.new("struct foo_s *")
    assert ffi.sizeof(s[0]) == 2 * ffi.sizeof('int')
    s = ffi.new("struct foo_s *", [424242])
    assert ffi.sizeof(s[0]) == 2 * ffi.sizeof('int')

def test_struct_ptr_to_array_field():
    ffi = FFI()
    ffi.cdef("struct foo_s { int (*a)[17]; ...; }; struct bar_s { ...; };")
    ffi.verify("struct foo_s { int x; int (*a)[17]; int y; };\n"
               "struct bar_s { int x; int *a; int y; };")
    assert ffi.sizeof('struct foo_s') == ffi.sizeof("struct bar_s")
    s = ffi.new("struct foo_s *")
    assert ffi.sizeof(s.a) == ffi.sizeof('int(*)[17]') == ffi.sizeof("int *")

def test_struct_with_bitfield_exact():
    ffi = FFI()
    ffi.cdef("struct foo_s { int a:2, b:3; };")
    ffi.verify("struct foo_s { int a:2, b:3; };")
    s = ffi.new("struct foo_s *")
    s.b = 3
    py.test.raises(OverflowError, "s.b = 4")
    assert s.b == 3

def test_struct_with_bitfield_enum():
    ffi = FFI()
    code = """
        typedef enum { AA, BB, CC } foo_e;
        typedef struct { foo_e f:2; } foo_s;
    """
    ffi.cdef(code)
    ffi.verify(code)
    s = ffi.new("foo_s *")
    s.f = 2
    assert s.f == 2

def test_unsupported_struct_with_bitfield_ellipsis():
    ffi = FFI()
    py.test.raises(NotImplementedError, ffi.cdef,
                   "struct foo_s { int a:2, b:3; ...; };")

def test_global_constants():
    ffi = FFI()
    # use 'static const int', as generally documented, although in this
    # case the 'static' is completely ignored.
    ffi.cdef("static const int AA, BB, CC, DD;")
    lib = ffi.verify("#define AA 42\n"
                     "#define BB (-43)\n"
                     "#define CC (22*2)\n"
                     "#define DD ((unsigned int)142)\n")
    assert lib.AA == 42
    assert lib.BB == -43
    assert lib.CC == 44
    assert lib.DD == 142

def test_global_const_int_size():
    # integer constants: ignore the declared type, always just use the value
    for value in [-2**63, -2**31, -2**15,
                  2**15-1, 2**15, 2**31-1, 2**31, 2**32-1, 2**32,
                  2**63-1, 2**63, 2**64-1]:
        ffi = FFI()
        if value == int(ffi.cast("long long", value)):
            if value < 0:
                vstr = '(-%dLL-1)' % (~value,)
            else:
                vstr = '%dLL' % value
        elif value == int(ffi.cast("unsigned long long", value)):
            vstr = '%dULL' % value
        else:
            raise AssertionError(value)
        ffi.cdef("static const unsigned short AA;")
        lib = ffi.verify("#define AA %s\n" % vstr)
        assert lib.AA == value
        assert type(lib.AA) is type(int(lib.AA))

def test_global_constants_non_int():
    ffi = FFI()
    ffi.cdef("static char *const PP;")
    lib = ffi.verify('static char *const PP = "testing!";\n')
    assert ffi.typeof(lib.PP) == ffi.typeof("char *")
    assert ffi.string(lib.PP) == b"testing!"

def test_nonfull_enum():
    ffi = FFI()
    ffi.cdef("enum ee { EE1, EE2, EE3, ... \n \t };")
    py.test.raises(VerificationMissing, ffi.cast, 'enum ee', 'EE2')
    ffi.verify("enum ee { EE1=10, EE2, EE3=-10, EE4 };")
    assert ffi.string(ffi.cast('enum ee', 11)) == "EE2"
    assert ffi.string(ffi.cast('enum ee', -10)) == "EE3"
    #
    # try again
    ffi.verify("enum ee { EE1=10, EE2, EE3=-10, EE4 };")
    assert ffi.string(ffi.cast('enum ee', 11)) == "EE2"

def test_full_enum():
    ffi = FFI()
    ffi.cdef("enum ee { EE1, EE2, EE3 };")
    ffi.verify("enum ee { EE1, EE2, EE3 };")
    py.test.raises(VerificationError, ffi.verify, "enum ee { EE1, EE2 };")
    e = py.test.raises(VerificationError, ffi.verify,
                       "enum ee { EE1, EE3, EE2 };")
    assert str(e.value) == 'enum ee: EE2 has the real value 2, not 1'
    # extra items cannot be seen and have no bad consequence anyway
    lib = ffi.verify("enum ee { EE1, EE2, EE3, EE4 };")
    assert lib.EE3 == 2

def test_enum_usage():
    ffi = FFI()
    ffi.cdef("enum ee { EE1,EE2 }; typedef struct { enum ee x; } *sp;")
    lib = ffi.verify("enum ee { EE1,EE2 }; typedef struct { enum ee x; } *sp;")
    assert lib.EE2 == 1
    s = ffi.new("sp", [lib.EE2])
    assert s.x == 1
    s.x = 17
    assert s.x == 17

def test_anonymous_enum():
    ffi = FFI()
    ffi.cdef("enum { EE1 }; enum { EE2, EE3 };")
    lib = ffi.verify("enum { EE1 }; enum { EE2, EE3 };")
    assert lib.EE1 == 0
    assert lib.EE2 == 0
    assert lib.EE3 == 1

def test_nonfull_anonymous_enum():
    ffi = FFI()
    ffi.cdef("enum { EE1, ... }; enum { EE3, ... };")
    lib = ffi.verify("enum { EE2, EE1 }; enum { EE3 };")
    assert lib.EE1 == 1
    assert lib.EE3 == 0

def test_nonfull_enum_syntax2():
    ffi = FFI()
    ffi.cdef("enum ee { EE1, EE2=\t..., EE3 };")
    py.test.raises(VerificationMissing, ffi.cast, 'enum ee', 'EE1')
    ffi.verify("enum ee { EE1=10, EE2, EE3=-10, EE4 };")
    assert ffi.string(ffi.cast('enum ee', 11)) == 'EE2'
    assert ffi.string(ffi.cast('enum ee', -10)) == 'EE3'
    #
    ffi = FFI()
    ffi.cdef("enum ee { EE1, EE2=\t... };")
    py.test.raises(VerificationMissing, ffi.cast, 'enum ee', 'EE1')
    ffi.verify("enum ee { EE1=10, EE2, EE3=-10, EE4 };")
    assert ffi.string(ffi.cast('enum ee', 11)) == 'EE2'
    #
    ffi = FFI()
    ffi.cdef("enum ee2 { EE4=..., EE5=..., ... };")
    ffi.verify("enum ee2 { EE4=-1234-5, EE5 }; ")
    assert ffi.string(ffi.cast('enum ee2', -1239)) == 'EE4'
    assert ffi.string(ffi.cast('enum ee2', -1238)) == 'EE5'

def test_get_set_errno():
    ffi = FFI()
    ffi.cdef("int foo(int);")
    lib = ffi.verify("""
        static int foo(int x)
        {
            errno += 1;
            return x * 7;
        }
    """)
    ffi.errno = 15
    assert lib.foo(6) == 42
    assert ffi.errno == 16

def test_define_int():
    ffi = FFI()
    ffi.cdef("#define FOO ...\n"
             "\t#\tdefine\tBAR\t...\t\n"
             "#define BAZ ...\n")
    lib = ffi.verify("#define FOO 42\n"
                     "#define BAR (-44)\n"
                     "#define BAZ 0xffffffffffffffffULL\n")
    assert lib.FOO == 42
    assert lib.BAR == -44
    assert lib.BAZ == 0xffffffffffffffff

def test_access_variable():
    ffi = FFI()
    ffi.cdef("int foo(void);\n"
             "int somenumber;")
    lib = ffi.verify("""
        static int somenumber = 2;
        static int foo(void) {
            return somenumber * 7;
        }
    """)
    assert lib.somenumber == 2
    assert lib.foo() == 14
    lib.somenumber = -6
    assert lib.foo() == -42
    assert lib.somenumber == -6
    lib.somenumber = 2   # reset for the next run, if any

def test_access_address_of_variable():
    # access the address of 'somenumber': need a trick
    ffi = FFI()
    ffi.cdef("int somenumber; static int *const somenumberptr;")
    lib = ffi.verify("""
        static int somenumber = 2;
        #define somenumberptr (&somenumber)
    """)
    assert lib.somenumber == 2
    lib.somenumberptr[0] = 42
    assert lib.somenumber == 42
    lib.somenumber = 2    # reset for the next run, if any

def test_access_array_variable(length=5):
    ffi = FFI()
    ffi.cdef("int foo(int);\n"
             "int somenumber[%s];" % (length,))
    lib = ffi.verify("""
        static int somenumber[] = {2, 2, 3, 4, 5};
        static int foo(int i) {
            return somenumber[i] * 7;
        }
    """)
    if length == '':
        # a global variable of an unknown array length is implicitly
        # transformed into a global pointer variable, because we can only
        # work with array instances whose length we know.  using a pointer
        # instead of an array gives the correct effects.
        assert repr(lib.somenumber).startswith("<cdata 'int *' 0x")
        py.test.raises(TypeError, len, lib.somenumber)
    else:
        assert repr(lib.somenumber).startswith("<cdata 'int[%s]' 0x" % length)
        assert len(lib.somenumber) == 5
    assert lib.somenumber[3] == 4
    assert lib.foo(3) == 28
    lib.somenumber[3] = -6
    assert lib.foo(3) == -42
    assert lib.somenumber[3] == -6
    assert lib.somenumber[4] == 5
    lib.somenumber[3] = 4    # reset for the next run, if any

def test_access_array_variable_length_hidden():
    test_access_array_variable(length='')

def test_access_struct_variable():
    ffi = FFI()
    ffi.cdef("struct foo { int x; ...; };\n"
             "int foo(int);\n"
             "struct foo stuff;")
    lib = ffi.verify("""
        struct foo { int x, y, z; };
        static struct foo stuff = {2, 5, 8};
        static int foo(int i) {
            switch (i) {
            case 0: return stuff.x * 7;
            case 1: return stuff.y * 7;
            case 2: return stuff.z * 7;
            }
            return -1;
        }
    """)
    assert lib.stuff.x == 2
    assert lib.foo(0) == 14
    assert lib.foo(1) == 35
    assert lib.foo(2) == 56
    lib.stuff.x = -6
    assert lib.foo(0) == -42
    assert lib.foo(1) == 35
    lib.stuff.x = 2      # reset for the next run, if any

def test_access_callback():
    ffi = FFI()
    ffi.cdef("int (*cb)(int);\n"
             "int foo(int);\n"
             "void reset_cb(void);")
    lib = ffi.verify("""
        static int g(int x) { return x * 7; }
        static int (*cb)(int);
        static int foo(int i) { return cb(i) - 1; }
        static void reset_cb(void) { cb = g; }
    """)
    lib.reset_cb()
    assert lib.foo(6) == 41
    my_callback = ffi.callback("int(*)(int)", lambda n: n * 222)
    lib.cb = my_callback
    assert lib.foo(4) == 887

def test_access_callback_function_typedef():
    ffi = FFI()
    ffi.cdef("typedef int mycallback_t(int);\n"
             "mycallback_t *cb;\n"
             "int foo(int);\n"
             "void reset_cb(void);")
    lib = ffi.verify("""
        static int g(int x) { return x * 7; }
        static int (*cb)(int);
        static int foo(int i) { return cb(i) - 1; }
        static void reset_cb(void) { cb = g; }
    """)
    lib.reset_cb()
    assert lib.foo(6) == 41
    my_callback = ffi.callback("int(*)(int)", lambda n: n * 222)
    lib.cb = my_callback
    assert lib.foo(4) == 887

def test_ctypes_backend_forces_generic_engine():
    from cffi.backend_ctypes import CTypesBackend
    ffi = FFI(backend=CTypesBackend())
    ffi.cdef("int func(int a);")
    lib = ffi.verify("int func(int a) { return a * 42; }")
    assert not hasattr(lib, '_cffi_python_module')
    assert hasattr(lib, '_cffi_generic_module')
    assert lib.func(100) == 4200

def test_call_with_struct_ptr():
    ffi = FFI()
    ffi.cdef("typedef struct { int x; ...; } foo_t; int foo(foo_t *);")
    lib = ffi.verify("""
        typedef struct { int y, x; } foo_t;
        static int foo(foo_t *f) { return f->x * 7; }
    """)
    f = ffi.new("foo_t *")
    f.x = 6
    assert lib.foo(f) == 42

def test_unknown_type():
    ffi = FFI()
    ffi.cdef("""
        typedef ... token_t;
        int foo(token_t *);
        #define TOKEN_SIZE ...
    """)
    lib = ffi.verify("""
        typedef float token_t;
        static int foo(token_t *tk) {
            if (!tk)
                return -42;
            *tk += 1.601;
            return (int)*tk;
        }
        #define TOKEN_SIZE sizeof(token_t)
    """)
    # we cannot let ffi.new("token_t *") work, because we don't know ahead of
    # time if it's ok to ask 'sizeof(token_t)' in the C code or not.
    # See test_unknown_type_2.  Workaround.
    tkmem = ffi.new("char[]", lib.TOKEN_SIZE)    # zero-initialized
    tk = ffi.cast("token_t *", tkmem)
    results = [lib.foo(tk) for i in range(6)]
    assert results == [1, 3, 4, 6, 8, 9]
    assert lib.foo(ffi.NULL) == -42

def test_unknown_type_2():
    ffi = FFI()
    ffi.cdef("typedef ... token_t;")
    lib = ffi.verify("typedef struct token_s token_t;")
    # assert did not crash, even though 'sizeof(token_t)' is not valid in C.

def test_unknown_type_3():
    ffi = FFI()
    ffi.cdef("""
        typedef ... *token_p;
        token_p foo(token_p);
    """)
    lib = ffi.verify("""
        typedef struct _token_s *token_p;
        token_p foo(token_p arg) {
            if (arg)
                return (token_p)0x12347;
            else
                return (token_p)0x12345;
        }
    """)
    p = lib.foo(ffi.NULL)
    assert int(ffi.cast("intptr_t", p)) == 0x12345
    q = lib.foo(p)
    assert int(ffi.cast("intptr_t", q)) == 0x12347

def test_varargs():
    ffi = FFI()
    ffi.cdef("int foo(int x, ...);")
    lib = ffi.verify("""
        int foo(int x, ...) {
            va_list vargs;
            va_start(vargs, x);
            x -= va_arg(vargs, int);
            x -= va_arg(vargs, int);
            va_end(vargs);
            return x;
        }
    """)
    assert lib.foo(50, ffi.cast("int", 5), ffi.cast("int", 3)) == 42

def test_varargs_exact():
    if sys.platform == 'win32':
        py.test.skip("XXX fixme: only gives warnings")
    ffi = FFI()
    ffi.cdef("int foo(int x, ...);")
    py.test.raises(VerificationError, ffi.verify, """
        int foo(long long x, ...) {
            return x;
        }
    """)

def test_varargs_struct():
    ffi = FFI()
    ffi.cdef("struct foo_s { char a; int b; }; int foo(int x, ...);")
    lib = ffi.verify("""
        struct foo_s {
            char a; int b;
        };
        int foo(int x, ...) {
            va_list vargs;
            struct foo_s s;
            va_start(vargs, x);
            s = va_arg(vargs, struct foo_s);
            va_end(vargs);
            return s.a - s.b;
        }
    """)
    s = ffi.new("struct foo_s *", [b'B', 1])
    assert lib.foo(50, s[0]) == ord('A')

def test_autofilled_struct_as_argument():
    ffi = FFI()
    ffi.cdef("struct foo_s { long a; double b; ...; };\n"
             "int foo(struct foo_s);")
    lib = ffi.verify("""
        struct foo_s {
            double b;
            long a;
        };
        int foo(struct foo_s s) {
            return s.a - (int)s.b;
        }
    """)
    s = ffi.new("struct foo_s *", [100, 1])
    assert lib.foo(s[0]) == 99
    assert lib.foo([100, 1]) == 99

def test_autofilled_struct_as_argument_dynamic():
    ffi = FFI()
    ffi.cdef("struct foo_s { long a; ...; };\n"
             "int (*foo)(struct foo_s);")
    e = py.test.raises(TypeError, ffi.verify, """
        struct foo_s {
            double b;
            long a;
        };
        int foo1(struct foo_s s) {
            return s.a - (int)s.b;
        }
        int (*foo)(struct foo_s s) = &foo1;
    """)
    msg ='cannot pass as an argument a struct that was completed with verify()'
    assert msg in str(e.value)

def test_func_returns_struct():
    ffi = FFI()
    ffi.cdef("""
        struct foo_s { int aa, bb; };
        struct foo_s foo(int a, int b);
    """)
    lib = ffi.verify("""
        struct foo_s { int aa, bb; };
        struct foo_s foo(int a, int b) {
            struct foo_s r;
            r.aa = a*a;
            r.bb = b*b;
            return r;
        }
    """)
    s = lib.foo(6, 7)
    assert repr(s) == "<cdata 'struct foo_s' owning 8 bytes>"
    assert s.aa == 36
    assert s.bb == 49

def test_func_as_funcptr():
    ffi = FFI()
    ffi.cdef("int *(*const fooptr)(void);")
    lib = ffi.verify("""
        int *foo(void) {
            return (int*)"foobar";
        }
        int *(*fooptr)(void) = foo;
    """)
    foochar = ffi.cast("char *(*)(void)", lib.fooptr)
    s = foochar()
    assert ffi.string(s) == b"foobar"

def test_funcptr_as_argument():
    ffi = FFI()
    ffi.cdef("""
        void qsort(void *base, size_t nel, size_t width,
            int (*compar)(const void *, const void *));
    """)
    ffi.verify("#include <stdlib.h>")

def test_func_as_argument():
    ffi = FFI()
    ffi.cdef("""
        void qsort(void *base, size_t nel, size_t width,
            int compar(const void *, const void *));
    """)
    ffi.verify("#include <stdlib.h>")

def test_array_as_argument():
    ffi = FFI()
    ffi.cdef("""
        int strlen(char string[]);
    """)
    ffi.verify("#include <string.h>")

def test_enum_as_argument():
    ffi = FFI()
    ffi.cdef("""
        enum foo_e { AA, BB, ... };
        int foo_func(enum foo_e);
    """)
    lib = ffi.verify("""
        enum foo_e { AA, CC, BB };
        int foo_func(enum foo_e e) { return e; }
    """)
    assert lib.foo_func(lib.BB) == 2
    py.test.raises(TypeError, lib.foo_func, "BB")

def test_enum_as_function_result():
    ffi = FFI()
    ffi.cdef("""
        enum foo_e { AA, BB, ... };
        enum foo_e foo_func(int x);
    """)
    lib = ffi.verify("""
        enum foo_e { AA, CC, BB };
        enum foo_e foo_func(int x) { return x; }
    """)
    assert lib.foo_func(lib.BB) == lib.BB == 2

def test_enum_values():
    ffi = FFI()
    ffi.cdef("enum enum1_e { AA, BB };")
    lib = ffi.verify("enum enum1_e { AA, BB };")
    assert lib.AA == 0
    assert lib.BB == 1
    assert ffi.string(ffi.cast("enum enum1_e", 1)) == 'BB'

def test_typedef_complete_enum():
    ffi = FFI()
    ffi.cdef("typedef enum { AA, BB } enum1_t;")
    lib = ffi.verify("typedef enum { AA, BB } enum1_t;")
    assert ffi.string(ffi.cast("enum1_t", 1)) == 'BB'
    assert lib.AA == 0
    assert lib.BB == 1

def test_typedef_broken_complete_enum():
    ffi = FFI()
    ffi.cdef("typedef enum { AA, BB } enum1_t;")
    py.test.raises(VerificationError, ffi.verify,
                   "typedef enum { AA, CC, BB } enum1_t;")

def test_typedef_incomplete_enum():
    ffi = FFI()
    ffi.cdef("typedef enum { AA, BB, ... } enum1_t;")
    lib = ffi.verify("typedef enum { AA, CC, BB } enum1_t;")
    assert ffi.string(ffi.cast("enum1_t", 1)) == '1'
    assert ffi.string(ffi.cast("enum1_t", 2)) == 'BB'
    assert lib.AA == 0
    assert lib.BB == 2

def test_typedef_enum_as_function_result():
    ffi = FFI()
    ffi.cdef("""
        typedef enum { AA, BB, ... } foo_t;
        foo_t foo_func(int x);
    """)
    lib = ffi.verify("""
        typedef enum { AA, CC, BB } foo_t;
        foo_t foo_func(int x) { return x; }
    """)
    assert lib.foo_func(lib.BB) == lib.BB == 2

def test_callback_calling_convention():
    py.test.skip("later")
    if sys.platform != 'win32':
        py.test.skip("Windows only")
    ffi = FFI()
    ffi.cdef("""
        int call1(int(*__cdecl cb)(int));
        int call2(int(*__stdcall cb)(int));
    """)
    lib = ffi.verify("""
        int call1(int(*__cdecl cb)(int)) {
            return cb(42) + 1;
        }
        int call2(int(*__stdcall cb)(int)) {
            return cb(-42) - 6;
        }
    """)
    xxx

def test_opaque_integer_as_function_result():
    import platform
    if platform.machine().startswith('sparc'):
        py.test.skip('Breaks horribly on sparc (SIGILL + corrupted stack)')
    # XXX bad abuse of "struct { ...; }".  It only works a bit by chance
    # anyway.  XXX think about something better :-(
    ffi = FFI()
    ffi.cdef("""
        typedef struct { ...; } myhandle_t;
        myhandle_t foo(void);
    """)
    lib = ffi.verify("""
        typedef short myhandle_t;
        myhandle_t foo(void) { return 42; }
    """)
    h = lib.foo()
    assert ffi.sizeof(h) == ffi.sizeof("short")

def test_cannot_name_struct_type():
    ffi = FFI()
    ffi.cdef("typedef struct { int x; } *sp; void foo(sp);")
    e = py.test.raises(VerificationError, ffi.verify,
                       "typedef struct { int x; } *sp; void foo(sp);")
    assert 'in argument of foo: unknown type name' in str(e.value)

def test_dont_check_unnamable_fields():
    ffi = FFI()
    ffi.cdef("struct foo_s { struct { int x; } someone; };")
    ffi.verify("struct foo_s { struct { int x; } someone; };")
    # assert did not crash

def test_nested_anonymous_struct_exact():
    if sys.platform == 'win32':
        py.test.skip("nested anonymous struct/union")
    ffi = FFI()
    ffi.cdef("""
        struct foo_s { struct { int a; char b; }; union { char c, d; }; };
    """)
    ffi.verify("""
        struct foo_s { struct { int a; char b; }; union { char c, d; }; };
    """)
    p = ffi.new("struct foo_s *")
    assert ffi.sizeof(p[0]) == 3 * ffi.sizeof("int")    # with alignment
    p.a = 1234567
    p.b = b'X'
    p.c = b'Y'
    assert p.a == 1234567
    assert p.b == b'X'
    assert p.c == b'Y'
    assert p.d == b'Y'

def test_nested_anonymous_struct_exact_error():
    if sys.platform == 'win32':
        py.test.skip("nested anonymous struct/union")
    ffi = FFI()
    ffi.cdef("""
        struct foo_s { struct { int a; char b; }; union { char c, d; }; };
    """)
    py.test.raises(VerificationError, ffi.verify, """
        struct foo_s { struct { int a; short b; }; union { char c, d; }; };
    """)
    py.test.raises(VerificationError, ffi.verify, """
        struct foo_s { struct { int a; char e, b; }; union { char c, d; }; };
    """)

def test_nested_anonymous_struct_inexact_1():
    ffi = FFI()
    ffi.cdef("""
        struct foo_s { struct { char b; ...; }; union { char c, d; }; };
    """)
    ffi.verify("""
        struct foo_s { int a, padding; char c, d, b; };
    """)
    assert ffi.sizeof("struct foo_s") == 3 * ffi.sizeof("int")

def test_nested_anonymous_struct_inexact_2():
    ffi = FFI()
    ffi.cdef("""
        struct foo_s { union { char c, d; }; struct { int a; char b; }; ...; };
    """)
    ffi.verify("""
        struct foo_s { int a, padding; char c, d, b; };
    """)
    assert ffi.sizeof("struct foo_s") == 3 * ffi.sizeof("int")

def test_ffi_union():
    ffi = FFI()
    ffi.cdef("union foo_u { char x; long *z; };")
    ffi.verify("union foo_u { char x; int y; long *z; };")

def test_ffi_union_partial():
    ffi = FFI()
    ffi.cdef("union foo_u { char x; ...; };")
    ffi.verify("union foo_u { char x; int y; };")
    assert ffi.sizeof("union foo_u") == 4

def test_ffi_union_with_partial_struct():
    ffi = FFI()
    ffi.cdef("struct foo_s { int x; ...; }; union foo_u { struct foo_s s; };")
    ffi.verify("struct foo_s { int a; int x; }; "
               "union foo_u { char b[32]; struct foo_s s; };")
    assert ffi.sizeof("struct foo_s") == 8
    assert ffi.sizeof("union foo_u") == 32

def test_ffi_union_partial_2():
    ffi = FFI()
    ffi.cdef("typedef union { char x; ...; } u1;")
    ffi.verify("typedef union { char x; int y; } u1;")
    assert ffi.sizeof("u1") == 4

def test_ffi_union_with_partial_struct_2():
    ffi = FFI()
    ffi.cdef("typedef struct { int x; ...; } s1;"
             "typedef union { s1 s; } u1;")
    ffi.verify("typedef struct { int a; int x; } s1; "
               "typedef union { char b[32]; s1 s; } u1;")
    assert ffi.sizeof("s1") == 8
    assert ffi.sizeof("u1") == 32
    assert ffi.offsetof("u1", "s") == 0

def test_ffi_struct_packed():
    if sys.platform == 'win32':
        py.test.skip("needs a GCC extension")
    ffi = FFI()
    ffi.cdef("struct foo_s { int b; ...; };")
    ffi.verify("""
        struct foo_s {
            char a;
            int b;
        } __attribute__((packed));
    """)

def test_tmpdir():
    import tempfile, os, shutil
    from testing.udir import udir
    tmpdir = tempfile.mkdtemp(dir=str(udir))
    ffi = FFI()
    ffi.cdef("int foo(int);")
    lib = ffi.verify("int foo(int a) { return a + 42; }", tmpdir=tmpdir)
    assert os.listdir(tmpdir)
    assert lib.foo(100) == 142

def test_bug1():
    ffi = FFI()
    ffi.cdef("""
        typedef struct tdlhandle_s { ...; } *tdl_handle_t;
        typedef struct my_error_code_ {
            tdl_handle_t *rh;
        } my_error_code_t;
    """)
    ffi.verify("""
        typedef struct tdlhandle_s { int foo; } *tdl_handle_t;
        typedef struct my_error_code_ {
            tdl_handle_t *rh;
        } my_error_code_t;
    """)

def test_bool():
    if sys.platform == 'win32':
        py.test.skip("_Bool not in MSVC")
    ffi = FFI()
    ffi.cdef("struct foo_s { _Bool x; };"
             "_Bool foo(_Bool);")
    lib = ffi.verify("""
        struct foo_s { _Bool x; };
        int foo(int arg) {
            return !arg;
        }
    """)
    p = ffi.new("struct foo_s *")
    p.x = 1
    assert p.x == 1
    py.test.raises(OverflowError, "p.x = -1")
    py.test.raises(TypeError, "p.x = 0.0")
    assert lib.foo(1) == 0
    assert lib.foo(0) == 1
    py.test.raises(OverflowError, lib.foo, 42)
    py.test.raises(TypeError, lib.foo, 0.0)
    assert int(ffi.cast("_Bool", long(1))) == 1
    assert int(ffi.cast("_Bool", long(0))) == 0
    assert int(ffi.cast("_Bool", long(-1))) == 1
    assert int(ffi.cast("_Bool", 10**200)) == 1
    assert int(ffi.cast("_Bool", 10**40000)) == 1
    #
    class Foo(object):
        def __int__(self):
            self.seen = 1
            return result
    f = Foo()
    f.seen = 0
    result = 42
    assert int(ffi.cast("_Bool", f)) == 1
    assert f.seen
    f.seen = 0
    result = 0
    assert int(ffi.cast("_Bool", f)) == 0
    assert f.seen
    #
    py.test.raises(TypeError, ffi.cast, "_Bool", [])

def test_bool_on_long_double():
    if sys.platform == 'win32':
        py.test.skip("_Bool not in MSVC")
    f = 1E-250
    if f == 0.0 or f*f != 0.0:
        py.test.skip("unexpected precision")
    ffi = FFI()
    ffi.cdef("long double square(long double f); _Bool opposite(_Bool);")
    lib = ffi.verify("long double square(long double f) { return f*f; }\n"
                     "_Bool opposite(_Bool x) { return !x; }")
    f0 = lib.square(0.0)
    f2 = lib.square(f)
    f3 = lib.square(f * 2.0)
    if repr(f2) == repr(f3):
        py.test.skip("long double doesn't have enough precision")
    assert float(f0) == float(f2) == float(f3) == 0.0  # too tiny for 'double'
    assert int(ffi.cast("_Bool", f2)) == 1
    assert int(ffi.cast("_Bool", f3)) == 1
    assert int(ffi.cast("_Bool", f0)) == 0
    py.test.raises(TypeError, lib.opposite, f2)

def test_cannot_pass_float():
    for basetype in ['char', 'short', 'int', 'long', 'long long']:
        for sign in ['signed', 'unsigned']:
            type = '%s %s' % (sign, basetype)
            ffi = FFI()
            ffi.cdef("struct foo_s { %s x; };\n"
                     "int foo(%s);" % (type, type))
            lib = ffi.verify("""
                struct foo_s { %s x; };
                int foo(%s arg) {
                    return !arg;
                }
            """ % (type, type))
            p = ffi.new("struct foo_s *")
            py.test.raises(TypeError, "p.x = 0.0")
            assert lib.foo(42) == 0
            assert lib.foo(0) == 1
            py.test.raises(TypeError, lib.foo, 0.0)

def test_cast_from_int_type_to_bool():
    ffi = FFI()
    for basetype in ['char', 'short', 'int', 'long', 'long long']:
        for sign in ['signed', 'unsigned']:
            type = '%s %s' % (sign, basetype)
            assert int(ffi.cast("_Bool", ffi.cast(type, 42))) == 1
            assert int(ffi.cast("bool", ffi.cast(type, 42))) == 1
            assert int(ffi.cast("_Bool", ffi.cast(type, 0))) == 0

def test_addressof():
    ffi = FFI()
    ffi.cdef("""
        struct point_s { int x, y; };
        struct foo_s { int z; struct point_s point; };
        struct point_s sum_coord(struct point_s *);
    """)
    lib = ffi.verify("""
        struct point_s { int x, y; };
        struct foo_s { int z; struct point_s point; };
        struct point_s sum_coord(struct point_s *point) {
            struct point_s r;
            r.x = point->x + point->y;
            r.y = point->x - point->y;
            return r;
        }
    """)
    p = ffi.new("struct foo_s *")
    p.point.x = 16
    p.point.y = 9
    py.test.raises(TypeError, lib.sum_coord, p.point)
    res = lib.sum_coord(ffi.addressof(p.point))
    assert res.x == 25
    assert res.y == 7
    res2 = lib.sum_coord(ffi.addressof(res))
    assert res2.x == 32
    assert res2.y == 18
    py.test.raises(TypeError, lib.sum_coord, res2)

def test_callback_in_thread():
    if sys.platform == 'win32':
        py.test.skip("pthread only")
    import os, subprocess, imp
    arg = os.path.join(os.path.dirname(__file__), 'callback_in_thread.py')
    g = subprocess.Popen([sys.executable, arg,
                          os.path.dirname(imp.find_module('cffi')[1])])
    result = g.wait()
    assert result == 0

def test_keepalive_lib():
    ffi = FFI()
    ffi.cdef("int foobar(void);")
    lib = ffi.verify("int foobar(void) { return 42; }")
    func = lib.foobar
    ffi_r = weakref.ref(ffi)
    lib_r = weakref.ref(lib)
    del ffi
    import gc; gc.collect()       # lib stays alive
    assert lib_r() is not None
    assert ffi_r() is not None
    assert func() == 42

def test_keepalive_ffi():
    ffi = FFI()
    ffi.cdef("int foobar(void);")
    lib = ffi.verify("int foobar(void) { return 42; }")
    func = lib.foobar
    ffi_r = weakref.ref(ffi)
    lib_r = weakref.ref(lib)
    del lib
    import gc; gc.collect()       # ffi stays alive
    assert ffi_r() is not None
    assert lib_r() is not None
    assert func() == 42

def test_FILE_stored_in_stdout():
    if not sys.platform.startswith('linux'):
        py.test.skip("likely, we cannot assign to stdout")
    ffi = FFI()
    ffi.cdef("int printf(const char *, ...); FILE *setstdout(FILE *);")
    lib = ffi.verify("""
        #include <stdio.h>
        FILE *setstdout(FILE *f) {
            FILE *result = stdout;
            stdout = f;
            return result;
        }
    """)
    import os
    fdr, fdw = os.pipe()
    fw1 = os.fdopen(fdw, 'wb', 256)
    old_stdout = lib.setstdout(fw1)
    try:
        #
        fw1.write(b"X")
        r = lib.printf(b"hello, %d!\n", ffi.cast("int", 42))
        fw1.close()
        assert r == len("hello, 42!\n")
        #
    finally:
        lib.setstdout(old_stdout)
    #
    result = os.read(fdr, 256)
    os.close(fdr)
    # the 'X' might remain in the user-level buffer of 'fw1' and
    # end up showing up after the 'hello, 42!\n'
    assert result == b"Xhello, 42!\n" or result == b"hello, 42!\nX"

def test_FILE_stored_explicitly():
    ffi = FFI()
    ffi.cdef("int myprintf(const char *, int); FILE *myfile;")
    lib = ffi.verify("""
        #include <stdio.h>
        FILE *myfile;
        int myprintf(const char *out, int value) {
            return fprintf(myfile, out, value);
        }
    """)
    import os
    fdr, fdw = os.pipe()
    fw1 = os.fdopen(fdw, 'wb', 256)
    lib.myfile = ffi.cast("FILE *", fw1)
    #
    fw1.write(b"X")
    r = lib.myprintf(b"hello, %d!\n", ffi.cast("int", 42))
    fw1.close()
    assert r == len("hello, 42!\n")
    #
    result = os.read(fdr, 256)
    os.close(fdr)
    # the 'X' might remain in the user-level buffer of 'fw1' and
    # end up showing up after the 'hello, 42!\n'
    assert result == b"Xhello, 42!\n" or result == b"hello, 42!\nX"

def test_global_array_with_missing_length():
    ffi = FFI()
    ffi.cdef("int fooarray[];")
    lib = ffi.verify("int fooarray[50];")
    assert repr(lib.fooarray).startswith("<cdata 'int *'")

def test_global_array_with_dotdotdot_length():
    ffi = FFI()
    ffi.cdef("int fooarray[...];")
    lib = ffi.verify("int fooarray[50];")
    assert repr(lib.fooarray).startswith("<cdata 'int[50]'")

def test_bad_global_array_with_dotdotdot_length():
    ffi = FFI()
    ffi.cdef("int fooarray[...];")
    py.test.raises(VerificationError, ffi.verify, "char fooarray[23];")

def test_struct_containing_struct():
    ffi = FFI()
    ffi.cdef("struct foo_s { ...; }; struct bar_s { struct foo_s f; ...; };")
    ffi.verify("struct foo_s { int x; }; struct bar_s { struct foo_s f; };")
    #
    ffi = FFI()
    ffi.cdef("struct foo_s { struct bar_s f; ...; }; struct bar_s { ...; };")
    ffi.verify("struct bar_s { int x; }; struct foo_s { struct bar_s f; };")

def test_struct_returned_by_func():
    ffi = FFI()
    ffi.cdef("typedef ... foo_t; foo_t myfunc(void);")
    e = py.test.raises(TypeError, ffi.verify,
                       "typedef struct { int x; } foo_t; "
                       "foo_t myfunc(void) { foo_t x = { 42 }; return x; }")
    assert str(e.value) in [
        "function myfunc: 'foo_t' is used as result type, but is opaque",
        "function myfunc: result type 'foo_t' is opaque"]

def test_include():
    ffi1 = FFI()
    ffi1.cdef("typedef struct { int x; ...; } foo_t;")
    ffi1.verify("typedef struct { int y, x; } foo_t;")
    ffi2 = FFI()
    ffi2.include(ffi1)
    ffi2.cdef("int myfunc(foo_t *);")
    lib = ffi2.verify("typedef struct { int y, x; } foo_t;"
                      "int myfunc(foo_t *p) { return 42 * p->x; }")
    res = lib.myfunc(ffi2.new("foo_t *", {'x': 10}))
    assert res == 420
    res = lib.myfunc(ffi1.new("foo_t *", {'x': -10}))
    assert res == -420

def test_include_enum():
    ffi1 = FFI()
    ffi1.cdef("enum foo_e { AA, ... };")
    lib1 = ffi1.verify("enum foo_e { CC, BB, AA };")
    ffi2 = FFI()
    ffi2.include(ffi1)
    ffi2.cdef("int myfunc(enum foo_e);")
    lib2 = ffi2.verify("enum foo_e { CC, BB, AA };"
                       "int myfunc(enum foo_e x) { return (int)x; }")
    res = lib2.myfunc(lib2.AA)
    assert res == 2

def test_enum_size():
    cases = [('123',           4, 4294967295),
             ('4294967295U',   4, 4294967295),
             ('-123',          4, -1),
             ('-2147483647-1', 4, -1),
             ]
    if FFI().sizeof("long") == 8:
        cases += [('4294967296L',        8, 2**64-1),
                  ('%dUL' % (2**64-1),   8, 2**64-1),
                  ('-2147483649L',       8, -1),
                  ('%dL-1L' % (1-2**63), 8, -1)]
    for hidden_value, expected_size, expected_minus1 in cases:
        if sys.platform == 'win32' and 'U' in hidden_value:
            continue   # skipped on Windows
        ffi = FFI()
        ffi.cdef("enum foo_e { AA, BB, ... };")
        lib = ffi.verify("enum foo_e { AA, BB=%s };" % hidden_value)
        assert lib.AA == 0
        assert lib.BB == eval(hidden_value.replace('U', '').replace('L', ''))
        assert ffi.sizeof("enum foo_e") == expected_size
        assert int(ffi.cast("enum foo_e", -1)) == expected_minus1
    # test with the large value hidden:
    # disabled so far, doesn't work
##    for hidden_value, expected_size, expected_minus1 in cases:
##        ffi = FFI()
##        ffi.cdef("enum foo_e { AA, BB, ... };")
##        lib = ffi.verify("enum foo_e { AA, BB=%s };" % hidden_value)
##        assert lib.AA == 0
##        assert ffi.sizeof("enum foo_e") == expected_size
##        assert int(ffi.cast("enum foo_e", -1)) == expected_minus1

def test_enum_bug118():
    maxulong = 256 ** FFI().sizeof("unsigned long") - 1
    for c1, c2, c2c in [(0xffffffff, -1, ''),
                        (maxulong, -1, ''),
                        (-1, 0xffffffff, 'U'),
                        (-1, maxulong, 'UL')]:
        if c2c and sys.platform == 'win32':
            continue     # enums may always be signed with MSVC
        ffi = FFI()
        ffi.cdef("enum foo_e { AA=%s };" % c1)
        e = py.test.raises(VerificationError, ffi.verify,
                           "enum foo_e { AA=%s%s };" % (c2, c2c))
        assert str(e.value) == ('enum foo_e: AA has the real value %d, not %d'
                                % (c2, c1))

def test_string_to_voidp_arg():
    ffi = FFI()
    ffi.cdef("int myfunc(void *);")
    lib = ffi.verify("int myfunc(void *p) { return ((signed char *)p)[0]; }")
    res = lib.myfunc(b"hi!")
    assert res == ord(b"h")
    p = ffi.new("char[]", b"gah")
    res = lib.myfunc(p)
    assert res == ord(b"g")
    res = lib.myfunc(ffi.cast("void *", p))
    assert res == ord(b"g")
    res = lib.myfunc(ffi.cast("int *", p))
    assert res == ord(b"g")

def test_callback_indirection():
    ffi = FFI()
    ffi.cdef("""
        int (*python_callback)(int how_many, int *values);
        int (*const c_callback)(int,...);   /* pass this ptr to C routines */
        int some_c_function(int(*cb)(int,...));
    """)
    lib = ffi.verify("""
        #include <stdarg.h>
        #ifdef _WIN32
        #include <malloc.h>
        #define alloca _alloca
        #else
        # ifdef __FreeBSD__
        #  include <stdlib.h>
        # else
        #  include <alloca.h>
        # endif
        #endif
        static int (*python_callback)(int how_many, int *values);
        static int c_callback(int how_many, ...) {
            va_list ap;
            /* collect the "..." arguments into the values[] array */
            int i, *values = alloca(how_many * sizeof(int));
            va_start(ap, how_many);
            for (i=0; i<how_many; i++)
                values[i] = va_arg(ap, int);
            va_end(ap);
            return python_callback(how_many, values);
        }
        int some_c_function(int(*cb)(int,...)) {
            int result = cb(2, 10, 20);
            result += cb(3, 30, 40, 50);
            return result;
        }
    """)
    seen = []
    @ffi.callback("int(int, int*)")
    def python_callback(how_many, values):
        seen.append([values[i] for i in range(how_many)])
        return 42
    lib.python_callback = python_callback

    res = lib.some_c_function(lib.c_callback)
    assert res == 84
    assert seen == [[10, 20], [30, 40, 50]]

def test_floatstar_argument():
    ffi = FFI()
    ffi.cdef("float sum3floats(float *);")
    lib = ffi.verify("""
        float sum3floats(float *f) {
            return f[0] + f[1] + f[2];
        }
    """)
    assert lib.sum3floats((1.5, 2.5, 3.5)) == 7.5
    p = ffi.new("float[]", (1.5, 2.5, 3.5))
    assert lib.sum3floats(p) == 7.5

def test_charstar_argument():
    ffi = FFI()
    ffi.cdef("char sum3chars(char *);")
    lib = ffi.verify("""
        char sum3chars(char *f) {
            return f[0] + f[1] + f[2];
        }
    """)
    assert lib.sum3chars((b'\x10', b'\x20', b'\x30')) == b'\x60'
    p = ffi.new("char[]", b'\x10\x20\x30')
    assert lib.sum3chars(p) == b'\x60'

def test_passing_string_or_NULL():
    ffi = FFI()
    ffi.cdef("int seeme1(char *); int seeme2(int *);")
    lib = ffi.verify("""
        int seeme1(char *x) {
            return (x == NULL);
        }
        int seeme2(int *x) {
            return (x == NULL);
        }
    """)
    assert lib.seeme1(b"foo") == 0
    assert lib.seeme1(ffi.NULL) == 1
    assert lib.seeme2([42, 43]) == 0
    assert lib.seeme2(ffi.NULL) == 1
    py.test.raises(TypeError, lib.seeme1, None)
    py.test.raises(TypeError, lib.seeme2, None)
    py.test.raises(TypeError, lib.seeme1, 0.0)
    py.test.raises(TypeError, lib.seeme2, 0.0)
    py.test.raises(TypeError, lib.seeme1, 0)
    py.test.raises(TypeError, lib.seeme2, 0)
    zeroL  = 99999999999999999999
    zeroL -= 99999999999999999999
    py.test.raises(TypeError, lib.seeme2, zeroL)

def test_typeof_function():
    ffi = FFI()
    ffi.cdef("int foo(int, char);")
    lib = ffi.verify("int foo(int x, char y) { return 42; }")
    ctype = ffi.typeof(lib.foo)
    assert len(ctype.args) == 2
    assert ctype.result == ffi.typeof("int")

def test_call_with_voidstar_arg():
    ffi = FFI()
    ffi.cdef("int f(void *);")
    lib = ffi.verify("int f(void *x) { return ((char*)x)[0]; }")
    assert lib.f(b"foobar") == ord(b"f")

def test_dir():
    ffi = FFI()
    ffi.cdef("""void somefunc(void);
                extern int somevar, somearray[2];
                static char *const sv2;
                enum my_e { AA, BB, ... };
                #define FOO ...""")
    lib = ffi.verify("""void somefunc(void) { }
                        int somevar, somearray[2];
                        #define sv2 "text"
                        enum my_e { AA, BB };
                        #define FOO 42""")
    assert dir(lib) == ['AA', 'BB', 'FOO', 'somearray',
                        'somefunc', 'somevar', 'sv2']

def test_typeof_func_with_struct_argument():
    ffi = FFI()
    ffi.cdef("""struct s { int a; }; int foo(struct s);""")
    lib = ffi.verify("""struct s { int a; };
                        int foo(struct s x) { return x.a; }""")
    s = ffi.new("struct s *", [-1234])
    m = lib.foo(s[0])
    assert m == -1234
    assert repr(ffi.typeof(lib.foo)) == "<ctype 'int(*)(struct s)'>"

def test_bug_const_char_ptr_array_1():
    ffi = FFI()
    ffi.cdef("""const char *a[...];""")
    lib = ffi.verify("""const char *a[5];""")
    assert repr(ffi.typeof(lib.a)) == "<ctype 'char *[5]'>"

def test_bug_const_char_ptr_array_2():
    from cffi import FFI     # ignore warnings
    ffi = FFI()
    ffi.cdef("""const int a[];""")
    lib = ffi.verify("""const int a[5];""")
    assert repr(ffi.typeof(lib.a)) == "<ctype 'int *'>"

def _test_various_calls(force_libffi):
    cdef_source = """
    int xvalue;
    long long ivalue, rvalue;
    float fvalue;
    double dvalue;
    long double Dvalue;
    signed char tf_bb(signed char x, signed char c);
    unsigned char tf_bB(signed char x, unsigned char c);
    short tf_bh(signed char x, short c);
    unsigned short tf_bH(signed char x, unsigned short c);
    int tf_bi(signed char x, int c);
    unsigned int tf_bI(signed char x, unsigned int c);
    long tf_bl(signed char x, long c);
    unsigned long tf_bL(signed char x, unsigned long c);
    long long tf_bq(signed char x, long long c);
    float tf_bf(signed char x, float c);
    double tf_bd(signed char x, double c);
    long double tf_bD(signed char x, long double c);
    """
    if force_libffi:
        cdef_source = (cdef_source
            .replace('tf_', '(*const tf_')
            .replace('(signed char x', ')(signed char x'))
    ffi = FFI()
    ffi.cdef(cdef_source)
    lib = ffi.verify("""
    int xvalue;
    long long ivalue, rvalue;
    float fvalue;
    double dvalue;
    long double Dvalue;

    #define S(letter)  xvalue = x; letter##value = c; return rvalue;

    signed char tf_bb(signed char x, signed char c) { S(i) }
    unsigned char tf_bB(signed char x, unsigned char c) { S(i) }
    short tf_bh(signed char x, short c) { S(i) }
    unsigned short tf_bH(signed char x, unsigned short c) { S(i) }
    int tf_bi(signed char x, int c) { S(i) }
    unsigned int tf_bI(signed char x, unsigned int c) { S(i) }
    long tf_bl(signed char x, long c) { S(i) }
    unsigned long tf_bL(signed char x, unsigned long c) { S(i) }
    long long tf_bq(signed char x, long long c) { S(i) }
    float tf_bf(signed char x, float c) { S(f) }
    double tf_bd(signed char x, double c) { S(d) }
    long double tf_bD(signed char x, long double c) { S(D) }
    """)
    lib.rvalue = 0x7182838485868788
    for kind, cname in [('b', 'signed char'),
                        ('B', 'unsigned char'),
                        ('h', 'short'),
                        ('H', 'unsigned short'),
                        ('i', 'int'),
                        ('I', 'unsigned int'),
                        ('l', 'long'),
                        ('L', 'unsigned long'),
                        ('q', 'long long'),
                        ('f', 'float'),
                        ('d', 'double'),
                        ('D', 'long double')]:
        sign = +1 if 'unsigned' in cname else -1
        lib.xvalue = 0
        lib.ivalue = 0
        lib.fvalue = 0
        lib.dvalue = 0
        lib.Dvalue = 0
        fun = getattr(lib, 'tf_b' + kind)
        res = fun(-42, sign * 99)
        if kind == 'D':
            res = float(res)
        assert res == int(ffi.cast(cname, 0x7182838485868788))
        assert lib.xvalue == -42
        if kind in 'fdD':
            assert float(getattr(lib, kind + 'value')) == -99.0
        else:
            assert lib.ivalue == sign * 99

def test_various_calls_direct():
    _test_various_calls(force_libffi=False)

def test_various_calls_libffi():
    _test_various_calls(force_libffi=True)

def test_ptr_to_opaque():
    ffi = FFI()
    ffi.cdef("typedef ... foo_t; int f1(foo_t*); foo_t *f2(int);")
    lib = ffi.verify("""
        #include <stdlib.h>
        typedef struct { int x; } foo_t;
        int f1(foo_t* p) {
            int x = p->x;
            free(p);
            return x;
        }
        foo_t *f2(int x) {
            foo_t *p = malloc(sizeof(foo_t));
            p->x = x;
            return p;
        }
    """)
    p = lib.f2(42)
    x = lib.f1(p)
    assert x == 42
