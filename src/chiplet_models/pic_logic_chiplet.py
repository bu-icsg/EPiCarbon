import json
import sys
import os
import math 

curr_file_path = os.path.realpath(__file__)
curr_dir = os.path.dirname(curr_file_path)
data_dir = curr_dir + "/../data/"

from chiplet import Chiplet

# actuation types = fcd, mems, both

class PIC_logic_chiplet(Chiplet):
    def __init__(self, chiplet_type, tech_node, area, act_type="default", verbose=False):       
       self.area = area  # cm2
       self.actuation_type = act_type
       Chiplet.__init__(self, chiplet_type, tech_node, verbose=verbose)
    
    
    def __get_yield (self, defect_rate = 0.1): # per cm^2
        # Poisson yield
        return math.exp (- self.area * 0.2 * defect_rate) # 20% sensitive area for photonics
        
    
    def set_area (self, area):
        self.area = area   
    
    
    def get_manufacturing_carbon(self, ci_fab, ghg_abatement=95, verbose=False):
        if verbose:
            print("\nINFO", self.log_key, "\t", "Calculating manufacturing carbon of", self, "...\n")
            
        # Energy per unit area
        with open(data_dir+"pic_logic/epa.json", 'r') as f:
            epa_config = json.load(f)

        # Raw materials per unit area
        with open(data_dir+"cmos_logic/materials.json", 'r') as f:
            materials_config = json.load(f)

        # Gasses per unit area
        if ghg_abatement == 95:
            with open(data_dir+"cmos_logic/gpa_95.json", 'r') as f:
                gpa_config = json.load(f)
        elif ghg_abatement == 99:
            with open(data_dir+"cmos_logic/gpa_99.json", 'r') as f:
                gpa_config = json.load(f)
        else:
            print("ERROR", self.log_key, "\t", "Unsupported GHG abatement percentage value for CMOS logic")
            sys.exit()

        # Aggregating model
        epa_key = self.actuation_type
        process_node_key_cmos_eqiv_upper_bound = str(65) + "nm" # Based on CACM paper analysis
        assert epa_key in epa_config.keys()
        assert process_node_key_cmos_eqiv_upper_bound in gpa_config.keys()
        assert process_node_key_cmos_eqiv_upper_bound in materials_config.keys()

        carbon_energy    = ci_fab * epa_config[epa_key] 
        carbon_gas       = gpa_config[process_node_key_cmos_eqiv_upper_bound]
        carbon_materials = materials_config[process_node_key_cmos_eqiv_upper_bound]

        self.carbon_per_area = (carbon_energy + carbon_gas + carbon_materials)
        self.fab_yield = self.__get_yield()
        self.ecf = self.carbon_per_area * self.area / self.fab_yield
        
        if verbose:
            print("INFO", self.log_key, "\t", "Actuation type: {}, EPA: {} kW-h/cm2\n".format(self.actuation_type, epa_config[epa_key] ))
            print("INFO", self.log_key, "\t", "Carbon/area from energy \t\t", carbon_energy, "g/cm2")
            print("INFO", self.log_key, "\t", "Carbon/area from gas \t\t", carbon_gas, "g/cm2")
            print("INFO", self.log_key, "\t", "Carbon/area from materials \t", carbon_materials, "g/cm2")
            print("INFO", self.log_key, "\t", "--------------------------------------------------------")
            print("INFO", self.log_key, "\t", "Aggregated: Carbon/area \t", self.carbon_per_area, "g/cm2")
            print("INFO", self.log_key, "\t", "--------------------------------------------------------")
            print("INFO", self.log_key, "\t", "Area\t", round(self.area, 2), "cm2")
            print("INFO", self.log_key, "\t", "Yield\t", round(self.fab_yield*100, 2), "%")
            print("INFO", self.log_key, "\t", "--------------------------------")
            print("INFO", self.log_key, "\t", self, "manufacturing carbon:", round(self.ecf, 2), "g")
            print("INFO", self.log_key, "\t", "--------------------------------")
    
        return self.ecf
