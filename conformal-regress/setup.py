from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="conformal-regress",
    version="0.1.0",
    author="Conformal Regress Team", 
    author_email="contact@conformal-regress.com",
    description="Fast, beginner-friendly conformal regression with R-like ergonomics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/conformal-regress",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jax>=0.4.0",
        "jaxlib>=0.4.0", 
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "formulaic>=0.6.0",
        "scipy>=1.7.0",  # For LAPACK routines
        "tidy-viewer-py>=0.1.0",  # For displaying results
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "conformal-regress=conformal_regress.cli:main",
        ],
    },
)