"""Spectra functions."""

import numpy as _np
import matplotlib.pyplot as _plt
from accelerator import StorageRingParameters
import mathphys
from tools import SourceFunctions
import json
import spectra
import sys
import time
import os

REPOS_PATH = os.path.abspath("./")

ECHARGE = mathphys.constants.elementary_charge
EMASS = mathphys.constants.electron_mass
LSPEED = mathphys.constants.light_speed
ECHARGE_MC = ECHARGE / (2 * _np.pi * EMASS * LSPEED)


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

        input_template["Accelerator"]["&sigma;<sub>z</sub> (mm)"] = (
            accelerator.sigmaz
        )

        input_template["Accelerator"]["Nat. Emittance (m.rad)"] = (
            accelerator.nat_emittance
        )

        input_template["Accelerator"]["Coupling Constant"] = (
            accelerator.coupling_constant
        )

        input_template["Accelerator"]["Energy Spread"] = (
            accelerator.energy_spread
        )

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

        input_template["Accelerator"]["Options"]["Injection Condition"] = (
            accelerator.injection_condition
        )

        input_template["Accelerator"]["Options"]["Zero Emittance"] = (
            accelerator.zero_emittance
        )

        input_template["Accelerator"]["Options"]["Zero Energy Spread"] = (
            accelerator.zero_energy_spread
        )

        return input_template


class GeneralConfigs(SourceFunctions):
    """Class with general configs."""

    class SourceType:
        """Sub class to define source type."""

        user_defined = "userdefined"
        horizontal_undulator = "linearundulator"
        vertical_undulator = "verticalundulator"
        helical_undulator = "helicalundulator"
        elliptic_undulator = "ellipticundulator"
        figure8_undulator = "figure8undulator"
        vertical_figure8_undulator = "verticalfigure8undulator"

    def __init__(self):
        """Class constructor."""
        self._distance_from_source = 10  # [m]
        self._source_type = self.SourceType.user_defined
        self._field = None
        self._bx_peak = None
        self._by_peak = None
        self._period = None
        self._kx = None
        self._ky = None
        self._id_length = None

    @property
    def source_type(self):
        """Source type.

        Returns:
            CalcConfigs variables: Magnetic field, it can be defined by user or
            generated by spectra.
        """
        return self._source_type

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
    def period(self):
        """Insertion device period [mm].

        Returns:
            float: ID's period [mm]
        """
        return self._period

    @property
    def by_peak(self):
        """Insertion device vertical peak field [T].

        Returns:
            float: by peak field [T]
        """
        return self._by_peak

    @property
    def bx_peak(self):
        """Insertion device horizontal peak field [T].

        Returns:
            float: bx peak field [T]
        """
        return self._bx_peak

    @property
    def ky(self):
        """Vertical deflection parameter (Ky).

        Returns:
            float: Vertical deflection parameter
        """
        return self._ky

    @property
    def kx(self):
        """Horizontal deflection parameter (Kx).

        Returns:
            float: Horizontal deflection parameter
        """
        return self._kx

    @property
    def id_length(self):
        """Insertion device's length.

        Returns:
            float: Id's length [m]
        """
        return self._id_length

    @property
    def distance_from_source(self):
        """Distance from source.

        Returns:
            float: Distance from source [m]
        """
        return self._distance_from_source

    @source_type.setter
    def source_type(self, value):
        self._source_type = value

    @field.setter
    def field(self, value):
        if self.source_type != self.SourceType.user_defined:
            raise ValueError(
                "Field can only be defined if source type is user_defined."
            )
        else:
            self._field = value

    @period.setter
    def period(self, value):
        if self.source_type == self.SourceType.user_defined:
            raise ValueError(
                "Period can only be defined if source type is not user_defined."  # noqa: E501
            )
        else:
            self._period = value
            if self._bx_peak is not None:
                self._kx = 1e-3 * ECHARGE_MC * self._bx_peak * self.period
            if self._by_peak is not None:
                self._ky = 1e-3 * ECHARGE_MC * self._by_peak * self.period
            if self._kx is not None:
                self._bx_peak = self._kx / (ECHARGE_MC * 1e-3 * self.period)
            if self._ky is not None:
                self._by_peak = self._ky / (ECHARGE_MC * 1e-3 * self.period)

    @by_peak.setter
    def by_peak(self, value):
        if self.source_type == self.SourceType.user_defined:
            raise ValueError(
                "By peak can only be defined if source type is not user_defined."  # noqa: E501
            )
        elif self.source_type == self.SourceType.vertical_undulator:
            raise ValueError(
                "By peak can not be defined if source type is a vertical undulator."  # noqa: E501
            )
        else:
            self._by_peak = value
            if self.period is not None:
                self._ky = 1e-3 * ECHARGE_MC * self._by_peak * self.period
                if (
                    self.source_type
                    == self.SourceType.vertical_figure8_undulator
                ):
                    self._ky *= 2

            if self.source_type == self.SourceType.helical_undulator:
                self._bx_peak = value
                if self.period is not None:
                    self._kx = self.ky

    @bx_peak.setter
    def bx_peak(self, value):
        if self.source_type == self.SourceType.user_defined:
            raise ValueError(
                "Bx peak can only be defined if source type is not user_defined."  # noqa: E501
            )
        elif self.source_type == self.SourceType.horizontal_undulator:
            raise ValueError(
                "Bx peak can not be defined if source type is a horizontal undulator."  # noqa: E501
            )
        else:
            self._bx_peak = value
            if self.period is not None:
                self._kx = 1e-3 * ECHARGE_MC * self._bx_peak * self.period
                if self.source_type == self.SourceType.figure8_undulator:
                    self._kx *= 2

            if self.source_type == self.SourceType.helical_undulator:
                self._by_peak = value
                if self.period is not None:
                    self._ky = self.kx

    @ky.setter
    def ky(self, value):
        if self.source_type == self.SourceType.user_defined:
            raise ValueError(
                "Ky can only be defined if source type is not user_defined."  # noqa: E501
            )
        elif self.source_type == self.SourceType.vertical_undulator:
            raise ValueError(
                "Ky can not be defined if source type is a vertical undulator."
            )  # noqa: E501
        else:
            self._ky = value
            if self.period is not None:
                self._by_peak = self._ky / (ECHARGE_MC * 1e-3 * self.period)
                if (
                    self.source_type
                    == self.SourceType.vertical_figure8_undulator
                ):
                    self._by_peak /= 2

            if self.source_type == self.SourceType.helical_undulator:
                self._kx = value
                if self.period is not None:
                    self._bx_peak = self.bx_peak

    @kx.setter
    def kx(self, value):
        if self.source_type == self.SourceType.user_defined:
            raise ValueError(
                "Kx can only be defined if source type is not user_defined."  # noqa: E501
            )
        elif self.source_type == self.SourceType.horizontal_undulator:
            raise ValueError(
                "Kx can not be defined if source type is a horizontal undulator."  # noqa: E501
            )
        else:
            self._kx = value
            if self.period is not None:
                self._bx_peak = self._kx / (ECHARGE_MC * 1e-3 * self.period)
                if self.source_type == self.SourceType.figure8_undulator:
                    self._bx_peak /= 2

            if self.source_type == self.SourceType.helical_undulator:
                self._kx = value
                if self.period is not None:
                    self._bx_peak = self.bx_peak

    @id_length.setter
    def id_length(self, value):
        if self.source_type == self.SourceType.user_defined:
            raise ValueError(
                "Id length can only be defined if source type is not user_defined"  # noqa: E501
            )
        else:
            self._id_length = value

    @distance_from_source.setter
    def distance_from_source(self, value):
        self._distance_from_source = value


class Calc(GeneralConfigs, SpectraTools):
    """Class with methods to calculate flux."""

    class CalcConfigs:
        """Sub class to define calculation parameters."""

        class Method:
            """Sub class to define calculation method."""

            near_field = "nearfield"
            far_field = "farfield"
            wigner = "wigner"

        class Variable:
            """Sub class to define independet variable."""

            energy = "en"
            mesh_xy = "xy"
            k = "k"

        class Output:
            """Sub class to define output type."""

            flux_density = "fluxdensity"
            flux = "partialflux"
            brilliance = "brilliance"

        class SlitShape:
            """Sub class to define slit shape."""

            none = ""
            circular = "circslit"
            rectangular = "retslit"

    def __init__(self, accelerator):
        """Class constructor."""
        super().__init__()
        self._method = self.CalcConfigs.Method.near_field
        self._indep_var = self.CalcConfigs.Variable.energy
        self._output_type = self.CalcConfigs.Output.flux_density
        self._slit_shape = self.CalcConfigs.SlitShape.none
        self._accelerator = accelerator
        self._input_template = None

        # Energy related
        self._energy_range = None
        self._energy_step = None
        self._slit_position = None
        self._slit_acceptance = None

        #  Mesh xy related
        self._target_energy = None
        self._x_range = None
        self._y_range = None
        self._x_nr_pts = None
        self._y_nr_pts = None

        #  K related
        self._harmonic_range = None
        self._k_range = None
        self._k_nr_pts = None
        self._slice_x = None
        self._slice_y = None
        self._slice_px = None
        self._slice_py = None

        #  Phase error
        self._add_phase_error = None
        self._random_seed = None
        self._rms_peak_field_var = None
        self._rms_phase_error = None
        self._rms_traj_error = None

        # Output
        self._output_captions = None
        self._output_data = None
        self._output_variables = None

        self._flux = None
        self._brilliance = None
        self._pl = None
        self._pc = None
        self._pl45 = None
        self._energies = None
        self._x = None
        self._y = None
        self._k = None

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
    def observation_angle(self):
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
    def target_energy(self):
        """Target energy.

        Returns:
            float: Target energy to analyse.
        """
        return self._target_energy

    @property
    def x_range(self):
        """Mesh x range.

        Returns:
            List of floats: x limits [mrad] [initial point, final point]
        """
        return self._x_range

    @property
    def y_range(self):
        """Mesh y range.

        Returns:
            List of floats: y limits [mrad] [initial point, final point]
        """
        return self._y_range

    @property
    def x_nr_pts(self):
        """Nr of x points.

        Returns:
            float: Number of horizontal mesh points
        """
        return self._x_nr_pts

    @property
    def y_nr_pts(self):
        """Nr of y points.

        Returns:
            float: Number of vertical mesh points
        """
        return self._y_nr_pts

    @property
    def harmonic_range(self):
        """Harmonic range.

        Returns:
            list of ints: List of harmonics to calculate brilliance.
        """
        return self._harmonic_range

    @property
    def k_range(self):
        """K range.

        Returns:
            list of ints: List of k to calculate brilliance [kmin, kmax].
        """
        return self._k_range

    @property
    def k_nr_pts(self):
        """Number of k points.

        Returns:
            int: Number of K points.
        """
        return self._k_nr_pts

    @property
    def slice_x(self):
        """Slice x.

        Returns:
            float: Horizontal source point where Wigner function is
             calculated [mm].
        """
        return self._slice_x

    @property
    def slice_y(self):
        """Slice y.

        Returns:
            float: Vertical source point where Wigner function is
             calculated [mm].
        """
        return self._slice_y

    @property
    def slice_px(self):
        """Slice x'.

        Returns:
            float: Horizontal source angle where Wigner function is
             calculated [mrad].
        """
        return self._slice_px

    @property
    def slice_py(self):
        """Slice y'.

        Returns:
            float: Horizontal source angle where Wigner function is
             calculated [mrad].
        """
        return self._slice_py

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

    @property
    def add_phase_error(self):
        """Add phase error.

        Returns:
            bool: If true user can set phase errors.
        """
        return self._add_phase_error

    @property
    def random_seed(self):
        """random phase error seed.

        Returns:
            float: Seed for generation of phase errors.
        """
        return self._random_seed

    @property
    def rms_peak_field_var(self):
        """RMS of the peak field variation.

        Returns:
            float: RMS of peak field variation.
        """
        return self._rms_peak_field_var

    @property
    def rms_phase_error(self):
        """RMS of phase error.

        Returns:
            float: RMS of phase error.
        """
        return self._rms_phase_error

    @property
    def rms_trajectory_error(self):
        """RMS of trajectory error.

        Returns:
            list of float: RMS of trajectory error [x, y].
        """
        return self._rms_traj_error

    @property
    def flux(self):
        """Flux output.

        Returns:
            numpy array: Flux [ph/s/mr²/0.1%B.W].
        """
        return self._flux

    @property
    def brilliance(self):
        """Brilliance output.

        Returns:
            numpy array: Brilliance [ph/s/mr²/0.1%B.W/mm²].
        """
        return self._brilliance

    @property
    def pl(self):
        """Linear polarization.

        Returns:
            numpy array: Linear polarization s1/s0
        """
        return self._pl

    @property
    def pc(self):
        """Circular polarization.

        Returns:
            numpy array: Circular polarization s3/s0
        """
        return self._pc

    @property
    def pl45(self):
        """Linear polarization 45°.

        Returns:
            numpy array: Linear polarization 45° s2/s0
        """
        return self._pl45

    @property
    def energies(self):
        """Energies.

        Returns:
            numpy array: Energyes [eV]
        """
        return self._energies

    @property
    def x(self):
        """Horizontal angle.

        Returns:
            numpy array: Horizontal angle [mrad]
        """
        return self._x

    @property
    def y(self):
        """Vertical angle.

        Returns:
            numpy array: Vertical angle [mrad]
        """
        return self._y

    @property
    def k(self):
        """Deflection parameter K.

        Returns:
            numpy array: Deflecetion parameter K.
        """
        return self._k

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
            self._slit_shape = self.CalcConfigs.SlitShape.none

    @output_type.setter
    def output_type(self, value):
        self._output_type = value
        if value == self.CalcConfigs.Output.flux_density:
            self._slit_shape = self.CalcConfigs.SlitShape.none

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

    @observation_angle.setter
    def observation_angle(self, value):
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

    @target_energy.setter
    def target_energy(self, value):
        if self.indep_var != self.CalcConfigs.Variable.mesh_xy:
            raise ValueError(
                "Target energy can only be defined if the variable is a xy mesh."  # noqa: E501
            )
        else:
            self._target_energy = value

    @x_range.setter
    def x_range(self, value):
        if self.indep_var != self.CalcConfigs.Variable.mesh_xy:
            raise ValueError(
                "X range can only be defined if the variable is a xy mesh."  # noqa: E501
            )
        else:
            self._x_range = value

    @y_range.setter
    def y_range(self, value):
        if self.indep_var != self.CalcConfigs.Variable.mesh_xy:
            raise ValueError(
                "Y range can only be defined if the variable is a xy mesh."  # noqa: E501
            )
        else:
            self._y_range = value

    @x_nr_pts.setter
    def x_nr_pts(self, value):
        if self.indep_var != self.CalcConfigs.Variable.mesh_xy:
            raise ValueError(
                "X range can only be defined if the variable is a xy mesh."  # noqa: E501
            )
        else:
            self._x_nr_pts = value

    @y_nr_pts.setter
    def y_nr_pts(self, value):
        if self.indep_var != self.CalcConfigs.Variable.mesh_xy:
            raise ValueError(
                "Y range can only be defined if the variable is a xy mesh."  # noqa: E501
            )
        else:
            self._y_nr_pts = value

    @harmonic_range.setter
    def harmonic_range(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "Harmonic range can only be defined if the variable is k."
            )
        else:
            self._harmonic_range = value

    @k_range.setter
    def k_range(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "K range can only be defined if the variable is k."
            )
        else:
            self._k_range = value

    @k_nr_pts.setter
    def k_nr_pts(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "K nr points can only be defined if the variable is k."
            )
        else:
            self._k_nr_pts = value

    @slice_x.setter
    def slice_x(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "Slice x can only be defined if the variable is k."
            )
        else:
            self._slice_x = value

    @slice_y.setter
    def slice_y(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "Slice y can only be defined if the variable is k."
            )
        else:
            self._slice_y = value

    @slice_px.setter
    def slice_px(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "Slice x' can only be defined if the variable is k."
            )
        else:
            self._slice_px = value

    @slice_py.setter
    def slice_py(self, value):
        if self.indep_var != self.CalcConfigs.Variable.k:
            raise ValueError(
                "Slice y' can only be defined if the variable is k."
            )
        else:
            self._slice_py = value

    @add_phase_error.setter
    def add_phase_error(self, value):
        if self.method != self.CalcConfigs.Method.near_field:
            raise ValueError(
                "Phase error can only be defined if the method of calculation is near field"  # noqa: E501
            )
        else:
            self._add_phase_error = value

    @random_seed.setter
    def random_seed(self, value):
        if self.add_phase_error is not True:
            raise ValueError(
                "Phase error's parameters can only be defined if add_phase_error is True"  # noqa: E501
            )
        else:
            self._random_seed = value

    @rms_peak_field_var.setter
    def rms_peak_field_var(self, value):
        if self.add_phase_error is not True:
            raise ValueError(
                "Phase error's parameters can only be defined if add_phase_error is True"  # noqa: E501
            )
        else:
            self._rms_peak_field_var = value

    @rms_phase_error.setter
    def rms_phase_error(self, value):
        if self.add_phase_error is not True:
            raise ValueError(
                "Phase error's parameters can only be defined if add_phase_error is True"  # noqa: E501
            )
        else:
            self._rms_phase_error = value

    @rms_trajectory_error.setter
    def rms_trajectory_error(self, value):
        if self.add_phase_error is not True:
            raise ValueError(
                "Phase error's parameters can only be defined if add_phase_error is True"  # noqa: E501
            )
        else:
            self._rms_traj_error = value

    def set_config(self):  # noqa: C901
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

        if self.ky is not None:
            if (
                self.source_type == self.SourceType.horizontal_undulator
                or self.source_type == self.SourceType.helical_undulator
            ):
                input_temp["Light Source"]["K value"] = self.ky

        if self.kx is not None:
            if self.source_type == self.SourceType.vertical_undulator:
                input_temp["Light Source"]["K value"] = self.kx

        if self.kx is not None and self.ky is not None:
            if (
                self.source_type == self.SourceType.elliptic_undulator
                or self.source_type == self.SourceType.figure8_undulator
                or self.source_type
                == self.SourceType.vertical_figure8_undulator
            ):
                input_temp["Light Source"]["K<sub>x,y</sub>"] = [
                    self.kx,
                    self.ky,
                ]

        if self.period is not None:
            input_temp["Light Source"]["&lambda;<sub>u</sub> (mm)"] = (
                self.period
            )

        if self.id_length is not None:
            input_temp["Light Source"]["Device Length (m)"] = self.id_length

        if self.energy_range is not None:
            input_temp["Configurations"]["Energy Range (eV)"] = (
                self.energy_range
            )

        if self.energy_step is not None:
            input_temp["Configurations"]["Energy Pitch (eV)"] = (
                self.energy_step
            )

        if self.observation_angle is not None:
            if self.output_type == self.CalcConfigs.Output.flux_density:
                input_temp["Configurations"][
                    "Angle &theta;<sub>x,y</sub> (mrad)"
                ] = self.observation_angle
            elif self.output_type == self.CalcConfigs.Output.flux:
                input_temp["Configurations"][
                    "Slit Pos.: &theta;<sub>x,y</sub> (mrad)"
                ] = self.observation_angle

        if self.slit_acceptance is not None:
            if self.slit_shape == self.CalcConfigs.SlitShape.circular:
                input_temp["Configurations"][
                    "Slit &theta;<sub>1,2</sub> (mrad)"
                ] = self.slit_acceptance
            elif self.slit_shape == self.CalcConfigs.SlitShape.rectangular:
                input_temp["Configurations"][
                    "&Delta;&theta;<sub>x,y</sub> (mrad)"
                ] = self.slit_acceptance

        if self.target_energy is not None:
            input_temp["Configurations"]["Target Energy (eV)"] = (
                self.target_energy
            )

        if self.x_range is not None:
            input_temp["Configurations"][
                "&theta;<sub>x</sub> Range (mrad)"
            ] = self.x_range
            input_temp["Configurations"][
                "&theta;<sub>y</sub> Range (mrad)"
            ] = self.y_range
            input_temp["Configurations"]["Points (x)"] = self.x_nr_pts
            input_temp["Configurations"]["Points (y)"] = self.y_nr_pts

        if self.harmonic_range is not None:
            input_temp["Configurations"]["Harmonic Range"] = (
                self.harmonic_range
            )
            input_temp["Configurations"]["K Range"] = self.k_range
            input_temp["Configurations"]["Points (K)"] = self.k_nr_pts
            input_temp["Configurations"]["Slice X (mm)"] = self.slice_x
            input_temp["Configurations"]["Slice Y (mm)"] = self.slice_y
            input_temp["Configurations"]["Slice X' (mrad)"] = self.slice_px
            input_temp["Configurations"]["Slice Y' (mrad)"] = self.slice_py

        input_temp["Configurations"]["Distance from the Source (m)"] = (
            self.distance_from_source
        )

        self._input_template = input_temp

    def verify_valid_parameters(self):  # noqa: C901
        """Check if calculation parameters are valid.

        Returns:
            bool: Returns True of False.
        """
        if self.indep_var == self.CalcConfigs.Variable.energy:
            if self.energy_range is None:
                raise ValueError("Energy range must be defined.")

            if self.energy_step is None:
                raise ValueError("Energy step must be defined.")

            if self.observation_angle is None:
                raise ValueError("Observation angle must be defined.")

            if self.output_type == self.CalcConfigs.Output.flux:
                if self.slit_acceptance is None:
                    raise ValueError("Slit acceptance must be defined.")

                if self.slit_shape is None:
                    raise ValueError("Slit shape must be defined.")

        if self.indep_var == self.CalcConfigs.Variable.mesh_xy:
            if self.target_energy is None:
                raise ValueError("Energy target must be defined")

            if self.x_range is None:
                raise ValueError("X range must be defined.")

            if self.y_range is None:
                raise ValueError("Y range must be defined.")

            if self.x_nr_pts is None:
                raise ValueError("Nr. of x points must be defined.")

            if self.y_nr_pts is None:
                raise ValueError("Nr. of y points must be defined.")

        if self.indep_var == self.CalcConfigs.Variable.k:
            if self.harmonic_range is None:
                raise ValueError("Harmonic range must be defined.")

            if self.k_range is None:
                raise ValueError("K range must be defined.")

            if self.k_nr_pts is None:
                raise ValueError("Number of K points must be defined.")

            if self.slice_x is None:
                raise ValueError("Slice x must be defined.")

            if self.slice_y is None:
                raise ValueError("Slice y must be defined.")

            if self.slice_px is None:
                raise ValueError("Slice px must be defined.")

            if self.slice_py is None:
                raise ValueError("Slice py must be defined.")

        return True

    def run_calculation(self):
        """Run calculation."""
        self.verify_valid_parameters()
        solver = self._run_solver(self._input_template)
        captions, data, variables = self.extractdata(solver)
        self._output_captions = captions
        self._output_data = data
        self._output_variables = variables
        self._set_outputs()

    def _set_outputs(self):
        data = self._output_data
        captions = self._output_captions
        self._flux = data[0, :]

        if self.indep_var == self.CalcConfigs.Variable.energy:
            if len(captions["titles"]) == 5:
                self._pl = data[1, :]
                self._pc = data[2, :]
                self._pl45 = data[3, :]
            elif len(captions["titles"]) == 6:
                self._brilliance = data[1, :]
                self._pl = data[2, :]
                self._pc = data[3, :]
                self._pl45 = data[4, :]
            self._energies = self._output_variables[0, :]

        elif self.indep_var == self.CalcConfigs.Variable.mesh_xy:
            self._pl = data[1, :]
            self._pc = data[2, :]
            self._pl45 = data[3, :]

            self._x = self._output_variables[0, :]
            self._y = self._output_variables[1, :]

            self._flux = _np.reshape(self._flux, (len(self._x), len(self._y)))
            self._flux = _np.flip(self._flux, axis=0)

            self._pl = _np.reshape(self._pl, (len(self._x), len(self._y)))
            self._pl = _np.flip(self._pl, axis=0)

            self._pc = _np.reshape(self._pc, (len(self._x), len(self._y)))
            self._pc = _np.flip(self._pc, axis=0)

            self._pl45 = _np.reshape(self._pl45, (len(self._x), len(self._y)))
            self._pl45 = _np.flip(self._pl45, axis=0)

    def extractdata(self, solver):
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
        if self.indep_var != self.CalcConfigs.Variable.k:
            variables = _np.array(solver.GetData()["variables"])
        else:
            nr_harmonics = (
                int((self.harmonic_range[-1] - self.harmonic_range[0]) / 2) + 1
            )
            variables = _np.zeros((nr_harmonics, self.k_nr_pts))
            data = _np.zeros((nr_harmonics, 2, self.k_nr_pts))
            for i in range(nr_harmonics):
                variables[i, :] = _np.array(
                    solver.GetDetailData(i)["variables"]
                )
                data[i, :, :] = _np.array(
                    solver.GetDetailData(i)["data"]
                )
        return captions, data, variables


class SpectraInterface:
    """Spectra Interface class."""

    def __init__(self):
        """Class constructor."""
        self._accelerator = StorageRingParameters()
        self._calc = Calc(self._accelerator)

    @property
    def accelerator(self):
        """Accelerator parameters.

        Returns:
            StorageRingParameters object: class to config accelerator.
        """
        return self._accelerator

    @property
    def calc(self):
        """CalcFlux object.

        Returns:
            CalcFlux object: Class to calculate flux
        """
        return self._calc
