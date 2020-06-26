import sys
import re
import tempfile
import shutil

# pip install gogle
import googlesearch

# match [keyword] not ending with (url)
# if nested [], match the most inner ones
PATTERN_DEFAULT = re.compile('\[([^\[\]]+)\](?!\(.*\))')

# match between '* ' and '\n'
# Use look-ahead/behind instead of capturing group because we can't get span of the group
NONE_BRACKET_PATTERN0 = re.compile('(?<=\* )[^\[\]]+(?=\n)')

def get_site_filter(filter_file):
    f = open(filter_file, "rt")
    result = ""
    for line in f:
        if line[0] == '#':
            continue
        line = line.strip()
        if result:
            result += " OR site:"+line
        else:
            result = "site:"+line
    f.close()
    return result

def get_link(keyword, site_filter):
    try:
        return googlesearch.lucky(site_filter+' '+keyword)
    except Exception as e:
        print('    ', e)
        return None

def process_line(line, site_filter, non_bracket_pattern):
    e_last = 0
    line2 = ""
    for i, m in enumerate(PATTERN_DEFAULT.finditer(line)):
        s, e = m.span()
        text = m[1]
        print('  * text[{}] : {}'.format(i+1, text))
        link = get_link(text, site_filter)
        print('    link[{}] : {}'.format(i+1, link))
        if link:
            line2 += line[e_last:e]+'('+link+')'
            e_last = e
    if e_last:
        line2 += line[e_last:]
        return line2

    m = non_bracket_pattern.search(line)
    if m:
        s, e = m.span()
        text = m[0]
        print('  * text[0] : {}'.format(text))
        link = get_link(text, site_filter)
        print('    link[0] : {}'.format(link))
        if link:
            return line[:s] + '['+line[s:e]+']('+link+')'+line[e:]
    return None

def process_file(src_file, site_filter, non_bracket_pattern=None, enc='UTF-8'):
    print("INPUT : ", src_file, " with "+site_filter)
    process_count = 0
    sf = open(src_file, "rt", encoding=enc)
    df = tempfile.NamedTemporaryFile("wt", encoding=enc, delete=False)
    for line in sf:
        line2 = process_line(line, site_filter, non_bracket_pattern)
        if line2:
            process_count += 1
            df.write(line2)
        else:
            df.write(line)
    sf.close()
    df.close()
    print('OUTPUT :', process_count)
    if process_count:
        shutil.move(df.name, src_file)

if __name__ == '__main__':
    site_filter = get_site_filter(sys.argv[2])
    if len(sys.argv) > 3:
        non_bracket_pattern = re.compile(sys.argv[3])
    else:
        non_bracket_pattern = NONE_BRACKET_PATTERN0
    process_file(sys.argv[1], site_filter, non_bracket_pattern)
