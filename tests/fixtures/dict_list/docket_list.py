
def docket_list_gen(num_of_items):
    docket_list = []
    for count in range(num_of_items):
        case_caption = "Commonwealth V. Zane, Zidane." if (count % 2 == 0) \
            else "Commonwealth V. Adam, Applegate"
        docket_list.append({
            "county": "Dauphin",
            "docketnum": count,
            "arresting_agency": "Harrisburg Police Dept",
            "township": "Harrisburg City",
            "case_caption": case_caption,
            "dob": "01/01/1986",
            "filing_date": "03/03/2019",
            "charges": "Receiving Stolen Property; Driving W/O A License",
            "bail": count * 100,
            "url": "https://ujsportal.pacourts.us/DocketSheets/MDJReport.ashx?docketNumber=MJ-12302-CR-0000110-2019&dnh=zj8BkxXzkOi23xMzscQ6hw%3d%3d"
        })
    return docket_list


docket_list = docket_list_gen(10)
