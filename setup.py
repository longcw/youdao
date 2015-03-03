# coding:utf-8

from setuptools import setup, find_packages

version = '0.1.4'

setup(name='youdao',
      version=version,
      description="基于有道API和有道词典web版的在terminal查询词的小工具",
      long_description="""基于有道API和有道词典web版的在terminal查询词的小工具,抓取web版后使用beautifulsoup解析""",
      keywords='python youdao dictionary terminal',
      author='longcw',
      author_email='longchsin@foxmail.com',
      url='https://github.com/longcw/youdao',
      license='',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'termcolor', 'requests', 'beautifulsoup4', 'peewee'
      ],
      entry_points={
        'console_scripts':[
            'yd = youdao.youdao:main',
        ]
      },
)
