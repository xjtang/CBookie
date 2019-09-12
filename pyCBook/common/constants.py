""" Module for commonly used constants
"""
DTYPES = [('date', '<i4'), ('above', '<f4'), ('emission', '<f8'),
            ('productivity', '<f8'), ('net', '<f8'), ('unreleased', '<f8')]
DTYPES2 = [('date', '<i4'), ('above', '<f4'), ('aboveUC', '<f4'),
            ('emission', '<f8'), ('emissionUC', '<f8'),
            ('productivity', '<f8'), ('productivityUC', '<f8'),
            ('net', '<f8'), ('netUC', '<f8'),
            ('unreleased', '<f8'), ('unreleasedUC', '<f8')]
SCALE_FACTOR = 0.47
PNAME = ['biomass', 'product', 'burned']
SPNAME = ['above', 'durable', 'fuel', 'pulp', 'burned']
FOREST = [1, 5]
SEB_CLASS = [1, 5]
UNCLASSIFIED = 0
REGROW_BIOMASS = [0.0, 0]
FOREST_MIN = 35.0
FORCE_START = 2000001
FORCE_END = 2020001
TRANSITIONS = ['sec', 'for_pas', 'for_sec', 'sec_gain', 'sec_pas']
MAP_NODATA = -9999
MAX_YEAR = 3000
HEADER = 'date,above,a_uc,emission,e_uc,productivity,p_uc,net,n_uc,unreleased,u_uc'
FMT = '%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f'
HEADER2 = 'date,above,emission,productivity,net,unreleased'
FMT2 = '%d,%f,%f,%f,%f,%f'
AREA = 518131758 * 30 * 30 / 100 / 100
SAREA = 13755 * 30 * 30 / 100 / 100
SCALE_FACTOR2 = 1000 * 1000
DIY = 365.25
