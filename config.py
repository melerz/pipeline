{
	data = {
		"name":"michal-80",
		#"illumina":"http://132.65.52.13:8080/illuminaapi/illumina/141113_NS500183_0047_AH19CRBGXX/",
		"csv":"michal-80",
		"job_id":"1",
		"illumina_name":"141113_NS500183_0047_AH19CRBGXX",
		"url":"manual-job-1-michal-80",
		"configuration":{
			"1":{"NumCycles":"75","IsIndexedRead":"N"},

			"2":{"NumCycles":"8","IsIndexedRead":"Y"},
			
			"3":{"NumCycles":"8","IsIndexedRead":"Y"}
		}
	}

	workflows = {
		"bcl_to_genome_browser":{	
			"pipeline":[
				'bcl_to_fastq.py',
				'fastq_to_bam.py',
				'bam_to_bigwig.py'
			]
		},
		"fastq_only":{
			"pipeline":[
				'bcl_to_fastq.py'
			]
		
		}
	}

	settings ={
		
		
	}
	
}
