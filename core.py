import csv
import os
import shutil
from ftplib import FTP

def get_operation(operation:str):
    if 'COMPRA CARTAO' in operation or 'PAGAMENTO FATURA INTER' in operation:
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
                balance = brazilian_money_to_us_money(row[3])

                transaction = (date.strip(), operation.strip(), amount, balance, destination)
                transactions.append(transaction)
    
    return transactions

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

if __name__ == '__main__':
    print(inter_fin(get_file()))
