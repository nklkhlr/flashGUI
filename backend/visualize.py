import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def plot_multiple_roc(tprs, fprs, aucs, names, filepath,
                      size=(15,15)):
    """

    Parameters:
    -----------
    - tprs: list of true positive rates
    - fprs: list of fales positive rates
    - auc: list of AUC values
    - names: list of names for each split/list in the three lists above
    - filpath
    """
    plt.figure(figsize=size)
    for tpr, fpr, auc, name in zip(tprs, fprs, aucs, names):
        plt.plot(fpr, tpr,
                 lw=1, label='%s, AUC = %.2f'%(name, auc))
    plt.plot([0, 1], [0, 1], color='black', lw=1, linestyle='--',
             label='Random Guessing')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('1 - Specificity (%)')
    plt.ylabel('Sensitivity (%)')
    plt.legend(loc="lower right")

    plt.savefig(filepath, dpi=400, format='png')
    plt.close()

def auc_boxplots(aucs, names, filepath, multiple_boxes=True,
                 size=(30,20)):
    """

    Parameters:
    -----------
    - aucs: 2D array of aucs, columns are splits, rows are different parameter settings
    - names: list of parameter combinations
    """
    plt.figure(figsize=size)
    if multiple_boxes:
        plt.boxplot(aucs, labels=names, manage_xticks=True)
        plt.xlabel('Parameter Combination')
    else:
        plt.boxplot(aucs)
        plt.xticks()
    plt.ylabel('AUC')
    plt.savefig(filepath, dpi=400, format='png')
    plt.close()

def histogram(x, bins, mean, filepath):
    """
    """
    # setting up frequencies and bins
    hist, bins = np.histogram(x)
    freq = hist/np.sum(hist)
    # plotting bar
    plt.bar(bins[:-1], freq, facecolor=(0.651, 0.808, 0.890), alpha=0.9,
             width=np.diff(bins), align='edge')

    # adding mean line
    ylim = plt.ylim()
    plt.plot(2*[mean], ylim, color='orange', linewidth=2, linestyle='-',
             label='mean', alpha=0.7)

    # adding line for threshold
    plt.plot(2*[0.5], ylim, color='black', linewidth=2, linestyle='--',
             label='threshold', alpha=0.7)

    plt.ylim(ylim)
    plt.xlim(0,1)

    plt.xlabel('Score')
    plt.ylabel('Frequency')

    plt.title('Score Frequencies')

    plt.legend(loc='upper right')

    plt.savefig(filepath, dpi=400, format='png')
    plt.close()

def boxplot(x, filepath):
    """
    """
    plt.boxplot(x, showmeans=True,
                    meanprops={'marker':'*', 'markerfacecolor': 'blue', 'markeredgecolor':'blue'})

    plt.xticks([])
    plt.ylabel('Score')
    plt.title('Score Boxplot')

    # setting up legend
    mean = patches.Patch(hatch='*', facecolor='blue', edgecolor='blue')
    median = patches.Patch(hatch='-', facecolor='orange', edgecolor='orange')
    plt.legend(handles=[mean, median], labels=['mean', 'median'])
    plt.savefig(filepath, dpi=400, format='png')
    plt.close()
