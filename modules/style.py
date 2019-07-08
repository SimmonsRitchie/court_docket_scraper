"""
This modules sets CSS styles
"""
import numpy as np


table_style = [
    {
        "selector": "td",
        "props": [
            ("padding", "0.3em"),
            ("border", "1px solid black"),
            # ('font-size', '1em'),
            ("font-weight", "200"),
            # ('font-family', 'Helvetica'),
            ("text-align", "center"),
            ("line-height", "normal"),
            ("border", "1px solid #21406F"),
        ],
    },
    {
        "selector": "th",
        "props": [
            ("padding", "0.3em"),
            ("background-color", "#21406F"),
            # ('font-size', '1em'),
            ("font-weight", "600"),
            # ('font-family', 'Helvetica'),
            ("color", "white"),
            ("border", "1px solid #21406F"),
            ("text-transform", "lowercase"),
        ],
    },
]

table_attribs = 'style="border-collapse:collapse; border:solid 1px black;"'

formats = {"URL": "{:.1%}"}


def make_clickable(val):
    return '<a href="{}">{}</a>'.format(val, "VIEW")


def currency_convert(value):
    """
    Because Pandas values are numpy objects, we determine nan values using np.isnan
    """
    if np.isnan(value):
        return ""
    else:
        return "${:,.0f}".format(value)


def highlight(s):
    color = "#efefef"
    return "background-color: %s" % color


def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = "red" if val == 0 else "black"
    return "color: %s" % color


"""
PANDAS STYLE CHEAT SHEET

############### FORMAT: ADDING PERCENTAGE SIGN/REDUCING DECIMAL #################

To reduce to 2dp and add percentage use:

    .format({'PERCENT_days_with_no_cases': '{:.2%}'})
    
Eg.

        df = df.style\
            .applymap(style.color_negative_red)\
            .applymap(style.highlight, subset=pd.IndexSlice[ 'TOTAL', : ])\
            .applymap(style.highlight, subset=pd.IndexSlice[:, ['TOTAL_cases', 'TOTAL_days','PERCENT_days_with_no_cases','TOTAL DAYS WITH NO CASES' ]]) \
            .set_table_styles(style.table_style) \
            .format({'PERCENT_days_with_no_cases': '{:.2%}'})\
            .set_table_attributes(style.table_attribs)\

############### SET TABLE PROPERTIES #################

Use this:

    .set_properties(**{'font-size': '9pt', 'font-family': 'Calibri', 'border': '1px solid black', 'text-align': 'center', 'padding':'none','margin':'none'})\

 """
