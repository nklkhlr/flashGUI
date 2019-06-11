# -*- coding: utf8 -*-

from backend import utils
import numpy as np

def flash(protein, pipeline):
        """
        Calculation of flash score

        Parameters:
        -----------
        - protein: tuple of protein ID and corresponding peptide property scores or array of peptide property scores
        - pipeline: sklearn pipeline object containing the pipeline to use for the prediction

        Returns:
        --------
        - tuple of protein ID and 2D array of probability scores (rows are samples, columns class probabilities) if input is tuple or only probability score (if input is array)
        """
        if protein.__class__ is tuple:
            if len(protein[1])!=0:
                return(protein[0], pipeline.predict_proba(protein[1]))#TODO: slicing
            else:
                return(protein[0], [])
        else:
            return(pipeline.predict_proba(protein))


def propertyScorePeptides(protein, aminos):
        """
        Calculating mean properties of peptides. Mean properties are calculated by averaging every property over all amino acids in peptide

        Parameters:
        -----------
        - protein: tuple of protein ID and sequences of digested peptides or array of peptide sequences
        - aminos: pandas DataFrame containing values for all properties (rows) and all amino acids (columns)

        Returns:
        --------
        - tuple of protein ID, list of property scores for all peptides, if input is tuple or 2D array of scores (rows are samples, columns properties) if input is array
        """
        if protein.__class__ is tuple:
            props = [np.array(aminos[[amino for amino in peptide]].mean(axis=1)) \
                                                        for peptide in protein[1]]
            return protein[0], props
        elif protein.__class__ is list:
            return [np.array(aminos[[amino for amino in peptide]].mean(axis=1)) \
                                                        for peptide in protein]
        else:
            return np.array(aminos[[amino for amino in protein]].mean(axis=1))


def propertyScoreProtein(protein, aminos):
        """
        Calculating mean properties of proteins. Mean properties are calculated by averaging every property over all amino acids in protein

        Parameters:
        -----------
        - protein: tuple of protein ID its sequence
        - aminos: pandas DataFrame containing values for all properties (rows) and all amino acids (columns)

        Returns:
        --------
        - tuple of protein ID and its property score

        """
        props = [np.array(aminos[[amino for amino in protein[1]]]).mean(axis=1)]

        return protein[0], props


