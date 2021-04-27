import locale
import re
from datetime import datetime as dt
from pathlib import Path

import pycountry
import gettext

import scrapy
import pandas as pd
locale.setlocale(locale.LC_TIME, "German")

data_dir = Path("assets/data")

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
                'risk': {'dt': '%d. %B %Y', 're': r'\d{1,2}\. +[äa-z]+ +\d{4}',
                         'fallback': '%d. %b %Y'}}

    h2_xpath = "//div[contains(@class, 'text')]/h2"
    li_xpath = "//following-sibling::ul[1]/li"

    risk_levels = ({'code': 4, 're': "^(?=.*risikogebiet)(?=.*kein)(?=.*(staat|region|gebiet)).*$"},
                   {'code': 3, 're': "^(?=.*risikogebiet)(?=.*(staat|region|gebiet)).*$"},
                   {'code': 2, 're': "^(?=.*hochinzidenz)(?=.*(staat|region|gebiet)).*$"},
                   {'code': 1, 're': "^(?=.*virusvariant)(?=.*(staat|region|gebiet)).*$"},)
    risk_priority = (3, 2, 1, 4)    # Used to resolve duplicates

    separators = ("(", "inkl", "–")
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

        return cls.clean(name), cls.unwrap(info)

    @classmethod
    def clean(cls, message):
        for d in cls.deletable:
            message = message.replace(d, '')
        return message

    @staticmethod
    def unwrap(message):
        match = re.search(r"^\([^()]+\)$", message)
        if match:
            return message[1:-1]
        else:
            return message

    @classmethod
    def extract_date(cls, info, preposition="seit"):
        re_fmt = cls.date_fmt["risk"]["re"]
        dt_fmt = cls.date_fmt["risk"]["dt"]
        fb_fmt = cls.date_fmt["risk"]["fallback"]
        ppt_fmt = rf'{preposition}[] +{re_fmt}'

        date_match = re.search(ppt_fmt, info, re.I)
        if date_match:
            prep_date = date_match.group()
            date = re.search(cls.date_fmt["risk"]["re"], prep_date, re.I).group()
            try:
                date_dt = dt.strptime(date, dt_fmt).date()
            except ValueError:
                date_dt = dt.strptime(date.replace('ä', ''), fb_fmt).date()     # Maerz workaround
            return date_dt
        else:
            return None

    def start_requests(self):
        urls = [
            'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Risikogebiete_neu.html',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = data_dir / 'scrapped/rki.html'

        stand = response.xpath("//div[contains(@class, 'subheadline')]/p/text()")
        match = re.search(self.date_fmt['de']['re'], stand.get())
        if not match:
            raise RuntimeError("Unable to find a date")

        db_old = pd.read_csv(data_dir / "db_scrapped.csv")
        old_date = dt.strptime(db_old[db_old["ISO3_CODE"] == "Field date"].at[0, "risk_level_code"],
                               self.date_fmt['db']).date()

        new_date = dt.strptime(match.group(), self.date_fmt['de']['dt']).date()

        if new_date > old_date:
            print(f"Current data from {old_date}. Newer data from {new_date} was found.\n")

            country_lut = self.country_names(german=True, lookup=True)

            name_err = []
            info_err = []
            dates_err = []
            risk_err = []

            db_old = db_old[db_old["ISO3_CODE"] != "ERROR"]
            db_regions = db_old[db_old['region'].notna()]
            db_regions = db_regions.assign(NAME_DE=db_regions["NAME_ENGL"].apply(de.gettext))
            reg_df = db_regions[["ISO3_CODE", "NAME_ENGL", "NAME_DE", "NUTS_CODE"]]

            db_old = db_old[~db_old['region'].notna()]
            iso3_names = db_old[["ISO3_CODE", "NAME_ENGL", "NAME_DE"]]
            iso3_en = iso3_names.set_index("ISO3_CODE")["NAME_ENGL"].to_dict()
            iso3_de_lut = iso3_names.set_index("NAME_DE")["ISO3_CODE"].to_dict()

            df_date = pd.DataFrame({"ISO3_CODE": ["Field date"], "risk_level_code": new_date})
            with open(filename, 'wb') as f:
                f.write(response.body)

            self.log(f'Saved file {filename}')
            risk_headers = response.xpath(f"{self.h2_xpath}/text()")
            df_collector = {1: None, 2: None, 3: None, 4: None}

            name_regions = []
            info_regions = []
            iso3_regions = []
            nuts_regions = []
            risk_regions = []
            dates_regions = []

            for i_h, h in enumerate(risk_headers, 1):
                h_text = h.get()
                code = -1
                for rl in self.risk_levels:
                    if re.search(rl['re'], h_text, re.I):
                        code = rl['code']
                        break
                print(f"The following header has been assigned to risk_level_code {code}:")
                print(f"{h_text}\n")

                if code >= 0:
                    date_ppt = "bis" if code == 4 else "seit"

                    states = response.xpath(f"({self.h2_xpath})[{i_h}]{self.li_xpath}")

                    risk_dates = []

                    name_states = []
                    info_states = []
                    iso3_states = []

                    for i_s, s in enumerate(states, 1):
                        iso3_found = None
                        regions = response.xpath(f"({self.h2_xpath})[{i_h}]{self.li_xpath}[{i_s}]/ul/li/text()")
                        msg = s.get()[4:-5]     # Remove <li></li>
                        msg = msg.replace("<p>", "").replace("</p>", "")

                        name_scrapped, info_scrapped = self.strip_country(msg)
                        if name_scrapped in iso3_de_lut.keys():     # Direct search from old DB
                            iso3_found = iso3_de_lut[name_scrapped]
                        else:
                            for name, iso3 in country_lut.items():  # Exhaustive search with pycountry and alias
                                if name in name_scrapped:
                                    iso3_found = iso3
                                    name_scrapped = name
                                    break
                        if not iso3_found:
                            for name, iso3 in country_lut.items():  # Repeat exhaustive search in the whole message
                                if name in msg:
                                    name_scrapped = name
                                    info_scrapped = self.clean(msg.replace(name, ""))
                                    iso3_found = iso3
                                    break
                        if not iso3_found:                          # Last check among the regions
                            region = db_regions[db_regions["NAME_DE"] == name_scrapped]
                            if not region.empty:
                                name_regions.append(name_scrapped)
                                risk_regions.append(code)
                                info_regions.append(info_scrapped)
                                dates_regions.append(self.extract_date(info_scrapped, preposition=date_ppt))
                                iso3_regions.append(region["ISO3_CODE"].iat[0])
                                nuts_regions.append(region["NUTS_CODE"].iat[0])
                                continue
                        if iso3_found:
                            name_states.append(name_scrapped)
                            info_states.append(info_scrapped)
                            risk_dates.append(self.extract_date(info_scrapped, preposition=date_ppt))
                            iso3_states.append(iso3_found)
                        else:
                            print(f"Unidentified state: {name_scrapped}")
                            print(f"Risk level code:\n\t{code}")
                            print(f"Info:\n\t{msg}\n")

                            name_err.append(name_scrapped)
                            info_err.append(msg)
                            dates_err.append(self.extract_date(msg, preposition=date_ppt))
                            risk_err.append(code)
                        country_regs = reg_df[reg_df["ISO3_CODE"] == iso3_found]
                        for r in regions:
                            name_sr, info_sr = self.strip_country(r.get())
                            nuts = country_regs[country_regs["NAME_DE"] == name_sr]["NUTS_CODE"]
                            nuts = None if nuts.empty else nuts.iloc[0]

                            name_regions.append(name_sr)
                            risk_regions.append(code)
                            info_regions.append(info_sr)
                            dates_regions.append(self.extract_date(info_sr, preposition=date_ppt))
                            iso3_regions.append(iso3_found)
                            nuts_regions.append(nuts)

                    df = pd.DataFrame({"ISO3_CODE": iso3_states, "NAME_DE": name_states,
                                       "NAME_ENGL": [iso3_en[i3r] for i3r in iso3_states],
                                       "risk_date": risk_dates, "INFO_DE": info_states})
                    df = df.assign(risk_level_code=code)
                    df_collector[code] = df

            db_new = pd.concat([df_collector[i] for i in self.risk_priority])
            db_curated = db_new.drop_duplicates(subset="ISO3_CODE")

            df_regions = pd.DataFrame({"ISO3_CODE": iso3_regions, "risk_level_code": risk_regions,
                                       "NAME_DE": name_regions, "NAME_ENGL": name_regions,
                                       "NUTS_CODE": nuts_regions,
                                       "risk_date": dates_regions, "INFO_DE": info_regions})
            df_regions = df_regions.assign(region=True).sort_values("ISO3_CODE")

            df_unknown = pd.DataFrame({"NAME_DE": name_err, "risk_level_code": risk_err, "INFO_DE": info_err})
            df_unknown = df_unknown.assign(ISO3_CODE="ERROR", ERROR="UNKNOWN_AREA")

            df_duplicated = pd.concat([db_curated, db_new]).drop_duplicates(keep=False)
            df_duplicated = df_duplicated.assign(ISO3_CODE="ERROR", ERROR="DUPLICATED")

            print(f"Process summary:")
            print(f"\t- {len(db_curated)} states have been succesfully processed")
            print(f"\t- {len(df_regions)} regions have been identified")
            print(f"\t- {len(df_duplicated)} states are duplicated")
            print(f"\t- {len(df_unknown)} states could not be identified")

            db_norisk = db_old.assign(risk_level_code=lambda x: x.where(x["ISO3_CODE"] == "DEU", 0)["risk_level_code"])
            db_curated = pd.concat([db_curated,
                                    db_norisk[["ISO3_CODE", "NAME_ENGL", "NAME_DE",
                                               "risk_level_code"]]]).drop_duplicates(subset="ISO3_CODE")
            db_curated = db_curated.sort_values("ISO3_CODE")

            db_final = pd.concat([df_date, db_curated, df_regions, df_duplicated, df_unknown]).set_index("ISO3_CODE")
            db_final.to_csv(data_dir / f"db_scrapped.csv", encoding='utf-8-sig', date_format=self.date_fmt['db'])
        else:
            print("Database is up to date.")

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
