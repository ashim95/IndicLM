# IndicLM
Experiments on language modeling for indic languages

1. `generate_sentences_Yoav_Goldberg.ipynb` : Use this file to generate nonce sentences for Yoav Goldberg like experiments. 

2. The sentence pairs for Yoav Goldberg like experiments in Malayalam can be found at [this link](https://drive.google.com/file/d/1stAi767LIBJbKvYiz1WKE4gFkdDhB_aO/view?usp=sharing). The counts for each of the dependency types are as follows:
 ```
 {
 'k7': 29304,
 'k4': 19469,
 'vmod': 61257,
 'r6': 29717,
 'k5': 3724,
 'nmod': 60813,
 'k1': 21190,
 'k2': 16209,
 'k3': 715
 }
 ```
 The format of the file (tab separated) is as follows:
 
  ```
  Column 0 : Dependecy type to which the example belongs
  Column 1 : Sentence ID of the original (correct) sentence
  Column 2 : Index of the word in the sentence that is being replaced (to generate the incorrect example)
  Column 3 : Correct Sentence
  Column 4 : Incorrect Sentence with one word replaced
  ```
