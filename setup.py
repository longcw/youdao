# coding:utf-8

from setuptools import setup, find_packages

version = '0.1.1'

setup(name='youdao',
      version=version,
      description="基于有道API的在terminal查询词的小工具",
      long_description="""基于有道API的在terminal查询词的小工具""",
      keywords='python youdao dictionary terminal',
      author='longcw',
      author_email='longchsin@foxmail.com',
      url='https://github.com/longcw/youdao',
      license='',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'termcolor', 'requests'
      ],
      entry_points={
        'console_scripts':[
            'yd = youdao.youdao:main',
        ]
      },
)
