

from distutils.core import setup
import glob
import py2exe


setup(windows=["cc.py"])
'''
,
      data_files=[("IMAGES_L", ["IMAGES_L/*"]),
                ("pgn", ["pgn/*"]),
                ("SOUNDS", ["SOUNDS/*"])]
)

'''
