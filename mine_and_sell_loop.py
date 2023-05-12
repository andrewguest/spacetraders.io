import os
from time import sleep

import requests
from dotenv import load_dotenv


# load .env file
load_dotenv()


# constants
BASE_URL = "https://api.spacetraders.io"

AGENT_ENDPOINT = "/v2/my/agent"
CARGO_ENDPOINT = "/v2/my/ships/ZER0-COOL-2/cargo"
COOLDOWN_ENDPOINT = "/v2/my/ships/ZER0-COOL-2/cooldown"
DOCK_ENDPOINT = "/v2/my/ships/ZER0-COOL-2/dock"
EXTRACT_ENDPOINT = "/v2/my/ships/ZER0-COOL-2/extract"
SELL_ENDPOINT = "/v2/my/ships/ZER0-COOL-2/sell"

HEADERS = {"Authorization": f'Bearer {os.getenv("BEARER_TOKEN")}'}

CONTINUE_MINING = True


def sell_cargo():
    """Check the ship's cargo and sell any cargo present"""

    #################################
    # Check if any cargo is present #
    #################################
    cargo_response_json = requests.get(
        f"{BASE_URL}{CARGO_ENDPOINT}", headers=HEADERS
    ).json()

    if cargo_response_json["data"]["units"] > 0:
        cargo_to_sell_dict = {
            resources_dict["symbol"]: resources_dict["units"]
            for resources_dict in cargo_response_json["data"]["inventory"]
        }

        print("Cargo present to sell:")
        [
            print(f"{symbol}: {units}")
            for symbol, units in cargo_to_sell_dict.items()
        ]

        ################################
        # Dock ship to be able to sell #
        ################################
        requests.post(f"{BASE_URL}{DOCK_ENDPOINT}", headers=HEADERS)

        ##############################
        # Sell all resources on ship #
        ##############################
        for resource_symbol, resource_units in cargo_to_sell_dict.items():
            response = requests.post(
                f"{BASE_URL}{SELL_ENDPOINT}",
                headers=HEADERS,
                data={"symbol": resource_symbol, "units": resource_units},
            )

        print("\n")
        print(f"Credit balance: {get_my_credit_balance():,}")
        print("\n")


def extract_resources():
    response_json = requests.post(
        f"{BASE_URL}{EXTRACT_ENDPOINT}", headers=HEADERS
    ).json()

    units = response_json["data"]["cargo"]["units"]
    capacity = response_json["data"]["cargo"]["capacity"]
    cooldown_timer = response_json["data"]["cooldown"]["remainingSeconds"] + 5

    return units, capacity, cooldown_timer


def get_ship_cooldown_timer():
    cooldown_response = requests.get(
        f"{BASE_URL}{COOLDOWN_ENDPOINT}", headers=HEADERS
    )

    # There is an active cooldown, so return the remaining seconds
    if cooldown_response.status_code == 200:
        return cooldown_response["data"]["remainingSeconds"] + 5

    # `204` means there's no active cooldown for this ship, so return 0
    elif cooldown_response.status_code == 204:
        return 0

    # Something else happened, so just return 65 seconds
    else:
        return 65


def get_my_credit_balance():
    agent_response_json = requests.get(
        f"{BASE_URL}{AGENT_ENDPOINT}", headers=HEADERS
    ).json()

    return agent_response_json["data"]["credits"]


if __name__ == "__main__":
    sell_cargo()

    cooldown_timer = get_ship_cooldown_timer()
    print(f"Sleeping for {cooldown_timer} seconds")
    sleep(cooldown_timer)

    while CONTINUE_MINING:
        # extract resources
        units, capacity, cooldown_timer = extract_resources()

        # if there's room left in the ship, continue mining
        if units == capacity:
            print("At capacity. Selling...")
            sell_cargo()
            print(f"Sleeping for {cooldown_timer} seconds")
            sleep(cooldown_timer)

        else:
            print(f"{units}/{capacity}")
            print(
                f"Continuing to mine... Sleeping for: {cooldown_timer} seconds"
            )
            sleep(cooldown_timer)
