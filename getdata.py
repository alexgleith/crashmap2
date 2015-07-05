#!/usr/bin/python2.4
#
# Small script to show PostgreSQL and Pyscopg together
#

import psycopg2
import json

def dumpLocations(locations, outDir):
	outLocFolder = os.path.join(outDir,'locations.geojson')
	
	d = json.dumps(locationsJSON, sort_keys=True, indent=2)
	with open(outLocFolder, 'w') as outfile:
		outfile.write('getLocations(' + d + ');')
	print 'wrote locations to: ',outLocFolder

try:
    conn = psycopg2.connect("dbname='gisdb' host='localhost'")
except:
    print "I am unable to connect to the database"

query1 = """select gid,ST_AsGeoJSON(ST_Transform(geom,4326),6),count from crash_intersections"""
query2 = """select trans_node_id,c.crash_date,c.crash_time,c.dca,c.severity,c.light_cond,c.speed_zone,c.unit_type,ST_AsGeoJSON(ST_Transform(geom,4326),6) from tnod_crash_rel as r,crash c where r.crash_id = c.id_0"""

cur = conn.cursor()
cur2 = conn.cursor()
try:
    cur.execute(query1)
    cur2.execute(query2)
except:
    print "I can't SELECT from bar"

rows = cur.fetchall()
rows2 = cur2.fetchall()

locationsJSON = {}
locationsJSON['type'] = 'FeatureCollection'
features = []
count = 0
for row in rows:
	feature = {}
	feature['type'] = 'Feature'
	feature['geometry'] = json.loads(row[1])
	props = {}
	crashes = []
	gid = row[0]
	for crash in rows2:
		tid = crash[0]
		if(gid==tid):
			c = {}
			c['crash_date'] = str(crash[1])
			c['crash_time'] = str(crash[2])
			c['dca'] = str(crash[3])
			c['severity'] = str(crash[4])
			c['speed_zone'] = str(crash[6])
			c['unit_type'] = str(crash[7])
			c['location'] = json.loads(crash[8])
			crashes.append(c)

	props['ncrashes'] = len(crashes)

	count = count + 1
	props['crashes'] = crashes

	feature['properties'] = props
	features.append(feature)
locationsJSON['features'] = features


d = json.dumps(locationsJSON, sort_keys=True)
with open("/Users/alex/govhack2015/data.geojson", 'w') as outfile:
	outfile.write('getLocations(' + d + ');')



