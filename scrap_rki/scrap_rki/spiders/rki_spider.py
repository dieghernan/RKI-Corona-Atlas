import locale
import re
from datetime import datetime as dt
from pathlib import Path

import pycountry
import gettext

import scrapy
import pandas as pd
locale.setlocale(locale.LC_TIME, "German")
pd.options.mode.chained_assignment = None

data_dir = Path("../assets/data")

de = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['de'])


class RKISpider(scrapy.Spider):
    name = "rki"

    alias = {'BLR': ('Belarus',),
             'COD': ('Kongo DR',),
             'COG': ('Kongo Rep',),
             'CZE': ('Tschechien',),
             'MKD': ('Nordmazedonien',),
             'PRK': ('Korea (Volksrepublik)',),
             'PSE': ('Palästinensische Gebiete',),
             'SUR': ('Surinam',),
             'SYR': ('Syrische Arabische Republik',),
             'TLS': ('Timor Leste',),
             'TTO': ('Trinidad Tobago',),
             'VAT': ('Vatikanstadt',),
             'USA': ('USA ', ' USA')}

    date_fmt = {'db': '%Y-%m-%d', 'de': {'dt': '%d.%m.%Y', 're': r'\d{1,2}\.\d{1,2}\.\d{4}'},
                'risk': {'dt': 'seit %d. %B %Y', 're': r'seit +\d{1,2}\. +[äa-z]+ +\d{4}',
                          'fallback': 'seit %d. %b %Y'}}

    header_xpath = "//div[contains(@class, 'text')]/h2"

    risk_levels = ({'code': 4, 're': "^(?=.*risikogebiet)(?=.*kein)(?=.*(staat|region|gebiet)).*$"},
                   {'code': 3, 're': "^(?=.*risikogebiet)(?=.*(staat|region|gebiet)).*$"},
                   {'code': 2, 're': "^(?=.*hochinzidenz)(?=.*(staat|region|gebiet)).*$"},
                   {'code': 1, 're': "^(?=.*virusvariant)(?=.*(staat|region|gebiet)).*$"},)

    separators = ("(", ":", "inkl", "–")
    deletable = ("(", ")", ":", "–")

    @classmethod
    def strip_country(cls, message):
        split_msg = message.split(" ")
        sep_index = len(split_msg)
        found = False
        for i, s in enumerate(split_msg):
            for sep in cls.separators:
                index = s.find(sep)
                if index == 0:
                    sep_index = i
                    found = True
                    break
                elif index != -1:
                    sep_index = i + 1
                    found = True
                    break
            if found:
                break

        name = " ".join(split_msg[:sep_index])
        info = " ".join(split_msg[sep_index:])

        return cls.clean(name), cls.clean(info)

    @classmethod
    def clean(cls, message):
        for d in cls.deletable:
            message = message.replace(d, '')
        return message

    def start_requests(self):
        urls = [
            'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Risikogebiete_neu.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = data_dir / 'scrapped/rki_de.html'

        stand = response.xpath("//div[contains(@class, 'subheadline')]/p/text()")
        match = re.search(self.date_fmt['de']['re'], stand.get())
        if not match:
            raise RuntimeError("Unable to find a date")

        db_old = pd.read_csv(data_dir / "db_countries.csv")
        old_date = dt.strptime(db_old[db_old["ISO3_CODE"] == "Field date"].at[0, "risk_level_code"],
                               self.date_fmt['db']).date()

        new_date = dt.strptime(match.group(), self.date_fmt['de']['dt']).date()

        if new_date > old_date:
            print(f"Current data from {old_date}. Newer data from {new_date} was found.\n")

            country_lut = self.country_names(german=True, lookup=True)

            name_err = []
            info_err = []
            risk_err = []

            db_old = db_old[~db_old['region'].notna()]  # TODO Drop regions for the moment
            db_old = db_old.assign(NAME_DE=db_old["NAME_ENGL"].apply(de.gettext))

            iso3_names = db_old[["ISO3_CODE", "NAME_ENGL", "NAME_DE"]]
            iso3_en = iso3_names.set_index("ISO3_CODE")["NAME_ENGL"].to_dict()
            iso3_de_lut = iso3_names.set_index("NAME_DE")["ISO3_CODE"].to_dict()

            df_date = pd.DataFrame({"ISO3_CODE": ["Field date"], "risk_level_code": new_date})
            with open(filename, 'wb') as f:
                f.write(response.body)

            self.log(f'Saved file {filename}')
            risk_headers = response.xpath(f"{self.header_xpath}/text()")
            df_collector = {1: None, 2: None, 3: None, 4: None}

            for counter, h in enumerate(risk_headers, 1):
                h_text = h.get()
                code = -1
                for rl in self.risk_levels:
                    if re.search(rl['re'], h_text, re.I):
                        code = rl['code']
                        break
                print(f"The following header has been assigned to risk_level_code {code}:")
                print(f"{h_text}\n")

                if code >= 0:
                    regions = response.xpath(f"({self.header_xpath})[{counter}]//following-sibling::ul[1]/li")

                    name_regions = []
                    info_regions = []
                    iso3_regions = []

                    for r in regions:
                        found = False
                        msg = r.get()[4:-5]     # Remove <li></li>
                        msg = msg.replace("<p>", "").replace("</p>", "")

                        name_scrapped, info_scrapped = self.strip_country(msg)
                        if name_scrapped in iso3_de_lut.keys():
                            iso3 = iso3_de_lut[name_scrapped]
                            name_regions.append(name_scrapped)
                            info_regions.append(info_scrapped)
                            iso3_regions.append(iso3)
                            found = True
                        if found:
                            continue
                        for name, iso3 in country_lut.items():
                            if name in name_scrapped:
                                name_regions.append(name)
                                info_regions.append(info_scrapped)
                                iso3_regions.append(iso3)
                                found = True
                                break
                        if found:
                            continue
                        for name, iso3 in country_lut.items():
                            if name in msg:
                                name_regions.append(name)
                                info_regions.append(self.clean(msg.replace(name, "")))
                                iso3_regions.append(iso3)
                                found = True
                                break
                        if not found:
                            print(f"Unidentified region: {name_scrapped}")
                            print(f"Risk level code:\n\t{code}")
                            print(f"Info:\n\t{msg}\n")

                            name_err.append(name_scrapped)
                            info_err.append(msg)
                            risk_err.append(code)

                    risk_dates = []
                    for inf in info_regions:
                        date_match = re.search(self.date_fmt['risk']['re'], inf, re.I)
                        if date_match:
                            date = date_match.group()
                            try:
                                risk_dates.append(dt.strptime(date, self.date_fmt['risk']['dt']).date())
                            except ValueError:
                                risk_dates.append(dt.strptime(date.replace('ä', ''),
                                                              self.date_fmt['risk']['fallback']).date())
                        else:
                            risk_dates.append(None)

                    df = pd.DataFrame({"ISO3_CODE": iso3_regions, "NAME_DE": name_regions,
                                       "NAME_ENGL": [iso3_en[i3r] for i3r in iso3_regions],
                                       "risk_level_code": [code] * len(iso3_regions),
                                       "risk_date": risk_dates, "INFO_DE": info_regions})
                    df_collector[code] = df

            db_new = pd.concat([df_collector[i] for i in (3, 2, 1, 4)])
            db_curated = db_new.drop_duplicates(subset="ISO3_CODE")

            df_unknown = pd.DataFrame({"ISO3_CODE": ["ERROR"] * len(risk_err), "NAME_DE": name_err,
                                       "risk_level_code": risk_err, "INFO_DE": info_err,
                                       "ERROR": ["UNKNOWN_AREA"] * len(risk_err)})
            df_duplicated = pd.concat([db_curated, db_new]).drop_duplicates(keep=False)
            df_duplicated = df_duplicated.assign(ISO3_CODE="ERROR", ERROR="DUPLICATED")

            print(f"Process summary:")
            print(f"\t- {len(db_curated)} regions have been succesfully processed")
            print(f"\t- {len(df_duplicated)} regions are duplicated")
            print(f"\t- {len(df_unknown)} regions could not be identified")

            db_norisk = db_old.assign(risk_level_code=0)
            db_curated = pd.concat([db_curated,
                                    db_norisk[["ISO3_CODE", "NAME_ENGL", "NAME_DE",
                                               "risk_level_code"]]]).drop_duplicates(subset="ISO3_CODE")
            db_curated = db_curated.sort_values("ISO3_CODE")

            db_final = pd.concat([df_date, db_curated, df_duplicated, df_unknown]).set_index("ISO3_CODE")
            db_final.to_csv(data_dir / f"db_scrapped.csv", encoding='utf-8-sig', date_format=self.date_fmt['db'])

    @classmethod
    def country_names(cls, german=True, lookup=True):

        countries = {k: list(v) for k, v in cls.alias.items()}

        for c in pycountry.countries:
            iso3 = c.alpha_3
            cname = c.name
            comma = False
            if ',' in cname:
                try:
                    cname = c.common_name
                except AttributeError:
                    comma = True
            try:
                cname_official = c.official_name
                c_names = [cname, cname_official]
                if comma:
                    c_names = c_names[::-1]
            except AttributeError:
                c_names = [cname]

            if german:
                c_names = [de.gettext(cn) for cn in c_names]

            try:
                countries[iso3] += c_names
            except KeyError:
                countries[iso3] = c_names

        if lookup:
            c_lut = {}
            while len(countries) > 0:
                deleted_iso3 = []
                for iso3 in countries.keys():
                    c_lut[countries[iso3].pop(0)] = iso3
                    if len(countries[iso3]) == 0:
                        deleted_iso3.append(iso3)
                for iso3 in deleted_iso3:
                    del countries[iso3]
            return c_lut
        else:
            return countries
