set ANT_OPTS=-Xmx1024m
ant -f build.xml -propertyfile build.properties backup-metadata
pause