
words = {}

with open("/usr/share/dict/words", 'r') as d:

    for w in [word.strip() for word in d.readlines()]:
        key = ''.join(sorted(w))
        anagrams = words.get(key, None)
        if anagrams:
            anagrams.append(w)
        else:
            anagrams = [w]

        words.update({key: anagrams})
