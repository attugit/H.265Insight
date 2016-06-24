#! /usr/bin/env python
# encoding: utf-8

VERSION='0.0.1'
PROJECT='hevc'
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

modes = [
  'DEBUG',
  'RELEASE',
]

def init(ctx):
  ctx.load('build_logs')

def options(opt):
  opt.load('compiler_cxx')
  opt.add_option( '-m', '--mode',
          action  = 'store',
          default = os.environ.get('MODE', modes[0]),
          metavar = 'MODE',
          dest    = 'mode',
          choices = modes,
          help    = 'Default build type, supported: ' + ', '.join(modes)
          )

def configure(conf):
  conf.setenv('base')
  conf.define('APPNAME', APPNAME)
  conf.define('PROJECT', PROJECT)
  conf.define('VERSION', VERSION)
  conf.load('compiler_cxx')
  conf.env.CXXFLAGS += flags
  for variant in modes:
    conf.setenv('base')
    newenv = conf.env.derive()
    newenv.detach()
    conf.setenv(variant.lower(), newenv)

  conf.setenv('debug')
  conf.env.CXXFLAGS += ['-g', '-O0']
  conf.env.DEFINES += ['DEBUG']

  conf.setenv('release')
  conf.env.CXXFLAGS += ['-O3', '-mtune=native', '-fPIC', '-fno-rtti', '-rdynamic']
  conf.env.DEFINES += ['NDEBUG', 'NO_DEBUG', ]
  conf.env.DEFINES += ['ABORT_ON_SEI_HASH_MISMATCH']

  conf.env.MODE = conf.options.mode.lower()
  conf.msg(msg='Default build mode',
          result=conf.env.MODE)

  conf.setenv(conf.env.MODE)
  mode = conf.env.derive()
  mode.detach()
  conf.setenv('default', mode)

import os
from waflib.Tools import waf_unit_test
def build(bld):
  if not bld.variant:
    bld.fatal('try "waf --help"')
  bld.env.INCLUDES += ['.', bld.bldnode.abspath()]
  bld.env.INCLUDES += ['src', 'src/ThirdParty/MD5']
  bld(
    source       = bld.path.ant_glob(['src/**/*.cpp'], excl=['src/Decoder/Extractor.cpp']),
    target       = PROJECT,
    features     = 'cxx cxxstlib',
    install_path = None,
  )
  bld(
    source       = bld.path.ant_glob(['src/ThirdParty/MD5/md5.c']),
    target       = 'md5',
    features     = 'cxx cxxstlib',
    install_path = None,
  )
  bld.env.LIB += ['pthread', 'm']
  bld(
    source       = bld.path.ant_glob(['apps/**/*.cpp']),
    target       = APPNAME,
    features     = 'cxx cxxprogram',
    use          = [PROJECT, 'md5'],
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
  class default(ctx):
    cmd = name
    variant = 'default'

