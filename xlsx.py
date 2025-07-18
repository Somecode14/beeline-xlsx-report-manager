import pandas
import logging
from datetime import datetime
import os

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

def get_worksheet(file, message, sz_number, custom_status, department, start_time, end_time):
    try:
        # Appends `file` data to database/database.xlsx is a smart way.
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

                    logging.info(f"Changing its CustomStatus from {matched_custom_status.values[0]} to {custom_status}.")
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

                new_row = pandas.Series(data = {"CellName": cell_name, "BsNumber": bs_number, "Стандарт": ran, "BSID": bsid, "Филиал": department, "CustomStatus": custom_status, "СЗ_Number": sz_number, "StartTime": start_time, "EndTime": end_time, "Время изменения": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Автор": bot.get_log_username(message.from_user)})
                new_rows = pandas.concat([new_rows, new_row.to_frame().T], ignore_index=True)
                cell_names.add(cell_name)
                logging.info(f"Added CellName {cell_name} to the database.")
        if new_cell_names or modified_cell_names:
            database = pandas.concat([database, new_rows], ignore_index=True)
            with pandas.ExcelWriter("database/database.xlsx", engine="xlsxwriter") as database_output:
                database.to_excel(database_output, index=False, sheet_name="Database")
                database_output_sheet = database_output.sheets["Database"]
                database_output_sheet.set_column("A:A", 19)
                database_output_sheet.set_column("B:C", 10)
                database_output_sheet.set_column("D:G", 12)
                database_output_sheet.set_column("H:K", 19)
                database_output_sheet.freeze_panes(1,0)
            logging.info("All changes have been written to database/database.xlsx.")
            bot.bot.reply_to(message, f"Добавлено {len(new_cell_names)} {records_amount_case(len(new_cell_names), False)} в базу.\nИзменён статус {len(modified_cell_names)} {records_amount_case(len(modified_cell_names), True)} в базе.")
        else:
            bot.bot.reply_to(message, "Служебная записка не содержит новых записей. Изменений в базу не внесено.")
            logging.info("Done — no changes to the database.")
    except Exception as e:
        bot.bot.reply_to(message, f"❌ Произошла непредвиденная ошибка при добавлении служебной записки в базу.\nПроверьте, что отправили файл в нужном формате.\n\n{e}")
        logging.exception(e)
    try:
        os.remove(file)
    except Exception as e:
        logging.exception(f"Couldn't remove temporary input file {file}: {e}")

def records_amount_case(amount_int, is_genitive: bool):
    amount = str(amount_int)
    if amount.endswith("1") and not amount.endswith("11"):
        if is_genitive:
            return "записи"
        else:
            return "запись"
    elif is_genitive:
        return "записей"
    elif (amount.endswith("2") or amount.endswith("3") or amount.endswith("4")) and not(amount.endswith("12") or amount.endswith("13") or amount.endswith("14")):
        return "записи"
    else:
        return "записей"

def analyze_stats(message):
    try:
        if config.read_database_on_each_input:
            read_database()
        global database
        logging.info("Loading stats...")
        stats = pandas.read_excel("database/stats.xlsx")

        # Sheet 2 - Stats by Cell

        stats_nonzero_traffic = stats.loc[pandas.to_numeric(stats["TRAFFIC DATA 3G"], errors="coerce").fillna(0) + pandas.to_numeric(stats["TRAFFIC DATA 4G"], errors="coerce").fillna(0) != 0]
        logging.info(f"Found {len(stats_nonzero_traffic)} nonzero traffic records. Checking which of these have CustomStatus == 'on' in the database...")
        custom_status_nonzero_records = database.merge(stats_nonzero_traffic, left_on="CellName", right_on="CELL_MNEMONIC")[["CellName", "TRAFFIC DATA 3G", "TRAFFIC DATA 4G", "BSID", "Филиал", "CustomStatus"]].loc[database["CustomStatus"] == "on"]
        total_custom_status_nonzero_records = len(custom_status_nonzero_records)
        logging.info(f"That's {total_custom_status_nonzero_records} records.")

        # Sheet 1 - Stats by Department

        logging.info(f"Now checking unique occurrences of CellName and BSID per department and wrapping up.")
        custom_status_nonzero_records_by_department = custom_status_nonzero_records.groupby(["Филиал"]).agg(
            CellNames=("CellName", "nunique"),
            BSIDs=("BSID", "nunique")
        ).reset_index()

        with pandas.ExcelWriter("output/stats.xlsx", engine="xlsxwriter") as stats_output:
            custom_status_nonzero_records_by_department.to_excel(stats_output, index=False, sheet_name="Филиалы")
            custom_status_nonzero_records.to_excel(stats_output, index=False, sheet_name="Cells")
            stats_output_sheet_departments = stats_output.sheets["Филиалы"]
            stats_output_sheet_departments.set_column("A:C", 19)
            stats_output_sheet_departments.freeze_panes(1,1)
            stats_output_sheet_cells = stats_output.sheets["Cells"]
            stats_output_sheet_cells.set_column("A:F", 19)
            stats_output_sheet_cells.freeze_panes(1,1)
        logging.info(f"Written to output/stats.xlsx.")
        status_output_file = open("output/stats.xlsx", "rb")
        bot.bot.send_document(message.chat.id, status_output_file, caption=f"Сводная таблица готова.\nВсего {total_custom_status_nonzero_records} {records_amount_case(total_custom_status_nonzero_records, False)} с 3G/4G-трафиком.\n\nСгенерировано {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", reply_to_message_id=message.message_id)
    except Exception as e:
        bot.bot.reply_to(message, f"❌ Произошла непредвиденная ошибка при анализе статистики.\n\n{e}")
        logging.exception(e)
