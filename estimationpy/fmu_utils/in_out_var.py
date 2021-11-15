"""
@author: Marco Bonvini
"""
import numpy
import pandas as pd

from estimationpy.fmu_utils.csv_reader import CsvReader
from estimationpy.fmu_utils import strings
import pyfmi

import logging

logger = logging.getLogger(__name__)


class InOutVar:
    """
    This class represents a generic input or output variable of a
    dynamic system.
    In case of state and parameter estimation both input and outputs 
    of a system have the characteristic of having measurements associated
    to them. These measurements, together with other informations that can
    quantify their unsertanty, are used by the estimation algorithm.
    
    This class can be seen as a wrapper around the class **pyfmi.fmi.ScalarVariable**
    with the addition of an object that represent a measurement time series.
    The time series can be directly defined as a pandas.Series object or with the
    convenience class :class:`estimationpy.fmu_utils.csv_reader.CsvReader`.
    
    **Note**
    
        When dealing with real systems not all the output measurements can be measured.
        For example a translational mechanic system can have as outputs the position of a mass, 
        it velocity, and its acceleration. However, in a real application one may only have 
        access to one of these measurements.
        The class uses a boolean flag to define whether an output is actually being measured and
        thus can be used by a state estimation algorithm.
    
    """

    def __init__(self, pyfmi_var=None):
        """
        Consttuctor for the class :class:`InOutVar`. The constructor takes as input
        parameter an object of type **pyfmi.fmi.ScalarVariable** that contains the
        information about the variable.
        The method initializes an empty **CsvReader** object and an empty **pandas.Series**
        object that can be futher defined.
        The method also initializes the covariance :math:`\sigma^2` associated to this variable to be 1.0,
        and the flag ``measOut = False``.
        
        The class provide, the CsvReader class associated to the input (that contains the data), 
        a dictionary called dataSeries = {"time": [], "data": []} that contains the two arrays that represent
        the data series (that are read from the csv file).
        
        The integer index is used when the data values are read using the function ReadFromDataSeries, while
        cov is the covariance associated to the data series.

        :param pyfmi.fmi.ScalarVariable pyfmi_var: the pyfmi object representing a variable.
        
        """
        self.pyfmi_var = pyfmi_var
        self.csvReader = CsvReader()
        self.dataSeries = pd.Series()

        self.index = 0
        self.cov = 1.0
        self.measOut = False

    def read_value_in_fmu(self, fmu):
        """
        This method reads the value of a variable/parameter 
        assumes in a specific FMU object.
        
        :param FmuModel fmu: an object representing an FMU model in PyFMI.
        
        :return: The value of the variable represented by an instance of this class.
          The method returns `None` is the type of the variable is not recognized as one
          of the available ones (Real, Integer, Boolean, Enumeration, String).
        
        :rtype: float, None
        
        """
        t = self.pyfmi_var.type
        if t == pyfmi.fmi.FMI_REAL:
            val = fmu.get_real(self.pyfmi_var.value_reference)
        elif t == pyfmi.fmi.FMI_INTEGER:
            val = fmu.get_integer(self.pyfmi_var.value_reference)
        elif t == pyfmi.fmi.FMI_BOOLEAN:
            val = fmu.get_boolean(self.pyfmi_var.value_reference)
        elif t == pyfmi.fmi.FMI_ENUMERATION:
            val = fmu.get_int(self.pyfmi_var.value_reference)
        elif t == pyfmi.fmi.FMI_STRING:
            val = fmu.get_string(self.pyfmi_var.value_reference)
        else:
            msg = "FMU-EXCEPTION, The type {0} is not known".format(t)
            logger.error(msg)
            return None
        return val[0]

    def set_measured_output(self, flag=True):
        """
        This method set the flag that indicates if the variable represents a measured output.
        
        :param bool flag: flag that indicates whether this variable is a measured output
          or not.
        """
        self.measOut = flag

    def is_measured_output(self):
        """
        This method returns the value of the boolean flag that describe
        if the variable is a measured output.
        
        :return: a boolean value that indicates if this variable is a measured output.

        :rtype: bool

        """
        return self.measOut

    def set_covariance(self, cov):
        """
        This method sets the covariance associated to
        an instance of the class :class:`InOutVar` that is used
        by the state and parameter estimation algorithm.
        
        :param float cov: The value to be used as initial value in the estimation
            algorithm. The value must be positive.
        
        :return: True if the value has been set corectly, False otherwise.
        
        :rtype: bool
        
        """
        if cov > 0.0:
            self.cov = cov
            return True
        else:
            msg = "The covariance must be positive"
            logger.error(msg)
            raise ValueError(msg)

    def get_covariance(self):
        """
        This method returns the covariance of the **InOutVar** object.
        
        :return: the covariance of the variable.
        :rtype: float
        
        """
        return self.cov

    def set_object(self, pyfmi_var):
        """
        This method sets the variable associated to the object of class
        **InOutVar**.
        
        :param pyfmi.fmi.ScalarVariable pyfmi_var: The variable associated to the input/output represented
          by the object.
        
        :raises TypeError: The method raises an exception if the parameter is not of the proper type.

        """
        if (isinstance(pyfmi_var, pyfmi.fmi.ScalarVariable)) or (isinstance(pyfmi_var, pyfmi.fmi.ScalarVariable2)):
            self.pyfmi_var = pyfmi_var
        else:
            raise TypeError(
                "The object passed to the method InOutVar.set_object() is not of type pyfmi.fmi.ScalarVariable ")

    def get_object(self):
        """
        Get the object associated to the **pyfmi.ScalarVariable** associated to this input/output
        variable.
        
        :return: the pyfmi variable object reference by this variable.
        :rtype: pyfmi.fmi.ScalarVariable

        """
        return self.pyfmi_var

    def set_csv_reader(self, reader):
        """
        This method associates an object of type :class:`estimationpy.fmu_utils.csv_reader.CsvReader` to this
        input/output variable. The **CsvReder** will be used to read data by the state and parameter estimation
        algorithm.

        :param estimationpy.fmu_utils.csv_reader.CsvReader reader: The **CsvReader** object to associate to this
        variable.
        
        :raises TypeError: The method raises an exception if the type of the argument reader is not correct.

        """
        if isinstance(reader, CsvReader):
            self.csvReader = reader
        else:
            msg = "The object passed to the method InOutVar.SetCsvReader() is not of type FmuUtils.CsvReader.CsvReader"
            msg += "\n it is of type %s" % (str(type(reader)))
            raise TypeError(msg)

    def get_csv_reader(self):
        """
        This method returns a reference to the **CsvReader** object associated to the
        input/output variable.
        
        :return: the reference to the **CsvReader** object.

        :rtype: estimationpy.fmu_utils.csv_reader.CsvReader

        """
        return self.csvReader

    def read_data_series(self):
        """
        This method reads the data series associated to this input/output variable.
        The method checks if the **CsvReader** object has a valid file name 
        associated to it. If not it looks if the data series has already been
        specified and is a not empty **pandas.Series**.
        The method returns True if the data is read, False otherwise.
        
        :return: True if the method is able to read the data from either the CsvReader obejct
          of the pandas.Series. False otherwise.
        :rtype: bool
        """
        # If the CsvReader has been specified the try to load the data from there
        if self.csvReader.filename == "" or self.csvReader.filename is None:

            # Check because the dataSeries may have bee specified using a pandas.Series
            if len(self.dataSeries) > 0:
                return True
            else:
                return False
        else:

            # Read the data from the CSV
            self.dataSeries = self.csvReader.get_data_series()
            if len(self.dataSeries) > 0:
                return True
            else:
                return False

    def get_data_series(self):
        """
        This method returns the data series associated to this input/output variable.
        The dat aseries can be either specified by a CSV file by means of a
        **Csvreader** object, or directly from a **pandas.Series** object.
        
        :return: the pandas.Series associated to this variable.
        :rtype: pandas.Series
        """
        return self.dataSeries

    def set_data_series(self, series):
        """
        This function sets a data series instead of reading it from the CSV file.
        The data series has to be a **pandas.Series** object that is indexed with
        a **pandas.tseries.index.DatetimeIndex**.
        
        :param pandas.Series series: the time series to be associated to this input/output
          variable.
        
        :raises TypeError: The method raise an error if the parameter ``series`` is
          not of the right type or it's a pandas.Series not indexed with a 
          **pandas.tseries.index.DatetimeIndex**.

        """
        if isinstance(series, pd.Series):
            if isinstance(series.index, pd.DatetimeIndex):
                self.dataSeries = series
            else:
                raise TypeError(
                    "The index of the Series passed to the method InOutVar.SetDataSeries() is not of type "
                    "pandas.DatetimeIndex")
        else:
            raise TypeError("The object passed to the method InOutVar.SetDataSeries() is not of type pandas.Series ")

    def read_from_data_series(self, ix):
        """
        This method reads and return the value associated to the input/output variable
        at the time specified by the parameter ``ix``. The parameter ``ix`` needs
        to be a vaid index that belongs to a **pandas.tseries.index.DatetimeIndex**.
        If the index ``ix`` is not one of the indexes of the pandas.Series the
        method performs a linear interpolation between the two closest values to 
        compute the value.
        
        :param ix: the time stamp for which providing the value.

        :return: the value that is read from the pandas.Series associated to the variable.
          if the index is out of range the method returns False.
        
        :rtype: float, bool
        
        """
        # Identify start and end date of the period covered by the time series
        from_start = (ix - self.dataSeries.index[0]).total_seconds()
        to_end = (self.dataSeries.index[-1] - ix).total_seconds()

        if from_start < 0.0 or to_end < 0.0:
            # The index ix is not contained in the array, it's either
            # before the start or after the end
            return False

        try:
            # try to read directly the index, if it exists it's done
            value = self.dataSeries.loc[ix]
            return value

        except KeyError:

            # The index ix is not present, an interpolation is needed.
            # Since it is a sequential access, store the last position to reduce the access time for the next iteration
            index = self.index
            N = len(self.dataSeries.index)

            # Start the identification of the position of the closest time step

            # If len(time) = 10 and index was 2, indexes is [2, 3, 4, 5, 6, 7, 8, 9, 0, 1]
            indexes = numpy.concatenate((numpy.arange(index, N), numpy.arange(index + 1)))

            # Start the iteration
            logger.debug("Indexes = {0}".format(indexes))

            for i in range(N):

                j = indexes[i]

                logger.debug("j = {0}".format(j))

                # Get the time values (of type Timestamp)
                T_a = self.dataSeries.index[indexes[i]]
                T_b = self.dataSeries.index[indexes[i + 1]]

                # Since the array is circular it may be necessary to sweep the values
                # This guarantees that T_0 is always the minimum and T_1 the maximum of 
                # the considered interval
                T_0 = min(T_a, T_b)
                T_1 = max(T_a, T_b)

                msg = "Time {0} and [{1}, {2}]".format(ix, T_0, T_1)
                logger.debug(msg)

                # Measure the difference in seconds between the desired index
                # and the two points 
                t_0 = (ix - T_0).total_seconds()
                t_1 = (ix - T_1).total_seconds()

                # Skip transition when restarting from the beginning (j == N-1)
                # If T_0 <= ix <= T_1 the exit
                if j != N - 1 and t_0 >= 0 >= t_1:
                    break
                else:
                    # Otherwise go to the next couple of points
                    j += 1

            # This takes into account that the array is circular and the algorithm may
            # finish in a zone where the order 
            if j < N - 1:
                index_0 = indexes[i]
                index_1 = indexes[i + 1]
            else:
                index_1 = indexes[i]
                index_0 = indexes[i - 1]

            msg = "Picked values are {0} : {1}".format(self.dataSeries.values[index_0], self.dataSeries.values[index_1])
            logger.debug(msg)

            # Get distances in seconds to compute the linear interpolation
            deltaT = (self.dataSeries.index[index_1] - self.dataSeries.index[index_0]).total_seconds()
            dT0 = (ix - self.dataSeries.index[index_0]).total_seconds()
            dT1 = (self.dataSeries.index[index_1] - ix).total_seconds()
            interpData = (dT0 * self.dataSeries.values[index_1] + dT1 * self.dataSeries.values[index_0]) / deltaT

            # Save the index
            self.index = j

            return interpData
