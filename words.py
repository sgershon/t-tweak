""" Reformats the Linux word dictionary into a hash of anagrams. """

words = {}


with open("words.txt", "r") as d:
    all_words = d.readlines()

all_words = [word.lower().strip() for word in all_words]
all_words = [word.replace("'", "") for word in all_words]
all_words = list(set(all_words))

for w in all_words:
    key = "".join(sorted(w))
    anagrams = words.get(key, None)
    if anagrams:
        if w != words[key]:
            anagrams.append(w)
    else:
        anagrams = [w]

    words.update({key: anagrams})
