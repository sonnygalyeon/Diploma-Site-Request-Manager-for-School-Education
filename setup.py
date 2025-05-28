from setuptools import setup, find_packages

setup(
    name="telegram_bot",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'run-bot=request_manager.telegram_bot_service.main:main'
        ]
    }
)