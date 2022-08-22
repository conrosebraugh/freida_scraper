import requests


def fetch_programs(offset=0):
    program_url = "https://freida-admin.ama-assn.org/api/node/program"

    payload = {
        "fields[node--program]": "title,path,field_address,field_expanded_listing,field_geolocation,field_program_id,field_specialty,field_survey,drupal_internal__nid",
        "fields[node--survey_2022]": "field_program_best_described_as,field_program_size,field_accepting_current_year,field_accepting_next_year,moderation_state,field_match_nrmp_main,field_participates_in_eras",
        "fields[node--survey_2023]": "field_program_best_described_as,field_program_size,field_accepting_current_year,field_accepting_next_year,moderation_state,field_match_nrmp_main,field_participates_in_eras",
        "fields[node--survey_2021]": "field_program_best_described_as,field_program_size,field_accepting_current_year,field_accepting_next_year,moderation_state,field_match_nrmp_main,field_participates_in_eras",
        "fields[node--survey_2020]": "field_program_best_described_as,field_program_size,field_accepting_current_year,field_accepting_next_year,moderation_state,field_match_nrmp_main,field_participates_in_eras",
        "include": "field_specialty,field_survey",
        "filter[specialty][condition][operator]": "IN",
        "filter[specialty][condition][path]": "field_specialty.drupal_internal__nid",
        # "filter[specialty][condition][value][]": "42771", # internal medicine
        # "filter[specialty][condition][value][]": "43086", # pediatric
        "filter[specialty][condition][value][]": "42736", # family medicine
        "page[limit]": "700",
        "page[offset]": str(offset)
    }
    j = requests.get(program_url, params=payload).json()
    return [x["id"] for x in j["data"] if x["type"] == "node--program"]

# hi angie


def get_programs():
    program_ids = fetch_programs()
    last_fetch_len = len(program_ids)
    while last_fetch_len == 50:
        curr_size = len(program_ids)
        program_ids.extend(fetch_programs(curr_size))
        last_fetch_len = len(program_ids) - curr_size
    return program_ids


def fetch_program_details(program_id):
    details_url = "https://freida-admin.ama-assn.org/api/node/program/{}".format(program_id)

    payload = {
        "include": "field_survey"
    }

    r = requests.get(details_url, payload)
    if r.status_code == 200:
        return r.json()
    else:
        print("problem fetching program_id {}".format(program_id))
        print(r.status_code)
        print(r.content)
        return None


def get_program_details(program_id):
    data = fetch_program_details(program_id)

    if not data:
        return None

    details = {}
    details["Program Name"] = data["data"]["attributes"].get("title", "")
    details["State"] = data["data"]["attributes"]["field_address"]["administrative_area"]
    details["City"] = data["data"]["attributes"]["field_address"]["locality"]
    if len(data["included"][0]["attributes"]["field_program_size"]) == 0:
        details["Number of Positions"] = "No Data"
    else:
        details["Number of Positions"] = data["included"][0]["attributes"]["field_program_size"][0]
    details["ERAS?"] = data["included"][0]["attributes"].get("field_participates_in_eras", False)
    details["Percent IMG"] = data["included"][0]["attributes"].get("field_pct_img", "")
    details["Step 1 Average"] = data["included"][0]["attributes"].get("field_usmle_step_1_avg", "")
    details["Step 1 Min Score"] = data["included"][0]["attributes"].get("field_usmle_step_1_minimum_score", "")
    details["Step 2 Min Score"] = data["included"][0]["attributes"].get("field_usmle_step_2_minimum_score", "")
    details["Years Since Graduation"] = data["included"][0]["attributes"].get("field_years_since_graduation", "")

    return details


def get_all_program_details(program_ids):
    program_details = []
    for program_id in program_ids:
        deets = get_program_details(program_id)
        if deets:
            program_details.append(deets)

    return [x for x in program_details if x["ERAS?"] == True]


if __name__ == '__main__':
    program_ids = get_programs()
    print("fetched {} program ids".format(len(program_ids)))

    eras_programs = get_all_program_details(program_ids)
    print("gathered details on {} programs that support ERAS".format(len(eras_programs)))
    import json
    with(open("eras_fam_med.json", "w", encoding="utf-8")) as f:
        json.dump(eras_programs, f, ensure_ascii=False, indent=4)
