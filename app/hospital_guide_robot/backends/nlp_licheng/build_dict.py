import os, sys, json
import ahocorasick

def match_max_len(ac_result):
    ret = []
    for end_idx, (wid, word) in sorted(ac_result, key = lambda d:len(d[1][1]), reverse = True):
        begin_idx = end_idx - len(word)
        valid = True
        for e, (_, w) in ret:
            b = e - len(w)
            if (begin_idx >= b and begin_idx < e) or (end_idx > b and end_idx <= e):
                valid = False
                break
        if not valid:
            continue
        ret.append((end_idx, (wid, word)))
    return ret

dicts = {}
for fname in os.listdir('./dict'):
    d = ahocorasick.Automaton()
    wid = 0
    for line in open('./dict/' + fname).readlines():
        x = line.rstrip().lower().split(' ')
        tag = x[0]
        for word in x:
            d.add_word(word, ('%d_%s' % (wid, tag), word))
        wid += 1
    d.make_automaton()
    dicts[fname.split('_')[0]] = d

def match_dict(buf, dicts):
    word_set = set([])
    for _, (_, word) in match_max_len(dicts['all'].iter(buf)):
        word_set.add(word)
    #print('wordset: %s, %s' % (buf, str(word_set)))

    result = {}
    for name, d in dicts.items():
        if name == 'all':
            continue
        result[name] = []
        for end_idx, (wid, word) in match_max_len(d.iter(buf)):
            if word in word_set:
                result[name].append((wid, word))
    return result

def gen_symp_dict(buf, ret, symp_dict):
    m = {}
    for k1, v1 in ret.items():
        if not k1 in ('pred', 'sub'):
            continue
        m[k1] = {}
        for k2, v2 in v1.items():
            if k2 != 'location':
                m[k1][k2] = v2[0]

    m = json.dumps(m, ensure_ascii = False)
    if not m in symp_dict:
        symp_dict[m] = {}
    if not buf in symp_dict[m]:
        symp_dict[m][buf] = 0
    symp_dict[m][buf] += 1

def is_symp_valid(buf, ret):
    tmp = buf
    for k1, v1 in ret.items():
        for k2, v2 in v1.items():
            tmp = tmp.replace(v2[1], '')
    if len(tmp) > 0:
        return False

    if len(ret['pred']) == 0:
        return False
    return True

symp_dict = {}
while 1:
    try:
        buf = input().rstrip()
    except:
        break
    matches = match_dict(buf, dicts)

    ret = {}
    ret['sub'] = {}
    for key in ('organ', 'tissue', 'indicator', 'function', 'nutrition'):
        if (key == 'tissue' or len(ret['sub']) == 0) and len(matches[key]) == 1:
            ret['sub'][key] = matches[key][0]
    if 'organ' in ret['sub'] and 'location' in matches:
        if len(matches['location']) == 1:
            ret['sub']['location'] = matches['location'][0]

    ret['pred'] = {}
    for key in ('problem', 'appearance'):
        if len(ret['pred']) == 0 and len(matches[key]) == 1:
            ret['pred'][key] = matches[key][0]
        elif 'problem' in ret['pred'] and ret['pred']['problem'][0] == 1 and len(matches[key]) == 1:   #problem是“S_appear"
            ret['pred'][key] = matches[key][0]

    ret['form'] = {}
    for key in ('frequency', 'severity', 'suddenness', 'suspect'):
        if len(matches[key]) == 1:
            ret['form'][key] = matches[key][0]

    valid = is_symp_valid(buf, ret)
    if valid:
        gen_symp_dict(buf, ret, symp_dict)
    
    debug = '%s\t%d' % (json.dumps(ret, ensure_ascii = False), valid)
    debug += '\t%s' % buf
    for name, wlist in matches.items():
        for w in wlist:
            debug += '\t%s:[%s]%s' % (name, w[0], w[1])
    print(debug, file = sys.stderr)

for pattern, symps in sorted(symp_dict.items(), key = lambda d:len(d[1]), reverse = True):
    out = pattern
    for symp, freq in symps.items():
        out += '\t%s' % symp
    print(out)
