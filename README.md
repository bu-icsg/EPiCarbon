# EPiCarbon

EPiCarbon is a Python-based tool for estimating the carbon footprint of electro-photonic systems. It calculates the **Embodied Carbon Footprint (ECF)**, **Operational Carbon Footprint (OCF)**, and the **Carbon Footprint (CF)** of a system based on its `architecture` and `energy usage`.


## Installation

1. Ensure you have **Python 3.8** or higher installed. You can check your Python version with:
   ```bash
   python --version

2. Clone the repository:
   ```bash
   git clone https://github.com/bu-icsg/EPiCarbon.git
   cd EPiCarbon
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## File Structure

- `epicarbon.py`: Main script for running the program.
- `src/`: Contains chiplet models, data files, and utility functions.
- `archs/`: Contains example architecture description files in JSON format.

  
## Usage

Run the program using the command line:

```bash
python epicarbon.py --estimate <metric> [--arch <arch_file>] [--energy <energy_per_inf>] [--verbose]
```

### Arguments

- `--estimate`: Select the metric to estimate. Options:
  - `ECF`: Embodied Carbon Footprint.
  - `OCF`: Operational Carbon Footprint.
  - `CF`: Carbon Footprint.
- `--arch`: Path to the architecture description file in JSON (required for `ECF` and `CF`)
- `--energy`: Energy per inference in joules (required for `OCF` and `CF`).
- `--verbose`: Enable detailed logging.

### Examples

1. **Calculate ECF**:
   ```bash
   python epicarbon.py --estimate ECF --arch archs/adept.json --verbose
   ```
   Alternatively, call the `get_carbon_embodied()` API by importing `epicarbon` from another script.

2. **Calculate OCF**:
   ```bash
   python epicarbon.py --estimate OCF --energy 1e-3 --verbose
   ```
   Alternatively, call the `get_carbon_operational()` API by importing `epicarbon` from another script.
   
4. **Calculate CF**:
   ```bash
   python epicarbon.py --estimate CF --arch archs/adept.json --energy 1e-3 --verbose
   ```
   Alternatively, call the `get_carbon_footprint()` API by importing `epicarbon` from another script.
   
## Architecture Files

Architecture files describe the system's chiplets and packaging. Example files are located in the `archs/` directory, such as:

- `archs/lt.json`
- `archs/adept.json`

### Structure of an Architecture File

An architecture file contains the following fields:

- **`chiplets`**: A list of chiplets in the system. Each chiplet includes:
  - **`type`**: The type of the chiplet (Options: `cmos-logic` or `pic-logic`).
  - **`tech`**: The technology node of the chiplet in nanometers (Options: for `pic-logic` use `-1`, for `cmos-logic` choose among `28`, `20`, `14`, `10`, `8`, `7`, `5`, or `3` nm).
  - **`area`**: The area of the chiplet in square centimeters.
  - **`num_chiplets`**: The number of identical chiplets of this type.
- **`package`**: The packaging type of the system (Options: `monolithic`, `3D`, `2.5D-active`, `2.5D-passive`).

### Example Architecture File

Below is an example architecture file for a system named "ADEPT":

```json
{
    "chiplets": [
        {
            "type": "cmos-logic",
            "tech": 20,
            "area": 6.51,
            "num_chiplets": 1
        },
        {
            "type": "pic-logic",
            "tech": -1,
            "area": 0.56,
            "num_chiplets": 4
        }
    ],
    "package": "3D"
}
```

## Configurable Parameters

Several default parameters are defined in the program that can be changed in code (`epicarbon.py`):

- **Fabrication (ci_fab):** 820 gCO2/kWh (coal-based electricity).
- **Operation (ci_op):** 11 gCO2/kWh (wind-based electricity).
- **Number of inferences per day (num_inf_per_day):** 1e9.
- **Lifetime (lifetime_days):** 5*365 days.


## Extending EPiCarbon

EPiCarbon can be easily extended to support a custom chiplet.

- Simply add your new chiplet inside `src/chiplet_models` folder by inheriting the `Chiplet` class. You can follow the example of `cmos_logic_chiplet` or `pic_logic_chiplet`.
- Implement the `get_manufacturing_carbon()` method of your new chiplet.
- Update the `build_chiplet()` method in `src/utils.py` to handle your create your new chiplet while parsing the architecture file.
  


## Publications

To be updated.

## Contact

For questions or feedback, please contact [ffayza@bu.edu].