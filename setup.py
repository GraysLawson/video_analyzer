from setuptools import setup, find_packages

setup(
    name="video_analyzer",
    version="1.0.0",
    description="Find and manage duplicate video files with different resolutions",
    author="Your Name",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
        'colorama>=0.4.6',
        'tabulate>=0.9.0',
        'tqdm>=4.65.0',
        'rich>=13.7.0',
        'plotext>=5.2.8',
        'humanize>=4.9.0'
    ],
    entry_points={
        'console_scripts': [
            'video-analyzer=video_analyzer.__main__:main',
        ],
    },
    python_requires='>=3.7',
) 