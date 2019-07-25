import requests

def helper_delete(s, rest_api, list_of_docketnums):
    """
    This helper function deletes data that has matching docketnums
    """
    hostname = rest_api["hostname"]
    delete_count = 0
    for docketnum in list_of_docketnums:
        delete_endpoint = hostname + "/case/" + docketnum
        r = s.delete(delete_endpoint)
        status_code = r.status_code
        data = r.json() if r.content else None
        # failure
        if status_code != 200:  # not status 'ok'
            print(data)
        else:
            # success
            print(f">> Deleted {docketnum}")
            delete_count += 1
    print(f"{delete_count} cases deleted")
    return s


def helper_get_docketnums_in_db(rest_api):
    """
    This helper function returns a list of all docketnums in our db
    """

    hostname = rest_api["hostname"]

    print("Getting cases...")
    get_cases_endpoint = hostname + "/cases"
    r = requests.get(get_cases_endpoint)
    status_code = r.status_code
    data = r.json()
    # failure
    if status_code != 200:  # not status 'ok'
        print(data)
        return
    # success
    cases = data["cases"]
    return [case["docketnum"] for case in cases]