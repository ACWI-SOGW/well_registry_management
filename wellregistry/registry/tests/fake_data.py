# pylint: skip-file

import io

TEST_RDB = b'#\n\
#\n\
# US Geological Survey\n\
# retrieved: 2020-09-15 16:44:45 -04:00	(sdas01)\n\
#\n\
# The Site File stores location and general information about groundwater,\n\
# surface water, and meteorological sites\n\
# for sites in USA.\n\
#\n\
# File-format description:  http://help.waterdata.usgs.gov/faq/about-tab-delimited-output\n\
# Automated-retrieval info: http://waterservices.usgs.gov/rest/Site-Service.html\n\
#\n\
# Contact:   gs-w_support_nwisweb@usgs.gov\n\
#\n\
# The following selected fields are included in this output:\n\
#\n\
#  agency_cd       -- Agency\n\
#  site_no         -- Site identification number\n\
#  station_nm      -- Site name\n\
#  site_tp_cd      -- Site type\n\
#  lat_va          -- DMS latitude\n\
#  long_va         -- DMS longitude\n\
#  dec_lat_va      -- Decimal latitude\n\
#  dec_long_va     -- Decimal longitude\n\
#  coord_meth_cd   -- Latitude-longitude method\n\
#  coord_acy_cd    -- Latitude-longitude accuracy\n\
#  coord_datum_cd  -- Latitude-longitude datum\n\
#  dec_coord_datum_cd -- Decimal Latitude-longitude datum\n\
#  district_cd     -- District code\n\
#  state_cd        -- State code\n\
#  county_cd       -- County code\n\
#  country_cd      -- Country code\n\
#  land_net_ds     -- Land net location description\n\
#  map_nm          -- Name of location map\n\
#  map_scale_fc    -- Scale of location map\n\
#  alt_va          -- Altitude of Gage/land surface\n\
#  alt_meth_cd     -- Method altitude determined\n\
#  alt_acy_va      -- Altitude accuracy\n\
#  alt_datum_cd    -- Altitude datum\n\
#  huc_cd          -- Hydrologic unit code\n\
#  basin_cd        -- Drainage basin code\n\
#  topo_cd         -- Topographic setting code\n\
#  instruments_cd  -- Flags for instruments at site\n\
#  construction_dt -- Date of first construction\n\
#  inventory_dt    -- Date site established or inventoried\n\
#  drain_area_va   -- Drainage area\n\
#  contrib_drain_area_va -- Contributing drainage area\n\
#  tz_cd           -- Time Zone abbreviation\n\
#  local_time_fg   -- Site honors Daylight Savings Time\n\
#  reliability_cd  -- Data reliability code\n\
#  gw_file_cd      -- Data-other GW files\n\
#  nat_aqfr_cd     -- National aquifer code\n\
#  aqfr_cd         -- Local aquifer code\n\
#  aqfr_type_cd    -- Local aquifer type code\n\
#  well_depth_va   -- Well depth\n\
#  hole_depth_va   -- Hole depth\n\
#  depth_src_cd    -- Source of depth data\n\
#  project_no      -- Project number\n\
#\n\
agency_cd	site_no	station_nm	site_tp_cd	lat_va	long_va	dec_lat_va	dec_long_va	coord_meth_cd	coord_acy_cd	coord_datum_cd	dec_coord_datum_cd	district_cd	state_cd	county_cd	country_cd	land_net_ds	map_nm	map_scale_fc	alt_va	alt_meth_cd	alt_acy_va	alt_datum_cd	huc_cd	basin_cd	topo_cd	instruments_cd	construction_dt	inventory_dt	drain_area_va	contrib_drain_area_va	tz_cd	local_time_fg	reliability_cd	gw_file_cd	nat_aqfr_cd	aqfr_cd	aqfr_type_cd	well_depth_va	hole_depth_va	depth_src_cd	project_no\n\
5s	15s	50s	7s	16s	16s	16s	16s	1s	1s	10s	10s	3s	2s	3s	2s	23s	20s	7s	8s	1s	3s	10s	16s	2s	1s	30s	8s	8s	8s	8s	6s	1s	1s	30s	10s	8s	1s	8s	8s	1s	12s\n\
USGS	443053094591001	LS-502    112N34W07CCCCBD01 LS-O01, recorder, LSIC	GW	443053.32	0945910.21	44.5148111	-94.9861694	D	H	NAD27	NAD27	26	26	123	US	SWSWSWS07 T112N R24W	MORTON, MINN.	  24000	 972.47	D	.03	NAD83	07020007		F	YNNYNNNNNNNYNYNNYNNNNNNNNNNNNN	20061206	20061206			CST	Y	C	YY Y Y	N100GLCIAL	348FILR	C	1070	120	S	MN-0022'

TEST_STREAM_RDB = b'#\n\
#\n\
# US Geological Survey\n\
# retrieved: 2020-09-15 16:44:45 -04:00	(sdas01)\n\
#\n\
# The Site File stores location and general information about groundwater,\n\
# surface water, and meteorological sites\n\
# for sites in USA.\n\
#\n\
# File-format description:  http://help.waterdata.usgs.gov/faq/about-tab-delimited-output\n\
# Automated-retrieval info: http://waterservices.usgs.gov/rest/Site-Service.html\n\
#\n\
# Contact:   gs-w_support_nwisweb@usgs.gov\n\
#\n\
# The following selected fields are included in this output:\n\
#\n\
#  agency_cd       -- Agency\n\
#  site_no         -- Site identification number\n\
#  station_nm      -- Site name\n\
#  site_tp_cd      -- Site type\n\
#  lat_va          -- DMS latitude\n\
#  long_va         -- DMS longitude\n\
#  dec_lat_va      -- Decimal latitude\n\
#  dec_long_va     -- Decimal longitude\n\
#  coord_meth_cd   -- Latitude-longitude method\n\
#  coord_acy_cd    -- Latitude-longitude accuracy\n\
#  coord_datum_cd  -- Latitude-longitude datum\n\
#  dec_coord_datum_cd -- Decimal Latitude-longitude datum\n\
#  district_cd     -- District code\n\
#  state_cd        -- State code\n\
#  county_cd       -- County code\n\
#  country_cd      -- Country code\n\
#  land_net_ds     -- Land net location description\n\
#  map_nm          -- Name of location map\n\
#  map_scale_fc    -- Scale of location map\n\
#  alt_va          -- Altitude of Gage/land surface\n\
#  alt_meth_cd     -- Method altitude determined\n\
#  alt_acy_va      -- Altitude accuracy\n\
#  alt_datum_cd    -- Altitude datum\n\
#  huc_cd          -- Hydrologic unit code\n\
#  basin_cd        -- Drainage basin code\n\
#  topo_cd         -- Topographic setting code\n\
#  instruments_cd  -- Flags for instruments at site\n\
#  construction_dt -- Date of first construction\n\
#  inventory_dt    -- Date site established or inventoried\n\
#  drain_area_va   -- Drainage area\n\
#  contrib_drain_area_va -- Contributing drainage area\n\
#  tz_cd           -- Time Zone abbreviation\n\
#  local_time_fg   -- Site honors Daylight Savings Time\n\
#  reliability_cd  -- Data reliability code\n\
#  gw_file_cd      -- Data-other GW files\n\
#  nat_aqfr_cd     -- National aquifer code\n\
#  aqfr_cd         -- Local aquifer code\n\
#  aqfr_type_cd    -- Local aquifer type code\n\
#  well_depth_va   -- Well depth\n\
#  hole_depth_va   -- Hole depth\n\
#  depth_src_cd    -- Source of depth data\n\
#  project_no      -- Project number\n\
#\n\
agency_cd	site_no	station_nm	site_tp_cd	lat_va	long_va	dec_lat_va	dec_long_va	coord_meth_cd	coord_acy_cd	coord_datum_cd	dec_coord_datum_cd	district_cd	state_cd	county_cd	country_cd	land_net_ds	map_nm	map_scale_fc	alt_va	alt_meth_cd	alt_acy_va	alt_datum_cd	huc_cd	basin_cd	topo_cd	instruments_cd	construction_dt	inventory_dt	drain_area_va	contrib_drain_area_va	tz_cd	local_time_fg	reliability_cd	gw_file_cd	nat_aqfr_cd	aqfr_cd	aqfr_type_cd	well_depth_va	hole_depth_va	depth_src_cd	project_no\n\
5s	15s	50s	7s	16s	16s	16s	16s	1s	1s	10s	10s	3s	2s	3s	2s	23s	20s	7s	8s	1s	3s	10s	16s	2s	1s	30s	8s	8s	8s	8s	6s	1s	1s	30s	10s	8s	1s	8s	8s	1s	12s\n\
USGS	543053094591001	LS-502    112N34W07CCCCBD01 LS-O01, recorder, LSIC	ST	443053.32	0945910.21	44.5148111	-94.9861694	D	H	NAD27	NAD27	26	26	123	US	SWSWSWS07 T112N R24W	MORTON, MINN.	  24000	 972.47	D	.03	NAD83	07020007		F	YNNYNNNNNNNYNYNNYNNNNNNNNNNNNN	20061206	20061206			CST	Y	C	YY Y Y	N100GLCIAL	348FILR	C	107	120	S	MN-0022'

TEST_NO_WELL_DEPTH_RDB = b'#\n\
#\n\
# US Geological Survey\n\
# retrieved: 2020-09-15 16:44:45 -04:00	(sdas01)\n\
#\n\
# The Site File stores location and general information about groundwater,\n\
# surface water, and meteorological sites\n\
# for sites in USA.\n\
#\n\
# File-format description:  http://help.waterdata.usgs.gov/faq/about-tab-delimited-output\n\
# Automated-retrieval info: http://waterservices.usgs.gov/rest/Site-Service.html\n\
#\n\
# Contact:   gs-w_support_nwisweb@usgs.gov\n\
#\n\
# The following selected fields are included in this output:\n\
#\n\
#  agency_cd       -- Agency\n\
#  site_no         -- Site identification number\n\
#  station_nm      -- Site name\n\
#  site_tp_cd      -- Site type\n\
#  lat_va          -- DMS latitude\n\
#  long_va         -- DMS longitude\n\
#  dec_lat_va      -- Decimal latitude\n\
#  dec_long_va     -- Decimal longitude\n\
#  coord_meth_cd   -- Latitude-longitude method\n\
#  coord_acy_cd    -- Latitude-longitude accuracy\n\
#  coord_datum_cd  -- Latitude-longitude datum\n\
#  dec_coord_datum_cd -- Decimal Latitude-longitude datum\n\
#  district_cd     -- District code\n\
#  state_cd        -- State code\n\
#  county_cd       -- County code\n\
#  country_cd      -- Country code\n\
#  land_net_ds     -- Land net location description\n\
#  map_nm          -- Name of location map\n\
#  map_scale_fc    -- Scale of location map\n\
#  alt_va          -- Altitude of Gage/land surface\n\
#  alt_meth_cd     -- Method altitude determined\n\
#  alt_acy_va      -- Altitude accuracy\n\
#  alt_datum_cd    -- Altitude datum\n\
#  huc_cd          -- Hydrologic unit code\n\
#  basin_cd        -- Drainage basin code\n\
#  topo_cd         -- Topographic setting code\n\
#  instruments_cd  -- Flags for instruments at site\n\
#  construction_dt -- Date of first construction\n\
#  inventory_dt    -- Date site established or inventoried\n\
#  drain_area_va   -- Drainage area\n\
#  contrib_drain_area_va -- Contributing drainage area\n\
#  tz_cd           -- Time Zone abbreviation\n\
#  local_time_fg   -- Site honors Daylight Savings Time\n\
#  reliability_cd  -- Data reliability code\n\
#  gw_file_cd      -- Data-other GW files\n\
#  nat_aqfr_cd     -- National aquifer code\n\
#  aqfr_cd         -- Local aquifer code\n\
#  aqfr_type_cd    -- Local aquifer type code\n\
#  well_depth_va   -- Well depth\n\
#  hole_depth_va   -- Hole depth\n\
#  depth_src_cd    -- Source of depth data\n\
#  project_no      -- Project number\n\
#\n\
agency_cd	site_no	station_nm	site_tp_cd	lat_va	long_va	dec_lat_va	dec_long_va	coord_meth_cd	coord_acy_cd	coord_datum_cd	dec_coord_datum_cd	district_cd	state_cd	county_cd	country_cd	land_net_ds	map_nm	map_scale_fc	alt_va	alt_meth_cd	alt_acy_va	alt_datum_cd	huc_cd	basin_cd	topo_cd	instruments_cd	construction_dt	inventory_dt	drain_area_va	contrib_drain_area_va	tz_cd	local_time_fg	reliability_cd	gw_file_cd	nat_aqfr_cd	aqfr_cd	aqfr_type_cd	well_depth_va	hole_depth_va	depth_src_cd	project_no\n\
5s	15s	50s	7s	16s	16s	16s	16s	1s	1s	10s	10s	3s	2s	3s	2s	23s	20s	7s	8s	1s	3s	10s	16s	2s	1s	30s	8s	8s	8s	8s	6s	1s	1s	30s	10s	8s	1s	8s	8s	1s	12s\n\
USGS	643053094591001	LS-502    112N34W07CCCCBD01 LS-O01, recorder, LSIC	GW	443053.32	0945910.21	44.5148111	-94.9861694	D	H	NAD27	NAD27	26	26	123	US	SWSWSWS07 T112N R24W	MORTON, MINN.	  24000	 972.47	D	.03	NAD83	07020007		F	YNNYNNNNNNNYNYNNYNNNNNNNNNNNNN	20061206	20061206			CST	Y	C	YY Y Y	N100GLCIAL	348FILR	C		120	S	MN-0022'
