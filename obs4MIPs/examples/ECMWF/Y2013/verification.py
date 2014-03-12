#!/usr/bin/env python

from ecmwfapi import ECMWFDataServer

# To run this example, you need an API key 
# available from https://api.ecmwf.int/v1/key/

server = ECMWFDataServer()

server.retrieve({ 
"levelist"    :   "1/2/3/5/7/10/20/30/50/70/100/125/150/175/200/225/250/300/350/400/450/500/550/600/650/700/750/775/800/825/850/875/900/925/950/975/1000",
"stream"      :   "moda",
"levtype"     :   "pl",
"param"       :   "129.128/130.128/131.128/132.128/133.128/135.128/138.128/155.128/157.128/203.128/246.128/247.128/248.128/60.128",
"dataset"     :   "interim",
"grid"        :   "0.75/0.75",
"date"        :   "20130101/20130201/20130301/20130401/20130501/20130601/20130701/20130801/20130901/20131001/20131101/20131201",
"target"      :   "ecint_prs_2013.nc",
"class"       :   "ei",
"format"      :   "netcdf",
"type"        :   "an"
})

