"""This module is main module for contestant's solution."""

from hackathon.utils.control import Control
from hackathon.utils.utils import ResultsMessage, DataMessage, PVMode, \
    TYPHOON_DIR, config_outs
from hackathon.framework.http_server import prepare_dot_dir


def worker(msg: DataMessage) -> ResultsMessage:
    """TODO: This function should be implemented by contestants."""
    # Details about DataMessage and ResultsMessage objects can be found in /utils/utils.py

    load_one = True
    load_two = True
    load_three = True
    power_reference = 0.0
    pv_mode = PVMode.ON

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

def blackout_handler(msg):
    if(msg.grid_status == False):
        power_reference = msg.current_max_load - msg.solar_production
        if(power_reference > 5):
            power_reference = 5


def LoadHandler(msg):
    if(blackout_flag and (msg.current_max_load > msg.solar_production + msg.bessPower)