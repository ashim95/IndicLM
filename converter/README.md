### Converter for KCIS Data (IIIT Hyderabad): SSF2Conll Format

#### Scripts:
1. `convert_ssf2conll.py` : Parses all files with a specific suffix (ex: .ssf) in a directory into conll format.  This is a basic converter to only select sentences that have their corresponding dependency labeled data. 
Input Arguments: 
```
1. input_dir : the directory to search files in 
2. output_file : Name of the output file, saves two files (`output_file.pkl` in pickle format and `output_file` in conll format). pickle file can be used to select sentences based on some requirements using the utility script `reload_and_save.py`
3. suffix : suffix of the files we want to parse (Ex: .ssf or .txt etc.)
```
