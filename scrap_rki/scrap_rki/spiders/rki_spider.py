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

    hardcoded_de = {'BLR': 'Belarus',
                    'COD': 'Kongo DR',
                    'COG': 'Kongo Rep',
                    'CZE': 'Tschechien',
                    'MKD': 'Nordmazedonien',
                    'PRK': 'Korea (Volksrepublik)',
                    'PSE': 'Palästinensische Gebiete',
                    'SUR': 'Surinam',
                    'SYR': 'Syrische Arabische Republik',
                    'TLS': 'Timor Leste',
                    'TTO': 'Trinidad Tobago',
                    'VAT': 'Vatikanstadt'}

    date_fmt = {'db': '%Y-%m-%d', 'de': {'dt': '%d.%m.%Y', 're': r'\d{1,2}\.\d{1,2}\.\d{4}'},
                'start': {'dt': 'seit %d. %B %Y', 're': r'seit +\d{1,2}\. +[äa-z]+ +\d{4}',
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

            iso3dict, iso3official = self.get_countries(german=True)

            name_err = []
            info_err = []
            risk_err = []

            db_old = db_old[~db_old['region'].notna()]  # TODO Drop regions for the moment
            db_old = db_old.assign(NAME_DE=db_old["NAME_ENGL"].apply(de.gettext))

            iso3_de = db_old[["NAME_DE", "ISO3_CODE"]]
            iso3_de_lut = iso3_de.set_index("NAME_DE")["ISO3_CODE"].to_dict()

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

                    name_df = []
                    info_df = []
                    iso3_df = []

                    for r in regions:
                        found = False
                        msg = r.get()[4:-5]     # Remove <li></li>
                        msg = msg.replace("<p>", "").replace("</p>", "")

                        name_de, info_de = self.strip_country(msg)
                        if name_de in iso3_de_lut.keys():
                            found = True
                            iso3 = iso3_de_lut[name_de]
                            name_df.append(name_de)
                            info_df.append(info_de)
                            iso3_df.append(iso3)
                        if found:
                            continue
                        for iso3, name in self.hardcoded_de.items():
                            if name in msg:
                                found = True
                                info_df.append(self.clean(msg.replace(name, "")))
                                name_df.append(name)
                                iso3_df.append(iso3)
                        for iso3, name in iso3dict.items():
                            if name in name_de:
                                found = True
                                info_df.append(msg)
                                name_df.append(name)
                                iso3_df.append(iso3)
                                break
                            if iso3 in name_de:
                                found = True
                                info_df.append(msg)
                                name_df.append(name)
                                iso3_df.append(iso3)
                                break
                        if found:
                            continue
                        for iso3, name in iso3official.items():
                            if name in name_de:
                                found = True
                                info_df.append(msg)
                                name_df.append(name)
                                iso3_df.append(iso3)
                                break
                        if not found:
                            print(f"Unidentified region: {name_de}")
                            print(f"Risk level code:\n\t{code}")
                            print(f"Info:\n\t{msg}\n")

                            name_err.append(name_de)
                            info_err.append(msg)
                            risk_err.append(code)

                    risk_dates = []
                    for inf in info_df:
                        date_match = re.search(self.date_fmt['start']['re'], inf, re.I)
                        if date_match:
                            date = date_match.group()
                            try:
                                risk_dates.append(dt.strptime(date, self.date_fmt['start']['dt']).date())
                            except ValueError:
                                risk_dates.append(dt.strptime(date.replace('ä', ''),
                                                               self.date_fmt['start']['fallback']).date())
                        else:
                            risk_dates.append(None)

                    df = pd.DataFrame({"ISO3_CODE": iso3_df, "NAME_DE": name_df,
                                       "risk_level_code": [code] * len(iso3_df),
                                       "risk_date": risk_dates, "INFO_DE": info_df})
                    df_collector[code] = df

            db_new = pd.concat([df_collector[i] for i in (3, 2, 1, 4)])
            db_curated = db_new.drop_duplicates(subset="ISO3_CODE")

            df_err = pd.DataFrame({"ISO3_CODE": [None] * len(risk_err), "NAME_DE": name_err,
                                   "risk_level_code": risk_err, "INFO_DE": info_err})
            df_duplicated = pd.concat([db_curated, db_new]).drop_duplicates(keep=False)
            db_residual = pd.concat([df_date, df_duplicated, df_err])

            db_norisk = db_old.assign(risk_level_code=0)
            db_curated = pd.concat([db_curated,
                                    db_norisk[["ISO3_CODE", "NAME_ENGL", "NAME_DE",
                                               "risk_level_code"]]]).drop_duplicates(subset="ISO3_CODE")
            db_curated = db_curated.sort_values("ISO3_CODE")
            db_curated = pd.concat([df_date, db_curated]).set_index("ISO3_CODE")

            db_residual.to_csv(data_dir / f"db_residual.csv", encoding='utf-8-sig', date_format=self.date_fmt['db'])
            db_curated.to_csv(data_dir / f"db_scrapped.csv", encoding='utf-8-sig', date_format=self.date_fmt['db'])

    @staticmethod
    def get_countries(german=True):
        iso3 = {c.alpha_3: c.name for c in pycountry.countries}
        iso3_official = {}
        for k, v in iso3.items():
            if ',' in v:
                try:
                    iso3[k] = pycountry.countries.get(alpha_3=k).common_name
                except AttributeError:
                    try:
                        iso3[k] = pycountry.countries.get(alpha_3=k).official_name
                    except AttributeError:
                        if k == "COD":
                            iso3[k] = "Congo DR"
            try:
                iso3_official[k] = pycountry.countries.get(alpha_3=k).official_name
            except AttributeError:
                pass
        if german:
            for k, v in iso3.items():
                iso3[k] = de.gettext(v)
            for k, v in iso3_official.items():
                iso3_official[k] = de.gettext(v)

        return iso3, iso3_official
