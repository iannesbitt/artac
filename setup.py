import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="artac",
    version="0.0.1",
    author="Ian Nesbitt",
    author_email="ian.nesbitt@gmail.com",
    license='GPLv3',
    description="Automated readgssi TeX Appendix Creator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iannesbitt/artac/",
    packages=setuptools.find_packages(),
    install_requires=['readgssi'],
    entry_points='''
        [console_scripts]
        artac=artac.artac:main
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Development Status :: 4 - Beta",
    ],
)