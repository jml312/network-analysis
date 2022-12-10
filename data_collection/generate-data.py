import subprocess
import jc
import csv
import json
import time


def dig_site(site):
    """Dig site and return query time and ip addresses"""
    start_time = time.time()
    sys_call = subprocess.run(
        ["dig", site], capture_output=True)
    end_time = time.time()
    output = jc.parse("dig", sys_call.stdout.decode("utf-8"))[0]
    return {
        "query_time_ms": output["query_time"],
        "ip_adresses": [item["data"] for item in output["answer"]],
        "ran_in": end_time - start_time
    }


def ping_site(site):
    """Ping site and return rtt and packet loss"""
    start_time = time.time()
    sys_call = subprocess.run(
        ["ping", "-c", "30", "-i", "0.2", site], capture_output=True)
    end_time = time.time()
    output = jc.parse("ping", sys_call.stdout.decode("utf-8"))
    return {
        "packets_transmitted": output["packets_transmitted"],
        "packets_received": output["packets_received"],
        "packet_loss_percent": output["packet_loss_percent"],
        "round_trip_ms_min": output["round_trip_ms_min"],
        "round_trip_ms_avg": output["round_trip_ms_avg"],
        "round_trip_ms_max": output["round_trip_ms_max"],
        "round_trip_ms_stddev": output["round_trip_ms_stddev"],
        "ran_in": end_time - start_time
    }


def traceroute_site(site):
    """Traceroute site and return hops, rtts, and time diffs"""
    start_time = time.time()
    sys_call = subprocess.run(
        ["traceroute", site], capture_output=True)
    end_time = time.time()
    output = jc.parse("traceroute", sys_call.stdout.decode("utf-8"))
    hops = output["hops"]
    rtts = [[probe["rtt"] for probe in hop["probes"]
             if probe["rtt"] is not None] for hop in hops]
    return {
        "hops": len(hops),
        "rtts": rtts,
        "ran_in": end_time - start_time
    }


def main():
    # read csv of sites
    NUM_SITES = 500
    sites = []
    with open("top-1m.csv") as csv_file:
        reader = csv.reader(csv_file)
        for _, site_name in list(reader)[:NUM_SITES]:
            sites.append(site_name)

    data = {"data": [], "ran_in": 0}
    errors = []
    print(f"Starting data collection on {NUM_SITES} sites...")
    start_time = time.time()
    for idx, site in enumerate(sites):
        msg = f"{idx + 1} / {NUM_SITES}..."
        curr_data = {}

        try:
            # dig
            curr_data.update({"dig": dig_site(site)})
        except Exception:
            errors.append({"site": site, "error": "dig"})
            print(f"{msg}ERROR")
            continue

        try:
            # ping
            curr_data.update({"ping": ping_site(site)})
        except Exception:
            errors.append({"site": site, "error": "ping"})
            print(f"{msg}ERROR")
            continue

        try:
            # traceroute
            curr_data.update({"traceroute": traceroute_site(site)})
        except Exception:
            errors.append({"site": site, "error": "traceroute"})
            print(f"{msg}ERROR")
            continue

        print(f"{msg}SUCCESS")
        data["data"].append({"site": site, **curr_data})

    data["ran_in"] = time.time() - start_time

    # write data to json file
    with open("results.json", "w") as json_file:
        json.dump(data, json_file)

    # write errors to json file
    with open("errors.json", "w") as json_file:
        json.dump(errors, json_file)


if __name__ == "__main__":
    main()
