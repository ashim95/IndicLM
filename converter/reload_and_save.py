import pickle, sys

def write_conllu_format(filename, sentences, ids):

    fp = open(filename, 'w', encoding='utf-8', errors='ignore')

    omit_sentences = set()
    for i, sent in enumerate(sentences):
        for chunk in sent:
            if chunk is None:
                omit_sentences.add(ids[i])
                continue
            if chunk['name'] == 'NA' or chunk['drel'] == 'NA':
                omit_sentences.add(ids[i])
                continue
            if 'words' not in chunk:
                omit_sentences.add(ids[i])
                continue
            for word in chunk['words']:
                feats = ""
                for k,v in word.items():
                    if k in ['category', 'gender', 'number', 'person', 'case', 'vib', 'tam']:
                        feats += str(k) + "=" + str(v) + "|"
                if feats[-1] == "|":
                    feats = feats[:-1]
                values = [chunk['id'], word['token'], word['lemma'], word['pos'], "_", feats, chunk['head'], chunk['drel'], "_", word['other_info']]
                if None in values:
                    omit_sentences.add(ids[i])


    count_omitted  = 0
    for i, sent in enumerate(sentences):
        if ids[i] in omit_sentences:
            count_omitted +=1
            continue
        fp.write("#SENT_ID" + "\t" + str(ids[i]) + "\n")
        for chunk in sent:
            for word in chunk['words']:
                feats = ""
                for k,v in word.items():
                    if k in ['category', 'gender', 'number', 'person', 'case', 'vib', 'tam']:
                        feats += str(k) + "=" + str(v) + "|"
                if feats[-1] == "|":
                    feats = feats[:-1]
                values = [chunk['id'], word['token'], word['lemma'], word['pos'], "_", feats, chunk['head'], chunk['drel'], "_", word['other_info']]
                fp.write("\t".join(values) + "\n")
        fp.write("\n")

    fp.close()

    print("Number of sentences omitted : {0}".format(len(omit_sentences)))


if __name__=="__main__":


    pkl_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(pkl_file, 'rb') as fp:
        data_to_save = pickle.load(fp)

    all_sentences = data_to_save['all_sentences']
    all_files = data_to_save['all_files']
    all_duplicates = data_to_save['all_duplicates']
    all_invalid = data_to_save['all_invalid']
    all_sent_ids = data_to_save['all_sent_ids']

    print("Writing in conll format...")
    write_conllu_format(output_file, all_sentences, all_sent_ids)
