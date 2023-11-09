"""
转换翻译文件的脚本
"""


def load_old_dat(dat_file: str):
    with open(dat_file, 'r', encoding='utf-8') as f:
        f_header = ''
        f_body = {}
        first_line = True
        for line in f:
            if first_line:  # 首行为65001
                f_header = line
                first_line = False
            else:
                f_index, f_line = line.split("=")
                f_body[f_index] = f_line
    return f_header, f_body


def load_new_translate(txt_file: str):
    with open(txt_file, 'r', encoding='utf-8') as f:
        f_return = {}
        for line in f:
            f_index, f_line = line.split("=")
            f_return[f_index] = f_line.replace("\n", "")
    return f_return


if __name__ == '__main__':
    header, body = load_old_dat('LangRUS.dat')
    new_translate = load_new_translate('newRUS.txt')
    for index in new_translate.keys():
        if index in body.keys():
            body[index] = body[index].split(',')[0] + "," + f'"{new_translate[index]}"\n'
        else:
            print("没有匹配项：%s" % index)
    with open('newLangRus.dat', 'w', encoding='utf-8') as f:
        f.write(header)
        for index in body.keys():
            f.write(index + "=" + body[index])
