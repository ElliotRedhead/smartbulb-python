import asyncio
import csv
import os

from datetime import datetime
from kasa import SmartPlug
from werkzeug.utils import secure_filename

from dotenv import load_dotenv

load_dotenv()


async def initialise_plug():
    plug_ip = os.environ["SMART_PLUG_IP"]

    plug = SmartPlug(plug_ip)
    await plug.update()
    return plug


def write_realtime_csv(plug, record_time):
    realtime_energy = plug.emeter_realtime

    dirpath = os.environ["REALTIME_DIRPATH"]
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
    plug = asyncio.run(initialise_plug())
    write_realtime_csv(plug, record_time)
