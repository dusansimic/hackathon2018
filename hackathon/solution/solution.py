"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir


def worker(msg: DataMessage) -> ResultsMessage:
    """TODO: This function should be implemented by contestants."""
    # Details about DataMessage and ResultsMessage objects can be found in /utils/utils.py

    (power_reference, pv_mode) = ChargingHandler(msg)
    (load_one, load_two, load_three, power_reference) = BlackoutHandler(msg, power_reference)

    # if msg.grid_status:
    #     if msg.bessSOC != 1 and msg.buying_price == msg.selling_price \
    #             and msg.current_load <8:
    #         if msg.bessSOC > 0.45:
    #             power_reference = -5.0
    #     elif msg.current_load > 8:
    #         power_reference = msg.current_load
    #
    # else:
    #     if msg.bessSOC == 1 and msg.solar_production > 0:
    #         if msg.solar_production < msg.current_load:
    #             power_reference = msg.current_load
    #             load_three = False
    #             pv_mode = PVMode.OFF
    #         else:
    #             power_reference = msg.current_load
    #     elif msg.bessSOC != 1:
    #         load_three = False
    #         pv_mode = PVMode.ON
    #
    #     elif msg.selling_price == msg.buying_price and msg.solar_production == 0:
    #         power_reference = msg.current_load

    # Dummy result is returned in every cycle here
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
    power_reference = 0.0
    pv_mode = PVMode.ON

    # Ako udjemo u gap gde je struja skupa a nema svetla
    if msg.solar_production == 0 and msg.buying_price == 8:
        power_reference = 5.0
    # Ako radi grid i napunjenost baterije je manje od 95%
    if msg.grid_status and msg.bessSOC < 0.95 and msg.buying_price == 3:
        power_reference = -5.0
    if not msg.grid_status:
        if msg.bessSOC >= 0.95:
            pv_mode = PVMode.OFF
        else:
            pv_mode = PVMode.ON

    return (power_reference, pv_mode)

"""
    Resavanje problema u slucaju blackouta
    Params: msg
    Returns: load_one, load_two, load_three, power_reference
"""
def BlackoutHandler(msg, power_reference):
    load_one = True
    load_two = True
    load_three = True

    # Ako nema grida
    if not msg.grid_status:
        # Povlacenje baterije je jednako opterecenju kuce bez panela
        power_reference = msg.current_load - msg.solar_production
        # Ako je opterecenje baterije vece od maksimalnog opterecenja
        if(power_reference > 5.0):
            power_reference = 5.0
            # Gasenje uredjaja radi sprecavanja preopterecenja
            (load_one, load_two, load_three) = LoadHandler(msg)

    return (load_one, load_two, load_three, power_reference)


def LoadHandler(msg):
    # Ako je opterecenje kuce vece od baterije i panela zajedno
    if msg.current_load > msg.solar_production + 5.0:
        # Ako je opterecenje kuce bez 3. uredjaja vece od baterije i panela zajedno
        if msg.current_load * 0.6 > msg.solar_production + msg.bessPower:
            # Gasi se 2. i 3. uredjaj
            return (True, False, False)
        # Gasi se 3. uredjaj
        return (True, True, False)
