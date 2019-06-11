# -*- coding: utf8 -*-

from backend.FlashScore import flashScore
import pandas as pd
import os
import sys
import tqdm
import click

# setting path
files = {'aaInfo': 'AAIndex2.csv',
         'locationForest': 'topologie.pkl',
         'scoreForest': 'scoreForest.pkl'}

### file and argument input
@click.command()

@click.option('--input_file',
              help='Full path of the file containing all protein sequences in fasta format')
@click.option('--result_folder', default=None,
              help='Full path to the folder you want to store all results in. Default is sequence file directory.')
@click.option('--enzyme', default='trypsin',
                help='Enzyme to use for in-silico digestion. Default is trypsin.')
@click.option('--file_format', default='fasta',
              help='Format of the protein sequences file. Default is fasta.')
@click.option('--min_length', default=5,
              help='Minimum length a peptide has to have after digestion in order to be considered for prediction.')
#@click.option('--lower_lim', default=0.,
#              help='Lower prediction score limit. All prediction scores below this value will be ignored when calculating the statistics. Default is 0.')
#@click.option('--upper_lim', default=1.,
#              help='Upper prediction score limit. All prediction scores above this value will be ignored when calculating the statistics. Default is 1.')

def makePredictions(input_file, result_folder, enzyme, min_length,
                    file_format):
    """
    Predicting the localization of proteins and the probability of their peptides to fly in MS
    """
    Flash = flashScore(input_file, seqFormat=file_format, enzyme=enzyme, min_length=min_length)
    Flash.predictScore()
    #Flash.predictLocalization()

    Flash.stats()
    Flash.visualizeStats(path=result_folder)
    Flash.writeResults(path=result_folder)

if __name__ == '__main__':
    print('Starting to make predictions...')
    makePredictions()

