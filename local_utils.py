import pandas as pd
import json
from typing import List
import os


def load_m49() -> pd.DataFrame:
    entries = []
    with open('un-m49.txt') as fp:
        for line in fp.readlines():
            entries.append({'region_id': line[:3].strip(),
                            'region_parent': line[4:7].strip(),
                            'region_code': line[8:11].strip(),
                            'region_name': line[11:].strip()})

    return pd.DataFrame(entries)


def read_rvrs_datafile(filename: str, rv_labels: List[str]) -> pd.DataFrame:
    if not os.path.exists(filename):
        return None

    with open(filename) as fp:
        raw_data = json.load(fp)

    if len(raw_data['data']) > 0:
        # There are data points
        tmp = pd.DataFrame(raw_data['data'])

        # TODO: There is a column 'rv_rtyp_seen' that needs expanding, as it's a list of values
        tmp2 = tmp.merge(tmp['rv_rtyp_seen'].apply(lambda x: vector2series(x, rv_labels)).fillna(0.0).astype(int),
                         left_index=True, right_index=True)

        for dc, sc in [ ['out_cc_ratio', 'outcc'],
                        ['in_cc_ratio', 'incc'],
                        ['same_as_ratio', 'sameas'],
                        ['google_pdns_ratio', 'googlepdns'],
                        ['all_open_res_ratio', 'allopnrvrs'],
                        ['non_open_res_ration', 'xopnrvrs']]:

            tmp2[dc] = round(100*tmp2[sc] / tmp2['rv_seen'], 2)

        tmp2['rv_dt'] = pd.to_datetime(tmp2['rv_dt'])

        return tmp2


def read_resolver_definition() -> pd.DataFrame:
    return pd.read_csv('apnic-resolver-info.csv')


def vector2series(vector: List[int], labels: List[str]) -> pd.Series:
    if len(vector) == 40:
        return pd.Series(dict(zip(labels, vector))).fillna(0.0).astype(int)
    elif len(vector) == 38:
        return pd.Series(dict(zip(labels[:38], vector))).fillna(0.0).astype(int)
    else:
        raise ValueError("Don't know how to handle this vector")

#%%
