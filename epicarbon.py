import os
import sys
import argparse


file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
sys.path.append(os.path.join(file_dir, "src"))

from src.utils import parse_arch_file

# ---------------------------------------------------------
# Default Carbon Intensity (CI) values in gCO2/kWh
# ---------------------------------------------------------
ci_fab = 820    # Manufacturing: Coal-based electricity
ci_op = 11      # Operation: Wind-based electricity


# ---------------------------------------------------------
# Setters for carbon intensity values
# ---------------------------------------------------------
def set_ci_fab(_ci_fab):
    """Set carbon intensity for fabrication (gCO2/kWh)."""
    global ci_fab
    ci_fab = _ci_fab


def set_ci_op(_ci_op):
    """Set carbon intensity for operation (gCO2/kWh)."""
    global ci_op
    ci_op = _ci_op


# ---------------------------------------------------------
# Operational Carbon Footprint (OCF)
# ---------------------------------------------------------
def get_carbon_operational(energy_per_inf, num_inf_per_day=1e9, lifetime_days=5*365, verbose=False):
    """
    Calculate operational carbon footprint (OCF) over device lifetime.

    Parameters:
        energy_per_inf (float): Energy per inference in joules.
        num_inf_per_day (float): Inferences per day (default 1e9).
        lifetime_days (int): Lifetime of the chip in days (default 5 years).
        verbose (bool): Print detailed logs.

    Returns:
        float: OCF in grams CO2-equivalent.
    """
    if verbose:
        print("\n[Operational Carbon Footprint Calculation]")
        print(f"Energy per inference       : {energy_per_inf:.2e} J")
        print(f"Inferences per day         : {num_inf_per_day:.0e}")
        print(f"Lifetime                   : {lifetime_days} days ({lifetime_days / 365:.1f} years)")
        print("--------------------------------------------------")

    # Convert J → kWh
    energy_per_inf_kWh = energy_per_inf / (1000 * 3600)
    ocf_per_inf = energy_per_inf_kWh * ci_op
    ocf_per_day = ocf_per_inf * num_inf_per_day
    ocf_total = ocf_per_day * lifetime_days

    if verbose:
        print(f"Energy per inference (kWh) : {energy_per_inf_kWh:.2e} kWh")
        print(f"Carbon per inference       : {ocf_per_inf:.2e} gCO2")
        print(f"Carbon per day             : {ocf_per_day:.2e} gCO2")
    print("--------------------------------------------------")
    print(f"Total OCF                  = {ocf_total:.2e} gCO2")

    return ocf_total


# ---------------------------------------------------------
# Embodied Carbon Footprint (ECF)
# ---------------------------------------------------------
def get_carbon_embodied(arch_file, verbose=False, return_breakdown=False):
    """
    Calculate embodied carbon footprint (ECF) for chip fabrication and packaging.

    Parameters:
        arch_file (str): Path to architecture JSON file.
        verbose (bool): Print detailed logs.
        return_breakdown (bool): Return component-wise breakdown.

    Returns:
        float or (float, dict): ECF in grams CO2, optionally with breakdown.
    """
    if verbose:
        print(f"\n[Embodied Carbon Footprint Calculation]")
        print(f"Architecture file          : {arch_file}")
        print(f"Fabrication CI              : {ci_fab} g/kWh")
        print("--------------------------------------------------")
        print("Building chip model...")

    # Parse architecture file into components
    chiplets, packager, _ = parse_arch_file(arch_file, verbose=verbose)

    # Calculate ECF per chiplet type
    ecf_breakdown = {}
    for chiplet in chiplets:
        ecf_chiplet = chiplet.get_manufacturing_carbon(ci_fab=ci_fab, ghg_abatement=95, verbose=verbose)
        ecf_breakdown[chiplet.chiplet_type] = ecf_breakdown.get(chiplet.chiplet_type, 0) + ecf_chiplet

    # Add packaging carbon
    ecf_breakdown["package"] = packager.get_packaging_carbon(chiplets, ci_fab, verbose=verbose)

    ecf_total = sum(ecf_breakdown.values())

    print("--------------------------------------------------")
    print(f"Total ECF                   = {ecf_total:.2f} gCO2")
    for comp, value in ecf_breakdown.items():
        print(f"{comp:15s}\t\t    : {value:.2f} gCO2")

    return (ecf_total, ecf_breakdown) if return_breakdown else ecf_total


# ---------------------------------------------------------
# Combined Carbon Footprint (CF)
# ---------------------------------------------------------
def get_carbon_footprint(arch_file, energy_per_inf, verbose=False):
    """
    Calculate total carbon footprint (CF) = ECF + OCF.

    Parameters:
        arch_file (str): Path to architecture JSON file.
        energy_per_inf (float): Energy per inference in joules.
        verbose (bool): Print detailed logs.

    Returns:
        tuple: (CF total, ECF, OCF) in grams CO2.
    """

    ecf = get_carbon_embodied(arch_file, verbose=verbose)
    ocf = get_carbon_operational(energy_per_inf, verbose=verbose)
    cf_total = ecf + ocf

    print("--------------------------------------------------")
    print(f"Total CF                    = {cf_total:.2f} gCO2")
    print(f"  - Operational (OCF)       : {ocf:.2f} gCO2")
    print(f"  - Embodied (ECF)          : {ecf:.2f} gCO2")

    return cf_total, ecf, ocf



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate the carbon footprint of an electro-photonic system.")
    parser.add_argument("--estimate", choices=['OCF', 'ECF', 'CF'], default="ECF",
                        help="Select which metric to estimate: 'OCF', 'ECF', or 'CF'.")
    parser.add_argument("--arch", default="archs/default_arch.json",
                        help="Path to architecture description file (JSON).")
    parser.add_argument("--energy", type=float,
                        help="Energy per inference in joules (required for OCF or CF).")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Enable detailed logging.")
    args = parser.parse_args()

    if args.verbose:
        print("[INFO] Verbose mode enabled.")
    else:
        print("[INFO] Verbose mode disabled.")

    # Execute chosen estimation
    if args.estimate == "ECF":
        get_carbon_embodied(args.arch, verbose=args.verbose)
    elif args.estimate == "OCF":
        if args.energy is None:
            raise ValueError("Energy per inference (--energy) must be provided for OCF calculation.")
        get_carbon_operational(energy_per_inf=args.energy, verbose=args.verbose)
    elif args.estimate == "CF":
        if args.energy is None:
            raise ValueError("Energy per inference (--energy) must be provided for CF calculation.")
        get_carbon_footprint(args.arch, args.energy, verbose=args.verbose)
