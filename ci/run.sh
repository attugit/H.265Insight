#!/bin/bash

./waf distclean configure build install --mode=${BUILD_TYPE} --prefix=$PWD/build && \
{
  if [[ "${BUILD_TYPE}" == "RELEASE" ]]; then
    export PATH=$PWD/build/bin:$PATH && \
    mkdir -p ./build/data && \
    mkdir -p ./build/streams && \
    wget -q --directory-prefix=./build/data --accept=zip --input-file=http://wftp3.itu.int/av-arch/jctvc-site/bitstream_exchange/draft_conformance/HEVC_v1 && \
    find ./build/data -maxdepth 1 -type f -name '*.zip' | while read f; do unzip -qq -o $f -d ./build/data/`basename $f .zip`; done && \
    find ./build/data -type f -name '*.bit' -or -name '*.bin' | while read f; do sha1sum $f; mv $f ./build/streams/`sha1sum $f | awk '{print $1}'`.`basename $f`; done && \
    virtualenv tests && \
    source ./tests/bin/activate && \
    pip install pytest && \
    py.test ./ci/bitstreams.py -v --capture=sys && \
    deactivate
  fi
}
