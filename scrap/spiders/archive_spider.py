import sys
import builtins
import locale
import re
from datetime import datetime as dt
from pathlib import Path

import pycountry
import gettext

import scrapy
import pandas as pd

try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "German")

assets = Path("assets")
dist_dir = assets / "dist"

data_dir = assets / "data"
db_fname = "db_scraped.csv"
date_fname = "report_date.csv"
log_fname = "logmsg.txt"
db_path = data_dir/db_fname
date_path = data_dir/date_fname

de = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['de'])


class RKISpider(scrapy.Spider):
    name = "archive"
    handle_httpstatus_list = [200, 404, 500]

    alias = {'BLR': ('Belarus',),
             'COD': ('Kongo DR',),
             'COG': ('Kongo Rep',),
             'CPV': ('Kap Verde',),
             'CZE': ('Tschechien',),
             'LCA': ('Lucia',),
             'MKD': ('Nordmazedonien',),
             'PRK': ('Korea (Volksrepublik)',),
             'PSE': ('Palästinensische Gebiete',),
             'SSD': ('Süd-Sudan',),
             'SUR': ('Surinam',),
             'SYR': ('Syrische Arabische Republik',),
             'TLS': ('Timor Leste',),
             'TTO': ('Trinidad Tobago',),
             'VAT': ('Vatikanstadt',),
             'VCT': ('Vincent und die Grenadinen',),
             'USA': ('USA ', ' USA')}

    date_fmt = {'db': '%Y-%m-%d', 'de': {'dt': '%d.%m.%Y', 're': r'\d{1,2}\.\d{1,2}\.\d{4}'},
                'risk': {'dt': '%d. %B %Y', 're': r'\d{1,2}\. +[äa-z]+ +\d{4}',
                         'fallback': '%d. %b %Y'}}

    h2_xpath = "//div[contains(@class, 'text')]/p"
    # h2_xpath = "//div[contains(@class, 'text')]/h2"
    li_xpath = "//following-sibling::ul[1]/li"

    @classmethod
    def get_risk_headers(cls, response):
        return response.xpath(f"{cls.h2_xpath}")

    @classmethod
    def get_states(cls, response, header_index):
        return response.xpath(f"({cls.h2_xpath})[{header_index}]{cls.li_xpath}")

    @classmethod
    def valid_header(cls, header_xpath):
        header = header_xpath.xpath("./strong/text()").get()
        if header:
            return re.search(r"^\s*\d\..+:\s*$", header)
        else:
            return False

    regex_exclude = r'ausgenommen'

    NO_MATCH = -1
    NO_RISK = 0
    VARIANT = 1
    HI_INC = 2
    RISK = 3
    PARTIAL = 4
    IGNORE = 5

    risk_labels = {0: "Not risk area",
                   1: "Variant of concern",
                   2: "High risk area",
                   3: "Risk area",
                   4: "Partial risk area"}
    risk_levels = ({'code': NO_RISK, 're': "^(?=.*risikogebiet)(?=.*kein)(?=.*(staat|region|gebiet)).*$"},
                   {'code': RISK, 're': "^(?=.*risikogebiet)(?=.*(staat|region|gebiet)).*$"},
                   {'code': HI_INC, 're': "^(?=.*hochinzidenz)(?=.*(staat|region|gebiet)).*$"},
                   {'code': VARIANT, 're': "^(?=.*virusvariant)(?=.*(staat|region|gebiet)).*$"},)
    risk_priority = (RISK, HI_INC, VARIANT, NO_RISK)    # Used to resolve duplicates

    separators = ("(", "inkl", "–", "-")
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
            try:
                prep_date = date_match.group()
                date = re.search(cls.date_fmt["risk"]["re"], prep_date, re.I).group()
            except AttributeError:
                return None
            try:
                date_dt = dt.strptime(date, dt_fmt).date()
            except ValueError:
                date_dt = dt.strptime(date.replace('ä', ''), fb_fmt).date()     # Maerz workaround
            return date_dt
        else:
            return None

    def start_requests(self):
        archive_dir = Path.cwd()/"timelapse/archive"
        urls = filter_snapshots(archive_dir, first_date=20210115,
                                last_date=20210219, period_days=1)
        for url in urls:
            out_dir = archive_dir/"parsed"/Path(url).stem
            out_dir.mkdir(parents=True, exist_ok=True)

            yield scrapy.Request(url=url, callback=self.parse,
                                 cb_kwargs={"out_dir": out_dir,
                                            "make_locals": False})

    # noinspection PyUnboundLocalVariable
    def parse(self, response, out_dir=None, make_locals=True):
        if response.status in (404, 500):
            raise RuntimeError(f"Site {response.url} not found")

        if out_dir is None:
            db_out = db_path
            date_out = date_path
            log_out = sys.stdout
        else:
            out_dir = Path(out_dir)
            db_out = out_dir/db_fname
            date_out = out_dir/date_fname
            log_out = open(out_dir/log_fname, "w", encoding="utf-8")

            with open(out_dir/'content.html', 'wb') as html_file:
                html_file.write(response.body)

            def print(*args, **kwargs):
                return builtins.print(*args, file=log_out, **kwargs)

        print(f"Scraping the following URL:\n# {response.url}\n")

        stand = response.xpath("//div[contains(@class, 'subheadline')]/p/text()")
        match = re.search(self.date_fmt['de']['re'], stand.get())
        if not match:
            raise RuntimeError("Unable to find a date")

        res_date = dt.strptime(match.group(), self.date_fmt['de']['dt']).date()

        print(f"Data from {res_date} was found.\n")

        country_lut = self.country_names(german=True, lookup=True)

        name_err = []
        info_err = []
        dates_err = []
        risk_err = []
        exc_err = []

        db_old = pd.read_csv(db_path)
        db_old = db_old[db_old["ISO3_CODE"] != "ERROR"]

        db_old = db_old[~db_old['region'].notna()]
        iso3_names = db_old[["ISO3_CODE", "NAME_DE"]]
        iso3_de_lut = iso3_names.set_index("NAME_DE")["ISO3_CODE"].to_dict()

        risk_headers = self.get_risk_headers(response)
        df_collector = {self.NO_RISK: None, self.RISK: None, self.HI_INC: None, self.VARIANT: None}

        for i_h, h in enumerate(risk_headers, 1):
            if not self.valid_header(h):
                continue
            h_text = h.xpath("./strong/text()").get()
            code = self.NO_MATCH
            for rl in self.risk_levels:
                if re.search(rl['re'], h_text, re.I):
                    code = rl['code']
                    break

            if code != self.NO_MATCH:
                print(f"The following header has been assigned risk level '{self.risk_labels[code]}':")
                print(f"\t{h_text}")
                date_ppt = "bis" if code == self.NO_RISK else "seit"

                states = self.get_states(response, i_h)

                risk_dates = []

                name_states = []
                info_states = []
                iso3_states = []
                risk_states = []
                exc_states = []

                for i_s, s in enumerate(states, 1):
                    iso3_found = None
                    state_text = s.xpath("./text()[normalize-space()]").get()
                    if state_text is None:
                        state_text = s.xpath("./p/text()[normalize-space()]").get()
                    regions = s.xpath(f"./ul/li/text()")
                    msg = state_text.replace("<p>", "").replace("</p>", "").replace("\n", "")

                    reg_excluded = None
                    country_code = code
                    if code == self.RISK and len(regions) > 0:
                        country_code = self.PARTIAL
                        reg_excluded = bool(re.search(self.regex_exclude, msg, re.I))

                    name_scraped, info_scraped = self.strip_country(msg)
                    if name_scraped in iso3_de_lut.keys():      # Direct search from old DB
                        iso3_found = iso3_de_lut[name_scraped]
                    else:
                        for name, iso3 in country_lut.items():  # Exhaustive search with pycountry and alias
                            if name in name_scraped:
                                iso3_found = iso3
                                name_scraped = name
                                break
                    if not iso3_found:
                        for name, iso3 in country_lut.items():  # Repeat exhaustive search in the whole message
                            if name in msg:
                                name_scraped = name
                                info_scraped = self.clean(msg.replace(name, ""))
                                iso3_found = iso3
                                break
                    # if not iso3_found:                          # Last check among the regions
                    #     region = db_regions.query("NAME_DE == @name_scraped")
                    #     if not region.empty:
                    #         region = region.iloc[0]
                    #         name_regions.append(name_scraped)
                    #         risk_regions.append(country_code)
                    #         info_regions.append(info_scraped)
                    #         dates_regions.append(self.extract_date(info_scraped, preposition=date_ppt))
                    #         iso3_regions.append(region["ISO3_CODE"])
                    #         nuts_regions.append(region["NUTS_CODE"])
                    #         continue
                    if iso3_found:
                        name_states.append(name_scraped)
                        info_states.append(info_scraped)
                        risk_dates.append(self.extract_date(info_scraped, preposition=date_ppt))
                        iso3_states.append(iso3_found)
                        risk_states.append(country_code)
                        exc_states.append(reg_excluded)
                        if len(regions) > 0:
                            print(f"\t\t{len(regions)} regions detected for {name_scraped}")
                    else:
                        print(f"Unidentified state: {name_scraped}")
                        print(f"Risk level code:\n\t{country_code}")
                        print(f"Info:\n\t{msg}\n")

                        name_err.append(name_scraped)
                        info_err.append(msg)
                        dates_err.append(self.extract_date(msg, preposition=date_ppt))
                        risk_err.append(country_code)
                        exc_err.append(reg_excluded)
                print(", ".join(name_states))
                print()

                df = pd.DataFrame({"ISO3_CODE": iso3_states, "risk_level_code": risk_states, "NAME_DE": name_states,
                                   "risk_date": risk_dates, "region": None, "REG_EXCLUDED": exc_states,
                                   "NUTS_CODE": None})
                df_collector[code] = df
            else:
                print(f"The following header was not assigned a risk level:")
                print(f"\t{h_text}\n")

        if all(df_c is None for df_c in df_collector.values()):
            print("No regions detected. Exiting...")
            return

        db_new = pd.concat([df_collector[i] for i in self.risk_priority])
        db_curated = db_new.drop_duplicates(subset="ISO3_CODE")

        df_duplicated = pd.concat([db_curated, db_new]).drop_duplicates(keep=False)
        df_duplicated = df_duplicated.assign(ISO3_CODE="ERROR", ERROR="DUPLICATED")

        df_unknown = pd.DataFrame({"NAME_DE": name_err, "risk_level_code": risk_err,
                                   "risk_date": dates_err, "REG_EXCLUDED": exc_err})
        df_unknown = df_unknown.assign(ISO3_CODE="ERROR", ERROR="UNKNOWN_AREA")

        print(f"Process summary:")
        print(f"\t- {len(db_curated)} states have been succesfully processed")
        for rval, rlabel in self.risk_labels.items():
            db_query = f"risk_level_code == {rval}"
            print(f"\t\t* {len(db_curated.query(db_query))} states as\t'{rlabel}'")
        print(f"\t- {len(df_duplicated)} states are duplicated")
        print(f"\t- {len(df_unknown)} states could not be identified")

        db_norisk = db_old.assign(risk_level_code=lambda x: x.where(x["ISO3_CODE"] == "DEU",
                                                                    self.NO_RISK)["risk_level_code"])

        db_curated = pd.concat([db_curated,
                                db_norisk[["ISO3_CODE", "NAME_DE",
                                           "risk_level_code"]]]).drop_duplicates(subset="ISO3_CODE")
        db_curated = db_curated.sort_values("ISO3_CODE")

        db_final = pd.concat([db_curated, df_duplicated, df_unknown]).set_index("ISO3_CODE")
        db_final.astype({"risk_level_code": int}).to_csv(db_out, encoding='utf-8-sig',
                                                         date_format=self.date_fmt['db'])

        pd.DataFrame({"report_date": [res_date]}).to_csv(date_out, index=False, date_format=self.date_fmt['db'])

        if out_dir is not None:
            log_out.close()

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


def filter_snapshots(directory, first_date=20200101, last_date=22222222, period_days=7):
    snapshots = []
    for p in sorted(Path(directory).iterdir(), reverse=True):
        if p.is_file():
            current_date = int(p.stem[:8])
            if first_date <= current_date <= last_date - period_days:
                last_date = current_date
                snapshots.append('file:///'+p.as_posix())
            elif current_date < first_date:
                break
    return snapshots
