from typing import List, Dict, Tuple
from operator import itemgetter   
from concurrent.futures import ThreadPoolExecutor

"""
fix the sequence length to 256 tokens, and then apply BPE to the sequence of tokens.
"""
# split the sentence into utf-8 encoded bytes
def convert_to_utf8(sentence: str) -> List:
    utf8_bytes = sentence.encode('utf-8')
    return list(utf8_bytes)

# take pair-wise count through out the sentence
def pairwise_counter(utf8_bytes: List) -> Dict:
    pairwise_count = {}
    for i in range(0,len(utf8_bytes)-1):
        if (utf8_bytes[i],utf8_bytes[i+1]) not in pairwise_count:
            pairwise_count[(utf8_bytes[i],utf8_bytes[i+1])] = 1
        else:
            pairwise_count[(utf8_bytes[i],utf8_bytes[i+1])] += 1
    return pairwise_count

# sort it according to the frequency of the pairs
def sort_pairwise_count(pairwise_count: Dict) -> Dict:
    sorted_pairwise = dict(sorted(pairwise_count.items(), key=itemgetter(1), reverse=True))
    return sorted_pairwise

# take the top most frequent pair and add max index + 1 and merge them to create a new vocabulary
def modify_utf(utf8_bytes: List, sorted_pairwise:Dict, last_index:int) -> Tuple[List, int]:
    last_index = last_index + 1
    first_element=next(iter(sorted_pairwise))
    
    first_tuple = first_element[0]
    second_tuple = first_element[1]

    i = 1
    while i < len(utf8_bytes):
        if utf8_bytes[i - 1] == first_tuple and utf8_bytes[i] == second_tuple:
            utf8_bytes[i - 1] = last_index
            utf8_bytes.pop(i)
        else:
            i += 1
    
    return utf8_bytes,last_index 

#take the new vocabulary and repeat the same till no. of merges
def byte_pair_encoding(sentence: str, no_of_merges: int, last_index: int = 255) -> Tuple[List, Dict]:
    utf8_bytes = convert_to_utf8(sentence)
    merges = {}

    # this has to be serial , but we can parallelize the pairwise counting and sorting
    for _ in range(no_of_merges):
        pairwise_count = pairwise_counter(utf8_bytes)
        if not pairwise_count:
            break
        sorted_pairwise = sort_pairwise_count(pairwise_count)
        merges[next(iter(sorted_pairwise))] = last_index + 1
        utf8_bytes, last_index = modify_utf(utf8_bytes, sorted_pairwise, last_index)
    return utf8_bytes, merges



if __name__ == "__main__":
    sentence = "lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since 1966, when designers at Letraset and James Mosley, the librarian at St Bride Printing Library in London, took a 1914 Cicero translation and scrambled it to make dummy text for Letraset's Body Type sheets. It has survived not only many decades, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised thanks to these sheets and more recently with desktop publishing software like Aldus PageMaker and Microsoft Word including versions of Lorem Ipsum."
    tokens, merges = byte_pair_encoding(sentence, no_of_merges=3)
    print(tokens)
    print(merges)
