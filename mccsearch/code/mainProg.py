'''
# running the program
# Kim Whitehall Nov 2012
# Last updated: 15 May 2013
'''

#import rcmes
import sys
import networkx as nx
import mccSearch
#import cloudclusters
import numpy as np
import numpy.ma as ma
import files
import matplotlib.pyplot as plt
import subprocess


def main():
    CEGraph = nx.DiGraph()
    prunedGraph = nx.DiGraph()
    MCCList =[]
    MCSList=[]
    MCSMCCNodesList =[]
    allMCSsList =[]
    allCETRMMList =[]
    subprocess.call('export DISPLAY=:0.0', shell=True)

    mainDirStr= "/Users/kimwhitehall/Documents/HU/research/thesis/presentation/caseStudies/BFStudy1"
    #mainDirStr= "/home/whitehal/mccsearch/caseStudy2"
    #directories for the original data
    #TRMMdirName ="/home/whitehal/summer2006TRMM"
    #CEoriDirName = "/home/whitehal/17Jul30Sep/mergNETCDF" 
    TRMMdirName = "/Users/kimwhitehall/Documents/HU/research/DATA/TRMM" #compSciPaper/case2/TRMM"
    CEoriDirName = "/Users/kimwhitehall/Documents/HU/research/DATA/mergNETCDF"
    #allMCSsDict ={{}}

    # mccSearch.preprocessingMERG("/Users/kimwhitehall/Documents/HU/research/DATA")
    # sys.exit()

    # # mccSearch.plotAccTRMM(TRMMCEdirName)
    # sys.exit()

    #create main directory and file structure for storing intel
    mccSearch.createMainDirectory(mainDirStr)
    TRMMCEdirName = mainDirStr+'/TRMMnetcdfCEs'
    CEdirName = mainDirStr+'/MERGnetcdfCEs'

    # #mccSearch.postProcessingNetCDF(3,CEoriDirName)
    # mccSearch.postProcessingNetCDF(2)
    # sys.exit()

    #using merg data ***********
    print "\n -------------- Read MERG Data ----------"
    mergImgs, timeList = mccSearch.readMergData(CEoriDirName)
    print ("-"*80)

    print "\n -------------- TESTING findCloudElements ----------"
    CEGraph = mccSearch.findCloudElements(mergImgs,timeList,TRMMdirName)
    #if the TRMMdirName isnt entered for what ever reason
    # CEGraph = mccSearch.findCloudElements(mergImgs,timeList)
    # allCETRMMList=mccSearch.findPrecipRate(TRMMdirName,timeList)
    #sys.exit()
    print ("-"*80)
    print "number of nodes in CEGraph is: ", CEGraph.number_of_nodes()
    print ("-"*80)    
    print "\n -------------- TESTING findCloudClusters ----------"
    prunedGraph = mccSearch.findCloudClusters(CEGraph)
    print ("-"*80)
    print "number of nodes in prunedGraph is: ", prunedGraph.number_of_nodes()
    print ("-"*80)
    #sys.exit()
    print "\n -------------- TESTING findMCCs ----------"
    MCCList,MCSList = mccSearch.findMCC(prunedGraph)
    print ("-"*80)
    print "MCC List has been acquired ", len(MCCList)
    # for eachList in MCCList:
    #     print eachList
    #     for eachNode in eachList:
    #         print eachNode, mccSearch.thisDict(eachNode)['nodeMCSIdentifier']
    print "MCS List has been acquired ", len(MCSList)
    # for eachList in MCSList:
    #     print eachList
    #     for eachNode in eachList:
    #         print eachNode, mccSearch.thisDict(eachNode)['nodeMCSIdentifier']
    print ("-"*80)
    #sys.exit()
    print "\n -------------- TESTING TRMM ----------"
    #now ready to perform various calculations/metrics
    print "\n -------------- TESTING METRICS ----------"
    #MCCTimes, tdelta = mccSearch.temporalAndAreaInfoMetric(MCCList)
    print ("-"*80)
    #print "MCCTimes is: ", MCCTimes
    #mccSearch.plotAccTRMM(MCCList)
    # mccSearch.displayPrecip(MCCList)
    # mccSearch.plotAccuInTimeRange('2009-09-01_00:00:00', '2009-09-01_23:00:00')
    # mccSearch.displaySize(MCCList)
    # mccSearch.displayPrecip(MCCList)
    # mccSearch.plotHistogram(MCCList)
    print "creating the MCC userfile ", mccSearch.createTextFile(MCCList,1)
    print "creating the MCS userfile ", mccSearch.createTextFile(MCSList,2)

    # print "number of MCCs is: ", mccSearch.numberOfFeatures(MCCList)
    # print "longest duration is: ", mccSearch.longestDuration(MCCTimes), "hrs"
    # print "shortest duration is: ", mccSearch.shortestDuration(MCCTimes), "hrs"
    # #print "Average duration is: ", mccSearch.convert_timedelta(mccSearch.averageMCCLength(MCCTimes))
    # print "Average duration is: ", mccSearch.averageDuration(MCCTimes), "hrs"
    # print "Average size is: ", mccSearch.averageFeatureSize(MCCList), "km^2" 
    
    # #print "Average duration is: ", mccSearch.convert_timedelta(mccSearch.averageMCCLength(MCCTimes))
    # hist, bin_edges = mccSearch.commonFeatureSize(allMCSsList)
    # print "Histogram is ", hist, bin_edges
    # plt.bar(bin_edges[:-1], hist, width = 10)
    # plt.xlim(min(bin_edges), max(bin_edges))
    # plt.show()   

    #some plots that work
    # mccSearch.plotAccTRMM(MCCList)
    # mccSearch.displayPrecip(MCCList)
    # mccSearch.plotAccuInTimeRange('2009-09-01_00:00:00', '2009-09-01_23:00:00')
    # mccSearch.displaySize(MCCList)
    # mccSearch.displayPrecip(MCCList)
    # mccSearch.plotHistograms(MCCList)
    #sys.exit()
    #
    print ("-"*80)

    # allCETRMMList = mccSearch.precipTotals(MCCList) #allMCSsList)
    # print "********** findPrecipRate found"
    # allCETRMMList = mccSearch.findPrecipRate(CEdirName,TRMMdirName)
    # allCETRMMList = mccSearch.precipTotals(MCCList) #allMCSsList)
    
    # allCETRMMList = mccSearch.precipTotals(MCCList) #allMCSsList)
    # print ("-"*80)
    # print "allCETRMMList List has been aquired ", len(allCETRMMList), allCETRMMList
    # print ("-"*80)
    # # sys.exit()
    
main()