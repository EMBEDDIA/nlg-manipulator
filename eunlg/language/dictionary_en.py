TEMPLATES = {
    # data
    "cphi": ["the", 1, "for", "price", "category", 2],  # cphi(0)_hicp2015(1)_cp-hi00(2)
    "income": [2, 1, 3, 4],  # income(0)_total(1)_f(2)_med-e(3)_eur(4)
    "health": [2, 1],  # health(0)_pc-che(1)_hf3(2)
    "env": ["the national expenditure in the category of", 1, "in charasteristics of", 2, "was in", 3],  # env_cepa3_eps-p1_mio-eur

    # general
    "month": "in {} {}",  # month, year
    "year": "in {}",  # year
    "year_change": "from {} to {}",  # from year to year
    "month_change": "from {} {} to {} {}",  # from month year to month year
    "place": "in {}",  # area_name
}

CPHI = {
    "hicp2015": ["harmonized", "consumer", "price", "index", "was"],  # harmonized consumer price index (2015=100)
    "rt1": ["value of HICP did", "grow", "from", "previous", "month"],  # growth rate on previous period (t/t-1)
    "rt12": ["growth", "rate", "was"],  # growth rate (t/t-12)
    "cp-hi00": ["all", "items"],
    "cp-hi01": ["food", "and non-alcoholic beverages"],
    "cp-hi02": ["alcoholic", "beverages", "and tobacco"],
    "cp-hi03": ["clothing", "and", "footwear"],
    "cp-hi04": ["housing, water,", "electric", "power, and gas and", "other", "fuels"],
    "cp-hi05": ["furnishings, household", "equipment", "and", "maintenance"],
    "cp-hi06": ["health"],
    "cp-hi07": ["transport"],
    "cp-hi08": ["communication"],
    "cp-hi09": ["recreation", "and", "culture"],
    "cp-hi10": ["education"],
    "cp-hi11": ["hotels, cafes and", "restaurants"],
    "cp-hi12": ["miscellaneous", "goods and services"],
    "cp-hi00xef": ["all items", "except", "energy, food,", "alcohol", "and", "tobacco"],
    "cp-hi00xtb": ["all items", "except", "tobacco"],
    "cp-hie": ["energy"],
    "cp-hif": ["food"],
    "cp-hifu": ["unprocessed", "food"],
    "cp-hig": ["all", "goods"],
    "cp-hiig": ["industrial", "goods"],
    "cp-his": ["all", "services"],
    "cp-hiigxe": ["other than energy", "{related, replace=True}", "industrial", "goods"],
    "cp-hi00xe": ["all items", "except", "energy"],
    "cp-hi00xefu": ["all items", "except", "energy and", "unprocessed", "food"],
    "cp-hi00xes": ["all items", "except", "energy and", "seasonal", "food"],
}

INCOME = {
    "f": ["women"],
    "m": ["males"],
    "t": ["people"],
    "eur": ["€"],
    "nac": ["in", "local", "currency of the", "country"],
    "pps": ["when expressed in purchasing power standard"],
    "med-e": ["got", "median", "net", "{salary, replace=True}", "of"],
    "mei-e": ["got", "mean", "net income of"],
    "total": ["all ages"],
    "y-lt6": ["less", "than 6 years of age"],
    "y6-10": ["from 6 to 10 years of age"],
    "y6-11": ["from 6 to 11 years of age"],
    "y11-15": ["from 11 to 15 years of age"],
    "y12-17": ["from 12 to 17 years of age"],
    "y-lt16": ["less", "than 16 years of age"],
    "y16-24": ["from 16 to 24 years of age"],
    "y16-64": ["from 16 to 64 years of age"],
    "y-ge16": ["16 years of age or", "older"],
    "y-lt18": ["18 years of age or", "{younger, replace=True}"],
    "y18-24": ["from 18 to 24 years of age"],
    "y18-64": ["from 18 to 64 years of age"],
    "y-ge18": ["18 years of age or", "older"],
    "y25-49": ["from 25 to 49 years of age"],
    "y25-54": ["from 25 to 54 years of age"],
    "y50-64": ["from 50 to 64 years of age"],
    "y55-64": ["from 55 to 64 years of age"],
    "y-lt60": ["60 years of age or", "{younger, replace=True}"],
    "y-ge60": ["60 years of age or", "older"],
    "y-lt65": ["65 years of age or", "{younger, replace=True}"],
    "y65-74": ["from 65 to 74 years of age"],
    "y-ge65": ["65 years of age or", "older"],
    "y-lt75": ["75 years of age or", "{younger, replace=True}"],
    "y-ge75": ["75 years of age or", "older"],
}

HEALTH = {
    "hf3": ["households did", "{make, replace=True}", "a monetary", "contribution", "of"],
    "pc-che": ["%", "towards", "their", "own", "healthcare"],
}

ENV = {
    "tot_cepa": "total environmental protection activities",
    "cepa1_4-9": "protection of ambient air and climate; protection and remediation of soil, groundwater and surface water; noise and vibration abatement; protection...",
    "cepa1": "protection of ambient air and climate",
    "cepa112_122": "protection of climate and ozone layer",
    "cepa2": "wastewater management",
    "cepa3": "waste management",
    "cepa4": "protection and remediation of soil, groundwater and surface water",
    "cepa5": "noise and vibration abatement (excluding workplace protection)",
    "cepa6": "protection of biodiversity and landscapes",
    "cepa7": "protection against radiation (excluding external safety)",
    "cepa8": "environmental research and development",
    "cepa9": "other environmental protection activities",
    "eps-p1": "output",
    "eps-p11": "market output",
    "eps-p13": "non-market output",
    "eps-p1-anc": "environmental protection related ancillary output",
    "eps-p2-eps-sp": "intermediate consumption of environmental protection services by corporations as specialist producers",
    "p3-eps": "final consumption expenditure of environmental protection services",
    "eps-p51g-np": "gross fixed capital formation and acquisition less disposals of non-produced non-financial assets",
    "p7-eps": "import of environmental protection services",
    "p6-eps": "export of environmental protection services",
    "eps-d21x31": "taxes less subsidies on products",
    "eps-sup-nu": "supply at purchasers' prices available for national uses",
    "ep-d3-7-92-99-p": "current and capital transfers for environmental protection, paid",
    "mio-eur": "million euros",
    "mio-nac": "million units of national currency",
}

DATA = {
    "cphi": CPHI,
    "income": INCOME,
    "health": HEALTH,
    "env": ENV,
}

SMALL_ORDINALS = {
    "1": "first",
    "2": "second",
    "3": "third",
    "4": "fourth",
    "5": "fifth",
    "6": "sixth",
    "7": "seventh",
    "8": "eighth",
    "9": "ninth",
    "10": "tenth",
    "11": "eleventh",
    "12": "twelfth",
    "else": "th",
}

SMALL_CARDINALS = {
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
    "10": "ten",
}

MONTHS = {
    "01": "January",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
    "reference_options": ["during the month", "also", "at the same time"],
}

YEARS = {
    "reference_options": ["in the same year", "also during the same year", "also"],
}

PLACES = {
    "M": "the municipality",
    "C": "the country",
}

COUNTRIES = {
    "EA": "Euro area (at that point in time)",  # (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)
    "EA19": "Euro area (19 countries)",
    "EA18": "Euro area (18 countries)",
    "EU": "European Union (at that point in time)",  # (EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)
    "EU28": "European Union (28 countries)",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DE": "Germany",  # (until 1990 former territory of the FRG)
    "EE": "Estonia",
    "IE": "Ireland",
    "EL": "Greece",
    "ES": "Spain",
    "FR": "France",
    "HR": "Croatia",
    "IT": "Italy",
    "CY": "Cyprus",
    "LV": "Latvia",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "HU": "Hungary",
    "MT": "Malta",
    "NL": "Netherlands",
    "AT": "Austria",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "FI": "Finland",
    "SE": "Sweden",
    "UK": "the United Kingdom",
    "IS": "Iceland",
    "NO": "Norway",
    "CH": "Switzerland",
    "MK": "North Macedonia",
    "RS": "Serbia",
    "TR": "Turkey",
    "US": "the United States",
}

COMPARISONS = {
    "more": "more than",
    "less": "less than",
    "eu": "EU average",
    "us": "US average",
    "similar": "the average for countries that are considered to be similar",
    "highest": "highest",
    "lowest": "lowest",
    "rank": "compared to other countries",
}
