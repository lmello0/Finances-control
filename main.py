from datetime import datetime
from time import sleep, time

import gspread

from core import *

if __name__ == '__main__':
    start = time()

    print('GETTING MONTH')
    MONTH = datetime.now().strftime('%B').lower()

    print('GETTING FILE')
    FILE = get_file()

    if FILE != None:
        print('LOGGING IN GOOGLE ACCOUNT')
        sa = gspread.service_account()
        sh = sa.open("Personal Finances 2022")

        print('OPENING WORKSHEET')
        wks = sh.worksheet(f"{MONTH}")

        print('READING BANK STATEMENT FILE')
        rows = inter_fin(FILE)

        row_num = 1
        for row in rows:
            print(f'INSERTING ROW {row_num}')
            wks.insert_row([row[0], row[1], row[4], row[2]], 8)
            
            sleep(1)
            row_num += 1
            
        move_bank_statement(FILE)

    end = time()
    print(f'\nDURATION.: {round(end - start, 2)}s')
