###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import absolute_import

import os
import sys
import pytest
import txaio

if os.environ.get('USE_ASYNCIO', False):
    from autobahn.asyncio.component import Component

    @pytest.mark.skipif(sys.version_info < (3, 5), reason="requires Python 3.5+")
    @pytest.mark.asyncio(forbid_global_loop=True)
    def test_asyncio_component(event_loop):
        orig_loop = txaio.config.loop
        txaio.config.loop = event_loop

        comp = Component(
            transports=[
                {
                    u"url": u"ws://localhost:12/bogus",
                    u"max_retries": 1,
                    u"max_retry_delay": 0.1,
                }
            ]
        )

        # if having trouble, try starting some logging (and use
        # "py.test -s" to get real-time output)
        # txaio.start_logging(level="debug")
        f = comp.start(loop=event_loop)
        txaio.config.loop = event_loop
        finished = txaio.create_future()

        def fail():
            finished.set_exception(AssertionError("timed out"))
            txaio.config.loop = orig_loop
        txaio.call_later(1.0, fail)

        def done(f):
            try:
                f.result()
                finished.set_exception(AssertionError("should get an error"))
            except RuntimeError as e:
                if 'Exhausted all transport connect attempts' not in str(e):
                    finished.set_exception(AssertionError("wrong exception caught"))
            finished.set_result(None)
            txaio.config.loop = orig_loop
        f.add_done_callback(done)
        return finished
