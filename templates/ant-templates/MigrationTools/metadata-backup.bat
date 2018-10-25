set ANT_OPTS=-Xmx1024m
cd /d %~dp0
ant -f build.xml -propertyfile build.properties backup-metadata
pause