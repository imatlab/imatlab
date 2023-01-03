from setuptools import setup, find_packages


setup(
    name="imatlab",
    description="A Juyter kernel for MATLAB.",
    long_description=open("README.rst", encoding="utf-8").read(),
    author="Antony Lee",
    url="https://github.com/imatlab/imatlab",
    license="MIT",
    classifiers=[
        "Framework :: IPython",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Shells",
    ],
    packages=find_packages("lib"),
    package_dir={"": "lib"},
    package_data={"imatlab": ["data/imatlab_export_fig.m"]},
    python_requires=">=3.5",
    setup_requires=["setuptools_scm"],
    use_scm_version=lambda: {
        "version_scheme": "post-release",
        "local_scheme": "node-and-date",
    },
    install_requires=[
        "ipykernel>=4.1",  # Current version of --user install.
        "importlib_metadata; python_version<'3.8'",
    ],
)
