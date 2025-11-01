from setuptools import setup, find_packages

setup(
name='crosstray',
version='0.1.0',
packages=find_packages(exclude=['tests'], where='src'),
package_dir={'': 'src'},
install_requires=[
'pywin32; platform_system=="Windows"',
],
author='Uman Sheikh',
author_email='muman014@gmail.com',
description='Lightweight system tray library for Windows (cross-platform coming soon)',
long_description=open('README.md', 'r', encoding='utf-8').read(),
long_description_content_type='text/markdown',
license='MIT',
keywords='system tray windows notification area',
url='https://github.com/umansheikh/crosstray',
classifiers=[
'Development Status :: 3 - Alpha',
'Intended Audience :: Developers',
'License :: OSI Approved :: MIT License',
'Programming Language :: Python :: 3',
'Programming Language :: Python :: 3.8',
'Programming Language :: Python :: 3.9',
'Programming Language :: Python :: 3.10',
'Programming Language :: Python :: 3.11',
'Programming Language :: Python :: 3.12',
],
python_requires='>=3.8',
)