import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ML4EFT",
    version="0.0.1",
    author="J.J. ter Hoeve",
    author_email="j.j.ter.hoeve@vu.nl",
    description="ML4EFT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "ncempy>=1.8.0",
        "matplotlib>=3.3.2",
        "numpy>=1.19.2",
        "natsort>=7.1.0",
        "scipy>=1.5.2",
        "pandas>=1.0.5",
        "seaborn>=0.11.0",
        "torch>=1.6.0",
        "scikit_learn>=1.0",
        "wget>=3.2",
        ],
    python_requires=">=3.7",
)
