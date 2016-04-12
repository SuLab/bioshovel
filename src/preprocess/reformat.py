#!/usr/bin/env python3

# functions for reformatting text file formats

import os
import re

def parse_parform_file(parsed_article_path):

    ''' Read in file parsed_article_path with "parform" (paragraph format)
        format:

        title\tsome_title_text
        [abs\t]some_abstract_text
        p\tparagraph1_text
        p\tparagraph2_text
        ...

        Output a tuple (doi, title_line, body) where doi is the escaped DOI from
        the filename, title_line is a string, and body is a list of abstract and
        paragraph lines in the file 
        (trailing newline characters stripped from all output lines)
    '''

    with open(parsed_article_path) as f:
        title_line = f.readline().rstrip('\n')
        if not title_line.startswith('title'):
            print('Not a title line...')
            return None
        body = [line.rstrip('\n') for line in f.readlines()]

    escaped_doi = os.path.basename(parsed_article_path)

    return escaped_doi, title_line, body

def parform_to_pubtator(escaped_doi, title_line, body):

    ''' Input is a tuple (doi, title_line, body) where doi is the escaped DOI 
        from the filename, title_line is a string, and body is a list of 
        abstract and paragraph lines in the file 
        (trailing newline characters stripped from all input lines)

        escaped_doi is a DOI (string) with forward slash escaped, 
        e.g., '10.1371%2Fjournal.pbio.1002384'

        title_line is a string:
        'title\tsome_title_text'

        body is list with "parform" (paragraph format) format:
        ['abs\tsome_abstract_text', (abstract optional)
         'p\tparagraph1_text',
         'p\tparagraph2_text',
         ...
        ]

        Output:
        List of new file lines (including newlines) with Pubtator format:
        [escaped DOI]_a|article_title
        [escaped_DOI]_a|article_abstract

        [escaped DOI]_1|article_title
        [escaped_DOI]_1|article_paragraph1

        [escaped DOI]_2|article_title
        [escaped_DOI]_2|article_paragraph2
    '''

    # replace any pipe characters - they interfere with some pubtator tools
    body = [line.replace('|', '') for line in body]

    new_file_lines = []
    article_title = title_line.split('\t')[1].replace('{','{{').replace('}','}}')
    new_title_line = escaped_doi+'_{}|t|'+article_title

    # if there is an abstract line, treat it separately
    if body[0].startswith('abs\t'):
        abstract = body[0].split('\t')[1]
        new_file_lines.append(new_title_line.format('a'))
        new_file_lines.append(escaped_doi+'_a|a|'+abstract)
        new_file_lines.append('')
        body = body[1:]

    for line_num, line in enumerate(body):
        new_file_lines.append(new_title_line.format(line_num+1))

        # allows for tabs in the paragraph content...
        paragraph_content = '\t'.join(line.split('\t')[1:])
        new_file_lines.append(escaped_doi+
                              '_{}|a|'.format(line_num+1)+
                              paragraph_content)
        new_file_lines.append('')

    return (escaped_doi, [line+'\n' for line in new_file_lines])

def parform_to_plaintext(title_line, body, 
                         newlines=False, period_following_title=False):

    ''' Input is a tuple (doi, title_line, body) where doi is the escaped DOI 
        from the filename, title_line is a string, and body is a list of 
        abstract and paragraph lines in the file 
        (trailing newline characters stripped from all input lines)

        title_line is a string:
        'title\tsome_title_text'

        body is list with "parform" (paragraph format) format:
        ['abs\tsome_abstract_text', (abstract optional)
         'p\tparagraph1_text',
         'p\tparagraph2_text',
         ...
        ]

        Output:
        title_line[.]
        [optional_newline if newlines]
        [abstract_line if it exists]
        paragraph1
        [optional_newline if newlines]
        paragraph2
        ...
    '''

    # replace any pipe characters - they interfere with some pubtator tools
    body = [line.replace('|', '') for line in body]

    article_title = title_line.split('\t')[1]
    if period_following_title and not article_title.endswith('.'):
        article_title += '.' # to help CoreNLP split title from paragraph 1

    regex = re.compile(r'(^\w+\t)')

    body_lines = [regex.sub('', p) for p in body]

    new_file_lines = [article_title]+body_lines

    if newlines:
        new_file_lines_with_newlines = []
        for i, line in enumerate(new_file_lines):
            if i%2 == 0:
                new_file_lines_with_newlines.append(line)
            else:
                new_file_lines_with_newlines.append('')
        new_file_lines = new_file_lines_with_newlines

    return [line+'\n' for line in new_file_lines]

def pubtator_to_plaintext(title_line, abstract_text, newlines=False):

    ''' Converts a single PubTator title_line+abstract_text pair to two strings
        without PMID or label information. For example:

        Input:
        title_line: string in pubtator format with title, e.g., 
        '3513765|t|Protein kinase C desensitization by phorbol esters and its impact on growth of human breast cancer cells.'

        abstract_text: string in pubtator format with abstract, e.g.,
        '3513765|a|Active phorbol esters such as TPA (12-0-tetra-decanoylphorbol-13-acetate) inhibited growth of mammary carcinoma cells (MCF-7 greater than BT-20 greater than MDA-MB-231 greater than = ZR-75-1 greater than HBL-100) with the exception of T-47-D cells presumably by interacting with the phospholipid/Ca2+-dependent protein kinase (PKC). The nonresponsive T-47-D cells exhibited the lowest PKC activity. A rapid (30 min) TPA-dependent translocation of cytosolic PKC to membranes was found in the five TPA-sensitive cell without affecting cell growth. However, TPA-treatment of more than 10 hours inhibited reversibly the growth of TPA-responsive cells. This effect coincided with the complete loss of cellular PKC activity due to the proteolysis of the translocated membrane-bound PKC holoenzyme (75K) into 60K and 50K PKC fragments. Resumption of cell growth after TPA-removal was closely related to the specific reappearance of the PKC holoenzyme activity (75K) in the TPA-responsive human mammary tumor cell lines suggesting an involvement of PKC in growth regulation.'

        Output:
        ['Protein kinase C desensitization by phorbol esters and its impact on growth of human breast cancer cells.',
         'Active phorbol esters such as TPA (12-0-tetra-decanoylphorbol-13-acetate) inhibited growth of mammary carcinoma cells (MCF-7 greater than BT-20 greater than MDA-MB-231 greater than = ZR-75-1 greater than HBL-100) with the exception of T-47-D cells presumably by interacting with the phospholipid/Ca2+-dependent protein kinase (PKC). The nonresponsive T-47-D cells exhibited the lowest PKC activity. A rapid (30 min) TPA-dependent translocation of cytosolic PKC to membranes was found in the five TPA-sensitive cell without affecting cell growth. However, TPA-treatment of more than 10 hours inhibited reversibly the growth of TPA-responsive cells. This effect coincided with the complete loss of cellular PKC activity due to the proteolysis of the translocated membrane-bound PKC holoenzyme (75K) into 60K and 50K PKC fragments. Resumption of cell growth after TPA-removal was closely related to the specific reappearance of the PKC holoenzyme activity (75K) in the TPA-responsive human mammary tumor cell lines suggesting an involvement of PKC in growth regulation.'
         ]
    '''

    plaintext = []
    for item in title_line, abstract_text:
        # correctly handle titles/abstracts with internal | character
        stripped_line = '|'.join(item.split('|')[2:])
        if newlines:
            stripped_line += '\n'
        plaintext.append(stripped_line)

    return plaintext

def pubtator_to_parform(title_line, abstract_text, newlines=False):

    ''' Converts a *single* PubTator title_line+abstract_text pair to two strings
        without PMID or label information. For example:

        Input:
        title_line: string in pubtator format with title, e.g., 
        '3513765|t|Protein kinase C desensitization by phorbol esters and its impact on growth of human breast cancer cells.'

        abstract_text: string in pubtator format with abstract, e.g.,
        '3513765|a|Active phorbol esters such as TPA (12-0-tetra-decanoylphorbol-13-acetate) inhibited growth of mammary carcinoma cells (MCF-7 greater than BT-20 greater than MDA-MB-231 greater than = ZR-75-1 greater than HBL-100) with the exception of T-47-D cells presumably by interacting with the phospholipid/Ca2+-dependent protein kinase (PKC). The nonresponsive T-47-D cells exhibited the lowest PKC activity. A rapid (30 min) TPA-dependent translocation of cytosolic PKC to membranes was found in the five TPA-sensitive cell without affecting cell growth. However, TPA-treatment of more than 10 hours inhibited reversibly the growth of TPA-responsive cells. This effect coincided with the complete loss of cellular PKC activity due to the proteolysis of the translocated membrane-bound PKC holoenzyme (75K) into 60K and 50K PKC fragments. Resumption of cell growth after TPA-removal was closely related to the specific reappearance of the PKC holoenzyme activity (75K) in the TPA-responsive human mammary tumor cell lines suggesting an involvement of PKC in growth regulation.'

        Output:
        a 2-item tuple: (abs_id, (title_line, abstract))

        abs_id is a string, e.g., '3513765'

        title_line is a string:
        'title\tsome_title_text'

        abstract is a string:
        'abs\tsome_abstract_text'
    '''

    abs_id = title_line.split('|')[0]
    parform_title = 'title\t'+'|'.join(title_line.split('|')[2:])
    parform_abs = 'abs\t'+'|'.join(abstract_text.split('|')[2:])

    if newlines:
        parform_title += '\n'
        parform_abs += '\n'

    return (abs_id, (parform_title, parform_abs))