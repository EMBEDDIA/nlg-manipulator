pronouns = {
    "fi": {
        1: "hän",
        2: "hän",
    },
    "en": {
        1: "he",
        2: "she",
    },
    "sv": {
        1: "han",
        2: "hon",
    }
}

vocabulary = {
    "fi": {
        "default_combiner": "ja",
        "inverse_combiner": "mutta",
        "subord_clause_start": ", mikä on",
        "comparator": "kuin",
    },
    "en": {
        "default_combiner": "and",
        "inverse_combiner": "but",
        "subord_clause_start": ", which is",
        "comparator": "than",
    },
    "sv": {
        "default_combiner": "och",
        "inverse_combiner": "men",
        "subord_clause_start": ", som är",
        "comparator": "än",
    },
}

errors = {
    "fi": {
        "no-messages-for-selection": "<p>Valtteri ei osaa kirjoittaa uutista valinnastasi.</p>",
        "general-error": "<p>Jotain meni vikaan. Yritäthän hetken kuluttua uudelleen.</p>",
        "no-template": "[<i>Haluaisin ilmaista jotain tässä mutten osaa</i>]",
    },
    "en": {
        "no-messages-for-selection": "<p>Valtteri is unable to write an article on your selection.</p>",
        "general-error": "<p>Something went wrong. Please try again later.</p>",
        "no-template": "[<i>I don't know how to express my thoughts here</i>]",
    },
    "sv": {
        "no-messages-for-selection": "<p>Valtteri kan inte skriva en nyhet utgående från dina val.</p>",
        "general-error": "<p>Något gick fel. Gör ett nytt försök om en stund.</p>",
        "no-template": "[<i>Jag vet inte hur jag ska uttrycka mina tankar här</i>]",
    },
}