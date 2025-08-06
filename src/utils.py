import json
import pandas as pd
import os
import sys

THIS_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(THIS_SCRIPT_DIR)

from packager import Packager
from chiplet_models.cmos_logic_chiplet import CMOS_logic_chiplet
from chiplet_models.pic_logic_chiplet import PIC_logic_chiplet
from chiplet_models.dram_chiplet import DRAM_chiplet



# ------------------------ DNN utils ----------------------------
def get_energy_per_inf (perf_file, dnn_name):
    #perf_file = "src/data/accelerators/" + perf_file
    print(perf_file, dnn_name)
    with open(perf_file,'r') as json_file:
        en_data = json.load(json_file)
        
    energy = en_data[dnn_name]
    print(energy)
    return energy
    


def parse_dnn_model (dnn_file, verbose = False):
    log_key = "utils"
    
    if verbose:
        print("INFO {} \t Parsing dnn model file...".format(log_key))
    
    # linear_layer_types = ['fc', 'conv', 'linear']
    model = pd.read_csv(dnn_file)
    
    linear_index = []
    nonlinear_index = []
    layer_types = []
    
    # check layer type
    num_layers = len(model['Channels'])
    for i in range(num_layers):    
        if model['Layer name'][i].endswith("fc") or model['Layer name'][i].endswith("linear"):
            layer_types.append("fc")
            linear_index.append(i)
        elif model['Layer name'][i].endswith("conv"): 
            layer_types.append("conv")
            linear_index.append(i)
        else:
            layer_types.append("nonlinear")
            nonlinear_index.append(i)
    
    # create linear and nonlinear layer lists (dataframe) (can be used later)
    linear_layers = model.loc[linear_index]
    nonlinear_layers = model.loc[nonlinear_index]

    num_linear_layers = len(linear_layers['Channels'])
    num_nonlinear_layers = len(nonlinear_layers['Channels'])
    perc_nonlinear = num_nonlinear_layers/num_layers * 100
        
    if verbose:
        print ("INFO {}\t Total layers\t : {}".format(log_key, num_layers))
        print ("INFO {}\t  --linear\t : {} ({:.2f}%)".format(log_key, num_linear_layers, 100 - perc_nonlinear))
        print ("INFO {}\t  --nonlinear\t : {} ({:.2f}%)".format(log_key, num_nonlinear_layers, perc_nonlinear))
        print("---------------------------------------------")
    return model, layer_types, perc_nonlinear





# ------------------------ ARCH utils ----------------------------

def get_area_from_arch_file(arch_file, verbose = False):
    log_key = "utils"
    
    if verbose:
        print("INFO {} \t Parsing arch file...".format(log_key))
              
    with open(arch_file,'r') as json_file:
        arch_config_json = json.load(json_file)
    
    areas = []
    chiplet_info_list = arch_config_json["chiplets"]
    for chiplet_info in chiplet_info_list:
        if "area" in chiplet_info:
            area = chiplet_info["area"]
            areas.append(area)
        
    return areas



def parse_arch_file (arch_file, verbose = False):
    log_key = "utils"
    
    if verbose:
        print("INFO {} \t Parsing arch file...".format(log_key))
    
    chiplets = []
    packager = None
              
    with open(arch_file,'r') as json_file:
        arch_config_json = json.load(json_file)
        
    chiplet_info_list = arch_config_json["chiplets"]
    for chiplet_info in chiplet_info_list:
        chiplet = build_chiplet(chiplet_info, verbose=verbose)
        
        num_chiplets = 1
        if "num_chiplets" in chiplet_info:
            num_chiplets = chiplet_info["num_chiplets"]
        
        for i in range (num_chiplets): chiplets.append(chiplet)    
    
    package_type = arch_config_json["package"]
    packager = Packager (package_type=package_type, verbose=verbose)
    
    chip_type = arch_config_json["type"]
    if verbose:
        print ("INFO {} \t {}(type:{}) chip created.".format(log_key, arch_config_json["name"], chip_type))
        print("---------------------------------------------")
        print("List of chiplets:")
        for c in chiplets: print(c)
        print("---------------------------------------------")
    return chiplets, packager, chip_type


def build_chiplet (chiplet_info, verbose = False):
    log_key = "utils"
    
    chiplet_type = chiplet_info["type"]
    chiplet = None
    
    if chiplet_type == "cmos-logic":
        chiplet = CMOS_logic_chiplet(chiplet_type, chiplet_info["tech"], chiplet_info["area"], verbose=verbose)
    elif chiplet_type == "pic-logic":
        act_type = "default"
        if "actuation_type" in chiplet_info:
            act_type = chiplet_info["actuation_type"]
        chiplet = PIC_logic_chiplet(chiplet_type, chiplet_info["tech"], chiplet_info["area"], act_type=act_type, verbose=verbose)
    elif chiplet_type == "dram":
        chiplet = DRAM_chiplet(chiplet_type, chiplet_info["tech"], chiplet_info["dram-type"], chiplet_info["size-gb"], verbose=verbose)
    else:
        print("ERROR", log_key, "\t", "Chiplet type not supported.")
    
    return chiplet

