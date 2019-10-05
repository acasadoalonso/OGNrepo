#!/bin/bash
server="UBUNTU"
cd /nfs/OGN/DIRdata
mv SARgetogn.log log/SARgetogn$(date +%y%m).log
mv SARerr.log    log/SARerr$(date    +%y%m).log
sqlite3 SAROGN.db "delete from receivers where idrec like 'FNB%'; " 
sqlite3 SAROGN.db "delete from receivers where idrec like 'XCG%'; " 
sqlite3 SAROGN.db "delete from receivers where idrec like 'XCG%'; " 
sqlite3 SAROGN.db "delete from receivers where idrec like 'BSKY%'; " 
sqlite3 SAROGN.db "vacuum;"
rm        db/SAROGN.BKUP.db
cp SAROGN.db db/SAROGN.BKUP.db
echo "delete from RECEIVERS where idrec like 'FNB%';"  |  mysql --login-path=SARogn -h $server OGNDB 		2>/dev/null
echo "delete from RECEIVERS where idrec like 'XCG%';"  |  mysql --login-path=SARogn -h $server OGNDB 		2>/dev/null
echo "delete from RECEIVERS where idrec like 'XCG%';"  |  mysql --login-path=SARogn -h $server OGNDB 		2>/dev/null
echo "delete from RECEIVERS where idrec like 'BSKY%';" |  mysql --login-path=SARogn -h $server OGNDB 		2>/dev/null
cd  log
mv *$(date +%y)*.log Y$(date +%y) 
bash ./compress.sh   Y$(date +%y) 
cd
