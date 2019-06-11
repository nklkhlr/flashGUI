# *- coding: utf8 -*-

import os, sys
from Bio import SeqIO
from pyteomics.parser import _cleave, expasy_rules
import pandas as pd
import pickle
import tqdm
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from tqdm import tqdm

def readSeq(file, seqformat='fasta', show_progress=False):
    """
    Simple helper function to read in sequence files.

    Parameters:
    -----------
    - file: filepath to file containing sequences
    - seqformat: file format

    Returns:
    --------
    - dict of sequences of structure protein ID: sequence
    """
    if seqformat not in list(iter(SeqIO._FormatToIterator)):
        raise ValueError('Invalid format of sequence, please choose one of the following options:\
                         %s' %list(iter(SeqIO._FormatToIterator)))

    return {seq.id: seq.seq for seq in SeqIO.parse(file, seqformat)}

def digest(seqs, enzyme, min_length=5):
    """
    Simple helper function to do in-silico digest of list of sequences.

    Parameters:
    ----------
    - seqs: list of sequences
    - enzyme: enzyme to be used for in-silico digest, see pyteomics.expasy_rules documentation for valid options

    Returns:
    --------
    - dictionary of digested peptides (values) with their corresponding description as keys
    """
    if enzyme not in list(iter(expasy_rules)):
        raise ValueError('Invalid enzyme selected, please select one of the following options:\
                         %s' %list(iter(expasy_rules)))

    return {ID: _cleave(str(seq), expasy_rules[enzyme], min_length=min_length)\
            for ID, seq in seqs.items()}

#TODO: adapt for other file formats as well?
def writeFasta(file, seqs, upperLim, lowerLim):
    """
    Simple helper function to write sequences to fasta files.

    Parameters:
    ----------
    - file: filepath to write data to
    - seqs: dictionary of sequences with keys being the sequence identifier and values a list of dicts of peptide sequence, and corresponding scores as by the flash score calculation
    - upperLim:
    - lowerLim:
    """
    with open(file, 'w') as fasta:
        for ID, peptides in seqs.items():
            pepList = [peptide['sequence'] for peptide in peptides[ID] \
                            if peptide['score'] >= lowerLim and peptide['score']<upperLim]
            if len(pepList)>0:
                fasta.write('>'+ID+'\n'+''.join(peptides)+'\n')

def writeScores(data, filename, delim='\t'):
    """
    Helper function to write dictionary to txt file

    Parameters:
    -----------
    - data: dictionary with protein ID as keys and tuple of peptide sequence, predicted class scores and class prediction as values
    - filename: full path to file scores should be written to
    - delim: delimiter to use to seperate tuple values
    """
    with open(filename, 'w') as file:
        for ID, peptides in data.items():
            file.write('>'+ID+'\n')
            for (seq, score, label) in peptides:
                file.write(seq+delim+str(score)+delim+str(label)+'\n')

def writeStats(stats, filename, delim='\t'):
    """
    Helper function to write score statistics to txt file

    Parameters:
    -----------
    - data: dictionary with protein ID as keys and tuple of peptide sequence, predicted class scores and class prediction as values
    - filename: full path to file scores should be written to
    - delim: delimiter to use to seperate tuple values
    """
    with open(filename, 'w') as file:
        for prop, value in stats.items():
            file.write(prop+delim+str(value)+'\n')

def writeParameters(data, filename, delim='\t'):
    with open(filename, 'w') as file:
        for n, comb in enumerate(data):
            file.write(str(n)+delim+str(comb)+'\n')

def loadData(folder, aaInfo, trainMode=False, locationForest=None, scoreForest=None):
    """
    Simple helper function to load data needed for prediction of scores.

    Parameters:
    -----------
    - folder: path to folder where files ALL input files for this function are stored
    - aaInfo: filename of csv file containing amino acid information
    - trainMode: if True seonly aaInfo is loaded, default is False.
    - locationForest: filename of pickle file containing random forest for location prediction, default is None but has to be specified as long as train mode is False
    - scoreForest: filename of pickle file containing random forest for score prediction, default is None but has to be specified as long as train mode is False

    Returns:
    --------
    - tuple of
    """
    aai = pd.read_csv(os.path.join(folder, aaInfo), index_col=0)

    if not trainMode:
        #if locationForest is None or scoreForest is None:
        if scoreForest is None:
            raise ValueError('Filepaths for location and score forest must both be given as input when not in training mode. Either one of them or both were not given')
        #sL = pickle.load(open(os.path.join(folder, locationForest), 'rb'))
        sF = pickle.load(open(os.path.join(folder, scoreForest), 'rb'))
        return (aai, sF)

    return aai

def genPipeline(data, model):
    """
    Simple helper function to generate a pipeline consisting of an imputer followed by a classifier

    Parameters:
    -----------
    - data: 2D np.array of values (rows=samples, columns=attritbutes) to fit the imputer to
    - model: already initialized sklearn classifier object

    Returns:
    --------
    - pipeline object
    """
    imputer = SimpleImputer(strategy='median')
    imputer.fit(data)

    pipeline = Pipeline([('imputer', imputer), ('model', model)])

    return pipeline

def data_to_dict(dictionary, item):
    """
    Helper function for appending to dictionary
    """
    if item[0] in dictionary.keys():
        dictionary[item[0]].append(item[1])
    else:
        dictionary[item[0]] = [item[1]]

def del_empty_seq(dictionary, item):
    """
    Helper function to delete empty sequences from dictionary
    """
    if len(item[1])<1:
        del(dictionary[item[0]])

def roc_curve_(y_true, y_pred):
    """

    """
    tpr, fpr, thrs = roc_curve(y_true, y_pred[:,1])

    return {'tpr':tpr,
            'fpr':fpr,
            'thrs': thrs}
