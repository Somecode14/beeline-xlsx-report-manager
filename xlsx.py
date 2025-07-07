import pandas
import logging
import numpy

import bot

database = pandas.read_excel("database/database.xlsx")
cell_names = set()
for cell_name in database["CellName"].values:
    cell_names.add(cell_name)

def get_worksheet(file, message, sz_number, custom_status):
    global database
    workbook = pandas.read_excel(file)
    new_rows = pandas.DataFrame()
    new_cell_names = []
    for row in workbook.index:
        cell_name = workbook.loc[row]["CellName"]
        if cell_name in cell_names:
            logging.info(f"CellName {cell_name} is already in the database.")

            matched_custom_status = database.loc[cell_name == database['CellName'], 'CustomStatus']
            if not matched_custom_status.empty and custom_status == matched_custom_status.values[0]:

                # Skip record
                logging.info(f"Skipping it.")

            else:

                # TODO: Only update CustomStatus for the record
                logging.info(f"Supposed to change the CustomStatus here.")

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

            new_row = pandas.Series(data = {"CellName": cell_name, "BsNumber": bs_number, "Стандарт": ran, "BSID": bsid, "Филиал": "", "CustomStatus": custom_status, "СЗ_Number": sz_number, "StartTime": "?", "EndTime": "?", "Время изменения": "?", "Автор": bot.get_log_username(message.from_user)})
            new_rows = pandas.concat([new_rows, new_row.to_frame().T])
            cell_names.add(cell_name)
    if new_cell_names:
        database = pandas.concat([database, new_rows])
        database.to_excel("database/database_new.xlsx", index=False)
        bot.bot.reply_to(message, f"Добавлено {len(new_cell_names)} записей в базу: {new_cell_names}.")
    else:
        bot.bot.reply_to(message, "Служебная записка не содержит новых записей. Изменений в базу не внесено.")

#def records_amount_case(amount):
    #if amount.ends == 1:
