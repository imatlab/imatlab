from setuptools import setup, find_packages
import versioneer


if __name__ == "__main__":
    setup(name="matlab_kernel",
          author="Antony Lee",
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass(),
          url="https://github.com/anntzer/matlab_kernel",
          license="BSD",
          long_description=open("README.rst").read(),
          classifiers=[
              "Framework :: IPython",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python :: 3.5",
              "Topic :: System :: Shells",
          ],
          packages=find_packages(include=["matlab_kernel", "matlab_kernel.*"]),
          python_requires="3.5",
          install_requires=[
              "ipykernel>=4.1",  # Current version of --user install.
          ])
