#!/usr/bin/env python

import os
import luigi
from luigi.util import requires
from ensembldb.core.utils import SimpleTask, Prepare

script_dir, script_name = os.path.split(os.path.abspath(__file__))
MODULE, _ = os.path.splitext(script_name)


class Pubvar:
    _module = MODULE


class TestPrepare(Prepare, Pubvar):
    pass


@requires(TestPrepare)
class TestRun(SimpleTask, Pubvar):
    pass


if __name__ == '__main__':
    luigi.run()
