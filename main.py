import sys
from datetime import datetime
from ftplib import FTP
from time import time

import gspread

from core import *

start = time()

print('LOGANDO FTP')
session = FTP(sys.argv[1], sys.argv[2], sys.argv[3])

print('GETTING MONTH')
MONTH = datetime.now().strftime('%B').lower()

print('GETTING FILE')
FILE = get_file(session)

print('OPENING WORKSHEET')
sa = gspread.service_account()
sh = sa.open("Personal Finances 2022")

worksheet = sh.worksheet(MONTH)

print('GETTING BANK STATEMENT FROM GOOGLE')
existing_bank_statement = get_existing_worksheet(worksheet)

print('READING BANK STATEMENT FILE')
new_bank_statement = inter_fin(FILE)

print('REMOVING EXISTING LINES')
diff = new_bank_statement.merge(existing_bank_statement.drop_duplicates(), how='left', on=['DATE', 'OPERATION', 'DESTINATION', 'AMOUNT'], indicator=True)
diff = diff[diff['_merge'] == 'left_only']
diff.pop("_merge")

row_num = 1
for row in diff.values.tolist():
    print(f'INSERTING ROW {row_num}')
    worksheet.insert_row([row[0], row[1], row[2], row[3]], 8)

    sleep(1)
    row_num += 1

print('MOVING FILE TO LOG')
move_bank_statement(FILE, session)

end = time()
print(f'\nDURATION.: {round(end - start, 2)}s')
