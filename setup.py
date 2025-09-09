"""
Setup configuration for the Financial Document Redactor package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="financial-document-redactor",
    version="2.0.0",
    author="Financial Document Redactor Team",
    description="A comprehensive library for redacting sensitive information from financial documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Security",
        "Topic :: Text Processing"
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyMuPDF>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800"
        ],
        "nlp": [
            "spacy>=3.4.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "redactor=redactor.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)