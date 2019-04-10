"""
Module sets CSS styles
"""
table_style = [
            {
                'selector': 'td',
                'props': [
                    ('padding', '1em 2em 1em 2em'),
                    ('border', '1px solid black'),
                    ('font-size', '10'),
                    ('font-weight', '200'),
                    ('font-family', 'Helvetica'),
                    ('text-align', 'center'),
                    ('border', '1px solid black')
                ]
            },
            {
                'selector': 'th',
                'props': [
                    ('padding', '1em 2em 1em 2em'),
                    ('background-color', '#187ce0'),
                    ('font-size', '10'),
                    ('font-weight', '600'),
                    ('font-family', 'Helvetica'),
                    ('color', 'white'),
                    ('border', '1px solid black')

                ]
            }
        ]

table_attribs = 'style="border-collapse:collapse; border:solid 1px black;"'

formats = {'TOTAL DAYS WITH NO CASES (%)': '{:.1%}'}

def highlight(s):
    color = '#efefef'
    return 'background-color: %s' % color

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val == 0 else 'black'
    return 'color: %s' % color



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
