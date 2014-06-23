import py, os, sys
import cffi, _cffi_backend

def setup_module(mod):
    if '_cffi_backend' in sys.builtin_module_names:
        py.test.skip("this is embedded version")

BACKEND_VERSIONS = {
    '0.4.2': '0.4',     # did not change
    '0.7.1': '0.7',     # did not change
    '0.7.2': '0.7',     # did not change
    '0.8.1': '0.8',     # did not change (essentially)
    }

def test_version():
    v = cffi.__version__
    version_info = '.'.join(str(i) for i in cffi.__version_info__)
    assert v == version_info
    assert BACKEND_VERSIONS.get(v, v) == _cffi_backend.__version__

def test_doc_version():
    parent = os.path.dirname(os.path.dirname(__file__))
    p = os.path.join(parent, 'doc', 'source', 'conf.py')
    content = open(p).read()
    #
    v = cffi.__version__
    assert ("version = '%s'\n" % v[:3]) in content
    assert ("release = '%s'\n" % v) in content

def test_doc_version_file():
    parent = os.path.dirname(os.path.dirname(__file__))
    v = cffi.__version__
    p = os.path.join(parent, 'doc', 'source', 'index.rst')
    content = open(p).read()
    assert ("cffi/cffi-%s.tar.gz" % v) in content

def test_setup_version():
    parent = os.path.dirname(os.path.dirname(__file__))
    p = os.path.join(parent, 'setup.py')
    content = open(p).read()
    #
    v = cffi.__version__
    assert ("version='%s'" % v) in content

def test_c_version():
    parent = os.path.dirname(os.path.dirname(__file__))
    v = cffi.__version__
    p = os.path.join(parent, 'c', 'test_c.py')
    content = open(p).read()
    assert (('assert __version__ == "%s"' % BACKEND_VERSIONS.get(v, v))
            in content)
