import pandas
import logging
from datetime import datetime

import bot
import config

database = None
cell_names = set()

def read_database():
    global database
    global cell_names
    database = pandas.read_excel("database/database.xlsx")
    cell_names = set()
    for cell_name in database["CellName"].values:
        cell_names.add(cell_name)
    logging.info(f"Loaded database ({len(cell_names)} records).")

read_database()

def get_worksheet(file, message, sz_number, custom_status, start_time, end_time):
    global database
    if config.read_database_on_each_input:
        read_database()
    workbook = pandas.read_excel(file)
    new_rows = pandas.DataFrame()
    new_cell_names = []
    modified_cell_names = []
    for row in workbook.index:
        cell_name = workbook.loc[row]["CellName"]
        if cell_name in cell_names:
            logging.info(f"CellName {cell_name} is already in the database.")

            matched_custom_status = database.loc[cell_name == database['CellName'], 'CustomStatus']
            if not matched_custom_status.empty and custom_status == matched_custom_status.values[0]:

                # Skip record
                logging.info(f"Skipping it.")

            else:

                logging.info(f"Changing the CustomStatus from {matched_custom_status.values[0]} to {custom_status}.")
                database.loc[matched_custom_status.index[0], "CustomStatus"] = custom_status
                modified_cell_names.append(cell_name)

        else:

            # Add new record to the database

            logging.info(f"Adding CellName {cell_name} to the database")
            new_cell_names.append(cell_name)

            # BsNumber

            bs_number = None
            if "BsNumber" in workbook:
                bs_number = workbook.loc[row]["BsNumber"]
            elif "Номер БС" in workbook:
                bs_number = workbook.loc[row]["Номер БС"]
            else:
                logging.warning(f"Unable to get BsNumber of {workbook.loc[row]['CellName']}.")
            logging.info(f"BsNumber: {bs_number}")

            # BSID

            bsid = None
            if "PositionCode" in workbook:
                bsid = workbook.loc[row]["PositionCode"]
            elif "Erp" in workbook:
                bsid = workbook.loc[row]["Erp"]
            else:
                logging.warning(f"Unable to get BSid of {workbook.loc[row]['CellName']}.")
            logging.info(f"BSID: {bsid}")

            # Стандарт

            ran = ""
            if "Ran" in workbook:
                ran = workbook.loc[row]["Ran"]
                logging.info(f"Ran: {ran}")
            else:
                logging.info(f"No Ran specified. Leaving it empty.")

            new_row = pandas.Series(data = {"CellName": cell_name, "BsNumber": bs_number, "Стандарт": ran, "BSID": bsid, "Филиал": "", "CustomStatus": custom_status, "СЗ_Number": sz_number, "StartTime": start_time, "EndTime": end_time, "Время изменения": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Автор": bot.get_log_username(message.from_user)})
            new_rows = pandas.concat([new_rows, new_row.to_frame().T])
            cell_names.add(cell_name)
            logging.info(f"Added CellName {cell_name} to the database.")
    if new_cell_names or modified_cell_names:
        database = pandas.concat([database, new_rows])
        database.to_excel("database/database.xlsx", index=False)
        logging.info(f"All changes have been written to the database.")
        bot.bot.reply_to(message, f"Добавлено {len(new_cell_names)} {records_amount_case(len(new_cell_names), False)} в базу: {new_cell_names}.\n\nИзменён статус {len(modified_cell_names)} {records_amount_case(len(new_cell_names), True)} в базе: {modified_cell_names}")
    else:
        bot.bot.reply_to(message, "Служебная записка не содержит новых записей. Изменений в базу не внесено.")

def records_amount_case(amount_int, is_genitive: bool):
    amount = str(amount_int)
    if amount.endswith("1") and not amount.endswith("11"):
        if is_genitive:
            return "запись"
        else:
            return "записи"
    elif is_genitive:
        return "записей"
    elif (amount.endswith("2") or amount.endswith("3") or amount.endswith("4")) and not(amount.endswith("12") or amount.endswith("13") or amount.endswith("14")):
        return "записи"
    else:
        return "записей"