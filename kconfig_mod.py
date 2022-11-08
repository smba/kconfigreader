#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob, os
import sys

from pathlib import Path

for path in Path(sys.argv[1]).rglob('Kconfig'):
    with open(path, 'r') as f:
        txt = f.read()

    txt = txt.replace('imply', 'select')
    
    with open(path, 'w') as f:
        f.write(txt)
    