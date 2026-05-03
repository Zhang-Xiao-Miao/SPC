# Modern External Slice Sampling

- Dataset: `BigCodeBench-Hard v0.1.4`
- Slice size: `50`
- Selection rule: keep tasks whose declared dependency roots are importable in the current environment; then take the first compatible tasks in dataset order.
- Retrieval support pool: `MBPP train`
- Caveat: this is a compatibility-filtered slice, not a random sample of the full benchmark.

| Task | Dependency Roots | Retrieved Support |
| --- | --- | --- |
| bigcodebench_13 | subprocess,ftplib,os | 700 |
| bigcodebench_15 | subprocess,csv,os | 886 |
| bigcodebench_17 | psutil,subprocess,time | 737 |
| bigcodebench_19 | glob,zipfile,os | 942 |
| bigcodebench_120 | pandas,datetime,random | 643 |
| bigcodebench_123 | glob,pandas,os | 649 |
| bigcodebench_147 | threading,socket,ipaddress | 904 |
| bigcodebench_161 | pandas,datetime,re | 971 |
| bigcodebench_184 | pandas,re,sklearn | 776 |
| bigcodebench_211 | zipfile,requests,os | 886 |
| bigcodebench_287 | json,collections,os | 858 |
| bigcodebench_308 | statistics,pandas,random | 649 |
| bigcodebench_310 | statistics,csv,random,os | 886 |
| bigcodebench_313 | shutil,datetime,re,os | 614 |
| bigcodebench_324 | subprocess,threading,time | 611 |
| bigcodebench_326 | glob,subprocess,os,sys | 780 |
| bigcodebench_346 | subprocess,time,os,sys | 804 |
| bigcodebench_368 | shutil,random,os | 922 |
| bigcodebench_409 | pandas,numpy,os | 717 |
| bigcodebench_424 | sklearn,numpy,cv2,os | 695 |
| bigcodebench_454 | glob,shutil,os | 737 |
| bigcodebench_458 | pandas,re,json | 737 |
| bigcodebench_461 | subprocess,psutil,os,time | 703 |
| bigcodebench_486 | pandas,datetime,numpy | 663 |
| bigcodebench_492 | pandas,datetime,random | 922 |
| bigcodebench_503 | pandas,datetime,numpy | 700 |
| bigcodebench_509 | difflib,pandas,csv | 689 |
| bigcodebench_526 | pandas,collections,numpy,json | 896 |
| bigcodebench_592 | csv,datetime,random,os | 886 |
| bigcodebench_594 | shutil,random,os,csv,datetime | 886 |
| bigcodebench_678 | pandas,shutil,json,os | 886 |
| bigcodebench_720 | csv,datetime,random,os | 886 |
| bigcodebench_752 | pandas,numpy,sklearn | 737 |
| bigcodebench_760 | pandas,numpy,codecs,re,datetime | 883 |
| bigcodebench_763 | collections,csv,numpy,json | 886 |
| bigcodebench_765 | shutil,pathlib,os | 886 |
| bigcodebench_771 | csv,pathlib,re,os | 896 |
| bigcodebench_777 | zipfile,re,os | 607 |
| bigcodebench_785 | subprocess,glob,os | 886 |
| bigcodebench_800 | csv,collections,os | 858 |
| bigcodebench_826 | shutil,re,os | 971 |
| bigcodebench_854 | math,itertools,functools | 886 |
| bigcodebench_857 | glob,warnings,time,shutil,os | 886 |
| bigcodebench_865 | pandas,numpy,scipy,sklearn | 946 |
| bigcodebench_870 | pandas,numpy,itertools | 896 |
| bigcodebench_879 | pandas,numpy,scipy | 663 |
| bigcodebench_906 | re,shutil,zipfile,os | 772 |
| bigcodebench_928 | collections,itertools,string | 737 |
| bigcodebench_945 | pandas,numpy,sklearn | 922 |
| bigcodebench_952 | pandas,datetime,random | 971 |
