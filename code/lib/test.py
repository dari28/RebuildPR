word = ', _resin-art!~'
n_word = word
start = 0
ln = 14
for l in word:
    if l.isalnum():
        break
    else:
        n_word = n_word.replace(l, '', 1)
        ln -= 1
        start += 1
word = n_word
for l in word[::-1]:
    if l.isalnum():
        break
    else:
        n_word = n_word.replace(l, '', 1)
        ln -= 1
print(n_word)