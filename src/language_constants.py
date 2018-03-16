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
    },
    "en": {
        "default_combiner": "and",
        "inverse_combiner": "but",
    },
    "sv": {
        "default_combiner": "och",
        "inverse_combiner": "men",
    },
}

errors = {
    "fi": {
        "no-messages-for-selection": "<p>Valtteri ei osaa kirjoittaa uutista valinnastasi. Mikäli valintasi sisältää puolueen, syynä on todennäköisesti se ettei puolueella ollut yhtään ehdokasta valitsemallasi alueella.</p>",
        "general-error": "<p>Jotain meni vikaan. Yritäthän hetken kuluttua uudelleen.</p>",
        "no-template": "[<i>Haluaisin ilmaista jotain tässä mutten osaa</i>]",
    },
    "en": {
        "no-messages-for-selection": "<p>Valtteri is unable to write an article on your selection. If your selection includes a party, that party likely has no candidates in the geographical area you chose.</p>",
        "general-error": "<p>Something went wrong. Please try again later.</p>",
        "no-template": "[<i>I don't know how to express my thoughts here</i>]",
    },
    "sv": {
        "no-messages-for-selection": "<p>Valtteri kan inte skriva en nyhet utgående från dina val. Ifall du valt ett parti är orsaken sannolikt den att partiet inte hade några kandidater i området som du valt.</p>",
        "general-error": "<p>Något gick fel. Gör ett nytt försök om en stund.</p>",
        "no-template": "[<i>Jag vet inte hur jag ska uttrycka mina tankar här</i>]",
    },
}