import bs4 as bs
import json
import re

'''
policzyć tekst główny biblii jako - przykładowo - tabele zagnieżdżonych list: 
    Rdz = [[1, 2, ..., ilość wersów w 1 rozdziale], [1, 2, ...]]
    albo jako słowniki słowników ewentualnie
zrobić schemat blokowy i ify na przeliczanie treści "Rdz 1, 2-8" na "Rdz [1][2], Rdz[1][3] ... Rdz[1][8]

zrobić łowienie w kalendarzu pod kątem odpowiedzi na pytanie "które fragmenty są czytane w niedziele i święta nakazane" "które fragmenty są
czytane kiedykolwiek" "które fragmenty są czytane nigdy"
- i na razie TYLKO pod tym kątem

potem zostanie tylko przeliczyć różnice między listami/słownikami :)
'''

# BUDOWANIE SŁOWNIKA


def save_dict_of_all_books():
    list_of_books = get_list_of_books()
    dict_of_all_books = build_dict_of_many_books(list_of_books)
    save_dict_as_json(dict_of_all_books, "dict_of_all_books")


def get_list_of_books():
    with open("list_of_books.txt", "r") as fp:
        list_of_books = list(fp.read().splitlines())
    return list_of_books


def build_dict_of_many_books(list_of_books):
    dict_of_many_books = build_skeleton_dict()
    for book in list_of_books:
        dict_of_one_book = build_dict_of_one_book(book)
        dict_of_many_books[book] = dict_of_one_book
    return dict_of_many_books


def build_skeleton_dict():
    skeleton_dict = {}
    list_of_books = get_list_of_books()
    for book in list_of_books:
        skeleton_dict.update(
                {
                    book: {}
                    }
                )
    return skeleton_dict


def build_dict_of_one_book(book_code):
    log.append(f"log: building dict of one book {book_code}")
    one_book_chaos_dict = {}
    for nr in range(1,1991):
        code_of_chapter = get_chapter_code(nr)
        if trim_chaptercode_to_bookname(code_of_chapter) == book_code:
            verses = get_verses(nr)
            one_book_chaos_dict[code_of_chapter] = verses
    one_book_dict = {}
    for nr in range(1, len(one_book_chaos_dict)+1):

        code_of_chapter = f"{book_code} {nr}"
        verses = one_book_chaos_dict[code_of_chapter]
        one_book_dict[code_of_chapter] = verses
    return one_book_dict


def get_chapter_code(nr):
    soup = open_chap_as_soup(nr)
    code_of_chapter = soup.title.string
    code_of_chapter = code_of_chapter.replace("Biblia Tysiąclecia - Pismo Święte Starego i Nowego Testamentu - ", "")
    return(code_of_chapter)


def trim_chaptercode_to_bookname(code_of_chapter):
    chapter_sliced = code_of_chapter.split(" ")
    chapter_sliced.pop()
    bookname = " ".join(chapter_sliced)
    return bookname


def get_verses(nr):
    log.append(f"log: getting list of verses from subpage {nr}")
    soup = open_chap_as_soup(nr)
    verses = []
    for x in soup.find_all(class_="werset"):
        verse = x.get_text()
        while not verse.isalnum():
            verse = verse[:-1]
        verses.append(verse)
    return verses


def open_chap_as_soup(nr): #(1,1991)
    filename = f"raw-chapter{nr}.html"
    soup = open_as_soup_if_chap(filename)
    return soup


def open_as_soup_if_chap(filename):
    with open(filename, mode="r", encoding="iso-8859-2") as fp:
        soup = bs.BeautifulSoup(fp, "html5lib")
        return soup


def save_dict_as_json(dictionary, filename):
    with open(f"{filename}.json", "w") as fp:
        json.dump(dictionary, fp)



# LISTY CZYTAŃ NIEDZIELNYCH (I INNYCH)

def make_list_of_some_excerpts(cal_nr_from, cal_nr_to):
    list_of_some_excerpts = []
    for nr in range(cal_nr_from, cal_nr_to+1):
        soup = open_calendar_as_soup(nr)
        if check_if_sunday(soup):
            liturgy_stage_list = get_readings(soup)
            excerpt_list = trim_liturgy_stage_to_excerpt_code(liturgy_stage_list)
            for excerpt in excerpt_list:
                list_of_some_excerpts.append(excerpt)
    return list_of_some_excerpts


def open_calendar_as_soup(nr): #(1,902)
    filename = f"raw-calendar{nr}.html"
    soup = open_as_soup_if_cal(filename)
    return soup


def open_as_soup_if_cal(filename):
    with open(filename, mode="r") as fp:
        text = []
        for line in fp:
            text.append(line.replace("<br />", "\n"))
        joined_text = "".join(text)
        soup = bs.BeautifulSoup(joined_text, "html5lib")
        return soup


def check_if_sunday(soup):
    is_sunday = False
    destyled_list = get_soup_as_destyled_list(soup)
    for line in destyled_list:
        if line.find("NIEDZIELA") != -1:
            is_sunday = True
    return is_sunday


def get_soup_as_destyled_list(soup):
    soup = soup.main
    souptext = soup.get_text()
    destyled_list = souptext.split("\n")
    return destyled_list


def get_readings(soup):
    destyled_list = get_soup_as_destyled_list(soup)
    readings_list = []
    liturgy_scheme = make_liturgy_scheme_list()
    for line in destyled_list:
        line = line.strip()
        for item in liturgy_scheme:
            if line.startswith(item):
                readings_list.append(line)
    return readings_list


def make_liturgy_scheme_list():
    liturgy_scheme = ("PIERWSZE CZYTANIE", "DRUGIE CZYTANIE", "EWANGELIA")
    return liturgy_scheme


def trim_liturgy_stage_to_excerpt_code(liturgy_stage_list):
    excerpt_list = []
    for stage in liturgy_stage_list:
        excerpt = stage[stage.find("("):]
        excerpt = excerpt.split("Refren")[0].strip()
        excerpt = excerpt[1:-1]
        if len(excerpt) > 0:
            excerpt_list.append(excerpt)
    return excerpt_list




# RÓŻNE

def open_calendar_spec_as_soup(nr): #(1,91)
    filename = f"raw-calendar-s{nr}.html"
    soup = open_as_soup_if_cal(filename)
    return soup



# POZYSKIWANIE DANYCH O ROZDZIAŁACH I WERSACH

def get_max_verse_chapter(nr):
    log.append(f"log:•getting•max•verse•from•subpage•{nr}")
    soup = open_chap_as_soup(nr)
    for x in soup.find_all(class_="werset"):
        verse = x.get_text()
    while not verse.isnumeric():
        verse = verse[:-1]
    max_verse = str(verse)
    return max_verse


def read_json(filename):
    with open(f"{filename}.json", "r") as fp:
        file = json.load(fp)
        return file



# POZYSKIWANIE DANYCH KALENDARZOWYCH

def get_psalm(soup):
    destyled_list = get_soup_as_destyled_list(soup)
    psalm_list = []
    for line in destyled_list:
        line = line.strip()
        if line.startswith("PSALM"):
            psalm_list.append(line)
    return psalm_list


def get_gospel_chant(soup):
    destyled_list = get_soup_as_destyled_list(soup)
    gospel_chant_list = []
    for line in destyled_list:
        line = line.strip()
        if line.startswith("ŚPIEW PRZED EWANGELIĄ"):
            gospel_chant_list.append(line)
    return gospel_chant_list


def unpack_excerpt_code(excerpt):
    excerpt_dict = {}
    list_of_books = get_list_of_books()
    dict_of_all_books = read_json("dict_of_all_books")
    for book in list_of_books:
        book_space = str(book + " ")
        if excerpt.startswith(book_space):
            bookname = book
    excerpt = excerpt.replace(bookname, "").replace(" ", "")
    log.append("trimmed excerpt: " + excerpt)
    subexcerpt_list = excerpt.split(";")
    log.append("subexcerpt_list: " + str(subexcerpt_list))
    for subexcerpt in subexcerpt_list:
        if not is_excerpt_multichapter(subexcerpt):
            log.append("subexcerpt is NOT multichapter")
            chapter_code = bookname + " " + subexcerpt.split(",")[0]
            log.append("chapter_code: " + chapter_code)
            verses = subexcerpt.split(",")[1]
            log.append("verses after , split: " + verses)
            verses = verses.split(".")
            log.append("verses after . split: " + str(verses))
            verses_list = []
            for verse in verses:
                start_verse = verse.split("-")[0]
                end_verse = verse.split("-")[-1]
                expanded_verse = expand_verses_in_chapter(chapter_code, start_verse, end_verse)
                log.append("expanded_verse: " + str(expanded_verse))
                verses_list = verses_list.extend(expanded_verse)
            excerpt_dict.update({chapter_code: verses_list})
        else:
            log.append("subexcerpt is multichapter")
            splitting_point = splitting_point_multichapter(subexcerpt)
            start_sequence = subexcerpt.split("-", splitting_point[0], splitting_point[1])[0]
            end_sequence = subexcerpt.split("-", splitting_point[0], splitting_point[1])[1]
    return excerpt_dict


def is_excerpt_multichapter(excerpt):
    is_excerpt_multichapter = False
    x = re.findall(",(.+?)-(.+?),", excerpt)
    if len(x) > 0:
        is_excerpt_multichapter = True
    return is_excerpt_multichapter


def splitting_point_multichapter(excerpt):
    x = re.search(",(.+?)-(.+?),", excerpt)
    start_of_regex = x.start()
    end_of_regex = x.start() + len(x)
    return [start_of_regex, end_of_regex]


def expand_verses_in_chapter(chapter_code, start_verse, end_verse):
    dict_of_all_books = read_json("dict_of_all_books")
    bookname = trim_chaptercode_to_bookname(chapter_code)
    all_verses_list = dict_of_all_books[bookname][chapter_code]
    verses_list = all_verses_list[all_verses_list.index(start_verse):all_verses_list.index(end_verse)+1]
    return verses_list


def expand_verses_multichapter(start_chapter, start_verse, end_chapter, end_verse):
    dict_of_all_books = read_json("dict_of_all_books")
    bookname = trim_chaptercode_to_bookname(start_chapter)
    starting_chapter_nr = int(start_chapter.split(" ")[-1])
    ending_chapter_nr = int(end_chapter.split(" ")[-1])
    dict_of_some_excerpts = {}
    all_verses_list = dict_of_all_books[bookname][star_chapter]
    verses_list = all_verses_list[all_verses_list.index(start_verse):]
    dict_of_some_excerpts.update({start_chapter: verses_list})
    current_chapter_nr = starting_chapter_nr + 1
    while not current_chapter_nr == ending_chapter_nr:
        verses_list = dict_of_all_books[bookname][f"{bookname} {current_chapter_nr}"]
        dict_of_some_excerpts.update({f"{bookname} {current_chapter_nr}": verses_list})
        current_chapter_nr += 1
    all_verses_list = dict_of_all_books[bookname][end_chapter]
    verses_list = all_verses_list[:all_verses_list.index(end_verse)+1]
    dict_of_some_excerpts.update({end_chapter: verses_list})
    return dict_of_some_excerpts


def integrate_excerpt_dict(excerpt_dict, many_excerpts_dict):
    return many_excerpts_dict



def unpack_ps_excerpt_code(excerpt):
    excerpt
    return excerpt_dict




log = []
def print_log():
    for lines in log:
        print(lines)

