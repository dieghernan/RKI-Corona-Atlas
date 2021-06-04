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
db_path = data_dir/"db_scraped.csv"
date_path = data_dir/"report_date.csv"

de = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['de'])

names = ["NAME_DE", "NAME_EN", "NAME_ES", "NAME_FR", "NAME_PL", "NAME_TR"]
translate = {f"NAME_{loc.upper()}":
             gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[loc])
             for loc in ('es', 'fr', 'pl', 'tr')}


class RKISpider(scrapy.Spider):
    name = "rki"
    handle_httpstatus_list = [200, 404, 500]

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
                'risk': {'dt': '%d %B %Y', 're': r'\d{1,2}\.? +[äa-z]+\.? +\d{4}',
                         'fallback': '%d %b %Y'}}

    h2_xpath = "//div[contains(@class, 'text')]/h2"
    li_xpath = "//following-sibling::ul[1]/li"

    excluded_tags = (r'ausgenommen', r'ausnahme')

    NO_MATCH = -1
    NO_RISK = 0
    VARIANT = 1
    HI_INC = 2
    RISK = 3
    PARTIAL = 4
    IGNORE = 5

    risk_labels = pd.read_csv(data_dir/"risk_level_code.csv", index_col="risk_level_code")["risk_level_en"]
    risk_levels = ({'code': NO_RISK, 're': "^(?=.*risikogebiet)(?=.*kein)(?=.*(staat|region|gebiet)).*$"},
                   {'code': RISK, 're': "^(?=.*risikogebiet)(?=.*(staat|region|gebiet)).*$"},
                   {'code': HI_INC, 're': "^(?=.*hochinzidenz)(?=.*(staat|region|gebiet)).*$"},
                   {'code': VARIANT, 're': "^(?=.*virusvariant)(?=.*(staat|region|gebiet)).*$"},)
    risk_priority = (RISK, HI_INC, VARIANT, NO_RISK)    # Used to resolve duplicates

    separators = ("(", "inkl", "–", "-")
    deletable = ("(", ")", ":", "–")

    @classmethod
    def strip_country(cls, message, separators=None):
        if separators is None:
            separators = cls.separators
        split_msg = message.split(" ")
        sep_index = len(split_msg)
        found = False
        for i, s in enumerate(split_msg):
            for sep in separators:
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
            prep_date = date_match.group().replace('.', '')     # Remove dots to handle typos
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
            'https://www.rki.de/risikogebiete',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status in (404, 500):
            raise RuntimeError(f"Site {response.url} not found")

        print(f"Scraping the following URL:\n{response.url}\n")

        stand = response.xpath("//div[contains(@class, 'subheadline')]/p/text()")
        match = re.search(self.date_fmt['de']['re'], stand.get())
        if not match:
            raise RuntimeError("Unable to find a date")

        db_date_df = pd.read_csv(date_path)
        db_date = dt.strptime(db_date_df.at[0, "report_date"], self.date_fmt['db']).date()

        res_date = dt.strptime(match.group(), self.date_fmt['de']['dt']).date()

        print(f"Saved data is from {db_date}, response data from {res_date} was found.\n")

        country_lut = self.country_names(german=True, lookup=True)

        name_err = []
        info_err = []
        dates_err = []
        risk_err = []
        exc_err = []

        db_old = pd.read_csv(db_path)
        db_old = db_old[db_old["ISO3_CODE"] != "ERROR"]

        try:
            db_regions = db_old[db_old['region'].notna()]
            reg_df = db_regions[["ISO3_CODE", "NUTS_CODE"] + names]
        except KeyError as e:
            key_name = re.search("'([^']*)'", str(e)).group(1)
            print(f"Adding new language {key_name}\n")
            db_old = db_old.assign(**{key_name: db_old["NAME_EN"].apply(translate[key_name].gettext)})

            db_regions = db_old[db_old['region'].notna()]
            reg_df = db_regions[["ISO3_CODE", "NUTS_CODE"] + names]

        db_old = db_old[~db_old['region'].notna()]

        iso3_names = db_old[["ISO3_CODE"] + names]
        iso3_de_lut = iso3_names.set_index("NAME_DE")["ISO3_CODE"].to_dict()
        iso3_names = {n: iso3_names.set_index("ISO3_CODE")[n].to_dict() for n in names if n != "NAME_DE"}

        risk_headers = response.xpath(f"{self.h2_xpath}/text()")
        df_collector = {self.NO_RISK: None, self.RISK: None, self.HI_INC: None, self.VARIANT: None}

        name_regions = []
        regions_translated = {name_i: [] for name_i in names if name_i != "NAME_DE"}
        info_regions = []
        iso3_regions = []
        nuts_regions = []
        risk_regions = []
        dates_regions = []

        for i_h, h in enumerate(risk_headers, 1):
            h_text = h.get()
            code = self.NO_MATCH
            for rl in self.risk_levels:
                if re.search(rl['re'], h_text, re.I):
                    code = rl['code']
                    break

            if code != self.NO_MATCH:
                print(f"The following header has been assigned risk level '{self.risk_labels[code]}':")
                print(f"\t{h_text}\n")
                date_ppt = "bis" if code == self.NO_RISK else "seit"

                states = response.xpath(f"({self.h2_xpath})[{i_h}]{self.li_xpath}")

                risk_dates = []

                name_states = []
                info_states = []
                iso3_states = []
                risk_states = []
                exc_states = []

                for i_s, s in enumerate(states, 1):
                    iso3_found = None
                    regions = response.xpath(f"({self.h2_xpath})[{i_h}]{self.li_xpath}[{i_s}]/ul/li/text()")
                    msg = s.get()[4:-5]     # Remove <li></li>
                    msg = msg.replace("<p>", "").replace("</p>", "").replace("\n", "")

                    country_code = code

                    excluded_msg = None
                    reg_excluded = None
                    for tag in self.excluded_tags:
                        search = re.compile(rf".*{tag}[ ]+(.*)$", re.I).search(msg)
                        if search:
                            excluded_msg = search.group(1)
                            break
                    if code == self.RISK:
                        if excluded_msg:
                            country_code = self.PARTIAL
                            reg_excluded = True
                        elif len(regions) > 0:
                            country_code = self.PARTIAL
                            reg_excluded = False

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
                    if not iso3_found:                          # Last check among the regions
                        region = db_regions.query("NAME_DE == @name_scraped")
                        if not region.empty:
                            region = region.iloc[0]
                            name_regions.append(name_scraped)
                            risk_regions.append(country_code)
                            info_regions.append(info_scraped)
                            dates_regions.append(self.extract_date(info_scraped, preposition=date_ppt))
                            iso3_regions.append(region["ISO3_CODE"])
                            nuts_regions.append(region["NUTS_CODE"])
                            continue
                    if iso3_found:
                        name_states.append(name_scraped)
                        info_states.append(info_scraped)
                        risk_dates.append(self.extract_date(info_scraped, preposition=date_ppt))
                        iso3_states.append(iso3_found)
                        risk_states.append(country_code)
                        exc_states.append(reg_excluded)
                    else:
                        print(f"Unidentified state: {name_scraped}")
                        print(f"Risk level code:\n\t{country_code}")
                        print(f"Info:\n\t{msg}\n")

                        name_err.append(name_scraped)
                        info_err.append(msg)
                        dates_err.append(self.extract_date(msg, preposition=date_ppt))
                        risk_err.append(country_code)
                        exc_err.append(reg_excluded)
                    country_regs = reg_df.query("ISO3_CODE == @iso3_found")
                    reg_code = self.NO_RISK if reg_excluded else code
                    if country_code == self.PARTIAL and len(regions) == 0:
                        for _, cr in country_regs.iterrows():
                            if cr["NAME_DE"] in excluded_msg:
                                name_regions.append(cr["NAME_DE"])
                                for name_k in regions_translated.keys():
                                    regions_translated[name_k].append(cr[name_k])
                                risk_regions.append(reg_code)
                                info_regions.append(None)
                                dates_regions.append(None)
                                iso3_regions.append(iso3_found)
                                nuts_regions.append(cr["NUTS_CODE"])
                    for r in regions:
                        name_sr, info_sr = self.strip_country(r.get(), separators=("(",))
                        reg_hit = country_regs.query("NAME_DE == @name_sr")
                        name_translate = {n: loc.gettext(name_sr) for n, loc in translate.items()}
                        name_translate["NAME_EN"] = name_sr
                        if reg_hit.empty:
                            nuts = None
                            for reg_de, iso3 in country_lut.items():
                                if reg_de in name_sr:
                                    name_en = pycountry.countries.get(alpha_3=iso3).name
                                    name_translate["NAME_EN"] = name_en
                                    for name_k, loc in translate.items():
                                        name_translate[name_k] = loc.gettext(name_en)
                                    nuts = iso3
                                    break
                        else:
                            reg_hit = reg_hit.iloc[0]
                            for name_k in name_translate.keys():
                                name_translate[name_k] = reg_hit[name_k]
                            nuts = reg_hit["NUTS_CODE"]

                        name_regions.append(name_sr)
                        for name_k in regions_translated.keys():
                            regions_translated[name_k].append(name_translate[name_k])
                        risk_regions.append(reg_code)
                        info_regions.append(info_sr)
                        dates_regions.append(self.extract_date(info_sr, preposition=date_ppt))
                        iso3_regions.append(iso3_found)
                        nuts_regions.append(nuts)
                dict_code = {"ISO3_CODE": iso3_states, "risk_level_code": risk_states, "NAME_DE": name_states}
                dict_code.update({name_k: [iso3lang[i3s] for i3s in iso3_states]
                                  for name_k, iso3lang in iso3_names.items()})
                dict_code.update({"risk_date": risk_dates, "region": None,
                                  "REG_EXCLUDED": exc_states, "NUTS_CODE": None, "INFO_DE": info_states})
                df_code = pd.DataFrame(dict_code)
                df_collector[code] = df_code
            else:
                print(f"The following header was not assigned a risk level:")
                print(f"\t{h_text}\n")

        db_new = pd.concat([df_collector[i] for i in self.risk_priority])
        db_curated = db_new.drop_duplicates(subset="ISO3_CODE")

        reg_dict = {"ISO3_CODE": iso3_regions, "risk_level_code": risk_regions, "NAME_DE": name_regions}
        reg_dict.update(regions_translated)
        reg_dict.update({"region": True, "NUTS_CODE": nuts_regions,
                         "risk_date": dates_regions, "INFO_DE": info_regions})
        df_regions = pd.DataFrame(reg_dict)
        df_regions = df_regions.sort_values(["ISO3_CODE", "NAME_DE"])

        df_unknown = pd.DataFrame({"NAME_DE": name_err, "risk_level_code": risk_err, "INFO_DE": info_err,
                                   "risk_date": dates_err, "REG_EXCLUDED": exc_err})
        df_unknown = df_unknown.assign(ISO3_CODE="ERROR", ERROR="UNKNOWN_AREA")

        df_duplicated = pd.concat([db_curated, db_new]).drop_duplicates(keep=False)
        df_duplicated = df_duplicated.assign(ISO3_CODE="ERROR", ERROR="DUPLICATED")

        print(f"Process summary:")
        print(f"\t- {len(db_curated)} states have been succesfully processed")
        print(f"\t- {len(df_regions)} regions have been identified")
        print(f"\t- {len(df_duplicated)} states are duplicated")
        print(f"\t- {len(df_unknown)} states could not be identified")

        db_norisk = db_old.assign(risk_level_code=lambda x: x.where(x["ISO3_CODE"] == "DEU",
                                                                    self.NO_RISK)["risk_level_code"])
        hidden_regions = db_regions.assign(risk_level_code=self.IGNORE).sort_values(["ISO3_CODE", "NAME_DE"])
        df_regions_full = pd.concat([df_regions, hidden_regions]).drop_duplicates(subset="NAME_DE")

        db_curated = pd.concat([db_curated, db_norisk[["ISO3_CODE", "risk_level_code"] +
                                                      names]]).drop_duplicates(subset="ISO3_CODE")
        db_curated = db_curated.sort_values("ISO3_CODE")

        db_final = pd.concat([db_curated, df_regions_full, df_duplicated, df_unknown]).set_index("ISO3_CODE")
        db_final = db_final[names + ["risk_level_code", "risk_date", "region", "NUTS_CODE", "ERROR"]]
        db_final.astype({"risk_level_code": int}).to_csv(db_path, encoding='utf-8-sig',
                                                         date_format=self.date_fmt['db'])

        pd.DataFrame({"report_date": [res_date]}).to_csv(date_path, index=False, date_format=self.date_fmt['db'])

        # Build local databases and jsons
        try:
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        except locale.Error:
            locale.setlocale(locale.LC_TIME, "English")

        db_curated = db_curated.assign(risk_date=pd.to_datetime(db_curated["risk_date"])).set_index("ISO3_CODE")
        df_regions = df_regions.assign(risk_date=pd.to_datetime(df_regions["risk_date"]))

        risk_json = db_curated['risk_level_code'].to_json(force_ascii=False, indent=1)
        with open(data_dir / "risk.js", "w") as f:
            f.write(f"var risk = {risk_json};")

        idioms = pd.read_csv(data_dir / "idioms.csv", index_col=0)
        risk_levels = pd.read_csv(data_dir / "risk_level_code.csv", index_col=0)
        region_exc = db_curated["REG_EXCLUDED"]
        for lang, idiom in idioms.iterrows():
            name_lang = f"NAME_{lang.upper()}"
            risk_labels = risk_levels[f"risk_level_{lang}"]

            locale_json = {'more_info': idiom['more_info'], 'risk_level': idiom['risk'],
                           'risk_labels': risk_labels.fillna('').to_dict()}

            db_lang = db_curated[[name_lang, "risk_level_code"]]
            db_lang = db_lang.assign(
                risk_level=db_lang.apply(lambda df: risk_labels[df["risk_level_code"]],axis=1)
            ).rename(columns={name_lang: "name"})

            if lang == 'de':
                info_lang = db_curated["INFO_DE"].fillna('')
            else:
                date_format = idiom['date_format']

                info_lang = db_curated["risk_date"].dt.strftime(date_format).fillna('').rename("info")

                regions_lang = df_regions[["ISO3_CODE", name_lang, 'risk_date']]
                regions_lang = regions_lang.assign(risk_date=regions_lang["risk_date"].dt.strftime(f", {date_format}"))
                regions_lang = regions_lang.assign(reg_list="<li>" + regions_lang[name_lang])
                regions_lang["reg_list"] += regions_lang["risk_date"].fillna('')
                regions_lang["reg_list"] += "</li>"
                region_infos = regions_lang.groupby("ISO3_CODE")["reg_list"].apply(''.join)
                region_infos = "<ul>" + region_infos + "</ul>"
                region_infos = pd.concat([region_infos, region_exc], axis=1, join="inner")
                region_infos["reg_prefix"] = idiom["excluded"]
                region_infos["reg_prefix"] = region_infos["reg_prefix"].where(
                    region_infos["REG_EXCLUDED"],
                    idiom["applying"]
                )
                region_infos["info_reg"] = ". " + region_infos["reg_prefix"] + region_infos["reg_list"]

                info_lang = pd.concat([info_lang, region_infos], axis=1)
                info_lang = info_lang["info"] + info_lang["info_reg"].fillna('')

            db_lang = db_lang.assign(info=info_lang)

            info_json = db_lang[["name", "info"]].T.to_json(force_ascii=False, indent=1)
            with open(data_dir / f"locale_{lang}.js", "w", encoding='utf-8') as f:
                f.write(f"var locale = {locale_json};\n")
                f.write(f"var info_rki = {info_json};\n")

            csv_lang = db_lang.reset_index()[['name', 'risk_level', 'info']]
            csv_lang['info'] = csv_lang['info'].\
                str.replace("<ul><li>", " -").str.replace("</li><li>", "; -").str.replace("<.*?>","", regex=True)

            csv_lang.columns = [idiom[col] for col in ("country", "risk", "details")]
            csv_lang.to_csv(dist_dir / f"db_countries_risk_{lang}.csv", encoding='utf-8-sig', index=False)

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
