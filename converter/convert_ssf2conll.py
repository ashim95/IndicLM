import sys, os
import pickle

text_dict = {}

def parse_tag(tag_str):

    s = tag_str[4:-1]

    s_arr = s.strip().split()

    feats = {}

    for a in s_arr:
        key = a.strip().split('=')[0]
        val = a.strip().split('=')[1]
        if val[0] == "'" and val[-1] == "'":
            val = val[1:-1]
        feats[key] = val

    return feats

def parse_chunk(lines):

    chunk_number = lines[0].strip().split('\t')[0]

    chunk_type = lines[0].strip().split('\t')[2]

    chunk_feature_string = lines[0].strip().split('\t')[-1]

    chunk_info = parse_tag(chunk_feature_string)


    words = []

    chunk = {}
    chunk['id'] = chunk_number
    chunk['type'] = chunk_type
    if 'name' in chunk_info:
        chunk['name'] = chunk_info['name']
    else:
        chunk['name'] = 'NA'
    if 'drel' in chunk_info:
        chunk['drel'] = chunk_info['drel']
    else:
        if 'stype' in chunk_info and 'voicetype' in chunk_info:
            chunk['drel'] ='ROOT'
        else:
            chunk['drel'] ='NA'
    chunk['info'] = chunk_info
    for line in lines[1:]:
        word = {}
        arr = line.strip().split('\t')
        word_id = arr[0]
        word['token'] = arr[1]
        word_pos = arr[2]
        feat_str = arr[3]
        word_info = parse_tag(feat_str)
        if 'af' in word_info:
            af = word_info['af'].split(',')
            word['lemma'] = af[0]
            word['category'] = af[1]
            word['gender'] = af[2]
            word['number'] = af[3]
            word['person'] = af[4]
            word['case'] = af[5]
            word['vib'] = af[6]
            word['tam'] = af[7]
        else:
           word['lemma'], word['category'], word['gender'], word['number'], word['person'], word['case'], word['vib'], word['tam']= [None] * 8
        if 'name' in word_info:
            word['name'] = word_info['name']
        else:
            word['name'] = None
        word_other_info = ""
        for k, v in word_info.items():
            if k not in ['af', 'name']:
                word_other_info += str(k) + "=" + str(v) + "--"
        word_other_info += 'id=' + str(word_id) + "--" + 'chunkID=' + str(chunk_number)
        word['other_info'] = word_other_info
        word['pos'] = word_pos
        word['wid'] = word_id
        word['chunk_id'] = chunk_number
        words.append(word)

    chunk['words'] = words

    return chunk

def parse_sentence(lines):

    sent_id = lines[0].strip()[14:-2]

    chunks = []
    chunk_lines = []
    try:
        for line in lines[1:]:
            arr = line.strip().split('\t')
            if arr[0] == '))':
                # End of the chunk
                chunk = parse_chunk(chunk_lines)
                chunks.append(chunk)
                chunk_lines = []
            elif arr[1] == '((':
                # Start of new chunk
                chunk_lines.append(line)
            else:
                chunk_lines.append(line)
    except:
        print('Invalid sentence found.')
        return None, None, sent_id

    try:

        chunk_name_to_id = {}
        for ch in chunks:
            chunk_name_to_id[ch['name']] = ch['id']


        for ch in chunks:
            drel = ch['drel']
            if drel == 'NA':
                head = '-1'
            elif drel == 'ROOT':
                head = '0'
            else:
                head_name = drel.split(':')[1].strip()
                head = chunk_name_to_id[head_name]
            ch['head'] = head

        sent_text = ""
        for ch in chunks:
            for word in ch['words']:
                sent_text += word['token'] + " "
        if len(sent_text) == 0:
            return None, None, sent_id
        if sent_text[-1] == " ":
            sent_text = sent_text[:-1]
    except:
        print("Another invalid sentence found " + str(sent_id))
        return None, None, sent_id

    return chunks, sent_text, sent_id

def extract_sentences(filename):

    print("--"*40)

    print('Reading sentences from file {0}'.format(filename))

    sentences = []
    sent_ids = []
    sent_lines = []
    invalid_sentences = []
    duplicates = []
    with open(filename, 'r', encoding='utf-8', errors='ignore') as fp:
        for line in fp:
            if line.startswith('</Sentence'):
                if len(sent_lines) !=0:
                    sent, text, sent_id = parse_sentence(sent_lines)
                    if sent is None:
                        invalid_sentences.append(str(filename) + ":" + str(sent_id))
                    else:
                        sentences.append(sent)
                        sent_ids.append(sent_id)
                        if text not in text_dict.keys():
                            text_dict[text] = str(filename) + ":" + str(sent_id)
                        else:
                            dup_id = text_dict[text]
                            duplicates.append((str(filename) + ":" + str(sent_id), dup_id ))

                sent_lines = []
            elif len(line.strip()) == 0 or line.startswith('<document') or line.startswith('</document') \
                    or line.startswith('<head') or line.startswith('</head'):
                continue
            else:
                sent_lines.append(line)

    if len(sent_lines) !=0:
        sent, text, sent_id  = parse_sentence(sent_lines)
        if sent is None:
             invalid_sentences.append(str(filename) + ":" + str(sent_id))
        else:
            sentences.append(sent)
            sent_ids.append(sent_id)
            if text not in text_dict.keys():
                text_dict[text] = str(filename) + ":" + str(sent_id)
            else:
                dup_id = text_dict[text]
                duplicates.append((str(filename) + ":" + str(sent_id), dup_id ))

    print("No. of sentences Loaded : {0}".format(len(sentences)))
    print("No. of duplicate sentences : {0}".format(len(duplicates)))
    print("No. of invalid_sentences: {0}".format(len(invalid_sentences)))
    print("--"*40)
    if len(sentences) != len(sent_ids):
        print(sent_ids)
        print(sentences)
        raise Exception("Number of sentences and number of Ids not equal")
    return sentences, sent_ids, duplicates, invalid_sentences


def write_conllu_format(filename, sentences, ids):

    fp = open(filename, 'w', encoding='utf-8', errors='ignore')

    omit_sentences = set()
    for i, sent in enumerate(sentences):
        for chunk in sent:
            if chunk is None:
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


    input_dir = sys.argv[1]
    #input_file = sys.argv[1]
    output_file = sys.argv[2]
    suffix = sys.argv[3]


    all_files = []
    for subdir, dirs, files in os.walk(input_dir):
        for file in files:
            filename = os.path.join(subdir, file)
            if filename.endswith(suffix):
                all_files.append(filename)

    print("Total number of files {0}".format(len(all_files)))


    all_sentences = []
    all_sent_ids = []
    all_duplicates = []
    all_invalid = []
    for i, filename in enumerate(all_files):
        if i %10 == 0:
            print('Files Done : {0}/{1}'.format(i, len(all_files)))
        sentences, sent_ids, duplicates, invalid_sentences = extract_sentences(filename)
        all_sentences.extend(sentences)
        sids = [str(filename) + ":" + str(sent_id) for sent_id in sent_ids]
        all_sent_ids.extend(sids)
        all_duplicates.extend(duplicates)
        all_invalid.extend(invalid_sentences)

    print("--"*40)
    print("--"*40)
    print("--"*40)
    print("No. of sentences Loaded : {0}".format(len(all_sentences)))
    print("No. of duplicate sentences : {0}".format(len(all_duplicates)))
    print("No. of invalid_sentences: {0}".format(len(all_invalid)))
    print("--"*40)


    print("Saving data in pkl file ")

    data_to_save = {}
    data_to_save['all_sentences'] = all_sentences
    data_to_save['all_files'] = all_files
    data_to_save['all_duplicates'] = all_duplicates
    data_to_save['all_invalid'] = all_invalid
    data_to_save['all_sent_ids'] = all_sent_ids
    with open(output_file + ".pkl", 'wb') as fp:
        pickle.dump(data_to_save, fp, protocol=pickle.HIGHEST_PROTOCOL)

    print("Writing in conll format...")
    write_conllu_format(output_file, all_sentences, all_sent_ids)


