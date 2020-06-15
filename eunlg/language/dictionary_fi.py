TEMPLATES = {
    # data
    "cphi": [2, 1],  # cphi_hicp2015_cp-hi00
    "income": [1, 2, 3, "oli", 4],  # income(0)_total(1)_f(2)_med-e(3)_eur(4)
    "health": [2, 1],  # health_pc-che_hf3

    # general
    "month": "{} {}",  # month, year
    "year": "vuonna {}",  # year
    "year_change": "vuodesta {} vuoteen {}",  # from year to year
    "month_change": "ajasta {} {} aikaan {} {}",  # from month year to month year
    "place": "{}",  # area_name
}

CPHI = {
    "hicp2015": ["yhdenmukaistettu", "kuluttajahintaindeksi", "oli"],  # harmonized consumer price index (2015=100)
    "rt1": ["kuluttajahintaindeksi", "kasvoi edellisestä", "kuukaudesta"],  # growth rate on previous period (t/t-1)
    "rt12": ["kuluttajahintaindeksi", "kasvoi edellisestä vuodesta"],  # growth rate (t/t-12)
    "cp-hi00": ["kaikki"],
    "cp-hi01": ["ruuan ja", "{empty, pos=DT}", "alkoholittomien", "juomien"],
    "cp-hi02": ["alkoholijuomat", "ja", "tupakka"],
    "cp-hi03": ["vaatteet", "ja", "kengät"],
    "cp-hi04": ["asuminen, vesi, sähkö, bensiini ja", "muut", "polttoaineet"],
    "cp-hi05": ["kalusteet, kodinkoneet ja", "kunnossapito"],
    "cp-hi06": ["terveyden"],
    "cp-hi07": ["kuljetus"],
    "cp-hi08": ["viestintä"],
    "cp-hi09": ["viihteen ja kulttuurin"],
    "cp-hi10": ["koulutus"],
    "cp-hi11": ["hotellit, kahvilat ja", "ravintolat"],
    "cp-hi12": ["sekalaisien", "tuotteiden ja palveluiden"],
    "cp-hi00xef": ["kaikki tuotteet", "lukuunottamatta", "energiaa, ruokaa, alkoholia ja tupakkaa"],
    "cp-hi00xtb": ["kaikki tuotteet", "lukuunottamatta", "tupakkaa"],
    "cp-hie": ["energia"],
    "cp-hif": ["ruoka"],
    "cp-hifu": ["prosessoimaton", "ruoka"],
    "cp-hig": ["kaikki", "tuotteet"],
    "cp-hiig": ["teollisuuuden", "tuotteet"],
    "cp-his": ["kaikki", "palvelut"],
    "cp-hiigxe": ["muut kuin energiaan", "liittyvät", "teollisuuden tuotteet"],
    "cp-hi00xe": ["kaikki", "lukuunottamatta", "energiaa"],
    "cp-hi00xefu": ["kaikki lukuunottamatta energiaa ja", "prosessoimatonta", "ruokaa"],
    "cp-hi00xes": ["kaikki lukuunottamatta energiaa ja", "sesonkiruokaa"],
}

INCOME = {
    "f": ["naisten"],
    "m": ["miesten"],
    "t": [""], # no need to lexicalize
    "eur": ["€"],
    "nac": ["paikallisessa", "valuutassa", "ilmaistuna"],
    "pps": ["ostovoiman", "standardissa", "ilmaistuna"],
    "med-e": ["tulojen", "mediaani"],
    "mei-e": ["keskitulo"],
    "total": [""],
    "y-lt6": ["6-vuotiaiden", "ja nuorempien"],
    "y6-10": ["6-10-vuotiaiden"],
    "y6-11": ["6-11-vuotiaiden"],
    "y11-15": ["11-15-vuotiaiden"],
    "y12-17": ["12-17-vuotiaiden"],
    "y-lt16": ["16-vuotiaiden", "ja nuorempien"],
    "y16-24": ["16-24-vuotiaiden"],
    "y16-64": ["16-64-vuotiaiden"],
    "y-ge16": ["16-vuotiaiden ja sitä vanhempien"],
    "y-lt18": ["18-vuotiaiden", "ja nuorempien"],
    "y18-24": ["18-24-vuotiaiden"],
    "y18-64": ["18-64-vuotiaiden"],
    "y-ge18": ["18-vuotiaiden ja sitä vanhempien"],
    "y25-49": ["25-49-vuotiaiden"],
    "y25-54": ["25-54-vuotiaiden"],
    "y50-64": ["50-64-vuotiaiden"],
    "y55-64": ["55-64-vuotiaiden"],
    "y-lt60": ["60-vuotiaiden", "ja nuorempien"],
    "y-ge65": ["65-vuotiaiden ja sitä vanhempien"],
    "y-ge60": ["60-vuotiaiden ja sitä vanhempien"],
    "y-lt65": ["65-vuotiaiden", "ja nuorempien"],
    "y65-74": ["65-74-vuotiaiden"],
    "y-ge65": ["65-vuotiaiden ja sitä vanhempien"],
    "y-lt75": ["alle", "75-vuotiaiden"],
    "y-ge75": ["75-vuotiaiden ja", "vanhempien"],
    "y-lt75": ["75-vuotiaiden", "ja nuorempien"],
}

HEALTH = {
    "hf3": ["{empty, pos=DT}", "kotitaloudet", "maksoivat", "terveydenhuollostaan", "itse"],
    "pc-che": ["%"],
}

DATA = {
    "cphi": CPHI,
    "income": INCOME,
    "health": HEALTH,
}

COUNTRIES = {
    "EA": "euroalue (kyseisellä ajanhetkellä)",  # (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)
    "EA19": "euroalue (19 maata)",
    "EA18": "euroalue (18 maata)",
    "EU": "Euroopan unioni (kyseisellä ajanhetkellä)",  # (EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)
    "EU28": "Euroopan unioni (28 maata)",
    "BE": "Belgiassa",
    "BG": "Bulgariassa",
    "CZ": "Tsekissä",
    "DK": "Tanskassa",
    "DE": "Saksassa",
    "EE": "Eestissä",
    "IE": "Irlannissa",
    "EL": "Kreikassa",
    "ES": "Espanjassa",
    "FR": "Ranskassa",
    "HR": "Kroatiassa",
    "IT": "Italiassa",
    "CY": "Kyproksella",
    "LV": "Latviassa",
    "LT": "Liettuassa",
    "LU": "Luxemburgissa",
    "HU": "Unkarissa",
    "MT": "Maltalla",
    "NL": "Alankomaissa",
    "AT": "Itävalassa",
    "PL": "Puolassa",
    "PT": "Portugalissa",
    "RO": "Romaniassa",
    "SI": "Sloveniassa",
    "SK": "Slovakiassa",
    "FI": "Suomessa",
    "SE": "Ruotsissa",
    "UK": "Yhdistyneesä Kuningaskunnassa",
    "IS": "Islannissa",
    "NO": "Norjassa",
    "CH": "Sveitsissä",
    "MK": "Pohjois-Makedoniassa",
    "RS": "Serbiassa",
    "TR": "Turkissa",
    "US": "Yhdysvalloissa",
}

PLACES = {
    "M": "kunta",
    "C": "maa",
}

COMPARISONS = {
    "more": "enemmän kuin",
    "less": "vähemmän kuin",
    "eu": "Euroopan Unionin keskiarvo",
    "us": "Yhdysvaltojen keskiarvo",
    "similar": "keskiarvo maille, joita pidetään samankaltaisina",
    "highest": "korkein",
    "lowest": "matalin",
    "rank": "verrattuna muihin maihin",
}

SMALL_ORDINALS = {
    "1": "ensimmäinen",
    "2": "toinen",
    "3": "kolmas",
    "4": "neljäs",
    "5": "viides",
    "6": "kuudes",
    "7": "seitsemäs",
    "8": "kahdeksas",
    "9": "yhdeksäs",
    "10": "kymmenes",
    "else": ".",
}

SMALL_CARDINALS = {
    "1": "yksi",
    "2": "kaksi",
    "3": "kolme",
    "4": "neljä",
    "5": "viisi",
    "6": "kuusi",
    "7": "seitsemän",
    "8": "kahdeksan",
    "9": "yhdeksän",
    "10": "kymmenen",
}

MONTHS = {
    "01": "tammikuussa",
    "02": "helmikuussa",
    "03": "maaliskuussa",
    "04": "huhtikuussa",
    "05": "toukokuussa",
    "06": "kesäkuussa",
    "07": "heinäkuussa",
    "08": "elokuussa",
    "09": "syyskuussa",
    "10": "lokakuussa",
    "11": "marraskuussa",
    "12": "joulukuussa",
    "reference_options": ["kyseisessä kuussa", "myös", "samaan aikaan"],
}

YEARS = {
    "reference_options": ["samana vuonna", "myös samana vuonna", "myös"],
}
