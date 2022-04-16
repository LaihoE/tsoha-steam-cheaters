import pandas as pd

def check_input(input_id):
    try:
        input_id = int(input_id)
    except ValueError:
            return False
    if len(str(input_id)) != len('76561197991348083') or not (75000000000000000 < input_id < 77000000000000000):
        return False
    return True


def dict_to_html_df(d, single_row=False):
    if single_row:
        return pd.DataFrame.from_dict({k:[v] for k, v in d.items()})
    else:
        return pd.DataFrame.from_dict(d)