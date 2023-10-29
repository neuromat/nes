PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 127
PASSWORD_REGEX = r"^(?=.*\d)(?=.*[a-z]).{8,127}$"

FIRSTNAME_REGEX = r"^[a-zA-Z]+((\s|\-)[a-zA-Z]+)?$"
LASTNAME_REGEX = r"^[a-zA-Z]+((\s|\-)[a-zA-Z]+)?$"

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


USERNAME_REGEX = r"^[A-Za-z][A-Za-z0-9_.]{4,29}$"
