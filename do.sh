#!/bin/bash

wget https://github.com/torvalds/linux/archive/refs/tags/v4.13-rc3.zip
unzip v4.13-rc3.zip
mv linux-4.13-rc3/ ../linux/


python3 kconfig_mod.py ../linux/
