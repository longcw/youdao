# coding:utf-8

from setuptools import setup, find_packages, Extension
from youdao.config import VERSION

setup(name='youdao',
      version=VERSION,
      description="基于有道API和有道词典web版的在terminal查询词的小工具,支持单词发音",
      long_description="""基于有道API和有道词典web版的在terminal查询词的小工具,抓取web版后使用beautifulsoup解析, 详情请见github""",
      keywords='python youdao dictionary terminal',
      author='longcw',
      author_email='longchsin@foxmail.com',
      url='https://github.com/longcw/youdao',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'termcolor', 'requests', 'beautifulsoup4', 'peewee', 'lxml'
      ],
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ],
      entry_points={
          'console_scripts': [
              'yd = youdao.main:main',
          ]
      },
      ext_modules=[Extension('youdao/lib/CPyStarDictIndex', sources=['youdao/lib/CPyStarDictIndex.cpp'])]
)
