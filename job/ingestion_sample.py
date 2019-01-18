from al2_commands.v3 import RegisterImpala, SparkScript, ImpalaQuery, TextToParquet, ShellCommand
from al2 import task
from al2.lib import hdfs
import collections

def DoTasks():

	genprefix = "${VERSION}_"

	filesets = collections.OrderedDict()
	filesets['pas']  =  {'sourcepattern':'ProjectID.*Company_PAS_TEST_201810.txt', 'delimiter': '|'}

	for filekey, filedata in filesets.items():
		task.run('Unify ' + filekey, TextToParquet,
			 {
			  'source': '/client/citz/projectid/raw/staged/pas_test',
			  'dest': '/client/citz/projectid/raw/staged/pas_test/processed',
			  'partitioncol': filedata['partitioncol'], 
			  'has_header': 'true',
			  'infer_schema' :'true',
			  'schema': '',
			  'delimiter': filedata['delimiter']})

		### register staged parquet in impala
		task.run('Register pas_test', RegisterImpala,
				 {'db': 'projectdb', 'source': '/client/citz/projectid/raw/staged/pas_test/processed/ProjectID.143253.xxx.Company_PAS_TEST_201810.txt',
				  'tablename': 'v201810_pas_test_staged', 'partitioncol': filedata['partitioncol']})
