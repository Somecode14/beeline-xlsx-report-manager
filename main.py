import logging

testing = False

if testing:
    # TESTING
    logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]: %(message)s', level=logging.DEBUG)
    logging.warning("Testing mode active. Disable before going to production.")
    import xlsx
    xlsx.get_worksheet("input/Формат 2.xlsx")
    exit()
else:
    # Enables logging.
    logging.basicConfig(format='[%(asctime)s %(name)s %(levelname)s]: %(message)s', level=logging.INFO)

import bot