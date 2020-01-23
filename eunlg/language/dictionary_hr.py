TEMPLATES = {
    # data
    "cphi": [1, "je za cijenovnu kategoriju", 2, "bio"],  # cphi(0)_hicp2015(1)_cp-hi00(2)
    "income": ["among", 2, "in age group", 1, "the", 3, "was in", 4],  # income(0)_total(1)_f(2)_med-e(3)_eur(4)
    "health": ["the", 1, "was for", 2],  # health(0)_pc-che(1)_hf3(2)

    # general
    "month": "za {} mjesec {}. godine",  # month, year
    "year": "{}. godine",  # year
    "year_change": "u periodu {}‒{}",  # from year to year
    "month_change": "u periodu {} {}‒{} {}",  # from month year to month year
    "place": "{}case=ine",  # area_name
}

CPHI = {
    "hicp2015": "usklađeni indeks potrošačkih cijena",  # harmonized consumer price index (2015=100)
    "rt1": "stopa rasta u odnosu na prethodni mjesec",  # growth rate on previous period (t/t-1)
    "rt12": "stopa rasta u odnosu na prethodnu godinu",  # growth rate (t/t-12)
    "cp-hi00": "svih predmeta",
    "cp-hi01": "hrana i bezalkoholna pića",
    "cp-hi02": "alkoholna pića i duhan",
    "cp-hi03": "odjeća i obuća",
    "cp-hi04": "kućište, voda, električna energija, plin i druga goriva",
    "cp-hi05": "namještaj, oprema za kućanstvo i održavanje",
    "cp-hi06": "zdravlje",
    "cp-hi07": "prijevoz",
    "cp-hi08": "komunikacija",
    "cp-hi09": "rekreacija i kultura",
    "cp-hi10": "obrazovanje",
    "cp-hi11": "hoteli, kafići i restorani",
    "cp-hi12": "razne robe i usluge",
    "cp-hi00xef": "svih predmeta osim energije, hrane, alkohola i duhana",
    "cp-hi00xtb": "svih predmeta osim duhana",
    "cp-hie": "energija",
    "cp-hif": "hrana",
    "cp-hifu": "neobrađena hrana",
    "cp-hig": "ukupna roba",
    "cp-hiig": "industrijska roba",
    "cp-his": "ukupne usluge",
    "cp-hiigxe": "neenergetska industrijska roba",
    "cp-hi00xe": "svih predmeta osim energije",
    "cp-hi00xefu": "svih predmeta osim energije i neobrađene hrane",
    "cp-hi00xes": "svih predmeta osim energije i sezonske hrane",
}

INCOME = {
    "f": "ženke",
    "m": "mužjaci",
    "t": "svih spolova",
    "eur": "eura",
    "nac": "nacionalna valuta",
    "pps": "standard kupovne moći",
    "med-e": "srednji ekvivalentni neto prihod",
    "mei-e": "znači ekvivalentni neto prihod",
    "total": "svih dobnih skupina",
    "y-lt6": "manje od 6 godina",
    "y6-10": "od 6 do 10 godina",
    "y6-11": "od 6 do 11 godina",
    "y11-15": "od 11 do 15 godina",
    "y12-17": "od 12 do 17 godina",
    "y-lT16": "manje od 16 godina",
    "y16-24": "od 16 do 24 godine",
    "y16-64": "od 16 do 64 godine",
    "y-ge16": "16 godina ili više ",
    "y-lT18": "manje od 18 godina",
    "y18-24": "od 18 do 24 godine",
    "y18-64": "od 18 do 64 godine",
    "y-ge18": "18 godina ili više",
    "y25-49": "od 25 do 49 godina",
    "y25-54": "od 25 do 54 godine",
    "y50-64": "od 50 do 64 godine",
    "y55-64": "od 55 do 64 godine",
    "y-lt60": "manje od 60 godina",
    "y-ge60": "60 godina ili više",
    "y-lt65": "manje od 65 godina",
    "y65-74": "od 65 do 74 godine",
    "y-ge65": "65 ili više godina",
    "y-lt75": "manje od 75 godina",
    "y-ge75": "75 godina ili više ",
}

HEALTH = {
    "hf3": "plaćanje kućanstva iz vlastitog džepa",
    "pc-che": "postotni udio u ukupnim tekućim zdravstvenim izdacima",
}

DATA = {
    "cphi": CPHI,
    "income": INCOME,
    "health": HEALTH,
}

SMALL_ORDINALS = {  # masculine/feminine/neuter
    "1": "prvi/prva/prvo",
    "2": "drugi/druga/drugo",
    "3": "treći/treća/treće",
    "4": "četvrti/četvrta/četvrto",
    "5": "peti/peta/peto",
    "6": "šesti/šesta/šesto",
    "7": "sedmi/sedma/sedmo",
    "8": "osmi/osma/osmo",
    "9": "deveti/deveta/deveto",
    "10": "deseti/deseta/deseto",
    "11": "jedanaesti/jedanaesta/jedanaesto",
    "12": "dvanaesti/dvanaesta/dvanaesto",
    "else": ".",
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
    "01": "siječanj",
    "02": "veljača",
    "03": "ožujak",
    "04": "travanj",
    "05": "svibanj",
    "06": "lipanj",
    "07": "srpanj",
    "08": "kolovoz",
    "09": "rujan",
    "10": "listopad",
    "11": "studeni",
    "12": "prosinac",
    "reference_options": ["tijekom mjeseca", "također", "u isto vrijeme"],
}

YEARS = {
    "reference_options": ["u istoj godini", "također tijekom iste godine", "također"],
}

PLACES = {
    "M": "općina",
    "C": "zemlja",
}

COUNTRIES = {
    "EA": "Eurozona (u tom trenutku)",  # (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)
    "EA19": "Eurozona (19 država)",
    "EA18": "Eurozona (18 država)",
    "EU": "Europska unija (u tom trenutku)",  # (EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)
    "EU28": "Europska unija (28 država)",
    "BE": "Belgija",
    "BG": "Bugarska",
    "CZ": "Češka",
    "DK": "Danska",
    "DE": "Njemačka",  # (do 1990. bivša teritorija FRG)
    "EE": "Estonija",
    "IE": "Irska",
    "EL": "Grčka",
    "ES": "Španjolska",
    "FR": "Francuska",
    "HR": "Hrvatska",
    "IT": "Italija",
    "CY": "Cipar",
    "LV": "Latvija",
    "LT": "Litva",
    "LU": "Luksemburg",
    "HU": "Mađarska",
    "MT": "Malta",
    "NL": "Nizozemska",
    "AT": "Austrija",
    "PL": "Poljska",
    "PT": "Portugal",
    "RO": "Rumunjska",
    "SI": "Slovenija",
    "SK": "Slovačka",
    "FI": "Finska",
    "SE": "Švedska",
    "UK": "Velika Britanija",
    "IS": "Island",
    "NE": "Norveška",
    "CH": "Švicarska",
    "MK": "Sjeverna Makedonija",
    "RS": "Srbija",
    "TR": "Turska",
    "US": "Sjedinjene Države",
}

COMPARISONS = {
    "more": "više od",
    "less": "manje od",
    "eu": "projek EU",
    "us": "prosjek US",
    "similar": "prosjeka za zemlje za koje se smatraju slične",
    "highest": "najviši",
    "lowest": "najniža",
    "rank": "u usporedbi s drugim zemljama",
}
