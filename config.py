
# CONFIG

read_database_on_each_input = False
# Reloads the database file on each .xlsx document sent by users.
# `False` is recommended unless the file is modified externally.
#
# `False` — loads the database file only when the script starts, then keeps the data in RAM, writing the file every time it gets modified.
# `True` — reloads the database file after each user input.