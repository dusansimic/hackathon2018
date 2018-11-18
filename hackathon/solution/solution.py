"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir

blackoutsCounter = 0
blackoutAdded = False

def worker(msg: DataMessage) -> ResultsMessage:
    """TODO: This function should be implemented by contestants."""
    # Details about DataMessage and ResultsMessage objects can be found in /utils/utils.py

    (power_reference, pv_mode) = ChargingHandler(msg)
    (load_one, load_two, load_three, power_reference) = BlackoutHandler(msg, power_reference)

    return ResultsMessage(data_msg=msg,
                          load_one=load_one,
                          load_two=load_two,
                          load_three=load_three,
                          power_reference=power_reference,
                          pv_mode=pv_mode)


def run(args) -> None:
    prepare_dot_dir()
    config_outs(args, 'solution')

    cntrl = Control()

    for data in cntrl.get_data():
        cntrl.push_results(worker(data))

"""
    Punjenje baterije
    Params: msg
    Returns: power_reference
"""
def ChargingHandler(msg):
    global blackoutsCounter
    power_reference = 0.0
    pv_mode = PVMode.ON

    # Ako udjemo u gap gde je struja skupa a nema svetla
    if msg.buying_price == 8:
        if msg.bessSOC > 0.25:
            usage = msg.solar_production - msg.current_load
            if usage < 0.0:
                power_reference = -(usage)
            elif usage > 0.0:
                power_reference = usage
        else:
            power_reference = 0.0

    # Ako udjemo u gap gde je struja jeftina a nema svetla
    if msg.solar_production == 0 and msg.buying_price == 3:
        if msg.bessSOC < 1.0:
            power_reference = -5.0

    # Ako radi grid i napunjenost baterije je manje od 99%
    if msg.solar_production != 0 and msg.solar_production > msg.current_load:
        # Punjenje baterije je jednako visko kao proizvodnja solarne energije
        power_reference = -(msg.solar_production - msg.current_load)
        # Ako radi grid i punjenje baterije je vece od granicne
        if msg.grid_status:
            if power_reference < -5.0:
                power_reference = -5.0
        else:
            if power_reference < -5.0:
                power_reference = 5.0
                pv_mode = PVMode.OFF
            if msg.bessSOC == 1:
                power_reference = 5.0
                pv_mode = PVMode.OFF

    if blackoutsCounter == 5:
        power_reference = msg.solar_production - msg.current_load
        if power_reference < 0.0:
            power_reference = -(power_reference)
            if power_reference > 5.0:
                power_reference = 5.0
        elif power_reference > 0.0:
            power_reference = -(power_reference)
            if power_reference > -5.0:
                power_reference = -5.0

    return (power_reference, pv_mode)

"""
    Resavanje problema u slucaju blackouta
    Params: msg
    Returns: load_one, load_two, load_three, power_reference
"""
def BlackoutHandler(msg, power_reference):
    global blackoutAdded
    global blackoutsCounter
    load_one = True
    load_two = True
    load_three = True

    # Ako nema grida
    if not msg.grid_status:
        # Povlacenje baterije je jednako opterecenju kuce bez panela
        power_reference = msg.current_load - msg.solar_production
        # Ako je opterecenje baterije vece od maksimalnog opterecenja
        if power_reference > 5.0:
            power_reference = 5.0
            # Gasenje uredjaja radi sprecavanja preopterecenja
            (load_one, load_two, load_three) = LoadHandler(msg)
        # Ako blackout nije uracunat uracunaj ga i reci da je uracunat
        if not blackoutAdded:
            blackoutsCounter+=1
            blackoutAdded = True
    # Ako ima grida i blackout je uracunat reci da nije uracunat
    if msg.grid_status and blackoutAdded:
        blackoutAdded = False

    return (load_one, load_two, load_three, power_reference)

"""
    Gasenje uredjaja u slucaju da je preveliko opterecenje
    Params: msg
    Returns: load_one, load_two, load_three
"""
def LoadHandler(msg):
    # Ako je opterecenje kuce vece od baterije i panela zajedno
    if msg.current_load > msg.solar_production + 5.0:
        # Ako je opterecenje kuce bez 3. uredjaja vece od baterije i panela zajedno
        if msg.current_load * 0.6 > msg.solar_production + 5.0:
            # Ako je opterecenje kuce u kurcu tj nemas bateriju a sve vrsti
            if msg.current_load * 0.2 > msg.solar_production and msg.bessSOC == 0:
                # Gasi se 1. 2. i 3. uredjaj
                return (False, False, False)
            # Gasi se 2. i 3. uredjaj
            return (True, False, False)
        # Gasi se 3. uredjaj
        return (True, True, False)
