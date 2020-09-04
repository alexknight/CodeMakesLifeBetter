#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-08-15 16:44
# @Author  : shefferliao
# @Site    :
# @File    :
# @Desc    :
import os

import xlrd

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
excel_path = os.path.join(base_dir, '3064544.xlsx')

key_values = ['英语']
black_boards = ['潮州', '汕头', '河源', '肇庆', '湛江', '云浮', '阳江', '揭阳', '江门', '茂名', '梅州', '汕尾', '韶关']
target_rows = []
wb = xlrd.open_workbook(excel_path)
sh1 = wb.sheet_by_index(0)

for index in range(sh1.nrows):
    is_next = False
    line = sh1.row_values(index)
    line = [str(x) for x in line]
    line_str = ''.join(line)
    if '招聘单位' in line_str:
        target_rows.append(line)
    for black_value in black_boards:
        if black_value in line_str:
            is_next = True
            break
    if is_next:
        continue

    for key_value in key_values:
        if key_value in line_str:
            target_rows.append(line)

with open(os.path.join(base_dir, 'target.csv'), 'w') as f:
    for line in target_rows:
        content = ','.join(line)
        f.write(content + '\n')

