from setuptools import find_namespace_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("requirements_dev.txt") as f:
    requirements_dev = f.read().splitlines()

with open("README.md") as f:
    long_description = f.read()

setup(
    name="xiao_et_al_utils",
    version="1.0.1",
    description="Behavior and imaging analysis for Xiao et al.",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires="==3.8.10",
    packages=find_namespace_packages(exclude=("docs", "tests*")),
    extras_require=dict(dev=requirements_dev),
    include_package_data=True,
    url="https://github.com/portugueslab/xiao_et_al",
    author="Luigi Petrucco",
    author_email="luigi.petrucco@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
