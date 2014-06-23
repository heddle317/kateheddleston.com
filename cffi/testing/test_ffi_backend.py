import py, sys, platform
import pytest
from testing import backend_tests, test_function, test_ownlib
from cffi import FFI
import _cffi_backend


class TestFFI(backend_tests.BackendTests,
              test_function.TestFunction,
              test_ownlib.TestOwnLib):
    TypeRepr = "<ctype '%s'>"

    @staticmethod
    def Backend():
        return _cffi_backend

    def test_not_supported_bitfield_in_result(self):
        ffi = FFI(backend=self.Backend())
        ffi.cdef("struct foo_s { int a,b,c,d,e; int x:1; };")
        e = py.test.raises(NotImplementedError, ffi.callback,
                           "struct foo_s foo(void)", lambda: 42)
        assert str(e.value) == ("<struct foo_s(*)(void)>: "
            "cannot pass as argument or return value a struct with bit fields")

    def test_inspecttype(self):
        ffi = FFI(backend=self.Backend())
        assert ffi.typeof("long").kind == "primitive"
        assert ffi.typeof("long(*)(long, long**, ...)").cname == (
            "long(*)(long, long * *, ...)")
        assert ffi.typeof("long(*)(long, long**, ...)").ellipsis is True

    def test_new_handle(self):
        ffi = FFI(backend=self.Backend())
        o = [2, 3, 4]
        p = ffi.new_handle(o)
        assert ffi.typeof(p) == ffi.typeof("void *")
        assert ffi.from_handle(p) is o
        assert ffi.from_handle(ffi.cast("char *", p)) is o
        py.test.raises(RuntimeError, ffi.from_handle, ffi.NULL)


class TestBitfield:
    def check(self, source, expected_ofs_y, expected_align, expected_size):
        # NOTE: 'expected_*' is the numbers expected from GCC.
        # The numbers expected from MSVC are not explicitly written
        # in this file, and will just be taken from the compiler.
        ffi = FFI()
        ffi.cdef("struct s1 { %s };" % source)
        ctype = ffi.typeof("struct s1")
        # verify the information with gcc
        ffi1 = FFI()
        ffi1.cdef("""
            static const int Gofs_y, Galign, Gsize;
            struct s1 *try_with_value(int fieldnum, long long value);
        """)
        fnames = [name for name, cfield in ctype.fields
                       if name and cfield.bitsize > 0]
        setters = ['case %d: s.%s = value; break;' % iname
                   for iname in enumerate(fnames)]
        lib = ffi1.verify("""
            struct s1 { %s };
            struct sa { char a; struct s1 b; };
            #define Gofs_y  offsetof(struct s1, y)
            #define Galign  offsetof(struct sa, b)
            #define Gsize   sizeof(struct s1)
            struct s1 *try_with_value(int fieldnum, long long value)
            {
                static struct s1 s;
                memset(&s, 0, sizeof(s));
                switch (fieldnum) { %s }
                return &s;
            }
        """ % (source, ' '.join(setters)))
        if sys.platform == 'win32':
            expected_ofs_y = lib.Gofs_y
            expected_align = lib.Galign
            expected_size  = lib.Gsize
        else:
            assert (lib.Gofs_y, lib.Galign, lib.Gsize) == (
                expected_ofs_y, expected_align, expected_size)
        # the real test follows
        assert ffi.offsetof("struct s1", "y") == expected_ofs_y
        assert ffi.alignof("struct s1") == expected_align
        assert ffi.sizeof("struct s1") == expected_size
        # compare the actual storage of the two
        for name, cfield in ctype.fields:
            if cfield.bitsize < 0 or not name:
                continue
            if int(ffi.cast(cfield.type, -1)) == -1:   # signed
                min_value = -(1 << (cfield.bitsize-1))
                max_value = (1 << (cfield.bitsize-1)) - 1
            else:
                min_value = 0
                max_value = (1 << cfield.bitsize) - 1
            for t in [1, 2, 4, 8, 16, 128, 2813, 89728, 981729,
                     -1,-2,-4,-8,-16,-128,-2813,-89728,-981729]:
                if min_value <= t <= max_value:
                    self._fieldcheck(ffi, lib, fnames, name, t)

    def _fieldcheck(self, ffi, lib, fnames, name, value):
        s = ffi.new("struct s1 *")
        setattr(s, name, value)
        assert getattr(s, name) == value
        raw1 = ffi.buffer(s)[:]
        t = lib.try_with_value(fnames.index(name), value)
        raw2 = ffi.buffer(t, len(raw1))[:]
        assert raw1 == raw2

    def test_bitfield_basic(self):
        self.check("int a; int b:9; int c:20; int y;", 8, 4, 12)
        self.check("int a; short b:9; short c:7; int y;", 8, 4, 12)
        self.check("int a; short b:9; short c:9; int y;", 8, 4, 12)

    def test_bitfield_reuse_if_enough_space(self):
        self.check("int a:2; char y;", 1, 4, 4)
        self.check("int a:1; char b  ; int c:1; char y;", 3, 4, 4)
        self.check("int a:1; char b:8; int c:1; char y;", 3, 4, 4)
        self.check("char a; int b:9; char y;", 3, 4, 4)
        self.check("char a; short b:9; char y;", 4, 2, 6)
        self.check("int a:2; char b:6; char y;", 1, 4, 4)
        self.check("int a:2; char b:7; char y;", 2, 4, 4)
        self.check("int a:2; short b:15; char c:2; char y;", 5, 4, 8)
        self.check("int a:2; char b:1; char c:1; char y;", 1, 4, 4)

    @pytest.mark.skipif("platform.machine().startswith('arm')")
    def test_bitfield_anonymous_no_align(self):
        L = FFI().alignof("long long")
        self.check("char y; int :1;", 0, 1, 2)
        self.check("char x; int z:1; char y;", 2, 4, 4)
        self.check("char x; int  :1; char y;", 2, 1, 3)
        self.check("char x; long long z:48; char y;", 7, L, 8)
        self.check("char x; long long  :48; char y;", 7, 1, 8)
        self.check("char x; long long z:56; char y;", 8, L, 8 + L)
        self.check("char x; long long  :56; char y;", 8, 1, 9)
        self.check("char x; long long z:57; char y;", L + 8, L, L + 8 + L)
        self.check("char x; long long  :57; char y;", L + 8, 1, L + 9)

    @pytest.mark.skipif("not platform.machine().startswith('arm')")
    def test_bitfield_anonymous_align_arm(self):
        L = FFI().alignof("long long")
        self.check("char y; int :1;", 0, 4, 4)
        self.check("char x; int z:1; char y;", 2, 4, 4)
        self.check("char x; int  :1; char y;", 2, 4, 4)
        self.check("char x; long long z:48; char y;", 7, L, 8)
        self.check("char x; long long  :48; char y;", 7, 8, 8)
        self.check("char x; long long z:56; char y;", 8, L, 8 + L)
        self.check("char x; long long  :56; char y;", 8, L, 8 + L)
        self.check("char x; long long z:57; char y;", L + 8, L, L + 8 + L)
        self.check("char x; long long  :57; char y;", L + 8, L, L + 8 + L)

    @pytest.mark.skipif("platform.machine().startswith('arm')")
    def test_bitfield_zero(self):
        L = FFI().alignof("long long")
        self.check("char y; int :0;", 0, 1, 4)
        self.check("char x; int :0; char y;", 4, 1, 5)
        self.check("char x; int :0; int :0; char y;", 4, 1, 5)
        self.check("char x; long long :0; char y;", L, 1, L + 1)
        self.check("short x, y; int :0; int :0;", 2, 2, 4)
        self.check("char x; int :0; short b:1; char y;", 5, 2, 6)
        self.check("int a:1; int :0; int b:1; char y;", 5, 4, 8)

    @pytest.mark.skipif("not platform.machine().startswith('arm')")
    def test_bitfield_zero_arm(self):
        L = FFI().alignof("long long")
        self.check("char y; int :0;", 0, 4, 4)
        self.check("char x; int :0; char y;", 4, 4, 8)
        self.check("char x; int :0; int :0; char y;", 4, 4, 8)
        self.check("char x; long long :0; char y;", L, 8, L + 8)
        self.check("short x, y; int :0; int :0;", 2, 4, 4)
        self.check("char x; int :0; short b:1; char y;", 5, 4, 8)
        self.check("int a:1; int :0; int b:1; char y;", 5, 4, 8)

    def test_error_cases(self):
        ffi = FFI()
        py.test.raises(TypeError,
            'ffi.cdef("struct s1 { float x:1; };"); ffi.new("struct s1 *")')
        py.test.raises(TypeError,
            'ffi.cdef("struct s2 { char x:0; };"); ffi.new("struct s2 *")')
        py.test.raises(TypeError,
            'ffi.cdef("struct s3 { char x:9; };"); ffi.new("struct s3 *")')

    def test_struct_with_typedef(self):
        ffi = FFI()
        ffi.cdef("typedef struct { float x; } foo_t;")
        p = ffi.new("foo_t *", [5.2])
        assert repr(p).startswith("<cdata 'foo_t *' ")

    def test_struct_array_no_length(self):
        ffi = FFI()
        ffi.cdef("struct foo_s { int x; int a[]; };")
        p = ffi.new("struct foo_s *", [100, [200, 300, 400]])
        assert p.x == 100
        assert ffi.typeof(p.a) is ffi.typeof("int *")   # no length available
        assert p.a[0] == 200
        assert p.a[1] == 300
        assert p.a[2] == 400

    @pytest.mark.skipif("sys.platform != 'win32'")
    def test_getwinerror(self):
        ffi = FFI()
        code, message = ffi.getwinerror(1155)
        assert code == 1155
        assert message == ("No application is associated with the "
                           "specified file for this operation")
        ffi.cdef("void SetLastError(int);")
        lib = ffi.dlopen("Kernel32.dll")
        lib.SetLastError(2)
        code, message = ffi.getwinerror()
        assert code == 2
        assert message == "The system cannot find the file specified"
        code, message = ffi.getwinerror(-1)
        assert code == 2
        assert message == "The system cannot find the file specified"
