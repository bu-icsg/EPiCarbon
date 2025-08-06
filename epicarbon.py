import os
import sys
import argparse

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
sys.path.append(file_dir + "/src")

from src.utils import parse_arch_file

ci_fab = 820    # coal, g/kWh
ci_op = 11      # wind, g/kWh


def set_ci_fab (_ci_fab):
    global ci_fab
    ci_fab = _ci_fab

def get_carbon_operational (energy_per_inf, num_inf_per_day=1e9, lifetime_days=5*365, verbose=False):
    if verbose:
        print ("\nEstimating OCF of running a DNN model with {:.2e} J/inference".format(energy_per_inf))
        print ("Number of inferences per day: {:.0e}".format(num_inf_per_day))
        print ("Lifetime of the chip: {} days ({:.1f} years)".format(lifetime_days, lifetime_days/365))
        print("---------------------------------------------")
    
    energy_per_inf_kWh = energy_per_inf/ (1000 * 3600)
    ocf_per_inf = energy_per_inf_kWh * ci_op
    ocf_per_day = ocf_per_inf * num_inf_per_day
    ocf = ocf_per_day * lifetime_days

    if verbose:
        print("Operational energy per inference\t : {:.2e} J --> {:.2e} kWh".format(energy_per_inf, energy_per_inf_kWh))
        print("Operational carbon per inference\t : {:.2e} g".format(ocf_per_inf))
        print("Operational carbon per day\t : {:.2e} g".format(ocf_per_day))
        print("---------------------------------------------")
        print ("Total operational carbon (OCF) = {:.2e} g".format(ocf))
    
    return ocf # g


def get_carbon_ebodied (arch_file, verbose=False, return_breakdown=False, print_none=False):
    if verbose:
        print ("\nEstimating ECF of {}".format(arch_file))
        print("---------------------------------------------")
        print("CI Fab: {} g/kWh".format(ci_fab))
        print("Building chip...")
        
    chiplets, packager, _ = parse_arch_file(arch_file, verbose=verbose)
    
    ecf_breakdown = {
        }
    for chiplet in chiplets:
        ecf_chiplet = chiplet.get_manufacturing_carbon(ci_fab=ci_fab, ghg_abatement=95, verbose=verbose)
        # grams
        
        if chiplet.chiplet_type not in ecf_breakdown.keys():
            ecf_breakdown[chiplet.chiplet_type] = ecf_chiplet
        else:
            ecf_breakdown[chiplet.chiplet_type] += ecf_chiplet
        
        #ecfs.append(chiplet.get_manufacturing_carbon(ci_fab=ci_fab, ghg_abatement=95, verbose=verbose))
        
        
    ecf_breakdown["package"] = packager.get_packaging_carbon (chiplets, ci_fab, verbose=verbose)

    
    ecf = sum(ecf_breakdown.values())
    if verbose:
        print("---------------------------------------------")
        print ("Total embodied carbon (ECF) = {:.2f} g".format(ecf))
        for key in ecf_breakdown.keys():
            print("{} \t\t {:.2f}".format(key, ecf_breakdown[key]))
    
    if return_breakdown:
        return ecf, ecf_breakdown
    else:
        return ecf


def get_carbon_footprint (arch_file, energy_per_inf, verbose=False):
    if verbose:
        print ("Estimating carbon footprint of {}".format(arch_file))
        print ("Energy/inf: {:.2e} J".format(energy_per_inf))
 
    ecf = get_carbon_ebodied(arch_file, verbose=verbose)
    ocf = get_carbon_operational(energy_per_inf, verbose=verbose)    
    
    cf = ecf + ocf
    
    if verbose:
        print("---------------------------------------------")
        print ("Total carbon footprint (CF) = {:.2f} g".format(cf))
       # if verbose:
        print("  ---operational: {:.2f} g".format(ocf))
        print("  ---embodied: {:.2f} g".format(ecf))
    
    return cf, ecf, ocf



if __name__ == "__main__":
    # Handle arguments
    parser = argparse.ArgumentParser(description="Calculate the carbon footprint of an electro-photonic system.")
    parser.add_argument("--estimate", choices=['OCF', 'ECF', 'CF'], help="Estimate 'OCF', 'ECF', or 'CF'", default="ECF")
    parser.add_argument("--arch", help="The architecture description file (json) directoty", default="archs/default_arch.json")
    parser.add_argument("--energy", help="Energy/inference in joule", type=float)
    
    parser.add_argument("--verbose", help="Show logs", action="store_true", default=False)
    
    args = parser.parse_args()
    
    estimate_what = args.estimate
    arch_file = args.arch
    energy = args.energy
    verbose = args.verbose
    
    if verbose:
        print ("Verbosity turned on.")
    else:
        print ("Verbosity turned off.")

    # Call the API according to "estimate"
    if estimate_what == "ECF":
        ecf = get_carbon_ebodied(arch_file, verbose=verbose)
    elif estimate_what == "OCF":
        ocf = get_carbon_operational(energy_per_inf=energy, verbose=verbose)
    else:
        cf = get_carbon_footprint(arch_file, energy, verbose=verbose)

    


    
    
    