import os
import unittest

from netCDF4 import Dataset

from test_aodntools.base_test import BaseTestCase
from aodntools.timeseries_products.hourly_timeseries import hourly_aggregator


TEST_ROOT = os.path.dirname(__file__)
BAD_FILE = 'IMOS_ANMN-NRS_TZ_20181213T080000Z_NRSROT_FV00_NRSROT-1812-SBE39-43_END-20181214T004000Z_C-20190827T000000Z.nc'
INPUT_FILES = [
    'IMOS_ANMN-NRS_BCKOSTUZ_20181213T080038Z_NRSROT_FV01_NRSROT-1812-WQM-55_END-20181215T013118Z_C-20190828T000000Z.nc',
    'IMOS_ANMN-NRS_TZ_20181213T080000Z_NRSROT_FV01_NRSROT-1812-SBE39-23_END-20190306T160000Z_C-20190827T000000Z.nc',
    'IMOS_ANMN-NRS_TZ_20190313T144000Z_NRSROT_FV01_NRSROT-1903-SBE39-27_END-20190524T010000Z_C-20190827T000000Z.nc',
    BAD_FILE
]
INPUT_PATHS = [os.path.join(TEST_ROOT, f) for f in INPUT_FILES]

INST_VARIABLES = {'instrument_id', 'source_file', 'LONGITUDE', 'LATITUDE', 'NOMINAL_DEPTH'}
OBS_VARIABLES = {'instrument_index', 'TIME'}
measured_variables = {'DEPTH', 'CPHL', 'CHLF', 'CHLU',
                      'DOX', 'DOX1', 'DOX1_2', 'DOX1_3', 'DOX2', 'DOX2_1', 'DOXS', 'DOXY',
                      'PRES', 'PRES_REL', 'PSAL', 'TEMP', 'TURB', 'PAR'
                      }
function_stats = ['_min', '_max', '_std', '_count']
for v in measured_variables:
    OBS_VARIABLES.add(v)
    for s in function_stats:
        OBS_VARIABLES.add(v + s)


class TestHourlyTimeseries(BaseTestCase):
    def test_hourly_aggregator(self):
        output_file, bad_files = hourly_aggregator(files_to_aggregate=INPUT_PATHS,
                                                   site_code='NRSROT',
                                                   qcflags=(1, 2),
                                                   file_path='/tmp'
                                                   )
        print('Output file:', output_file)
        print('Bad files:', bad_files)

        self.assertEqual(1, len(bad_files))
        for path, errors in bad_files.items():
            self.assertEqual(os.path.join(TEST_ROOT, BAD_FILE), path)
            self.assertSetEqual(set(errors), {'no NOMINAL_DEPTH', 'Wrong file version: Level 0 - Raw Data'})

        dataset = Dataset(output_file)
        self.assertSetEqual(set(dataset.dimensions), {'OBSERVATION', 'INSTRUMENT', 'string256'})
        self.assertTrue(set(dataset.variables.keys()).issubset(OBS_VARIABLES | INST_VARIABLES))

        inst_variables = {n for n, v in dataset.variables.items() if v.dimensions[0] == 'INSTRUMENT'}
        self.assertSetEqual(inst_variables, INST_VARIABLES)
        obs_variables = {n for n, v in dataset.variables.items() if v.dimensions == ('OBSERVATION',)}
        self.assertTrue(obs_variables.issubset(OBS_VARIABLES))


if __name__ == '__main__':
    unittest.main()
