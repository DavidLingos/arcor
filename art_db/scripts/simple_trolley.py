#!/usr/bin/env python

import sys
import rospy
from art_msgs.msg import Program, ProgramBlock, ProgramItem
from copy import deepcopy
from art_utils import ArtApiHelper
from art_utils.art_msgs_functions import obj_type, wait_item, feeder_item, grid_item, drill_item, place_item,\
    item, polygon_item, visual_inspection_item, place_container_item
from geometry_msgs.msg import PolygonStamped


def main(args):

    rospy.init_node('simple_trolley_init_script', anonymous=True)

    art = ArtApiHelper()
    # art.wait_for_api()

    # delete all created programs
    ph = art.get_program_headers()
    if ph:
        for h in ph:

            art.program_clear_ro(h.id)
            art.delete_program(h.id)

    # -------------------------------------------------------------------------------------------
    # Training program 1
    # -------------------------------------------------------------------------------------------

    prog = Program()
    prog.header.id = 1
    prog.header.name = "Trenink - oblast"

    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Zvedni ze stolu a poloz"
    pb.on_success = 1
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(polygon_item(1))
    pb.items.append(place_item(2, ref_id=[1], on_success=3, on_failure=0))
    pb.items.append(item(3, "GetReady", on_success=4, on_failure=0))
    pb.items.append(wait_item(4, ref_id=[2], on_success=1, on_failure=0))

    art.store_program(prog)
    art.program_set_ro(prog.header.id)

    # -------------------------------------------------------------------------------------------
    # Training program 2
    # -------------------------------------------------------------------------------------------

    prog = Program()
    prog.header.id = 2
    prog.header.name = "Trenink - podavac"

    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Zvedni z podavace a poloz"
    pb.on_success = 1
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(feeder_item(1))
    pb.items.append(place_item(2, ref_id=[1], on_success=3, on_failure=0))
    pb.items.append(feeder_item(3, ref_id=[1]))
    pb.items.append(place_item(4, ref_id=[3], on_success=5, on_failure=0))
    pb.items.append(item(5, "GetReady", on_success=6, on_failure=0))
    pb.items.append(wait_item(6, ref_id=[4], on_success=1, on_failure=0))

    art.store_program(prog)
    # art.program_set_ro(prog.header.id)

    # -------------------------------------------------------------------------------------------
    # Training program 3
    # -------------------------------------------------------------------------------------------

    prog = Program()
    prog.header.id = 3
    prog.header.name = "Trenink - lepidlo"

    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Aplikace lepidla"
    pb.on_success = 0
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(drill_item(1, on_success=1, on_failure=2, obj_type=[""]))
    pb.items.append(item(2, "GetReady", on_success=3, on_failure=0))
    pb.items.append(drill_item(3, on_success=3, on_failure=4, obj_type=[""]))
    pb.items.append(item(4, "GetReady", on_success=0, on_failure=0))

    art.store_program(prog)
    art.program_set_ro(prog.header.id)

    # -------------------------------------------------------------------------------------------
    # Training program 4
    # -------------------------------------------------------------------------------------------

    prog = Program()
    prog.header.id = 4
    prog.header.name = "Trenink - inspekce"

    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Vizualni inspekce"
    pb.on_success = 0
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(polygon_item(1))
    pb.items.append(visual_inspection_item(2, ref_id=[1], on_success=3, on_failure=5))
    pb.items.append(visual_inspection_item(3, ref_id=[1], on_success=4, on_failure=5))
    pb.items.append(place_item(4, ref_id=[1], on_success=1, on_failure=0, name="OK parts"))
    pb.items.append(place_item(5, ref_id=[1], on_success=1, on_failure=0, name="NOK parts"))

    art.store_program(prog)
    art.program_set_ro(prog.header.id)

    # -------------------------------------------------------------------------------------------
    # Training program 5
    # -------------------------------------------------------------------------------------------

    prog = Program()
    prog.header.id = 5
    prog.header.name = "Trenink - krabice"

    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Polozeni do krabice"
    pb.on_success = 0
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(polygon_item(1))
    pb.items.append(place_container_item(2, ref_id=[1], on_success=1, on_failure=0))
    # p = ProgramItem()
    # p.id = 2
    # p.type = "PlaceToContainer"
    # p.polygon.append(PolygonStamped())
    # p.object.append("")
    # p.on_success = 1
    # p.on_failure = 0
    # p.ref_id.append(1)
    #
    # pb.items.append(p)

    art.store_program(prog)
    # art.program_set_ro(prog.header.id)

    # -------------------------------------------------------------------------------------------
    # Simplified trolley assembly: object types
    # -------------------------------------------------------------------------------------------

    art.store_object_type(obj_type("Spojka", 0.046, 0.046, 0.154))
    art.store_object_type(obj_type("Kratka_noha", 0.046, 0.046, 0.298, container=True))
    art.store_object_type(obj_type("Dlouha_noha", 0.046, 0.046, 0.398))
    art.store_object_type(obj_type("Modry_kontejner", 0.1, 0.14, 0.08, container=True))

    # -------------------------------------------------------------------------------------------
    # Simplified trolley assembly: program
    # -------------------------------------------------------------------------------------------

    prog = Program()
    prog.header.id = 20
    prog.header.name = "Montaz stolicky"

    # --- left side of the trolley ------------------------------------------------------
    pb = ProgramBlock()
    pb.id = 1
    pb.name = "Bocnice 1"
    pb.on_success = 2
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(wait_item(2, on_failure=2))

    # each side consists of four profiles (of two types)
    pb.items.append(feeder_item(3, obj_type=""))
    pb.items.append(place_item(4, ref_id=[3], on_failure=4))

    pb.items.append(feeder_item(5, ref_id=[3]))
    pb.items.append(place_item(6, ref_id=[5], on_failure=6))

    pb.items.append(feeder_item(7, obj_type=""))
    pb.items.append(place_item(8, ref_id=[7], on_failure=8))

    pb.items.append(feeder_item(9, ref_id=[7]))
    pb.items.append(place_item(10, ref_id=[9], on_failure=10))

    # after p&p, let's drill holes
    pb.items.append(drill_item(11, on_success=11, on_failure=13, obj_type=[""]))

    pb.items.append(item(13, "GetReady", on_success=0, on_failure=13))

    # --- right side of the trolley ------------------------------------------------------
    pb = deepcopy(pb)
    pb.id = 2
    pb.name = "Bocnice 2"
    pb.on_success = 3
    pb.on_failure = 0
    prog.blocks.append(pb)

    # --- connecting profiles ------------------------------------------------------------
    pb = ProgramBlock()
    pb.id = 3
    pb.name = "Spojovaci dily"
    pb.on_success = 1
    pb.on_failure = 0
    prog.blocks.append(pb)

    pb.items.append(wait_item(1, on_success=10, on_failure=1))

    pb.items.append(feeder_item(10, obj_type=""))
    pb.items.append(place_item(11, ref_id=[10], on_failure=11))

    pb.items.append(feeder_item(12, ref_id=[10]))
    pb.items.append(place_item(13, ref_id=[12], on_failure=13))

    pb.items.append(feeder_item(14, ref_id=[10]))
    pb.items.append(place_item(15, ref_id=[14], on_failure=15))

    pb.items.append(feeder_item(16, ref_id=[10]))
    pb.items.append(place_item(17, ref_id=[16], on_failure=17))

    pb.items.append(item(18, "GetReady", on_success=0, on_failure=18))

    art.store_program(prog)
    art.program_set_ro(prog.header.id)


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("Shutting down")
