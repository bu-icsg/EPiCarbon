import numpy as np
import json
import os
from chiplet_models.cmos_logic_chiplet import CMOS_logic_chiplet


curr_file_path = os.path.realpath(__file__)
curr_dir = os.path.dirname(curr_file_path)
data_dir = curr_dir + "/data/"


class Packager:
    def __init__(self, package_type, verbose=False):
      self.package_type = package_type
      self.log_key = "packegar"
      
      if verbose:
          print("INFO", self.log_key, "\t", "Creating packager:", self)
    
    def __str__(self):
      return f"Packager ({self.package_type})"
    
    
    def get_packaging_carbon(self, _chiplets, ci_fab, verbose=False):
      ## TODO -- need to decide on this
      if self.package_type == "monolithic": 
            packaging_carbon = 0
      else:
          chiplets = []
          for ch in _chiplets:
              if ch.chiplet_type != "dram":
                  chiplets.append(ch)
          
          bonding_yield = 0.99
          interposer_node = 65
          interposer_type = "cmos-logic"
          
          num_chiplets = len(chiplets)
          areas = [c.area for c in chiplets]
          
          areas_mm2 = [c.area*100 for c in chiplets]
          #print(areas_mm2)
          # calculate interposer area
          interposer_area, num_if = recursive_split(areas_mm2)
          num_if = int(np.ceil(num_if))
          interposer_area = np.prod(interposer_area)/100
             
          # get scaling factor of metal layers
          with open(data_dir+"cmos_logic/beol_feol_scaling.json", 'r') as f:
              beol_feol_config = json.load(f)      
          process_node_key = str(interposer_node)+"nm"
          scaling_factor = beol_feol_config[process_node_key]
          
          # build an interposer
          interposer_chip = CMOS_logic_chiplet(interposer_type, interposer_node, interposer_area, is_interposer=True, verbose=False)
          interposer_chip.set_cpa_scaling_factor(scaling_factor)
          interposer_carbon = interposer_chip.get_manufacturing_carbon(ci_fab, verbose=False)
    
              
          if self.package_type == "3D":
              tsv_pitch=0.025
              tsv_size=0.005
              dims = np.sqrt(np.array(areas, dtype=np.float64))
              num_tsv_1d = np.floor(dims/tsv_pitch)
              overhead_3d = (num_tsv_1d**2) * (tsv_size**2)
              areas_3d = areas + overhead_3d
              
              carbon_2d = [c.get_manufacturing_carbon(ci_fab) for c in chiplets]
              
              for i in range (num_chiplets):
                  chiplets[i].set_area(areas_3d[i])
                               
              carbon_3d = [c.get_manufacturing_carbon(ci_fab) for c in chiplets]
              
              # set back the original area
              for i in range (num_chiplets):
                  chiplets[i].set_area(areas[i])
    
              packaging_carbon = np.sum(np.array(carbon_3d)-np.array(carbon_2d)) 
              packaging_carbon /= (bonding_yield**num_chiplets)
            
          
          elif self.package_type == "2.5D-passive":
              packaging_carbon = interposer_carbon
              
             # router_areas = [0.33/100] * num_chiplets
              packaging_carbon /= bonding_yield
              if verbose:
                  print("Interposer area {:.2f} cm2, carbon: {:.2f} g".format(interposer_area, interposer_carbon))
                
                
          elif self.package_type == "2.5D-active":
              router_area = 4.47/100 * num_chiplets ## Ask about source of it
              
              router_carbon = interposer_carbon * router_area / interposer_area          
              packaging_carbon = interposer_carbon-router_carbon
              packaging_carbon /= bonding_yield
              if verbose:
                  print("Interposer area {:.2f} cm2, carbon: {:.2f} g".format(interposer_area, interposer_carbon))
                  
                  
          elif self.package_type == "RDL": 
              RDLLayers = 6
              numBEOL = 8
              packaging_carbon = interposer_carbon * RDLLayers/numBEOL
              packaging_carbon /= bonding_yield
              
          elif self.package_type == "EMIB":
              emib_area =  5*5/100
              emib_chip = CMOS_logic_chiplet("cmos-logic", 20, emib_area, verbose=False)
              
              process_node_key = str(20)+"nm"
              scaling_factor = beol_feol_config[process_node_key]
              emib_chip.set_cpa_scaling_factor(scaling_factor)
              
              emib_carbon = emib_chip.get_manufacturing_carbon(ci_fab, _yield=bonding_yield, verbose=verbose)
              packaging_carbon = emib_carbon * num_if
              packaging_carbon /= bonding_yield
             
          else:
              packaging_carbon = 150 # grams (ACT)
      
      if verbose:
          print()
          print("INFO", self.log_key, "\t", "Packaging carbon:", round(packaging_carbon, 2), "g")
      return packaging_carbon # grams
  
    
  
    
## from ECO-CHIP https://github.com/ASU-VDA-Lab/ECO-CHIP/blob/main/src/CO2_func.py #####

def recursive_split(areas, axis=0, emib_pitch=10):
    sorted_areas = np.sort(areas[::-1])
    if len(areas)<=1:
        v = (np.sum(areas)/2)**0.5
        size_2_1 = np.array((v + v*((axis+1)%2), v +axis*v))
#         print("single", axis, size_2_1)
        return size_2_1, 0
    else:
        sums = np.array((0.0,0.0))
        blocks= [[],[]]
        for i, area in enumerate(sorted_areas):
            blocks[np.argmin(sums)].append(area)
            sums[np.argmin(sums)] += area
#         print("blocks",axis, blocks)
        left, l_if = recursive_split(blocks[0], (axis+1)%2, emib_pitch)
#         print("left",axis, left)
        right, r_if = recursive_split(blocks[1], (axis+1)%2, emib_pitch)
#         print("right",axis, right)
        sizes = np.array((0.0,0.0))
        sizes[axis] = left[axis] + right[axis] + 0.5
        sizes[(axis+1)%2] = np.max((left[(axis+1)%2], right[(axis+1)%2]))
        t_if = l_if + r_if 
        t_if += np.ceil(np.min((left[(axis+1)%2], right[(axis+1)%2]))/emib_pitch) # for overlap 1 interface per 10mm
        return sizes, t_if