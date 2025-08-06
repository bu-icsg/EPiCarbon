class Chiplet:
    def __init__(self, chiplet_type, tech_node, verbose = False):
      self.chiplet_type = chiplet_type
      self.tech_node = tech_node
      self.log_key = "chiplet"
      self.cpa_scaling_factor = 1
      
      if self.tech_node != -1:
          self.str_val = f"Chiplet ({self.chiplet_type}, {self.tech_node}nm)"
      else:
          self.str_val = f"Chiplet ({self.chiplet_type})"
      
      if verbose:
          print("INFO", self.log_key, "\t", "Creating chiplet:", self)
                    
    def __repr__(self):
        return "Test()"
    def __str__(self):
        return self.str_val
    
    def set_cpa_scaling_factor (self, scaling_factor):
        self.cpa_scaling_factor = scaling_factor
    
    def get_manufacturing_carbon(self, ci_fab, ghg_abatement=95, verbose=False):
        # To be implemented by child node
        raise NotImplementedError("get_manufacturing_carbon must be inplemented in child class.")
