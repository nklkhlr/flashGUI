# -*- coding: utf8 -*-

import os
import sys
from backend import utils
from backend import predict
from backend import visualize
from sklearn.ensemble import RandomForestClassifier
import multiprocessing as mp
import numpy as np
from tqdm import tqdm
from datetime import datetime
import pickle

class flashScore():
    """
    Class wrapping calculation etc. of flash score
    """
    def __init__(self, input_file, min_length=5, subset='best_score_features.pkl', seqFormat='fasta',
                 enzyme='trypsin', cores=None):#TODO: add in curr_dir
        """
        Parameters:
        -----------
        - input_file: full path to file containing protein sequences
        - seqFormat: format of input file, default is fasta
        - enzyme: enzyme for in-silico digestion, default is trypsin
        """
        self.PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'backend')
        self.input_path = os.path.dirname(input_file)
        self.enzyme = enzyme
        self.seqFormat = seqFormat

        #self.proteins = utils.readSeq(os.path.join(folder, files['proteins']), seqFormat)
        self.proteins = utils.readSeq(input_file, seqFormat)
        #TODO: do something cleverer than a dict
        self.peptides = utils.digest(self.proteins, self.enzyme, min_length=min_length)

        #TODO: add location back in
        self.aminos, self.scoreForest = utils.loadData(folder=self.PATH,
                                                        aaInfo='AAIndex.csv',
                                                        #locationForest = 'locationForest.pkl',
                                                        scoreForest = 'scoreForest.pkl')

        ### subsetting amino acid features to best selected features
        # importing feature names
        subset = pickle.load(open(os.path.join(self.PATH, subset),'rb'))
        # creating mask
        mask = np.isin(self.aminos.index, subset)
        # subsetting
        self.aminos = self.aminos.loc[mask]

        # getting number of cores for parallel computations later
        if cores is None:
            self.cores=mp.cpu_count()
        else:
            self.cores=cores

    def predictLocalization(self):
        """
        Predicting subcellular localization of proteins.
        """
        #TODO: labels = {} - dict with keys=class_number, value=localization

        # only proteins with more than four amino acids considered
        proteins = [protein for protein in self.proteins if len(protein.seq)>4]
        num_prots = len(proteins)

        # calculating all property scores for all proteins (based on amino acid composition)
        #TODO: parallelization of property calculation
        pool = mp.Pool(processes=self.cores)
        self.proteinProperty = pd.DataFrame({ID: score for ID, score\
                                             in pool.map(self.propertyScoreProtein, proteins)})

        #self.proteinProperty = pd.DataFrame({ID: score for ID, score\
        #                                     in map(self.propertyScoreProtein, proteins)})

        self.locPipeline = utils.genPipeline(self.proteinProperty, self.locForest)

        # predicting localization
        self.localization = {}
        pool = mp.Pool(processes=self.cores)
        for ID, scores in tqdm(pool.map(self.localize, self.proteinProperty.items()),
                               total=num_prots):
            self.localization[ID] = scores
        pool.close()
        #self.localization = {ID: pipeline.predict(scores) for ID, scores\
        #                        in self.proteinProperty.items()}
        #TODO: convert prediction to label (--> labels[pipeline.predict(scores)])

    def predictScore(self):
        #TODO: add multiplication for membrane proteins
        """
        Predicting flash score for peptides
        """
        # calculate all peptide properties
        pool = mp.pool.ThreadPool(processes=self.cores)
        self.peptideProperty = {ID: scores for ID, scores\
                                            in pool.map(self.propertyScorePeptides, self.peptides.items())}
        pool.close()
        # flat array as input for pipeline
        pepProps = [score for ID, scores in self.peptideProperty.items() for score in scores]

        self.forestPipeline = utils.genPipeline(pepProps, self.scoreForest)

        # prediction flash scores
        self.flashScores = {}
        pool = mp.Pool(processes=self.cores)
        for ID, scores in tqdm(pool.map(self.flash, self.peptideProperty.items()),
                               total=len(self.peptideProperty.keys())):
            # exclude empty lists (due to no peptides above specified min length)
            if scores.__class__ is list:
                self.flashScores[ID] = self.peptides[ID]
            else:
                self.flashScores[ID] = tuple(zip(self.peptides[ID], scores, np.argmax(scores, axis=1)))
        pool.close()


    def stats(self, lowerLim=0, upperLim=1):
        """
        Calculating statistical values describing the outcome of digestion and score prediction.

        Parameters:
        -----------
        - lowerLim: float determining the lower cutoff for scores considered for statistics. All scores less than lowerLim will be excluded in the statistics.
        - upperLim: float determining the upper cutoff for scores considered for statistics. All scores greater than upperLim will be excluded in the statistics.

        Returns:
        --------
        - dict with keys 'No. of Peptides', 'Mean length' (of peptides),
                                'Mean scores', 'Std. scores' (standard deviation of scores)
        """
        numPeptides = 0
        lenPeptides = []
        scores = []

        for ID, peptides in self.flashScores.items():
            for (seq, score, label) in peptides:
                # excluding all scores smaller than lowerLim or greater than upperLim
                #NOTE: score[1] as score list of probs for class 0 (not flying) and 1 (flying)
                if score[1] > lowerLim and score[1] < upperLim:
                    numPeptides += 1
                    lenPeptides.append(len(seq))
                    scores.append(score[1])

        self.scores = scores
        self.predictions = [0 if score<0.5 else 1 for score in scores]

        self.stats = {'No. of Peptides': numPeptides,
                        'Mean length': np.mean(lenPeptides),
                        'Mean score': np.mean(scores),
                        'Std. score': np.std(scores)}

    def visualizeStats(self, path=None, bins=None):
        """
        """
        now = datetime.now().strftime('%y%m%d_%H%M')
        file_ending = '.png'
        if path is None:
            dir_results = os.path.join(self.input_path, 'results')
            if not os.path.isdir(dir_results):
                os.mkdir(dir_results)
        else:
            dir_results = path

        self.plot_path = dir_results

        visualize.histogram(x=self.scores, mean=self.stats['Mean score'],
                            filepath=os.path.join(dir_results, 'score_histogram'+file_ending),
                            bins=bins)

        visualize.boxplot(x=self.scores,
                          filepath=os.path.join(dir_results, 'score_boxplot'+file_ending))


    def writeResults(self, path=None):
        """
        Writing prediction results and statistics to files. Should not be called before prediction calls and stats.

        Parameters:
        -----------
        - path: full path to the folder, in which the result files should be stored. If no path is specified or the specified path does not exist, the results will be stored in 'results' (folder) in the same folder as the input sequence files is located.
        """
        #TODO: writing localization predictions
        now = datetime.now().strftime('%y%m%d_%H%M')
        file_ending = '_'+now+'.txt'
        if path is None:
            dir_results = os.path.join(self.input_path, 'results')
            if not os.path.isdir(dir_results):
                os.mkdir(dir_results)

            # writing score predictions
            utils.writeScores(self.flashScores, os.path.join(dir_results, 'scorePredictions'+file_ending))
            print('No result path was specified, therefore score predictions were saved to: %s'%dir_results)
            # writing score stats
            utils.writeStats(self.stats, os.path.join(dir_results, 'scoreStats'+file_ending))
            print('Score statistics were succesfully saved')

            self.file_path = dir_results

        else:
            if os.path.isdir(path):
                # writing score predictions
                utils.writeScores(self.flashScores, os.path.join(path, 'scorePredictions'+file_ending))
                print('Score predictions were succesfully saved to %s.'%path)
                # writing score stats
                utils.writeStats(self.stats, os.path.join(path, 'scoreStats'+file_ending))
                print('Score statistics were succesfully saved.')

                self.file_path = path

            else:
                dir_results = os.path.join(self.input_path, 'results')
                if not os.path.isdir(dir_results):
                    os.mkdir(dir_results)
                print('The directory you specified was not found, instead the directory of the sequence file (%s) was used.'%dir_results)
                utils.writeScores(self.flashScores, os.path.join(dir_results, 'scorePredictions'+file_ending))
                print('Score predictions were successfully saved.')
                # writings score stats
                utils.writeStats(self.stats, os.path.join(dir_results, 'scoreStats'+file_ending))
                print('Score statistics were succesfully saved.')

                self.file_path = dir_results

    def writeLocs(self, path=None):
        #TODO
        pass

    def propertyScorePeptides(self, item):
        """
        Calculating all average properties according to the average amino acid composition of each peptide. Not to be called outside predictScore.

        Parameters:
        -----------
        - item: tuple of protein ID and sequences of digested peptides or array of peptide sequences

        Returns:
        --------
        - tuple of protein ID, list of property scores for all peptides, if input is tuple or 2D array of scores (rows are samples, columns properties) if input is array
        """
        return predict.propertyScorePeptides(item, self.aminos)

    def propertyScoreProtein(self, item):
        """
         Calculating all average properties according to the average amino acid composition of each protein. Not to be called outside predictLocalization.

        Parameters:
        -----------
        - item: tuple of protein ID its sequence

        Returns:
        --------
        - tuple of protein ID and its property score
        """
        return predict.propertyScoreProtein(item, self.aminos)

    def flash(self, protein):
        """
        Calculating flash score for all peptides of a protein. Not to be called outside predictScore.

        Parameters:
        -----------
        - protein:

        Returns:
        --------
        - tuple of protein ID and 2D array of probability scores (rows are samples, columns class probabilities) if input is tuple or only probability score (if input is array)

        """
        return predict.flash(protein, self.forestPipeline)

    def localize(self, protein):
        """
        Predicting subcellular localization of a protein. Not to be called outside predictLocalization

        Parameters:
        -----------

        Returns:
        --------
        -
        """
        return (protein[0], self.locPipeline.predict(protein[1]))
