TEMPLATES = {
    'cphi': [1, 'oli hintakategorialle', 2], # cphi_hicp2015_cp-hi00
    'income': [2, 'ikäryhmässä', 1, 3, 'oli', 4], # income(0)_total(1)_f(2)_med-e(3)_eur(4)
    'health': [1, 'oli', 2], # health_pc-che_hf3
    'month_ssa': 'ajassa {} {}',
    'year_ssa': 'vuonna {}',
}

CPHI = {
    'hicp2015': 'yhdenmukaistettu kuluttajahintaindeksi', # harmonized consumer price index (2015=100)
    'rt1': 'kasvutahti verrattuna edelliseen kuukauteen', # growth rate on previous period (t/t-1)
    'rt12': 'kasvutahti', # growth rate (t/t-12)
    'cp-hi00': 'kaikki',
    'cp-hi01':	'ruoka ja alkoholittomat juomat',
    'cp-hi02':	'alkoholijuomat ja tupakka',
    'cp-hi03':	'vaatteet ja kengät',
    'cp-hi04':	'asuminen, vesi, sähkö, bensiini ja muut polttoaineet',
    'cp-hi05':	'kalusteet, kodinkoneet ja kunnossapito',
    'cp-hi06':	'terveys',
    'cp-hi07':	'kuljetus',
    'cp-hi08':	'viestintä',
    'cp-hi09': 'viihde ja kulttuuri',
    'cp-hi10':	'koulutus',
    'cp-hi11':	'hotellit, kahvilat ja ravintolat',
    'cp-hi12':	'sekalaiset tuotteet ja palvelut',
    'cp-hi00xef': 'kaikki tuotteet poislukien energia ruoka, alkoholi ja tupakka',
    'cp-hi00xtb': 'kaikki tuotteet poislukien tupakka',
    'cp-hie': 'energia',
    'cp-hif': 'ruoka',
    'cp-hifu':	'prosessoimaton ruoka',
    'cp-hig': 'kaikki tuotteet',
    'cp-hiig':	'teollisuustuotteet',
    'cp-his': 'kaikki palvelut',
    'cp-hiigxe': 'ei-energia teollisuustuotteet',
    'cp-hi00xe': 'kaikki poislukien energia',
    'cp-hi00xefu': 'kaikki poislukien energia ja prosessoimaton ruoka',
    'cp-hi00xes': 'kaikki poislukien energia ja sesonkiruoka',
}

INCOME = {
    'f': 'naisten',
    'm': 'miesten',
    't': 'kaikkien sukupuolien',
    'eur': 'euroissa',
    'nac': 'paikallisessa valuutassa',
    'pps': 'ostovoiman standardissa',
    'med-e': 'tasoitettu mediaanitulo',
    'mei-e': 'tasoitettu keskitulo',
    'total': 'kaikki',
    'y-lt6': 'nuorempi kuin 6 vuotta',
    'y6-10': '6-10 vuotta',
    'y6-11': '6-11 vuotta',
    'y11-15': '11-15 vuotta',
    'y12-17': '12-17 vuotta',
    'y-lT16': 'nuorempi kuin 16 vuotta',
    'y16-24': '16-24 vuotta',
    'y16-64': '16-64 vuotta',
    'y-ge16': '16 vuotta tai enemmän',
    'y-lT18': 'nuorempi kuin 18 vuotta',
    'y18-24': '18-24 vuotta',
    'y18-64': '18-64 vuotta',
    'y-ge18': '18 vuotta tai enemmän',
    'y25-49': '25-49 vuotta',
    'y25-54': '25-54 vuotta',
    'y50-64': '50-64 vuotta',
    'y55-64': '55-64 vuotta',
    'y-lT60': 'nuorempi kuin 60 vuotta',
    'y-ge60': '60 vuotta tai enemmän',
    'y-lT65': 'nuorempi kuin 65 vuotta',
    'y65-74': '65-74 vuotta',
    'y-ge65': '65 vuotta tai enemmän',
    'y-lT75': 'nuorempi kuin 75 vuotta',
    'y-ge75': '75 vuotta tai enemmän',
}

HEALTH = {
    'hf3': "kotitalouksien suoraan maksamana",
    'pc-che': "prosentuaalinen osuus nykyisistä terveysmenoista",
}

COUNTRIES = {
  'EA': 'euroalue (EA11-2000, EA12-2006, EA13-2007, EA15-2008, EA16-2010, EA17-2013, EA18-2014, EA19)',
	'EA19': 'euroalue (19 maata)',
	'EA18':	'euroalue (18 maata)',
	'EU': 'Euroopan unioni (EU6-1958, EU9-1973, EU10-1981, EU12-1986, EU15-1995, EU25-2004, EU27-2007, EU28-2013)',
	'EU28':	'Euroopan unioni - 28 maata',
	'BE': 'Belgia',
	'BG': 'Bulgaria',
	'CZ': 'Tsekki',
	'DK': 'Tanska',
	'DE': 'Saksa',
	'EE': 'Eesti',
	'IE': 'Irlanti',
	'EL': 'Kreikka',
	'ES': 'Espanja',
	'FR': 'Ranska',
	'HR': 'Kroatia',
	'IT': 'Italia',
	'CY': 'Kypros',
	'LV': 'Latvia',
	'LT': 'Liettua',
	'LU': 'Luxemburg',
	'HU': 'Unkari',
	'MT': 'Malta',
	'NL': 'Alankomaat',
	'AT': 'Itävalta',
	'PL': 'Puola',
	'PT': 'Portugali',
	'RO': 'Romania',
	'SI': 'Slovenia',
	'SK': 'Slovakia',
	'FI': 'Suomi',
	'SE': 'Ruotsi',
	'UK': 'Yhdistynyt Kuningaskunta',
	'IS': 'Islanti',
	'NO': 'Norja',
	'CH': 'Sveitsi',
	'MK': 'Pohjois-Makedonia',
	'RS': 'Serbia',
	'TR': 'Turkki',
	'US': 'Yhdysvallat',
}

PLACES = {
    'M': 'kunta',
    'C': 'maa',
}

COMPARISONS = {
    'more': 'enemmän kuin',
    'less': 'vähemmän kuin',
    'eu': "Euroopan Unionin keskiarvo",
    'us': "Yhdysvaltojen keskiarvo",
    'similar': "keskiarvo maille, joita pidetään samankaltaisina",
    'highest': 'korkein',
    'lowest': 'matalin',
    'rank': 'verrattuna muihin maihin',
}

SMALL_ORDINALS = {
    '1': "ensimmäinen",
    '2': "toinen",
    '3': "kolmas",
    '4': "neljäs",
    '5': "viides",
    '6': "kuudes",
    '7': "seitsemäs",
    '8': "kahdeksas",
    '9': "yhdeksäs",
    '10': "kymmenes",
}

ORDINALS = {
    'else': '.',
}

SMALL_CARDINALS = {
    '1': "yksi",
    '2': "kaksi",
    '3': "kolme",
    '4': "neljä",
    '5': "viisi",
    '6': "kuusi",
    '7': "seitsemän",
    '8': "kahdeksan",
    '9': "yhdeksän",
    '10': "kymmenen",
}

MONTHS = {
    '01': "tammikuu",
    '02': "helmikuu",
    '03': "maaliskuu",
    '04': "huhtikuu",
    '05': "toukokuu",
    '06': "kesäkuu",
    '07': "heinäkuu",
    '08': "elokuu",
    '09': "syyskuu",
    '10': "lokakuu",
    '11': "marraskuu",
    '12': "joulukuu",
    'reference_options': ["kyseisessä kuussa", "myös", "samaan aikaan"],
}

YEARS = {
    'reference_options': ["samana vuonna", "myös samana vuonna", "myös"],
}
