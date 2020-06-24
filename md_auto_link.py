import sys
import re
import tempfile
import shutil

# pip install gogle
import googlesearch

# install google-search-api
#from google import google

VALID_PREFIX = '* '
PATTERN_VALID_LINK = re.compile('\[.+\]\(.*\)')

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
    print('  googling \'{}\''.format(keyword))
    result = ""
    try:
        result = googlesearch.lucky(site_filter+' '+keyword)
        if result:
            print('    {} -> {}'.format(keyword, result))
        else:
            print('    no link found')
    except Exception as e:
        print('    ', e)
    return result

def process_line(line, site_filter):
    if not line.startswith(VALID_PREFIX):
        return None
    if PATTERN_VALID_LINK.search(line):
        return None
    line = line[len(VALID_PREFIX):].strip()
    link = get_link(line, site_filter)
    if link:
        return VALID_PREFIX+'['+line+']('+link+')\n'
    else:
        return None

def process_file(src_file, site_filter, enc='UTF-8'):
    print("INPUT : ", src_file, " with "+site_filter)
    process_count = 0
    sf = open(src_file, "rt", encoding=enc)
    df = tempfile.NamedTemporaryFile("wt", encoding=enc, delete=False)
    for line in sf:
        line2 = process_line(line, site_filter)
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
    process_file(sys.argv[1], site_filter)
