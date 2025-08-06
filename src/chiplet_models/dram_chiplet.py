import json
import sys
import os
import math 

curr_file_path = os.path.realpath(__file__)
curr_dir = os.path.dirname(curr_file_path)
data_dir = curr_dir + "/../data/"

from chiplet import Chiplet


class DRAM_chiplet(Chiplet):
    def __init__(self, chiplet_type, tech_node, dram_type, size_gb, verbose=False):               
        self.dram_type = dram_type  
        self.size_gb = size_gb
        Chiplet.__init__(self, chiplet_type, tech_node, verbose=verbose)
    
    
    # def __get_yield (self, defect_rate = 0.1): # per cm^2
    #     # Poisson yield
    #     return math.exp (- self.area * defect_rate)
        
    
    def get_manufacturing_carbon(self, ci_fab, ghg_abatement=95, verbose=False):
        if verbose:
            print("\nINFO", self.log_key, "\t", "Calculating manufacturing carbon of", self, "...\n")
       
        
        with open(data_dir + "dram/dram_hynix.json", 'r') as f:
            dram_config = json.load(f)
        
        assert self.dram_type in dram_config.keys() and "DRAM configuration not found"
        
        self.fab_yield = 0.875
        
        self.carbon_per_gb = dram_config[self.dram_type] / self.fab_yield        
        self.ecf = self.carbon_per_gb * self.size_gb / self.fab_yield
        
        if verbose:
            print("INFO {} \t Carbon/GB for {} is {:.2f}".format(self.log_key, self.dram_type, self.carbon_per_gb))
            print("INFO", self.log_key, "\t", "--------------------------------")
            print("INFO", self.log_key, "\t", self, "manufacturing carbon:", round(self.ecf, 2), "g")
            print("INFO", self.log_key, "\t", "--------------------------------")         
        return self.ecf