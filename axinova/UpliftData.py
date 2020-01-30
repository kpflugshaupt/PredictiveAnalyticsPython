## make imports from pa_lib possible (parent directory of file's directory)
import sys
from pathlib import Path

file_dir = Path.cwd()
parent_dir = file_dir.parent
sys.path.append(str(parent_dir))

from dataclasses import dataclass

from pa_lib.file import project_dir, load_bin, load_pickle
from pa_lib.util import list_items

from axinova.UpliftLib import (
    VarId,
    StringList,
    IntList,
    VarCodes,
    StationDef,
    DataFrame,
    VarDict,
    VarStruct,
    VarSelection,
)

########################################################################################
# Data Types
########################################################################################
@dataclass
class UpliftData:
    ax_data: DataFrame = None
    ax_var_struct: DataFrame = None
    spr_data: DataFrame = None
    population_codes: DataFrame = None
    global_codes: DataFrame = None
    station_codes: DataFrame = None
    all_stations: StringList = None
    all_weekdays: StringList = None
    all_timescales: StringList = None
    var_info: VarDict = None

    def __str__(self):
        description = "\n".join(
            [
                "Data Object sizes:",
                f"ax_data: '{self.ax_data.shape}'",
                f"ax_var_struct: {self.ax_var_struct.shape}",
                f"spr_data: '{self.spr_data.shape}'",
                f"population_codes: {self.population_codes.shape}",
                f"global_codes: {self.global_codes.shape}",
                f"station_codes: {self.station_codes.shape}",
            ]
        )
        return description

    # Access data objects  #############################################################
    def variable_label(self, var_id: VarId) -> str:
        return self.var_info[var_id]["Label"]

    def variable_code_labels(self, var_id: VarId) -> StringList:
        return self.var_info[var_id]["Codes"]

    def variable_code_order(self, var_id: VarId) -> IntList:
        return self.var_info[var_id]["Order"]

    def ax_population_ratios(self, var_id: VarId) -> DataFrame:
        ratios = self.population_codes.loc[
            self.population_codes["Variable"] == var_id
        ].pivot_table(values="Pop_Ratio", index="Variable", columns="Code")
        return ratios

    def ax_global_ratios(self, var_id: VarId) -> DataFrame:
        ratios = self.global_codes.loc[
            self.global_codes["Variable"] == var_id
        ].pivot_table(values="Ratio", index="Variable", columns="Code")
        return ratios

    def ax_station_ratios(self, var_id: VarId) -> DataFrame:
        ratios = self.station_codes.loc[
            self.station_codes["Variable"] == var_id
        ].pivot_table(values="Ratio", index="Station", columns="Code", fill_value=0)
        return ratios

    # Validate Uplift parameters #######################################################
    def check_stations(self, stations: StationDef) -> StationDef:
        if stations is None or stations == list():
            checked_stations = self.all_stations
        else:
            checked_stations = [
                station for station in stations if station in self.all_stations
            ]
            if len(checked_stations) != len(stations):
                raise ValueError(
                    f"Unknown station found in {stations}, known are: {self.all_stations}"
                )
        return checked_stations

    def check_var_def(self, variables: VarCodes) -> VarSelection:
        checked_var: VarSelection = {}
        for (var_id, code_nr) in variables.items():
            try:
                var_label = self.variable_label(var_id)
            except KeyError:
                raise KeyError(
                    f"Unknown variable '{var_id}', known are {list(self.var_info.keys())}"
                ) from None
            try:
                code_labels = list_items(self.variable_code_labels(var_id), code_nr)
            except IndexError:
                raise ValueError(
                    f"Unknown code index(es) for variable {var_id} in {code_nr}, known are "
                    f"{self.variable_code_order(var_id)}"
                ) from None
            code_order = list_items(self.variable_code_order(var_id), code_nr)
            checked_var[var_id] = VarStruct(var_label, code_labels, code_order)
        return checked_var

    def check_timescale(self, timescale: str) -> str:
        if timescale not in self.all_timescales:
            raise ValueError(
                f"Unknown timescale '{timescale}', known are: {self.all_timescales}"
            )
        return timescale


########################################################################################
# Load data files
########################################################################################
def load_data() -> UpliftData:
    """Load base data and calculate derived objects. Return data container class."""
    data = UpliftData()
    with project_dir("axinova"):
        data.ax_data = load_bin("ax_data.feather")
        data.ax_var_struct = load_bin("ax_var_struct.feather")
        data.population_codes = load_pickle("population_ratios.pkl")
        data.global_codes = load_pickle("global_code_ratios.pkl")
        data.station_codes = load_pickle("station_code_ratios.pkl")
        data.spr_data = load_pickle("spr_data.pkl")

    # derived data
    data.all_stations = data.ax_data["Station"].cat.categories.to_list()
    data.all_timescales = ["Time", "ShortTime", "Hour", "TimeSlot"]
    data.var_info = {}
    for (var_id, struct) in data.ax_var_struct.groupby("Variable"):
        data.var_info[var_id] = dict(
            Label=struct["Variable_Label"].max(),
            Codes=struct["Label"].to_list(),
            Order=list(range(len(struct["Label_Nr"].to_list()))),
        )
    return data
