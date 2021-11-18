"""
A script to get my Hero's stamina from the CLI
"""
import requests
import os
import json
import time
import math
from typing import List

# endpoint
url = "https://graph2.defikingdoms.com/subgraphs/name/defikingdoms/apiv5"

# loading queries and params from files
pwd = os.path.dirname(os.path.realpath(__file__))
queries_folder = pwd + "/queries"

# creating query variables programatically
for query in os.listdir(queries_folder):
    for data in os.listdir(queries_folder + "/" + query):
        path = queries_folder + "/" + query + "/" + data
        if "params" in data:
            globals()[f"{query}_params"] = json.load(open(path))
        if "query" in data:
            globals()[f"{query}_query"] = open(path).read()


def get_all_heroes(address: str) -> List[dict]:
    """
    Returns all heroes for a given user
    """
    query = get_all_heroes_query
    params = get_all_heroes_params
    params["owner"] = address

    return json.loads(
        requests.post(url, data=json.dumps({"query": query, "variables": params})).text
    )["data"]["heros"]


def get_heroes_and_stamina(address: str) -> List[dict]:
    return [
        {
            "hero_id": hero["id"],
            "time_until_stamina_full": str(
                math.ceil((int(hero["staminaFullAt"]) - int(time.time())) / 60)
            )
            + " minutes",
        }
        for hero in get_all_heroes(address)
    ]


def get_all_heroes_floor() -> float:
    """Floor price for heroes in Jewel"""
    response = requests.post(
        url,
        data=json.dumps(
            {
                "query": get_all_heroes_floor_query,
                "variables": get_all_heroes_floor_params,
            }
        ),
    )
    return (
        int(
            json.loads(response.text)["data"]["heros"][0]["saleAuction"][
                "startingPrice"
            ]
        )
        / 10 ** 18
    )


if __name__ == "__main__":
    
    # hero stamina
    heroes = get_heroes_and_stamina(os.environ["DFK_ADDRESS"])
    from pprint import pprint

    for hero in heroes:
        pprint(hero)

    # hero floor price
    print(f"Floor price: {str(get_all_heroes_floor())} JEWEL")
