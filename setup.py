version="1.0.3"from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ethical-ai-framework",
    version="1.0.3",
    description="A transparent, consent-based, non-weaponizable ethical AI framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cherokee",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
