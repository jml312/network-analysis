import requests
import json
import time


def lookup_ip(ip_address):
    """Lookup ip address associated with site name and return location data"""
    API_URL = f"http://ip-api.com/json/{ip_address}"
    result = requests.get(API_URL)
    json = result.json()
    return {
        "latitude": json["lat"],
        "longitude": json["lon"],
        "country": json["country"],
        "country_code": json["countryCode"],
        "ip_address": ip_address
    }


def main():
    with open('data.json') as f:
        raw_data = json.load(f)
        data = []
        NUM_SITES = len(raw_data["data"])
        num_errors = 0
        print(f"Getting locations for {NUM_SITES} sites...")
        for idx, site_data in enumerate(raw_data["data"]):
            print(f"{idx + 1} / {NUM_SITES}...")

            site_name, ip_addresses = site_data["site"], site_data["dig"]["ip_adresses"]

            curr_data = {"site": site_name}

            locations = []
            for ip_address in ip_addresses:
                try:
                    locations.append(lookup_ip(ip_address))
                    time.sleep(1)
                except Exception:
                    num_errors += 1
                    locations.append(ip_address)

                    if num_errors > 10:
                        print("Too many errors, exiting...")
                        exit(1)

            curr_data.update({"locations": locations})

            data.append(curr_data)

        with open("locations.json", "w") as json_file:
            json.dump(data, json_file)


if __name__ == "__main__":
    main()
