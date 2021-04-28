# Corona Atlas <img src="assets/img/corona-atlas-icon.png" align="right" width="120"/>

Interactive map of the international COVID-19 risk areas as designated by the German authorities.

The data is updated periodically from the website of the [Robert Koch Institute][rki].

Data scraping is performed on **Python** with
[**scrapy**](https://scrapy.org/).
The scraper also uses
[**pandas**](https://pandas.pydata.org/) and
[**pycountry**](https://pypi.org/project/pycountry/).

Map visualization is based in **R** _(@dieghernan something to add here??)_

The website uses [**Chulapa**](https://dieghernan.github.io/chulapa/)
as its Jekyll theme.

## Additional resources

-   [NUTS finder](https://dieghernan.github.io/RKI-Corona-Atlas/nuts): Search NUTS codes.
-   [LAU finder](https://dieghernan.github.io/RKI-Corona-Atlas/lau): Search LAU (local urban areas) codes. Basically town codes over the whole EU.
-   [RKI website][rki]: Data source.


[rki]: https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Risikogebiete_neu.html
