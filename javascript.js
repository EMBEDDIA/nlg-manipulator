var cities=[
{"rank": 0, "city":"Helsinki", "population":562400, "latitude":60.170, "longitude":24.940},
{"rank": 1, "city":"Espoo", "population":227400, "latitude":60.210, "longitude":24.660},
{"rank": 2, "city":"Tampere", "population":202700, "latitude":61.520, "longitude":23.760},
{"rank": 3, "city":"Vantaa", "population":185900, "latitude":60.290, "longitude":25.040},
{"rank": 4, "city":"Turku", "population":175800, "latitude":60.450, "longitude":22.250},
{"rank": 5, "city":"Oulu", "population":127600, "latitude":65.020, "longitude":25.470},
{"rank": 6, "city":"Lahti", "population":98600, "latitude":60.990, "longitude":25.660},
{"rank": 7, "city":"Kuopio", "population":88500, "latitude":62.900, "longitude":27.700},
{"rank": 8, "city":"Jyvaskyla", "population":83300, "latitude":62.260, "longitude":25.750},
{"rank": 9, "city":"Pori", "population":76100, "latitude":61.490, "longitude":21.770},
{"rank": 10, "city":"Lappeenranta", "population":59100, "latitude":61.060, "longitude":28.180},
{"rank": 11, "city":"Vaasa", "population":57000, "latitude":63.100, "longitude":21.610},
{"rank": 12, "city":"Kotka", "population":54400, "latitude":60.470, "longitude":26.930},
{"rank": 13, "city":"Joensuu", "population":52800, "latitude":62.610, "longitude":29.780},
{"rank": 14, "city":"Hameenlinna", "population":47100, "latitude":61.000, "longitude":24.450},
{"rank": 15, "city":"Porvoo", "population":46500, "latitude":60.390, "longitude":25.660},
{"rank": 16, "city":"Mikkeli", "population":46100, "latitude":61.700, "longitude":27.260},
{"rank": 17, "city":"Hyvinkaa", "population":43600, "latitude":60.640, "longitude":24.870},
{"rank": 18, "city":"Jarvenpaa", "population":37500, "latitude":60.480, "longitude":25.100},
{"rank": 19, "city":"Rauma", "population":36700, "latitude":61.130, "longitude":21.520},
{"rank": 20, "city":"Rovaniemi", "population":36600, "latitude":66.490, "longitude":25.700},
{"rank": 21, "city":"Lohja", "population":36300, "latitude":60.250, "longitude":24.080},
{"rank": 22, "city":"Kokkola", "population":35600, "latitude":63.840, "longitude":23.120},
{"rank": 23, "city":"Kajaani", "population":35400, "latitude":64.230, "longitude":27.730},
{"rank": 24, "city":"Tuusula", "population":32500, "latitude":60.400, "longitude":25.030},
{"rank": 25, "city":"Kerava", "population":32200, "latitude":60.410, "longitude":25.110},
{"rank": 26, "city":"Kouvola", "population":32000, "latitude":60.880, "longitude":26.700},
{"rank": 27, "city":"Kirkkonummi", "population":31000, "latitude":60.120, "longitude":24.430},
{"rank": 28, "city":"Imatra", "population":30200, "latitude":61.180, "longitude":28.760},
{"rank": 29, "city":"Nurmijarvi", "population":29900, "latitude":60.470, "longitude":24.790},
{"rank": 30, "city":"Seinajoki", "population":28600, "latitude":62.790, "longitude":22.840},
{"rank": 31, "city":"Savonlinna", "population":28100, "latitude":61.870, "longitude":28.910},
{"rank": 32, "city":"Nokia", "population":27600, "latitude":61.490, "longitude":23.480},
{"rank": 33, "city":"Riihimaki", "population":26600, "latitude":60.740, "longitude":24.790},
{"rank": 34, "city":"Vihti", "population":25200, "latitude":60.420, "longitude":24.330},
{"rank": 35, "city":"Salo", "population":25100, "latitude":60.390, "longitude":23.130},
{"rank": 36, "city":"Raisio", "population":24200, "latitude":60.490, "longitude":22.180},
{"rank": 37, "city":"Iisalmi", "population":24100, "latitude":63.570, "longitude":27.180},
{"rank": 38, "city":"Varkaus", "population":23600, "latitude":62.320, "longitude":27.910},
{"rank": 39, "city":"Kemi", "population":23300, "latitude":65.760, "longitude":24.550},
{"rank": 40, "city":"Tornio", "population":22900, "latitude":65.860, "longitude":24.170},
{"rank": 41, "city":"Kangasala", "population":22700, "latitude":61.470, "longitude":24.080},
{"rank": 42, "city":"Heinola", "population":21900, "latitude":61.210, "longitude":26.030},
{"rank": 43, "city":"Ylojarvi", "population":21500, "latitude":61.550, "longitude":23.600},
{"rank": 44, "city":"Hollola", "population":21100, "latitude":61.050, "longitude":25.430},
{"rank": 45, "city":"Kaarina", "population":20800, "latitude":60.420, "longitude":22.420},
{"rank": 46, "city":"Valkeakoski", "population":20600, "latitude":61.270, "longitude":24.030},
{"rank": 47, "city":"Kuusankoski", "population":20600, "latitude":60.920, "longitude":26.610},
{"rank": 48, "city":"Sillinjarvi", "population":20400, "latitude":63.080, "longitude":27.660},
{"rank": 49, "city":"Pietarsaari", "population":19500, "latitude":63.680, "longitude":22.700},
{"rank": 50, "city":"Raahe", "population":18800, "latitude":64.690, "longitude":24.480},
{"rank": 51, "city":"Forssa", "population":18800, "latitude":60.820, "longitude":23.630},
{"rank": 52, "city":"Kuusamo", "population":18800, "latitude":65.960, "longitude":29.180},
{"rank": 53, "city":"Mantsala", "population":17700, "latitude":60.650, "longitude":25.300},
{"rank": 54, "city":"Uusikaupunki", "population":17600, "latitude":60.800, "longitude":21.410},
{"rank": 55, "city":"Laukaa", "population":17500, "latitude":62.420, "longitude":25.940},
{"rank": 56, "city":"Anjalankoski", "population":17300, "latitude":60.690, "longitude":26.800},
{"rank": 57, "city":"Sipoo", "population":17300, "latitude":60.370, "longitude":25.260},
{"rank": 58, "city":"Mustasaari", "population":16900, "latitude":63.090, "longitude":21.710},
{"rank": 59, "city":"Lempaala", "population":16700, "latitude":61.320, "longitude":23.740},
{"rank": 60, "city":"Haukipudas", "population":16300, "latitude":65.190, "longitude":25.350},
{"rank": 61, "city":"Janakkala", "population":15700, "latitude":60.900, "longitude":24.590},
{"rank": 62, "city":"Vammala", "population":15300, "latitude":61.340, "longitude":22.910},
{"rank": 63, "city":"Tammisaari", "population":15200, "latitude":59.980, "longitude":23.440},
{"rank": 64, "city":"Lieksa", "population":15100, "latitude":63.320, "longitude":30.040},
{"rank": 65, "city":"Kauhajoki", "population":15000, "latitude":62.440, "longitude":22.180},
{"rank": 66, "city":"Nastola", "population":15000, "latitude":60.950, "longitude":25.930},
{"rank": 67, "city":"Orimattila", "population":14700, "latitude":60.800, "longitude":25.740},
{"rank": 68, "city":"Aanekoski", "population":14300, "latitude":62.610, "longitude":25.690},
{"rank": 69, "city":"Lapua", "population":14100, "latitude":62.990, "longitude":22.970},
{"rank": 70, "city":"Naantali", "population":14100, "latitude":60.470, "longitude":22.020},
{"rank": 71, "city":"Lieto", "population":14100, "latitude":60.500, "longitude":22.440},
{"rank": 72, "city":"Ylivieska", "population":14000, "latitude":64.080, "longitude":24.530},
{"rank": 73, "city":"Jamsa", "population":13600, "latitude":61.860, "longitude":25.180},
{"rank": 74, "city":"Kankaanpaa", "population":12800, "latitude":61.810, "longitude":22.410},
{"rank": 75, "city":"Kempele", "population":12600, "latitude":64.920, "longitude":25.500},
{"rank": 76, "city":"Pirkkala", "population":12500, "latitude":61.500, "longitude":23.610},
{"rank": 77, "city":"Parainen", "population":12400, "latitude":60.310, "longitude":22.280},
{"rank": 78, "city":"Keuruu", "population":12200, "latitude":62.270, "longitude":24.690},
{"rank": 79, "city":"Ulvila", "population":12200, "latitude":61.440, "longitude":21.870},
{"rank": 80, "city":"Vehkalahti", "population":12100, "latitude":60.620, "longitude":27.250},
{"rank": 81, "city":"Nivala", "population":11600, "latitude":63.920, "longitude":24.960},
{"rank": 82, "city":"Ilmajoki", "population":11600, "latitude":62.740, "longitude":22.570},
{"rank": 83, "city":"Valkeala", "population":11300, "latitude":60.950, "longitude":26.800},
{"rank": 84, "city":"Hanko", "population":11300, "latitude":59.830, "longitude":22.950},
{"rank": 85, "city":"Joutseno", "population":11100, "latitude":61.100, "longitude":28.500},
{"rank": 86, "city":"Maarianhamina", "population":10800, "latitude":60.100, "longitude":19.940},
{"rank": 87, "city":"Kurikka", "population":10800, "latitude":62.630, "longitude":22.380},
{"rank": 88, "city":"Kemijarvi", "population":10700, "latitude":66.730, "longitude":27.390},
{"rank": 89, "city":"Loviisa", "population":9800, "latitude":60.460, "longitude":26.220},
{"rank": 90, "city":"Hamina", "population":9400, "latitude":60.570, "longitude":27.210},
{"rank": 91, "city":"Eura", "population":9300, "latitude":61.140, "longitude":22.120},
{"rank": 92, "city":"Huittinen", "population":9000, "latitude":61.190, "longitude":22.700},
{"rank": 93, "city":"Oulainen", "population":8900, "latitude":64.260, "longitude":24.830},
{"rank": 94, "city":"Kristiinankaupunki", "population":8800, "latitude":62.270, "longitude":21.360},
{"rank": 95, "city":"Kokemaki", "population":8700, "latitude":61.260, "longitude":22.330},
{"rank": 96, "city":"Muhos", "population":8300, "latitude":64.800, "longitude":25.990},
{"rank": 97, "city":"Harjavalta", "population":7900, "latitude":61.320, "longitude":22.130},
{"rank": 98, "city":"Uusikarlepyy", "population":7600, "latitude":63.520, "longitude":22.530},
{"rank": 99, "city":"Noormarkku", "population":6100, "latitude":61.590, "longitude":21.830},
{"rank": 100, "city":"Eurajoki", "population":5900, "latitude":61.220, "longitude":21.710},
{"rank": 10, "city":"Nakkila", "population":5900, "latitude":61.370, "longitude":21.970},
{"rank": 102, "city":"Sakyla", "population":5000, "latitude":61.050, "longitude":22.370}
];
var R = 6371e3;//meters
var x,y,d,min,arr,index;
console.log("cities-arr-length"+cities.length);
for(var cityRank = 26;cityRank<=cities.length-1;cityRank++) //iterate from the 26th city []
{
	for(var rank=0;rank<25;rank++)
	{
		console.log("distance between "+cities[cityRank].city);
		console.log("and "+cities[rank].city);
		x = (cities[cityRank].longitude-cities[rank].longitude)*Math.cos((cities[cityRank].latitude+cities[rank].latitude)/2);
		y = (cities[cityRank].latitude-cities[rank].latitude);
		d = Math.sqrt(x*x+y*y)*R;
		cities[cityRank][rank.toString()] = d;
		console.log(d);
	}
	min = cities[cityRank][0];
	console.log("first min"+min);
	index=0;
	for(var i=1;i<25;i++){
		console.log("i"+i);
		if(cities[cityRank][i]<min){
			console.log(cities[cityRank][i]+"<"+min);
			min=cities[cityRank][i];
			index=i;
			cities[cityRank]['PORef']=index;
		}
	}
	console.log("min"+min+"index"+index+"city"+cities[index].city+"longitude"+cities[index].longitude+"latitude"+cities[index].latitude);
}
console.log(cities);
