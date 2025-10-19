import sys
import subprocess
import re
import xml.etree.ElementTree as ET
import codecs
import datetime
import os
import zipfile
import json

from bacs_converter_settings import *


def read_file(path):
    print("Reading file", path, "...")

    data = ""
    with open(path, 'r', encoding='UTF-8') as file:
        data = file.read()

    assert data != ""

    return data


def write_file_utf8(path, content):
    print("Writing file", path, "...")

    with codecs.open(path, 'w', 'utf-8') as file:
        file.write(content)


def write_file(path, content):
    print("Writing file", path, "...")

    with open(path, 'w') as file:
        file.write(content)


def xml_check_predicate(node, p):
    if type(p) is str:
        p = {'tag': p}

    for key, value in p.items():
        if key == 'tag':
            if node.tag != p['tag']:
                return False
            continue

        if key not in node.attrib: return False
        if node.attrib[key] != p[key]: return False

    return True


def retrieve_xml(node, *predicate_sequence, match_all=False):
    matched = [node]
    for p in predicate_sequence:
        children_matched = []
        for node in matched:
            for child in node:
                if xml_check_predicate(child, p):
                    children_matched.append(child)

        matched = children_matched

    if match_all:
        return matched

    if len(matched) == 0:
        raise ValueError(f'No nodes matched')

    return matched[0]


def load_lang_data():
    json_str = read_file(ROOT / "ISO-639-1-language.json")

    lang_data = json.loads(json_str)

    # format and correct names
    for lang in lang_data:
        lang['name'] = lang['name'].lower()

        for sep in [';', ',']:
            lang['name'] = lang['name'].partition(sep)[0]

    return {lang['name']: lang for lang in lang_data}


def run(task_from, lang_data=None):
    TASK_FROM = f"{ROOT}\\input\\{task_from}"
    TASK_DEST = ""

    # load lang_data
    if lang_data is None:
        lang_data = load_lang_data()

    # do all in source task
    if not DEBUG_SKIP_PROBLEM_PACKAGE_DO_ALL:
        subprocess.run("doall.bat", cwd=TASK_FROM, shell=True)

    # get problem config
    problem_config = ET.parse(f"{TASK_FROM}\\problem.xml")
    problem_config_root = problem_config.getroot()
    problem_config_polygon_name = u''.join(problem_config_root.attrib['short-name'])
    problem_config_polygon_revision = u''.join(problem_config_root.attrib['revision'])
    problem_config_polygon_url = u''.join(problem_config_root.attrib['url'])
    problem_config_langs = {node.attrib['language']: lang_data[node.attrib['language']] for node in retrieve_xml(problem_config_root, 'names', 'name', match_all=True)}
    problem_config_name_by_lang = {node.attrib['language']: node.attrib['value'] for node in retrieve_xml(problem_config_root, 'names', 'name', match_all=True)}
    problem_config_time_limit_ms = int(retrieve_xml(problem_config_root, 'judging', 'testset', 'time-limit').text)
    problem_config_memory_limit_bytes = int(retrieve_xml(problem_config_root, 'judging', 'testset', 'memory-limit').text)
    problem_config_test_count = len(retrieve_xml(problem_config_root, 'judging', 'testset', 'tests', 'test', match_all=True))
    problem_config_pretest_count = len(retrieve_xml(problem_config_root, 'judging', 'testset', 'tests', {'sample': 'true'}, match_all=True))

    if MAIN_LANG not in problem_config_name_by_lang:
        raise ValueError(
            f"{MAIN_LANG=} not found in problem '{problem_config_polygon_name}' package. "
            f"Language options are {list(problem_config_langs.keys())}"
        )

    problem_config_name = problem_config_name_by_lang[MAIN_LANG]

    print(f"""
        PROBLEM CONFIG:
        problem_config_polygon_name => {problem_config_polygon_name}
        problem_config_name_by_lang => {problem_config_name_by_lang}
        problem_config_name => {problem_config_name}
        problem_config_time_limit_ms => {problem_config_time_limit_ms}
        problem_config_memory_limit_bytes => {problem_config_memory_limit_bytes}
        problem_config_test_count => {problem_config_test_count}
        problem_config_pretest_count => {problem_config_pretest_count}
    """)

    TASK_ID = NAME_PREFIX + problem_config_polygon_name + NAME_SUFFIX

    # autofill task dest
    if TASK_DEST == "":
        TASK_DEST = f"{ROOT}\\output\\{TASK_ID}"

    # cleanup possible old task dir
    subprocess.run(f"rmdir {TASK_ID} /S /Q", cwd=f"{ROOT}\\output", shell=True)

    # make new task dir
    subprocess.run("mkdir " + TASK_ID, cwd=f"{ROOT}\\output", shell=True)

    # checker
    subprocess.run("mkdir checker", cwd=TASK_DEST, shell=True)
    subprocess.run(f"xcopy {TASK_BACS_EXAMPLE}\\checker\\config.ini* {TASK_DEST}\\checker\\config.ini* /y", cwd=ROOT, shell=True)
    subprocess.run(f"xcopy {TASK_FROM}\\check.cpp* {TASK_DEST}\\checker\\check.cpp* /y", cwd=ROOT, shell=True)

    # misc solution
    subprocess.run("mkdir misc\\solution", cwd=TASK_DEST, shell=True)
    subprocess.run(f"xcopy {TASK_FROM}\\solutions\\* {TASK_DEST}\\misc\\solution\\* /s /e /y", cwd=ROOT, shell=True)
    subprocess.run("del misc\\solution\\*.exe", cwd=TASK_DEST, shell=True)
    subprocess.run("rmdir misc\\solution", cwd=TASK_DEST, shell=True)

    # misc materials
    subprocess.run("mkdir misc\\materials", cwd=TASK_DEST, shell=True)
    subprocess.run(f"xcopy {TASK_FROM}\\problem.xml* {TASK_DEST}\\misc\\materials\\problem.xml* /y", cwd=ROOT, shell=True)

    subprocess.run("mkdir misc\\materials\\statements", cwd=TASK_DEST, shell=True)
    for lang_name in problem_config_langs:
        subprocess.run(f"mkdir misc\\materials\\statements\\{lang_name}", cwd=TASK_DEST, shell=True)
        subprocess.run(f"xcopy {TASK_FROM}\\statements\\{lang_name}\\* {TASK_DEST}\\misc\\materials\\statements\\{lang_name}\\* /s /e /y", cwd=ROOT, shell=True)

    subprocess.run("mkdir misc\\materials\\files", cwd=TASK_DEST, shell=True)
    subprocess.run(f"xcopy {TASK_FROM}\\files\\* {TASK_DEST}\\misc\\materials\\files\\* /s /e /y", cwd=ROOT, shell=True)
    subprocess.run("del misc\\materials\\files\\*.exe", cwd=TASK_DEST, shell=True)
    subprocess.run("del misc\\materials\\files\\testlib.h", cwd=TASK_DEST, shell=True)
    subprocess.run("del misc\\materials\\files\\olymp.sty", cwd=TASK_DEST, shell=True)
    subprocess.run("del misc\\materials\\files\\statements.ftl", cwd=TASK_DEST, shell=True)

    # misc tutorial
    subprocess.run("mkdir misc\\tutorial", cwd=TASK_DEST, shell=True)
    for lang_name in problem_config_langs:
        subprocess.run(f"xcopy {TASK_FROM}\\statements\\.pdf\\{lang_name}\\tutorial.pdf* {TASK_DEST}\\misc\\tutorial\\tutorial_{lang_name}.pdf* /y", cwd=ROOT, shell=True)
    subprocess.run("rmdir misc\\tutorial", cwd=TASK_DEST, shell=True)

    # misc contacts.txt
    write_file_utf8(f"{TASK_DEST}\\misc\\contacts.txt",
        "This problem was converted from polygon.codeforces.com package\n" +
        "You can contact ATSTNG and request access for original polygon problem or additional info\n" +
        "\n" +
        "https://vk.com/atstng\n" +
        "https://t.me/ATSTNG\n" +
        "atstng@gmail.com\n" +
        "codeforces.com/profile/ATSTNG\n" +
        "\n" +
        f"Polygon name: {problem_config_polygon_name}\n" +
        f"Polygon revision: {problem_config_polygon_revision}\n" +
        f"Polygon URL: {problem_config_polygon_url}\n" +
        f"Conversion timestamp: {datetime.datetime.now().isoformat()}\n" +
        f"BACS converter revision: {BACS_CONVERTER_REVISION.isoformat()}\n"
    )

    # statement
    subprocess.run("mkdir statement", cwd=TASK_DEST, shell=True)

    for lang_name, lang in problem_config_langs.items():
        subprocess.run(f"xcopy {TASK_BACS_EXAMPLE}\\statement\\html_{lang['code']}.ini* {TASK_DEST}\\statement\\html_{lang['code']}.ini* /y", cwd=ROOT, shell=True)

        subprocess.run(f"mkdir statement\\{lang_name}", cwd=TASK_DEST, shell=True)

        problem_html_data = read_file(f"{TASK_FROM}\\statements\\.html\\{lang_name}\\problem.html")
        problem_html_data = problem_html_data.replace(
            "https://polygon.codeforces.com/lib/MathJax/MathJax.js?config=TeX-MML-AM_CHTML",
            "/MathJax.js?config=TeX-MML-AM_CHTML"
        )
        problem_html_data = problem_html_data.replace(
            "problem-statement.css",
            "/problem-statement.css"
        )
        write_file_utf8(f"{TASK_DEST}\\statement\\{lang_name}\\problem.html", problem_html_data)

    # statement pictures and other files
    pic_extensions = ['png', 'gif', 'bmp', 'jpg', 'jpeg']
    for lang_name in problem_config_langs:
        for ext in pic_extensions:
            subprocess.run(f"xcopy {TASK_FROM}\\statements\\.html\\{lang_name}\\*.{ext} {TASK_DEST}\\statement\\{lang_name}\\*.{ext} /s /e /y", cwd=ROOT, shell=True)

    # tests
    subprocess.run("mkdir tests", cwd=TASK_DEST, shell=True)
    subprocess.run(f"xcopy {TASK_FROM}\\tests\\* {TASK_DEST}\\tests\\* /s /e /y", cwd=ROOT, shell=True)

    for command in [
        "ren *. *.in",
        "ren *.a *.out",
        "ren 01.* 1.*",
        "ren 02.* 2.*",
        "ren 03.* 3.*",
        "ren 04.* 4.*",
        "ren 05.* 5.*",
        "ren 06.* 6.*",
        "ren 07.* 7.*",
        "ren 08.* 8.*",
        "ren 09.* 9.*",
    ]:
        print("Running", command, "...")
        subprocess.run(command, cwd=f"{TASK_DEST}\\tests\\", shell=True)

    # config.ini
    config_ini_data_list = [
        f"[info]",
        f"name = {problem_config_name}",
        f"maintainers = {' '.join(MAINTAINERS_LIST)}",
        f"",
        f"[resource_limits]",
        f"time = {problem_config_time_limit_ms / 1000}s",
        f"memory = {problem_config_memory_limit_bytes / 1024 / 1024}MiB",
        f"",
        f"[tests]",
        f"group_pre = {' '.join(str(x) for x in range(1, 1 + problem_config_pretest_count))}",
        f"score_pre = 0",
        f"continue_condition_pre = WHILE_OK",
        f"score = 100",
        f"continue_condition = ALWAYS",
        f"",
        f"[info.names]",
    ] + [
        f"{lang_data[lang_name]['code']} = {problem_name}" for lang_name, problem_name in problem_config_name_by_lang.items()
    ]

    config_ini_data = "".join(line + "\n" for line in config_ini_data_list)
    write_file_utf8(f"{TASK_DEST}\\config.ini", config_ini_data)

    # format
    subprocess.run(f"xcopy {TASK_BACS_EXAMPLE}\\format* {TASK_DEST}\\format* /y", cwd=ROOT, shell=True)


if __name__ == "__main__":
    lang_data = load_lang_data()

    if MAIN_LANG not in lang_data:
        raise ValueError(
            f"{MAIN_LANG=} is not a valid language name. "
            f"Suggested options are ['english', 'russian', 'spanish']"
        )

    # find all zip-archived Polygon packages in input folder, unpack and run conversion for each of them
    for input_dir_entry in os.listdir(f"{ROOT}\\input\\"):
        if not input_dir_entry.endswith(".zip"):
            continue

        task_archive_name = input_dir_entry.replace(".zip", "")

        with zipfile.ZipFile(f"{ROOT}\\input\\{task_archive_name}.zip", 'r') as zip_ref:
            zip_ref.extractall(f"{ROOT}\\input\\{task_archive_name}")

        run(task_archive_name, lang_data=lang_data)
