from setuptools import setup, find_packages
import versioneer


if __name__ == "__main__":
    setup(name="imatlab",
          author="Antony Lee",
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass(),
          url="https://github.com/imatlab/imatlab",
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
          package_data={"imatlab": ["resources/imatlab_export_fig.m",
                                    "resources/matlab.tpl"]},
          python_requires=">=3.5",
          install_requires=[
              "ipykernel>=4.1",  # Current version of --user install.
              "nbconvert>=4.2",  # Exporter API.
              "plotly>=1.13.0",  # First version to test Py3.5.
              "widgetsnbextension>=1.0",  # Anything works.
              "matlabengineforpython>=R2016b",  # Not PyPI installable.
          ],
          entry_points = {
              "nbconvert.exporters": [
                  "matlab = imatlab._exporter:MatlabExporter",
              ],
          })
