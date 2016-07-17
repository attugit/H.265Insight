#! /usr/bin/env python
# encoding: utf-8

VERSION='0.0.1'
APPNAME='i265'

top = '.'
out = 'build'
flags = [
  '-std=c++14',
  '-Wall',
  '-Wextra',
  '-Wshadow',
  '-Wunused',
  '-Wno-parentheses',
  '-Wno-unused-local-typedefs',
  '-fno-exceptions',
  '-pedantic',
  '-pedantic-errors',
]

def init(ctx):
  ctx.load('build_logs')

def options(opt):
  opt.load('compiler_cxx')

def configure(conf):
  conf.load('compiler_cxx')

def build(bld):
  if not bld.variant:
    bld.fatal('try "waf --help"')
  bld.define('APPNAME', APPNAME)
  bld.define('VERSION', VERSION)
  bld.env.CXXFLAGS += flags
  if bld.variant == 'debug':
    bld.env.CXXFLAGS += ['-g', '-O0']
    bld.env.DEFINES += ['DEBUG']
  if bld.variant == 'release':
    bld.env.CXXFLAGS += ['-O3', '-mtune=native', '-fPIC', '-fno-rtti', '-rdynamic', '-pg']
    bld.env.LINKFLAGS += ['-pg']
    bld.env.DEFINES += ['NDEBUG', 'ABORT_ON_SEI_HASH_MISMATCH']
  bld.env.INCLUDES += ['.', bld.bldnode.abspath()]
  bld.env.INCLUDES += ['src', 'src/ThirdParty/MD5']
  bld(
    source       = bld.path.ant_glob(['src/**/*.cpp'], excl=['src/Decoder/Extractor.cpp']),
    target       = 'hevc',
    features     = 'cxx cxxstlib',
    install_path = None,
  )
  bld(
    source       = bld.path.ant_glob(['src/ThirdParty/MD5/md5.c']),
    target       = 'MD5',
    features     = 'cxx cxxstlib',
    install_path = None,
  )
  bld.env.LIB += ['pthread', 'm']
  bld(
    source       = bld.path.ant_glob(['apps/**/*.cpp']),
    target       = APPNAME,
    features     = 'cxx cxxprogram',
    use          = ['hevc', 'MD5'],
  )

from waflib.Build import BuildContext
from waflib.Build import CleanContext
from waflib.Build import InstallContext
from waflib.Build import UninstallContext

for ctx in (BuildContext, CleanContext, InstallContext, UninstallContext):
  name = ctx.__name__.replace('Context','').lower()
  class debug(ctx):
    cmd = name + '_debug'
    variant = 'debug'
  class release(ctx):
    cmd = name + '_release'
    variant = 'release'

