# Review
### Reviewers:
- Ella van Loenen
- Gert Hakkenberg

## Probleem 1: Comments en docstrings
### 1. Wat is het tegengekomen probleem?
Beide reviewers hadden uiteindelijk toch hulp nodig met het doorgronden van de werking van de code. Tijdens beide reviews werden docstrings en comments genoemd als mogelijke factoren die de begrijpbaarheid zouden kunnen vergroten.
### 2. Hoe zou je dit beter kunnen maken?
Er zouden meer comments en uitgebreidere docstrings geschreven kunnen worden om het voor een lezer duidelijker te maken wat er binnen de code gebeurt.
### 3. Wat voor afweging maak je? 
Er zijn wat mij betreft 3 factoren die ervoor hebben gezordg dat ik de comments en docstrings zo heb geschreven als ze zijn.
1. De code is een uitwerking van meerdere papers gebaseerd op conceptueel ingewikkelde natuurkundige ideeën. Het begrijpen van deze onderliggende ideeën is onmisbaar om de werkelijke functionaliteit en de gemaakte keuzes binnen de code te kunnen doorgronden, maar het overbrengen van alle benodigde concepten in docstrings en comments is niet haalbaar. Daarom is ervoor gekozen om documentatie te richten op een puur code-technisch begrip. Ik kreeg bijvoorbeeld tijdens de reviews vragen over waarom de gekozen loss-functie 'loss_per_weight = (1 - labels) * w_e * outputs ** 2 + labels * w_e * (1 - outputs) ** 2' bevatte, maar dit is een directe implementatie van de formule $l[f] = \sum w_e(\bar{c})[f(x_e)]^2 + \sum w_e(0) [f(x_e) - 1]^2$ uit [Chen *et al.*, 2023](https://arxiv.org/pdf/2308.05704.pdf). Om een begrip van de natuurkunde die deze formule vormgeeft te vermijden, bevatten docstrings en comments dus alleen dingen als het datatype en de vorm van tensoren; dingen die begrip van de werking van de code verhogen, maar niet verdwijnen in de natuurkunde.
2. Ik werkte voor dit project samen met de originele ontwikkelaars van het ML4EFT framework aan de implementatie van reweighting. Het framework is ook na deze toevoeging nog ver van deployment-ready, en ook is het zo dat er nu gewerkt kan worden met reweighted data, maar dat er nog wel dingen moeten gebeuren om deze functionaliteit parallel aan eerdere functionaliteiten te laten werken. Hierdoor is de code zoals hij nu is waarschijnlijk behoorlijk anders dan de eindversie zal zijn, en wordt hij ook alleen door de developers gelezen. Hierom is het in overleg met andere developer besloten dat comments en docstrings voor nu vooral voor ons duidelijk moeten zijn, en dat de energie die het perfectioneren van documentatie kost beter in het werkend krijgen van de code gestopt kon worden. 
3. In tegenstelling tot de meeste projecten die we tijdens de minor ondernomen hebben kreeg ik bij dit project niet de ruimte om dingen precies te doen zoals ik ze wilde, maar was ik gebonden aan hoe eerdere ontwikkelaars dingen bepaald hebben, zowel technisch als stylistisch. Hierom ben ik in zowel de manier als de hoeveelheid documentatie dichtbij de originele intenties gebleven, die misschien van de optimale vorm verschillen, maar die nu eenmaal zo vastgelegd waren voordat ik bij het project kwam. Ook is het zo dat ik maar aan een klein deel van de totale code-base heb gewerkt. Ik heb me dus ook bij het schrijven van documentatie en bijvoorbeeld type hints beperkt tot de delen van de code waar ik iets substantieels aan veranderd heb. Daartegenover staat dat ik waar ik dat gepast achtte wél aanpassingen aan bestaande code heb gedaan, zowel stylistisch als kwalitatief, waar ik van mening was dat het geen te groot sub-project werd.

### Voorbeelden

## Probleem 1: Comments en docstrings
Beide reviewers hadden uiteindelijk toch hulp nodig met het door 
### 1. Wat is het tegengekomen probleem?
### 2. Hoe zou je dit beter kunnen maken?
### 3. Wat voor afweging maak je? 
### Voorbeelden

## Probleem 1: Comments en docstrings
Beide reviewers hadden uiteindelijk toch hulp nodig met het door 
### 1. Wat is het tegengekomen probleem?
### 2. Hoe zou je dit beter kunnen maken?
### 3. Wat voor afweging maak je? 
### Voorbeelden

## Probleem 1: Comments en docstrings
Beide reviewers hadden uiteindelijk toch hulp nodig met het door 
### 1. Wat is het tegengekomen probleem?
### 2. Hoe zou je dit beter kunnen maken?
### 3. Wat voor afweging maak je? 
### Voorbeelden

## Probleem 1: Comments en docstrings
Beide reviewers hadden uiteindelijk toch hulp nodig met het door 
### 1. Wat is het tegengekomen probleem?
### 2. Hoe zou je dit beter kunnen maken?
### 3. Wat voor afweging maak je? 
### Voorbeelden