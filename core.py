import csv
import os
from ftplib import FTP
from time import sleep

import pandas as pd


def get_operation(operation:str):
    if 'COMPRA CARTAO' in operation or \
        'PAGAMENTO FATURA INTER' in operation or \
        'TED RECEBIDA' in operation:
        return operation[:operation.find('-')].strip(), operation[operation.find('-')+2:].strip()
    
    return operation[:operation.find(':')-5].strip(), operation[operation.find(':')+10:]

def brazilian_money_to_us_money(balance:str):
    cents = balance[balance.find(',')+1:]
    balance = balance[:-3].replace('.', '')

    balance = float(f'{balance}.{cents}')
    return balance

def inter_fin(file):
    with open(file, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        count_line = 0
        transactions = []

        for row in csv_reader:
            row = [column.upper() for column in row]
            count_line += 1

            if count_line > 6:
                date = row[0].strip()
                operation, destination = get_operation(row[1].strip())
                amount = float(row[2].strip().replace(',', '.'))

                transaction = [date.strip(), operation.strip(), destination, amount]
                transactions.append(transaction)
    
    COLUMNS = ['DATE', 'OPERATION', 'DESTINATION', 'AMOUNT']
    dataframe = pd.DataFrame(transactions, columns=COLUMNS)

    return dataframe

def get_existing_worksheet(worksheet):
    total_rows = worksheet.row_count

    COLUMNS = ['DATE', 'OPERATION', 'DESTINATION', 'AMOUNT']
    dataframe = pd.DataFrame(columns=COLUMNS)

    for i in range(8, total_rows):
        row_value = worksheet.row_values(i)

        if len(row_value) != 0:
            row = pd.DataFrame([row_value], columns=COLUMNS)
            dataframe = pd.concat([dataframe, row])
            sleep(1.5)
        else:
            break

    dataframe = dataframe.iloc[::-1]
    dataframe = dataframe.reset_index(drop=True)
    dataframe['AMOUNT'] = dataframe['AMOUNT'].astype('string')
    dataframe['AMOUNT'].replace('[\$,]', '', regex=True, inplace=True)
    dataframe['AMOUNT'] = dataframe['AMOUNT'].astype('float64')
    return dataframe

def get_file(session:FTP):
    for file in session.nlst():
        if file.endswith('.csv'):
            session.retrbinary(f'RETR {file}', open(file, 'wb').write)
            return file

    return None

def move_bank_statement(file:str, session:FTP):
    session.storbinary(f'STOR ./log/{file}', open(file, 'rb'))
    session.delete(file)
    os.remove(file)
