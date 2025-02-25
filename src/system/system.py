from channel.free_space_channel import FreeSpaceChannel
from link.link_manager import LinkManager
from scheduler.round_robin.round_robin_capacity_calculator import CapacityCalculator
from transceiver.base_station.base_station_manager import BaseStationManager
from transceiver.user_equipment.user_equipment_manager import UserEquipmentManager


class System:

    def __init__(self):
        self._base_stations = []
        self._user_equipments = []
        self._channel = None
        self._results_file_handle = None
        self._bandwidth = 180e3
        self._frequency = 2600e6
        self._slot_duration_in_seconds = 0.5e-3
        self._number_of_slots = 10
        self._resource_blocks_per_slot = 3
        self._tx_power = 40
        self._base_station_manager = BaseStationManager(
            self._slot_duration_in_seconds, self._resource_blocks_per_slot)
        self._user_equipment_manager = UserEquipmentManager(
            self._slot_duration_in_seconds, self._resource_blocks_per_slot)
        self._link_manager = LinkManager(
            self._base_stations, self._user_equipments, self._channel)
        self._capacity = None

    @property
    def base_stations(self):
        return self._base_station_manager.base_stations

    @property
    def user_equipments(self):
        return self._user_equipment_manager.user_equipments

    @property
    def base_station_to_user_equipment_links(self):
        return self._link_manager.base_station_to_user_equipment_links

    @property
    def user_equipment_to_base_station_links(self):
        return self._link_manager.user_equipment_to_base_station_links

    @property
    def capacity(self):
        return self._capacity

    def configure_basics(self):
        self.channel = FreeSpaceChannel(self._frequency)

        self._base_station_manager.set_all_base_stations_transmit_power_in_watts(self._tx_power)
        self._user_equipment_manager.update_all_user_equipment_slot_duration(self._slot_duration_in_seconds)

        self._link_manager.update_channel(self.channel)
        self._link_manager.base_stations = self._base_station_manager.base_stations
        self._link_manager.user_equipments = self._user_equipment_manager.user_equipments
        self._link_manager.update_links()
        self._link_manager.associate_all_user_equipment()

        self._base_station_manager.initialize_base_station_associated_user_equipment_scheduled_counters()
        self._base_station_manager.initialize_base_station_round_robin_schedulers()

    def simulate_scenario_1(self):
        self._base_station_manager.create_base_station('FIXED', 10, 20)
        self._base_station_manager.create_base_station('FIXED', 50, 20)

        self._user_equipment_manager.create_user_equipments('FIXED', 0, 0, 1)
        self._user_equipment_manager.create_user_equipments('FIXED', 20, 0, 1)
        self._user_equipment_manager.create_user_equipments('FIXED', 40, 0, 1)
        self._user_equipment_manager.create_user_equipments('FIXED', 60, 0, 1)

        self.configure_basics()

        self._capacity = CapacityCalculator(self._base_station_manager,
                                            self._user_equipment_manager,
                                            self._link_manager,
                                            self._number_of_slots,
                                            self._resource_blocks_per_slot,
                                            self._slot_duration_in_seconds)

        throughput = self._capacity.calculate_downlink_round_robin_aggregate_throughput_over_number_of_slots()
        print(f"Aggregate throughput: {throughput} bits/second.")
