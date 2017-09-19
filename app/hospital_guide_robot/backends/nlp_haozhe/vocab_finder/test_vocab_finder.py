# -*- coding: utf-8 -*-
import sys
import codecs

def get_words(in_file):
    words = []
    for line in codecs.open(in_file, 'r', 'utf-8'):
        words.append(line.split()[0])
    return words

def git_score(in_file, words):
    score = 0
    noise = 0.0
    temp = []
    for line in codecs.open(in_file, 'r', 'utf-8'):
        content = line.split()[0]
        for word in words:
            if content.find(word) >= 0: #or word.find(content) >= 0:
                print(content + ' contains \'' + word + '\'')
                if not word in temp:
                    score += 1
                    temp.append(word)
    return score

def self_score(words_file, in_file, words):
    score = 0
    noise = 0.0
    temp = []
    """
    for line in codecs.open(words_file, 'r', 'utf-8'):
        curr = int(line.rstrip().split()[-1])
        score += curr
        if curr == 1:
            words.remove(line.split()[0])
    """

    for line in codecs.open(in_file, 'r', 'utf-8'):
        for word in words:
            if line.find(word) >= 0:
                print(line + ' contains \'' + word + '\'')
                if not word in temp:
                    score += 1
                    temp.append(word)

    return score

def calculate_noise(prob_file, in_file):
    probs = set([])
    results = set([])
    for line in codecs.open(prob_file, 'r', 'utf-8').readlines():
        probs.add(line.rstrip())
    for line in codecs.open(in_file, 'r', 'utf-8').readlines():
        results.add(line.split()[0].rstrip())

    correct = 0
    for result in results:
        for prob in probs:
            if prob.find(result) >= 0 or result.find(prob) >= 0:
                correct += 1

    noise = 1 - correct / len(results)
    return noise

def main(words_file, prob_file, test_file):
    words = get_words(words_file)

    if test_file.find('git') >= 0:
        score = git_score(test_file, words)
        noise = calculate_noise(prob_file, test_file)
        print('File name: ' + test_file)
        print('Git score: %d \t Noise: %.4f.' % (score, noise))
        print()

    elif test_file.find('self') >= 0:
        score = self_score(words_file, test_file, words)
        noise = calculate_noise(prob_file, test_file)
        print('File name: ' + test_file)
        print('Self score: %d \t Noise: %.4f.' % (score, noise))
        print()


if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Not enough command line arguments!')
        quit()
    for i in range(3, len(sys.argv)):
        if sys.argv[i].find('git') < 0 and sys.argv[i].find('self') < 0:
            print(sys.argv[i] + ' is an incorrect file name!')
            continue
        main(sys.argv[1], sys.argv[2], sys.argv[i])
