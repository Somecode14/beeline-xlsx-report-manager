import pandas
import logging

import bot

database = pandas.read_excel("database/database.xlsx")
cell_names = set()
for cell_name in database["CellName"].values:
    cell_names.add(cell_name)

def get_worksheet(file, message, sz_number):
    global database
    workbook = pandas.read_excel(file)
    new_rows = pandas.DataFrame()
    new_cell_names = []
    for row in workbook.index:
        if workbook.loc[row]["CellName"] in cell_names:
            logging.warning(f"CellName {workbook.loc[row]["CellName"]} is already in the database.")
        else:
            logging.info(f"Adding CellName {workbook.loc[row]["CellName"]} to the database")
            new_cell_names.append(workbook.loc[row]["CellName"])

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

            new_row = pandas.Series(data = {"CellName": workbook.loc[row]["CellName"], "BsNumber": bs_number, "Стандарт": "?", "BSID": bsid, "Филиал": "?", "CustomStatus": "?", "СЗ_Number": sz_number, "StartTime": "?", "EndTime": "?", "Время изменения": "?", "Автор": "?"})
            new_rows = pandas.concat([new_rows, new_row.to_frame().T])
            cell_names.add(workbook.loc[row]["CellName"])
    if new_cell_names:
        database = pandas.concat([database, new_rows])
        database.to_excel("database/database_new.xlsx", index=False)
        bot.bot.reply_to(message, f"Добавлено {len(new_cell_names)} записей в базу: {new_cell_names}.")
    else:
        bot.bot.reply_to(message, "Служебная записка не содержит новых записей. Нет изменений в базе.")