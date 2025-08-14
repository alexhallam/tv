from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="conformal-regress",
    version="0.1.0",
    author="Conformal Regress Team",
    author_email="team@conformal-regress.org",
    description="A beginner-friendly, speed-first conformal regression package with R-like ergonomics",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/conformal-regress/conformal-regress",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jax>=0.4.0",
        "jaxlib>=0.4.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "formulaic>=0.6.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "display": [
            "tidy-viewer-py>=0.1.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)