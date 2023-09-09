from setuptools import setup, find_packages

setup(
    name="chronoqueue_sdk",
    version="0.1.0",  # Start with a base version, consider semantic versioning
    packages=find_packages(exclude=["tests*"]),  # Automatically discover and include all packages in the package directory
    install_requires=[
        "grpcio",  # Since the SDK requires gRPC
    ],
    extras_require={
        "dev": [  # Optional dependencies for development
            "grpcio-tools",  # Required for generating gRPC Python classes
            "mypy-protobuf", # Required for generating gRPC Python classes
            "pytest", # Required for unit test
        ]
    },
    python_requires=">=3.11",  # Minimal Python version supported by the SDK
    author="Adrien Ndikumana",
    author_email="n.adrien@mun.ca",
    description="Python SDK for interacting with Chronoqueue",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adrien19/chronoqueue_sdk",  # Link to the SDK's repository or documentation
    classifiers=[
        "Development Status :: 3 - Alpha",  # You can adjust this as per the SDK's development state
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # If using MIT license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="chronoqueue, grpc, sdk",  # Keywords related to the SDK
    project_urls={
        "Source": "https://github.com/adrien19/chronoqueue_sdk",
        "Tracker": "https://github.com/adrien19/chronoqueue_sdk/issues",
    },
)

