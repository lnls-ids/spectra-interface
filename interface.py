"""Spectra functions."""
import numpy as _np
import matplotlib.pyplot as _plt
from accelerator import StorageRingParameters
import json
import spectra
import sys
import time
import copy

REPOS_PATH = "/home/gabriel/repos/spectra-interface"


class SpectraTools:
    """Class with general spectra tools."""

    @staticmethod
    def _run_solver(input_template):
        """Run spectra.

        Args:
            input_template (dict): Dictionary containing
            calculation parameters.

        Returns:
            dict: Output data dictionary
        """
        input_str = json.dumps(input_template)

        # call solver with the input string (JSON format)
        solver = spectra.Solver(input_str)

        # check if the parameter load is OK
        isready = solver.IsReady()
        if isready is False:
            print("Parameter load failed.")
            sys.exit()

        t0 = time.time()
        # start calculation
        solver.Run()
        dt = time.time() - t0
        print("elapsed time: {0:.1f} s".format(dt))
        return solver

    @staticmethod
    def _set_accelerator_config(accelerator, input_template):
        input_template["Accelerator"]["Energy (GeV)"] = accelerator.energy
        input_template["Accelerator"]["Current (mA)"] = accelerator.current

        input_template["Accelerator"][
            "&sigma;<sub>z</sub> (mm)"
        ] = accelerator.sigmaz

        input_template["Accelerator"][
            "Nat. Emittance (m.rad)"
        ] = accelerator.nat_emittance

        input_template["Accelerator"][
            "Coupling Constant"
        ] = accelerator.coupling_constant

        input_template["Accelerator"][
            "Energy Spread"
        ] = accelerator.energy_spread

        input_template["Accelerator"]["&beta;<sub>x,y</sub> (m)"] = [
            accelerator.betax,
            accelerator.betay,
        ]

        input_template["Accelerator"]["&alpha;<sub>x,y</sub>"] = [
            accelerator.alphax,
            accelerator.alphay,
        ]

        input_template["Accelerator"]["&eta;<sub>x,y</sub> (m)"] = [
            accelerator.etax,
            accelerator.etay,
        ]

        input_template["Accelerator"]["&eta;'<sub>x,y</sub>"] = [
            accelerator.etapx,
            accelerator.etapy,
        ]

        input_template["Accelerator"]["Options"][
            "Injection Condition"
        ] = accelerator.injection_condition

        input_template["Accelerator"]["Options"][
            "Zero Emittance"
        ] = accelerator.zero_emittance

        input_template["Accelerator"]["Options"][
            "Zero Energy Spread"
        ] = accelerator.zero_energy_spread

        return input_template


class GeneralConfigs:
    """Class with general configs."""

    def __init__(self):
        """Class constructor."""
        self._distance_from_source = 10  # [m]

    @property
    def distance_from_source(self):
        """Distance from source.

        Returns:
            float: Distance from source [m]
        """
        return self._distance_from_source

    @distance_from_source.setter
    def distance_from_source(self, value):
        self._distance_from_source = value


class CalcFlux(GeneralConfigs, SpectraTools):
    """Class with methods to calculate flux."""

    class CalcConfigs:
        """Sub class to define calculation parameters."""

        class SourceType:
            """Sub class to define source type."""

            user_defined = "userdefined"

        class Method:
            """Sub class to define calculation method."""

            near_field = "nearfield"
            wigner = "wigner"

        class Variable:
            """Sub class to define independet variable."""

            energy = "en"
            mesh_xy = "xy"

        class Output:
            """Sub class to define output type."""

            flux_density = "fluxdensity"
            flux = "partialflux"

        class SlitShape:
            """Sub class to define slit shape."""

            none = ""
            circular = "circslit"
            retangular = "retslit"

    def __init__(self, accelerator):
        """Class constructor."""
        self._source_type = self.CalcConfigs.SourceType.user_defined
        self._method = self.CalcConfigs.Method.near_field
        self._indep_var = self.CalcConfigs.Variable.energy
        self._output_type = self.CalcConfigs.Output.flux_density
        self._slit_shape = self.CalcConfigs.SlitShape.none
        self._distance_from_source = 1
        self._accelerator = accelerator
        self._field = None
        self._energy_range = None
        self._energy_step = None
        self._slit_position = None
        self._slit_acceptance = None
        self._input_template = None
        self._output_captions = None
        self._output_data = None
        self._output_variables = None

    @property
    def source_type(self):
        """Source type.

        Returns:
            CalcConfigs variables: Magnetic field, it can be defined by user or
            generated by spectra.
        """
        return self._source_type

    @property
    def method(self):
        """Method of calculation.

        Returns:
            CalcConfigs variables: Method of calculation, it can be near field
            or wigner functions, for example.
        """
        return self._method

    @property
    def indep_var(self):
        """Independent variable.

        Returns:
            CalcConfigs variables: Independet variable, it can be energy of a
            mesh in the xy plane
        """
        return self._indep_var

    @property
    def output_type(self):
        """Output type.

        Returns:
            CalcConfigs variables: Output type, it can be flux density or
            partial flux, for example.
        """
        return self._output_type

    @property
    def field(self):
        """Magnetic field defined by user.

        Returns:
            numpy array: First column contains longitudinal spatial
            coordinate (z) [mm], second column contais vertical field
            [T], and third column constais horizontal field [T].
        """
        return self._field

    @property
    def energy_range(self):
        """Energy range.

        Returns:
            List of ints: Energy range to calculate spectrum
             [initial point, final point].
        """
        return self._energy_range

    @property
    def energy_step(self):
        """Energy step.

        Returns:
            float: Spectrum energy step.
        """
        return self._energy_step

    @property
    def observation_position(self):
        """Observation position [mrad].

        Returns:
            List of floats: Slit position [xpos, ypos] [mrad]
        """
        return self._slit_position

    @property
    def slit_acceptance(self):
        """Slit acceptance [mrad].

        Returns:
            List of floats: Slit acceptance [xpos, ypos] [mrad]
        """
        return self._slit_acceptance

    @property
    def slit_shape(self):
        """Slit shape.

        Returns:
            string: It can be circular or rectangular.
        """
        return self._slit_shape

    @property
    def output_captions(self):
        """Output captions.

        Returns:
            dict: Captions with spectra output
        """
        return self._output_captions

    @property
    def output_data(self):
        """Output data.

        Returns:
            dict: Data output from spectra
        """
        return self._output_data

    @property
    def output_variables(self):
        """Output variables.

        Returns:
            dict: Variables from spectra
        """
        return self._output_variables

    @source_type.setter
    def source_type(self, value):
        self._source_type = value

    @method.setter
    def method(self, value):
        self._method = value

    @indep_var.setter
    def indep_var(self, value):
        self._indep_var = value
        if value == self.CalcConfigs.Variable.energy:
            self._slit_position = [0, 0]
        elif value == self.CalcConfigs.Variable.mesh_xy:
            self._slit_position = None

    @output_type.setter
    def output_type(self, value):
        self._output_type = value

    @field.setter
    def field(self, value):
        if self.source_type != self.CalcConfigs.SourceType.user_defined:
            raise ValueError(
                "Field can only be defined if source type is user_defined."
            )
        else:
            self._field = value

    @energy_range.setter
    def energy_range(self, value):
        if self.indep_var != self.CalcConfigs.Variable.energy:
            raise ValueError(
                "Energy range can only be defined if the independent variable is energy."  # noqa: E501
            )
        else:
            self._energy_range = value

    @energy_step.setter
    def energy_step(self, value):
        if self.indep_var != self.CalcConfigs.Variable.energy:
            raise ValueError(
                "Energy step can only be defined if the independent variable is energy."  # noqa: E501
            )
        else:
            self._energy_step = value

    @observation_position.setter
    def observation_position(self, value):
        if self.indep_var != self.CalcConfigs.Variable.energy:
            raise ValueError(
                "Observation position can only be defined if the independent variable is energy."  # noqa: E501
            )
        else:
            self._slit_position = value

    @slit_acceptance.setter
    def slit_acceptance(self, value):
        if self.output_type != self.CalcConfigs.Output.flux:
            raise ValueError(
                "Slit acceptance can only be defined if the output type is flux."  # noqa: E501
            )
        else:
            self._slit_acceptance = value

    @slit_shape.setter
    def slit_shape(self, value):
        if self.output_type != self.CalcConfigs.Output.flux:
            raise ValueError(
                "Slit shape can only be defined if the output type is flux."  # noqa: E501
            )
        else:
            self._slit_shape = value

    def set_config(self):
        """Set calc config."""
        config_name = REPOS_PATH + "/calculation_parameters/"
        config_name += self.source_type
        config_name += "_"
        config_name += self.method
        config_name += "_"
        config_name += self.indep_var
        config_name += "_"
        config_name += self.output_type

        if self.slit_shape != "":
            config_name += "_"
            config_name += self.slit_shape

        config_name += ".json"

        file = open(config_name)
        input_temp = json.load(file)
        input_temp = self._set_accelerator_config(
            self._accelerator, input_temp
        )

        if self.field is not None:
            data = _np.zeros((3, len(self.field[:, 0])))
            data[0, :] = self.field[:, 0]
            data[1, :] = self.field[:, 1]
            data[2, :] = self.field[:, 2]
            input_temp["Light Source"]["Field Profile"]["data"] = data.tolist()

        if self.energy_range is not None:
            input_temp["Configurations"][
                "Energy Range (eV)"
            ] = self.energy_range

        if self.energy_step is not None:
            input_temp["Configurations"][
                "Energy Pitch (eV)"
            ] = self.energy_step

        if self.observation_position is not None:
            if self.output_type == self.CalcConfigs.Output.flux_density:
                input_temp["Configurations"][
                    "Angle &theta;<sub>x,y</sub> (mrad)"
                ] = self.observation_position
            elif self.output_type == self.CalcConfigs.Output.flux:
                input_temp["Configurations"][
                    "Slit Pos.: &theta;<sub>x,y</sub> (mrad)"
                ] = self.observation_position

        if self.slit_acceptance is not None:
            if self.slit_shape == self.CalcConfigs.SlitShape.circular:
                input_temp["Configurations"][
                        "Slit &theta;<sub>1,2</sub> (mrad)"
                    ] = self.slit_acceptance
            elif self.slit_shape == self.CalcConfigs.SlitShape.retangular:
                input_temp["Configurations"][
                        "&Delta;&theta;<sub>x,y</sub> (mrad)"
                    ] = self.slit_acceptance

        input_temp["Configurations"][
            "Distance from the Source (m)"
        ] = self.distance_from_source

        self._input_template = input_temp

    def run_calculation(self):
        """Run calculation."""
        solver = self._run_solver(self._input_template)
        captions, data, variables = self.extractdata(solver)
        self._output_captions = captions
        self._output_data = data
        self._output_variables = variables

    @staticmethod
    def extractdata(solver):
        """Extract solver data.

        Args:
            solver (spectra solver): Spectra solver object

        Returns:
            dict: captions
            dict: data
            dict: variables
        """
        captions = solver.GetCaptions()
        data = _np.array(solver.GetData()["data"])
        variables = _np.array(solver.GetData()["variables"])
        return captions, data, variables


class SpectraInterface:
    """Spectra Interface class."""

    def __init__(self):
        """Class constructor."""
        self._accelerator = StorageRingParameters()
        self._calc_flux = CalcFlux(self._accelerator)

    @property
    def accelerator(self):
        """Accelerator parameters.

        Returns:
            StorageRingParameters object: class to config accelerator.
        """
        return self._accelerator

    @property
    def calc_flux(self):
        """CalcFlux object.

        Returns:
            CalcFlux object: Class to calculate flux
        """
        return self._calc_flux
