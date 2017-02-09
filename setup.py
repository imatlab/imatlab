from setuptools import setup, find_packages
import versioneer


if __name__ == "__main__":
    setup(name="imatlab",
          author="Antony Lee",
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass(),
          url="https://github.com/anntzer/imatlab",
          license="BSD",
          long_description=open("README.rst").read(),
          classifiers=[
              "Framework :: IPython",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python :: 3.5",
              "Programming Language :: Python :: 3.6",
              "Topic :: System :: Shells",
          ],
          packages=find_packages(include=["imatlab", "imatlab.*"]),
          python_requires=">=3.5",
          install_requires=[
              "ipykernel>=4.1",  # Current version of --user install.
              "matlabengineforpython",  # Not actually PyPI installable.
          ])
