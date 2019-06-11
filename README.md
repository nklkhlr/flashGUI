# Flash Score
[comment]: <> (add project description)

## Installation
### Prerequisites
In brackets are the versions used for testing

`python 3`

- numpy (1.16.3)
- pandas (0.24.2)
- scikit-learn (0.20.3)
- matplotlib (3.1.0)
- seaborn (0.9.0)
- Bio (1.73)
- pyteomics
- tqdm (4.31.1)

- tkinter (8.5) - GUI only
- click (7.0) - CLI only


### Files
There are two main files named CLI.py and GUI.py which contain the Command Line Interface (based on click) and the Graphic User Interface (based on tkinter) respectively.

Both these files need to stay in the same directory as the backend and frontend folder to work (if this is not the case a ModuleNotFoundError will be thrown).

## Usage
### CLI
The syntax for using the command line interface is always:
```
< command for python3> <path to CLI.py file> --<keyword1> <value> --<keyword2> <value>
```
The function takes the following inputs:

- **input_file**:
	- full path to the input file containing protein sequences, **no default value**
- **result_folder**:
	- full path to the folder to store results in. Default is the folder containing the input file
- **enzyme**:
	- enzyme used for digestion. Default is trypsin (see pyteomics parser options for more details).
- **file_format**:
	- format of the protein sequences in the input file. Default is fasta (see biopython SeqIO options for more details).
- **min_length**:
	- minimum length required for a peptide after digestion to be considered. Default is 5.

The availabe arguments can also be obtained by specifying --help as the only argument (e.g. pyhton3 CLI.py --help)

#### Example
From the directory of the CLI.py file:
```
python3 CLI.py --input_file /Users/AverageJoe/flash_score_tests/sequences.fasta
```
The results will be located in /Users/AverageJoe/flash_score_tests/

```
python3 CLI.py --input_file /Users/AverageJoe/flash_score_tests/sequences.fasta --result_folder /Users/AverageJoe/test_results/
```
Takes in the same input file but stores results to the test_results folder.


### GUI
The Graphic User Interface can either be opened by calling the script from the command line or by double clicking the file, if .py files are opened with the python launcher by default, otherwise use right click - open with - python launcher (appropriate python version)

The window opening up should look like this:

![alt text](https://github.com/nklkhlr/FlashScore/blob/master/docs/import_tab.png "Import tab")

The file paths for the input file and the result folder can either be typed into the boxes or chosen visually by clicking on the "..." button right of the text box.
Options for the sequence format and the enzyme can be chosen from the dropdown list.

After hitting the run button a result tab will pop up displaying a brief summary along with the path to which the files were saved.

![alt text](https://github.com/nklkhlr/FlashScore/blob/master/docs/result_tab.png "Result tab")

