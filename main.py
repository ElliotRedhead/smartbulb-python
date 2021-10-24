import asyncio
import csv
import os
import sys

from datetime import datetime
from kasa import SmartPlug
from werkzeug.utils import secure_filename

from dotenv import load_dotenv

load_dotenv()


def env_var_fail_message(env_var_name):
    datetime_string = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    return (
        f"{datetime_string}: Environmental variable was not found for {env_var_name}.\n"
    )


async def initialise_plug(plug_ip):
    plug = SmartPlug(plug_ip)
    await plug.update()
    return plug


def write_realtime_csv(plug, record_time):
    realtime_energy = plug.emeter_realtime

    try:
        dirpath = os.environ["REALTIME_DIRPATH"]
    except KeyError:
        # Create default dirpath as fallback
        dirpath = "./data/"
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open("smarterkasalog.txt", "a") as f:
            f.write(env_var_fail_message("REALTIME_DIRPATH"))

    filename = secure_filename(
        f"{record_time.strftime('%Y%m%d')}_{plug.alias.lower()}_realtime_energy.csv"
    )

    file_exists = os.path.isfile(dirpath + filename)

    realtime_energy
    with open(dirpath + filename, "a", newline="") as csvfile:
        fieldnames = [
            "device_alias",
            "device_ip",
            "device_mac",
            "datetime",
            "epoch_time",
            "power_w",
            "current_a",
            "voltage_v",
            "total_kwh",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                fieldnames[0]: plug.alias,
                fieldnames[1]: plug.host,
                fieldnames[2]: plug.mac,
                fieldnames[3]: record_time.strftime("%H:%M:%S"),
                fieldnames[4]: record_time.timestamp(),
                fieldnames[5]: realtime_energy.power,
                fieldnames[6]: realtime_energy.current,
                fieldnames[7]: realtime_energy.voltage,
                fieldnames[8]: realtime_energy.total,
            }
        )


if __name__ == "__main__":
    record_time = datetime.now()
    try:
        plug_ips = os.environ["SMART_PLUG_IPS"].split(",")
    except KeyError:
        # Very basic log, and quit execution
        with open("smarterkasalog.txt", "a") as f:
            f.write(env_var_fail_message("SMART_PLUG_IPS"))
        sys.exit(1)
    for plug_ip in plug_ips:
        plug = asyncio.run(initialise_plug(plug_ip))
        write_realtime_csv(plug, record_time)
