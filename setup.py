from setuptools import setup

setup(
    name='',
    version='1.0',
    packages=['context_agnostic_engagement', 'context_agnostic_engagement.helper_tools',
              'context_agnostic_engagement.feature_extraction', 'context_agnostic_engagement.models'],
    url='',
    license='',
    author='',
    author_email='',
    description='This python package includes the datasets and the helpfer functions that allow building models for predicting context-agnostic (population-based) of video lectures. ',
    install_requires=[
        'numpy>=1.14.1',
        'pandas>=0.22.0',
        'scipy>=1.0.1',
        'nltk>=3.2.5',
        'ujson>=1.35',
        'scikit-learn>=0.19.1',
        'pyspark>=2.4.5',
        'textatistic>=0.0.1']
)
