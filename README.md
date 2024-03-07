# Boxing Sentiment Analysis Project

## Overview
This repository contains the code and datasets for a sentiment analysis project focused on YouTube comments related to boxing. The project utilizes Natural Language Processing (NLP) techniques to analyze sentiments expressed about boxers, with a case study on the match between Tyson Fury and Oleksandr Usyk.

## Structure
The repository is organized as follows:

- `Boxing_sentiment_analysis.ipynb`: Jupyter notebook with the main analysis, including data processing, model training, and evaluation.
- `config.json`: Configuration file containing parameters and settings used across the project.
- `data/`: Directory containing various datasets and results:
  - `annotated/`: Annotated datasets used for training and validating models.
  - `datasets/`: Original and processed datasets, including auxiliary, balanced, and keyword-based (kwb) datasets.
  - `human_feedback_annotations/`: Data related to human feedback for annotations, accuracy scoring, and standard datasets.
  - `preprocessed/`: Preprocessed data files ready for model consumption.
  - `raw/`: Raw YouTube comments data.
  - `results/`: Results from model predictions and evaluations.
- `images/`: Various images depicting project designs, diagrams, and result visualizations.
- `src/`: Source code for the project:
  - `annotator.py`: Script for annotation processing.
  - `data_loader.py`: Module for loading datasets.
  - `data_preprocessing.py`: Functions for data cleaning and preparation.
  - `data_saver.py`: Utilities to save processed data.
  - `feature_engineering.py`: Code for generating and selecting features for the models.
  - `human_feedback_annotation_openai.py`: Scripts for incorporating OpenAI's feedback into annotations.
  - `youtube_scrapping.py`: Script for scraping YouTube comments.

## Usage
To use this project:

1. Clone the repository.
2. Install the required dependencies.
3. Run the `Boxing_sentiment_analysis.ipynb` notebook to perform the sentiment analysis.
4. Explore the `data/` directory for datasets and the `images/` directory for visualization of results and architectures.

## Dependencies
List all libraries and frameworks with their respective versions that are necessary to run the project.

## License
This project is licensed under the terms of the MIT license.
