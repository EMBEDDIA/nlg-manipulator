# News generation for Finnish Municipal Elections

Work-in-progress.


## API

### Get a random news article:
`GET /api/random`

### Get a news article for a specific location and person
`GET /api/news`

Possible query parameters:
`who`, `where`, `who_type`, `where_type`. At least one of `who` or `where` must be specified or an error with HTTP 400 will be returned.

Example:
`GET /api/news?where=91`

## Example output as of 14/3/2017:

>Suomen Keskusta on suurin puolue ja sai eniten ääniä. Puolue sai 1953 ääntä ja 1,2 prosenttia enemmän ääniä kuin edellisissä kuntavaaleissa. Puolue sai 57,7 prosenttia äänistä ja 197 ääntä enemmän kuin edellisissä kuntavaaleissa ja piti paikkojensa määrän samana.
>
>Kansallinen Kokoomus sai 2 eniten paikkoja uudessa valtuustossa ja menetti 1 paikkaa. Puolue saa 4 paikkaa uudessa valtuustossa ja sai 11,2 prosenttia äänistä. Se sai 2,5 prosenttia vähemmän ääniä kuin edellisissä kuntavaaleissa ja 47 ääntä vähemmän kuin edellisissä kuntavaaleissa ja 380 ääntä.
>
>Suomen Sosiaalidemokraattinen Puolue sai 3 eniten paikkoja uudessa valtuustossa ja 116 ääntä enemmän kuin edellisissä kuntavaaleissa. Puolue sai 2,9 prosenttia enemmän ääniä kuin edellisissä kuntavaaleissa ja 301 ääntä. Puolue sai 3 eniten ääniä ja 1 paikkaa lisää ja saa 3 paikkaa uudessa valtuustossa.
>
>Vasemmistoliitto sai 3 eniten paikkoja uudessa valtuustossa ja saa 3 paikkaa uudessa valtuustossa. Se menetti 1 paikkaa ja sai 120 ääntä vähemmän kuin edellisissä kuntavaaleissa. Puolue sai 280 ääntä ja 4,6 prosenttia vähemmän ääniä kuin edellisissä kuntavaaleissa ja 5 eniten ääniä.
>
>Perussuomalaiset sai 3 eniten paikkoja uudessa valtuustossa ja 139 ääntä enemmän kuin edellisissä kuntavaaleissa. Puolue sai 8,6 prosenttia äänistä ja 2 paikkaa lisää. Se sai 4 eniten ääniä ja 3,7 prosenttia enemmän ääniä kuin edellisissä kuntavaaleissa ja 292 ääntä. 


## Benchmarks

Latest benchmark: 14/3/2017

Generated 1224 stories

Timings:
```
real	1m53.513s
user	1m53.308s
sys	0m0.548s
```

Avg. time per component call (rounded):
```
Message Generator:            102 323 μs
Nucleus Selector:               9 943 μs
Template Selector:              6 442 μs
Aggregator:                     1 760 μs
Named Entity Resolver:            685 μs
Satellite Selector:               618 μs
Aggregate Message Generator:      220 μs
Surface Realizer:                 104 μs
Document Planner:                  23 μs

TOTAL                         122 115 μs
```
