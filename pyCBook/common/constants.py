""" Module for commonly used constants
"""
DTYPES = [('date', '<i4'), ('burned', '<f8'), ('emission', '<f8'),
            ('productivity', '<f8'), ('net', '<f8'), ('unreleased', '<f8')]
DTYPES2 = [('date', '<i4'), ('burned', '<f8'), ('burnedUC', '<f8'),
            ('emission', '<f8'), ('emissionUC', '<f8'),
            ('productivity', '<f8'), ('productivityUC', '<f8'),
            ('net', '<f8'), ('netUC', '<f8'),
            ('unreleased', '<f8'), ('unreleasedUC', '<f8')]
SCALE_FACTOR = 0.47
PNAME = ['biomass', 'product', 'burned']
SPNAME = ['above', 'durable', 'fuel', 'pulp', 'burned']
FOREST = [2,4,5,19,20,9]
REGROW = [26,18]
SEB_CLASS = [2,4,5,9,18,19,20]
UNCLASSIFIED = 0
REGROW_BIOMASS = [0.0, 0]
FOREST_MIN = 35.0
FORCE_START = 2001001
FORCE_END = 2016001
TRACK_START = 2001001
TRACK_END = 2050001
TRANSITIONS = ['sec', 'for_pas', 'for_sec', 'sec_gain', 'sec_pas']
MAP_NODATA = -9999
MAX_YEAR = 3000
HEADER = 'date,burned,b_uc,emission,e_uc,productivity,p_uc,net,n_uc,unreleased,u_uc'
FMT = '%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f'
HEADER2 = 'date,burned,emission,productivity,net,unreleased'
FMT2 = '%d,%f,%f,%f,%f,%f'
AREA = 518131758 * 30 * 30 / 100 / 100
SAREA = 13755 * 30 * 30 / 100 / 100
SCALE_FACTOR2 = 1000 * 1000
DIY = 365.25
