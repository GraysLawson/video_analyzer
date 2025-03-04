from setuptools import setup, find_packages

setup(
    name="video_analyzer",
    version="1.0.0",
    description="Find and manage duplicate video files with different resolutions",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        'colorama',
        'tabulate',
        'tqdm',
        'rich',
        'plotext',
        'humanize'
    ],
    extras_require={
        'dev': [
            'pyinstaller>=6.3.0'
        ]
    },
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'video-analyzer=video_analyzer.__main__:main',
        ],
    },
) 