#!/usr/bin/env python3
"""
Setup configuration for CogniFlow.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cogniflow",
    version="1.0.0",
    author="Your Name",
    author_email="rosemkatt@gmail.com",
    description="A modern Python library for building sophisticated conversational AI applications with cognitive intelligence and workflow automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/voidfemme/llm_playground",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cogniflow=chatbot_library.cli:main",
        ],
    },
    keywords="ai, chatbot, llm, conversation, prompt-management, thinking-modes, cognitive-ai, workflow-automation",
    project_urls={
        "Bug Reports": "https://github.com/voidfemme/llm_playground/issues",
        "Source": "https://github.com/voidfemme/llm_playground",
        "Documentation": "https://github.com/voidfemme/llm_playground/docs",
    },
)