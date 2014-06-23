import py, os, sys, shutil
import imp
import subprocess
from testing.udir import udir

def create_venv(name):
    tmpdir = udir.join(name)
    try:
        subprocess.check_call(['virtualenv', '--distribute',
                               '-p', os.path.abspath(sys.executable),
                               str(tmpdir)])
    except OSError as e:
        py.test.skip("Cannot execute virtualenv: %s" % (e,))

    site_packages = None
    for dirpath, dirnames, filenames in os.walk(str(tmpdir)):
        if os.path.basename(dirpath) == 'site-packages':
            site_packages = dirpath
            break
    if site_packages:
        try:
            from cffi import _pycparser
            modules = ('cffi', '_cffi_backend')
        except ImportError:
            modules = ('cffi', '_cffi_backend', 'pycparser')
            try:
                import ply
            except ImportError:
                pass
            else:
                modules += ('ply',)   # needed for older versions of pycparser
        for module in modules:
            target = imp.find_module(module)[1]
            os.symlink(target, os.path.join(site_packages,
                                            os.path.basename(target)))
    return tmpdir

SNIPPET_DIR = py.path.local(__file__).join('..', 'snippets')

def really_run_setup_and_program(dirname, venv_dir, python_snippet):
    def remove(dir):
        dir = str(SNIPPET_DIR.join(dirname, dir))
        shutil.rmtree(dir, ignore_errors=True)
    remove('build')
    remove('__pycache__')
    for basedir in os.listdir(str(SNIPPET_DIR.join(dirname))):
        remove(os.path.join(basedir, '__pycache__'))
    olddir = os.getcwd()
    python_f = udir.join('x.py')
    python_f.write(py.code.Source(python_snippet))
    try:
        os.chdir(str(SNIPPET_DIR.join(dirname)))
        vp = str(venv_dir.join('bin/python'))
        subprocess.check_call((vp, 'setup.py', 'clean'))
        subprocess.check_call((vp, 'setup.py', 'install'))
        subprocess.check_call((vp, str(python_f)))
    finally:
        os.chdir(olddir)

def run_setup_and_program(dirname, python_snippet):
    venv_dir = create_venv(dirname + '-cpy')
    really_run_setup_and_program(dirname, venv_dir, python_snippet)
    #
    sys._force_generic_engine_ = True
    try:
        venv_dir = create_venv(dirname + '-gen')
        really_run_setup_and_program(dirname, venv_dir, python_snippet)
    finally:
        del sys._force_generic_engine_
    # the two files lextab.py and yacctab.py are created by not-correctly-
    # installed versions of pycparser.
    assert not os.path.exists(str(SNIPPET_DIR.join(dirname, 'lextab.py')))
    assert not os.path.exists(str(SNIPPET_DIR.join(dirname, 'yacctab.py')))

def test_infrastructure():
    run_setup_and_program('infrastructure', '''
    import snip_infrastructure
    assert snip_infrastructure.func() == 42
    ''')

def test_distutils_module():
    run_setup_and_program("distutils_module", '''
    import snip_basic_verify
    p = snip_basic_verify.C.getpwuid(0)
    assert snip_basic_verify.ffi.string(p.pw_name) == b"root"
    ''')

def test_distutils_package_1():
    run_setup_and_program("distutils_package_1", '''
    import snip_basic_verify1
    p = snip_basic_verify1.C.getpwuid(0)
    assert snip_basic_verify1.ffi.string(p.pw_name) == b"root"
    ''')

def test_distutils_package_2():
    run_setup_and_program("distutils_package_2", '''
    import snip_basic_verify2
    p = snip_basic_verify2.C.getpwuid(0)
    assert snip_basic_verify2.ffi.string(p.pw_name) == b"root"
    ''')

def test_setuptools_module():
    run_setup_and_program("setuptools_module", '''
    import snip_setuptools_verify
    p = snip_setuptools_verify.C.getpwuid(0)
    assert snip_setuptools_verify.ffi.string(p.pw_name) == b"root"
    ''')

def test_setuptools_package_1():
    run_setup_and_program("setuptools_package_1", '''
    import snip_setuptools_verify1
    p = snip_setuptools_verify1.C.getpwuid(0)
    assert snip_setuptools_verify1.ffi.string(p.pw_name) == b"root"
    ''')

def test_setuptools_package_2():
    run_setup_and_program("setuptools_package_2", '''
    import snip_setuptools_verify2
    p = snip_setuptools_verify2.C.getpwuid(0)
    assert snip_setuptools_verify2.ffi.string(p.pw_name) == b"root"
    ''')
