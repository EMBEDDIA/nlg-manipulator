TEMPLATES = {
    # data
    'cphi': [1, 'war', 'für Preisklasse', 2], # cphi(0)_hicp2015(1)_cp-hi00(2)
    'income': ['bei', 2, 'in der Altersgruppe', 1, '', 3, 'war in', 4], # income(0)_bistal(1)_f(2)_med-e(3)_eur(4)
    'health': ['der', 1, 'war für', 2], # health(0)_pc-che(1)_hf3(2)

    # general
    'month': 'im {} {}', # month, year
    'year': 'im Jahr {}', # year
    'year_change': 'von {} bis {}', # von {year} bis {year}
    'month_change': 'von {} {} bis {} {}', # von month year bis month year
    'place': 'in {}', # area_name
}

CPHI = {
    'hicp2015': 'harmonisierten Verbraucherpreisindex', # harmonized consumer price index (2015=100)
    'rt1': 'Wachstumsrate gegenüber dem Vormonat', # growth rate on previous period (t/t-1)
    'rt12': 'Wachstumsrate gegenüber dem Vorjahr', # growth rate (t/t-12)
    'cp-hi00': 'alle Artikel',
    'cp-hi01': 'Lebensmittel und alkoholfreie Getränke',
    'cp-hi02': 'alkoholische Getränke und Tabak',
    'cp-hi03': 'Kleidung und Schuhe',
    'cp-hi04': 'Wohnen, Wasser, Elektrizität, Gas und andere Brennstoffe',
    'cp-hi05': 'Einrichtung, Haushaltsausstattung und Wartung',
    'cp-hi06': 'Gesundheit',
    'cp-hi07': 'Transport',
    'cp-hi08': 'Kommunikation',
    'cp-hi09': 'Erholung und Kultur',
    'cp-hi10': 'Bildung',
    'cp-hi11': 'Hotels, Cafés und Restaurants',
    'cp-hi12': 'verschiedene Waren und Dienstleistungen',
    'cp-hi00xef': 'alle Artikel außer Energie, Lebensmittel, Alkohol und Tabak',
    'cp-hi00xtb': 'alle Artikel außer Tabak',
    'cp-hie': 'Energie',
    'cp-hif': 'Lebensmittel',
    'cp-hifu': 'unverarbeitetes Lebensmittel',
    'cp-hig': 'Waren ingesamt',
    'cp-hiig': 'Industriegüter',
    'cp-his': 'Dienstleistungen ingesamt',
    'cp-hiigxe': 'nicht energiebezogene Industriegüter',
    'cp-hi00xe': 'alle Artikel außer Energie',
    'cp-hi00xefu': 'alle Artikel außer Energie und unverarbeitetes Lebensmittel',
    'cp-hi00xes': 'alle Artikel ohne Energie und saisonale Lebensmittel',
}

INCOME = {
    'f': 'Frauen',
    'm': 'Männer',
    't': 'alle Geschlechter',
    'eur': 'Euro',
    'nac': 'nationale Währung',
    'pps': 'Kaufkraftstandard',
    'med-e': 'Median des äquivalenten Nettoeinkommens',
    'mei-e': 'mittleres äquivalenziertes Nettoeinkommen',
    'total': 'jedes Alter',
    'y-lt6': 'weniger als 6 Jahre',
    'y6-10': 'von 6 bis 10 Jahren',
    'y6-11': 'von 6 bis 11 Jahren',
    'y11-15': 'von 11 bis 15 Jahren',
    'y12-17': 'von 12 bis 17 Jahren',
    'y-lT16': 'less than 16 Jahren',
    'y16-24': 'von 16 bis 24 Jahren',
    'y16-64': 'von 16 bis 64 Jahren',
    'y-ge16': '16 Jahren oder älter',
    'y-lT18': 'less than 18 Jahren',
    'y18-24': 'von 18 bis 24 Jahren',
    'y18-64': 'von 18 bis 64 Jahren',
    'y-ge18': '18 Jahren oder älter',
    'y25-49': 'von 25 bis 49 Jahren',
    'y25-54': 'von 25 bis 54 Jahren',
    'y50-64': 'von 50 bis 64 Jahren',
    'y55-64': 'von 55 bis 64 Jahren',
    'y-lt60': 'less than 60 Jahren',
    'y-ge60': '60 Jahren oder älter',
    'y-lt65': 'less than 65 Jahren',
    'y65-74': 'von 65 bis 74 Jahren',
    'y-ge65': '65 Jahren oder älter',
    'y-lt75': 'less than 75 Jahren',
    'y-ge75': '75 Jahren oder älter',
}

HEALTH = {
    'hf3': "Haushalt Auszahlung",
    'pc-che': "prozentualer Anteil an den gesamten laufenden Gesundheitsausgaben",
}

DATA =  {
    'cphi': CPHI,
    'income': INCOME,
    'health': HEALTH,
}

SMALL_ORDINALS = {
    '1': "erste",
    '2': "zweite",
    '3': "dritte",
    '4': "vierte",
    '5': "fünfte",
    '6': "sechste",
    '7': "siebte",
    '8': "achte",
    '9': "neunte",
    '10': "zehnte",
    '11': "elfte",
    '12': "twölfte",
    'else': '.',
}

SMALL_CARDINALS = {
    '1': "eins",
    '2': "zwei",
    '3': "drei",
    '4': "vier",
    '5': "fünf",
    '6': "sechs",
    '7': "sieben",
    '8': "acht",
    '9': "neun",
    '10': "zehn",
    '11': 'elf',
    '12': 'zwölf',
}

MONTHS = {
    '01': "Januar",
    '02': "Februar",
    '03': "März",
    '04': "April",
    '05': "Mai",
    '06': "Juni",
    '07': "Juli",
    '08': "August",
    '09': "September",
    '10': "Oktober",
    '11': "November",
    '12': "Dezember",
    'reference_options': ["auch im selben Monat", "gleichzeitich"],
}

YEARS = {
    'reference_options': ["auch im selben Jahr", "gleichzeitich"],
}

PLACES = {
    'M': 'die Gemeinde',
    'C': 'das Land',
}

COUNTRIES = {
    'EA': 'Euro Gebiet (zu diesem Zeitpunkt)', #(EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)
    'EA19': 'Euro Gebiet (19 Länder)',
    'EA18':	'Euro Gebiet (18 Länder)',
    'EU': 'Europäische Union (zu diesem Zeitpunkt)', #(EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)',
    'EU28':	'Europäische Union (28 Länder)',
    'BE': 'Belgien',
    'BG': 'Bulgarien',
    'CZ': 'Tschechien',
    'DK': 'Dänemark',
    'DE': 'Deutschland', #(until 1990 former territory of the FRG)
    'EE': 'Estland',
    'IE': 'Irland',
    'EL': 'Griechenland',
    'ES': 'Spanien',
    'FR': 'Frankreich',
    'HR': 'Kroatien',
    'IT': 'Italien',
    'CY': 'Zypern',
    'LV': 'Lettland',
    'LT': 'Litauen',
    'LU': 'Luxemburg',
    'HU': 'Ungarn',
    'MT': 'Malta',
    'NL': 'Niederlande',
    'AT': 'Österreich',
    'PL': 'Polen',
    'PT': 'Portugal',
    'RO': 'Rumänien',
    'SI': 'Slowenien',
    'SK': 'Slowakei',
    'FI': 'Finnland',
    'SE': 'Schweden',
    'UK': 'Großbritannien',
    'IS': 'Island',
    'NO': 'Norwegen',
    'CH': 'Schweiz',
    'MK': 'Nordmakedonien',
    'RS': 'Serbien',
    'TR': 'Türkei',
    'US': 'der Vereinigte Staaten',
}

COMPARISONS = {
    'more': 'mehr als',
    'less': 'weniger als',
    'eu': "der Durchschnitt der EU",
    'us': "der Durchschnitt der US",
    'similar': "der Durchschnitt für ähnliche Länder",
    'highest': 'der höchste',
    'lowest': 'der niedrigste',
    'rank': 'im Vergleich zu anderen Ländern',
}