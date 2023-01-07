---
title: Informations sur les zones à risque d'exposition au COVID-19 internationales
subtitle: établies par le gouvernement allemand
permalink: /fr
header_type: hero
excerpt: |
  La carte interactive suivante présente les zones à risque
  actuelles dans le monde pour chaque pays selon le gouvernement allemand.
always_allow_html: yes
output: 
  md_document:
    preserve_yaml: true
    variant: gfm
---

<!-- Modify _R/index_fr.Rmd file instead -->

<p class="text-right font-weight-bold">

mis à jour le 07/01/2023

</p>

## Carte du risque Covid-19

La carte interactive suivante présente les zones à risque actuelles dans
le monde à partir des informations données par le ministère allemand des
Affaires étrangères, le ministère allemand de la santé et le ministère
allemand de l’intérieur.

<!--more-->

Cliquez sur un pays spécifique pour lire plus de détails sur son statut
actuel ainsi que celui de ses régions.


<div id="leaflet" style="width:100%;height:75vh;" class="leaflet html-widget"></div>
<script src="https://corona-atlas.de/assets/data/locale_fr.js"></script>
<script src="https://corona-atlas.de/assets/js/map.js"></script>

Toutes les indications sont données sans garantie car elles sont
récupérées automatiquement sur la page web de l’institut Robert Koch
plusieurs fois par jour. Vous retrouverez l’intégralité des informations
concernant les zones à risque sur [leur site
web](https://rki.de/risikogebiete).

Les restrictions liées aux voyages vers l’Allemagne depuis l’étranger
sont récupérées sur [le site internet du ministère allemand de la
santé](https://www.bundesgesundheitsministerium.de/coronavirus-infos-reisende).

## Banque de donnée

Vous pouvez aussi télécharger les informations concernant toutes les
zones définies comme étant à risque dans le monde depuis notre banque de
donnée.

<div class="reactable html-widget html-fill-item-overflow-hidden html-fill-item" id="reactable" style="width:auto;height:auto;"></div>
<script type="application/json" data-for="reactable">{"x":{"tag":{"name":"Reactable","attribs":{"data":{"Pays/Région":["Afghanistan","Angola","Albanie","Andorre","Émirats arabes unis","Argentine","Arménie","Antigua-et-Barbuda","Australie","Autriche","Azerbaïdjan","Burundi","Belgique","Bénin","Burkina Faso","Bangladesh","Bulgarie","Bahreïn","Bahamas","Bosnie-Herzégovine","Bélarus","Belize","Bolivie","Brésil","Barbade","Brunei","Bhoutan","Botswana","République Centrafricaine","Canada","Suisse","Chili","Chine","Côte d'Ivoire","Cameroun","République démocratique du Congo","Congo","Colombie","Comores","Cap-Vert","Costa Rica","Cuba","Chypre","Tchéquie","Allemagne","Djibouti","Dominique","Danemark","République Dominicaine","Algérie","Équateur","Égypte","Érythrée","Espagne","Estonie","Éthiopie","Finlande","Fidji","France","Micronésie","Gabon","Royaume-Uni","Géorgie","Ghana","Guinée","Gambie","Guinée-Bissau","Guinée Équatoriale","Grèce","Grenade","Guatemala","Guyana","Hong-Kong","Honduras","Croatie","Haïti","Hongrie","Indonésie","Inde","Irlande","Iran","Irak","Islande","Israël","Italie","Jamaïque","Jordanie","Japon","Kazakhstan","Kenya","Kirghizistan","Cambodge","Kiribati","Saint-Kitts-et-Nevis","Corée du Sud","Koweït","Laos","Liban","Libéria","Libye","Sainte-Lucie","Liechtenstein","Sri Lanka","Lesotho","Lituanie","Luxembourg","Lettonie","Maroc","Monaco","Moldavie","Madagascar","Maldives","Mexique","Îles Marshall","Macédoine du Nord","Mali","Malte","Myanmar/Burma","Monténégro","Mongolie","Mozambique","Mauritanie","Maurice","Malawi","Malaisie","Namibie","Niger","Nigeria","Nicaragua","Nioue","Pays-Bas","Norvège","Népal","Nauru","Nouvelle-Zélande","Oman","Pakistan","Panama","Pérou","Philippines","Palaos","Papouasie-Nouvelle-Guinée","Pologne","Corée du Nord","Portugal","Paraguay","Palestine","Qatar","Roumanie","Russie","Rwanda","Arabie saoudite","Soudan","Sénégal","Singapour","Îles Salomon","Sierra Leone","El Salvador","San Marin","Somalie","Serbie","Soudan du Sud","Sao Tomé-et-Principe","Surinam","Slovaquie","Slovénie","Suède","Eswatini","Seychelles","Syrie","Tchad","Togo","Thaïlande","Tadjikistan","Turkménistan","Timor-Leste","Tonga","Trinité-et-Tobago","Tunisie","Turquie","Tuvalu","République unie de Tanzanie","Ouganda","Ukraine","Uruguay","États-Unis","Ouzbékistan","Vatican","Saint-Vincent-et-les-Grenadines","Vénézuela","Vietnam","Vanuatu","Samoa","Kosovo","Yémen","Afrique du Sud","Zambie","Zimbabwe"],"Niveau de risque":["Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque",null,"Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque","Zone sans risque"],"Détails":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null]},"columns":[{"id":"Pays/Région","name":"Pays/Région","type":"character"},{"id":"Niveau de risque","name":"Niveau de risque","type":"character"},{"id":"Détails","name":"Détails","type":"logical"}],"filterable":true,"searchable":true,"showPageSizeOptions":true,"paginationType":"jump","striped":true,"elementId":"reactable","dataKey":"7f494e8ab2ce5fc743257592795e0a1c"},"children":[]},"class":"reactR_markup"},"evals":[],"jsHooks":[]}</script>

<p class="text-center my-5">

<a href="assets/dist/db_countries_risk_fr.csv" class="btn btn-primary">Télécharger
les informations (Fichier CSV)</a>

</p>
