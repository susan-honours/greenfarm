import setuptools
import distutils.spawn
import os
import subprocess
import time
from stat import *

setuptools.setup(
    name="GreenFarm",
    version="0.1.0",
    url="",

    author="Susan",
    author_email="",

    description="",

    packages=[
              'greenfarm',
    ],

    install_requires=[
        'pyyaml',
        'kivy',
        'pybase64',
        'bson',
        'datetime',
        'passlib',
        'pymongo',
        'matplotlib',
        'numpy',        
    ],
)

python_loc = distutils.spawn.find_executable('python3')
greenfarm_app_loc = os.path.dirname(os.path.abspath(__file__))

desktop_file_loc = os.path.join(os.path.expanduser("~"),"Desktop","GreenFarm.desktop")
with open(desktop_file_loc, 'w') as f:
    f.write(\
'''[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Exec={} {}/greenfarm/main.py
Name=GreenFarm
Comment=GreenFarm
Icon={}/greenfarm/images/app_logo.png'''.format(python_loc,greenfarm_app_loc,greenfarm_app_loc,greenfarm_app_loc,)\
)
    
os.chmod(desktop_file_loc, S_IRWXU | S_IRWXG | S_IRWXO )
