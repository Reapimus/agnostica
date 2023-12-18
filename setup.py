import re
import setuptools

with open('README.md', 'r') as rmd:
    long_description = rmd.read()

version = ''
with open('agnostica/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Version is not set.')

setuptools.setup(
    name='agnostica',
    version=version,
    author='reapimus',
    description='A platform-agnostic library for creating multi-platform chat bots with ease.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/reapimus/agnostica',
    project_urls={
        'Documentation': 'https://github.com/Reapimus/agnostica',
        'Issue tracker': 'https://github.com/Reapimus/agnostica/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English'
    ],
    packages=[
        'agnostica',
    ],
    license='MIT',
    python_requires='>=3.11',
    install_requires=['aiohttp'],
)