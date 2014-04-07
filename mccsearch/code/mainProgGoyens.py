'''
# running the program
# Kim Whitehall Nov 2012
# Last updated: 15 May 2013
'''

#import rcmes
import sys
import networkx as nx
import mccSearchGoyens
#import cloudclusters
import numpy as np
import numpy.ma as ma
import files
import matplotlib.pyplot as plt

def main():
    CEGraph = nx.DiGraph()
    prunedGraph = nx.DiGraph()
    MCCList =[]
    MCSList=[]
    MCSMCCNodesList =[]
    allMCSsList =[]
    allCETRMMList =[]
    mainDirStr= "/Users/kimwhitehall/Documents/HU/research/mccSearchGoyens/caseStudy1"
    #directories for the original data
    TRMMdirName = "/Users/kimwhitehall/Documents/HU/research/DATA/TRMM" #compSciPaper/case2/TRMM"
    CEoriDirName = "/Users/kimwhitehall/Documents/HU/research/DATA/mergNETCDF"
    #allMCSsDict ={{}}

    # mccSearchGoyens.preprocessingMERG("/Users/kimwhitehall/Documents/HU/research/DATA")
    # sys.exit()

    # # mccSearchGoyens.plotAccTRMM(TRMMCEdirName)
    # sys.exit()

    #create main directory and file structure for storing intel
    mccSearchGoyens.createMainDirectory(mainDirStr)
    TRMMCEdirName = mainDirStr+'/TRMMnetcdfCEs'
    CEdirName = mainDirStr+'/MERGnetcdfCEs'

    # #mccSearchGoyens.postProcessingNetCDF(3,CEoriDirName)
    # mccSearchGoyens.postProcessingNetCDF(2)
    # sys.exit()

    #using merg data ***********
    print "\n -------------- Read MERG Data ----------"
    mergImgs, timeList = mccSearchGoyens.readMergData(CEoriDirName)
    print ("-"*80)

    print 'in main', len(mergImgs)
    print "\n -------------- TESTING findCloudElements ----------"
    CEGraph = mccSearchGoyens.findCloudElements(mergImgs,timeList,TRMMdirName)
    #if the TRMMdirName isnt entered for what ever reason
    # CEGraph = mccSearchGoyens.findCloudElements(mergImgs,timeList)
    # allCETRMMList=mccSearchGoyens.findPrecipRate(TRMMdirName)
    # sys.exit()
    print ("-"*80)
    print "number of nodes in CEGraph is: ", CEGraph.number_of_nodes()
    print ("-"*80)    
    print "\n -------------- TESTING findCloudClusters ----------"
    prunedGraph = mccSearchGoyens.findCloudClusters(CEGraph)
    print ("-"*80)
    print "number of nodes in prunedGraph is: ", prunedGraph.number_of_nodes()
    print ("-"*80)
    #sys.exit()
    print "\n -------------- TESTING findMCCs ----------"
    MCCList,MCSList = mccSearchGoyens.findMCC(prunedGraph)
    print ("-"*80)
    print "MCC List has been acquired ", len(MCCList)
    # for eachList in MCCList:
    #     print eachList
    #     for eachNode in eachList:
    #         print eachNode, mccSearchGoyens.thisDict(eachNode)['nodeMCSIdentifier']
    print "MCS List has been acquired ", len(MCSList)
    # for eachList in MCSList:
    #     print eachList
    #     for eachNode in eachList:
    #         print eachNode, mccSearchGoyens.thisDict(eachNode)['nodeMCSIdentifier']
    print ("-"*80)
    #sys.exit()
    print "\n -------------- TESTING TRMM ----------"
    #now ready to perform various calculations/metrics
    print "\n -------------- TESTING METRICS ----------"
    #MCCTimes, tdelta = mccSearchGoyens.temporalAndAreaInfoMetric(MCCList)
    print ("-"*80)
    #print "MCCTimes is: ", MCCTimes
    print "creating the MCS userfile ", mccSearchGoyens.createTextFile(MCCList)

    # print "number of MCCs is: ", mccSearchGoyens.numberOfFeatures(MCCList)
    # print "longest duration is: ", mccSearchGoyens.longestDuration(MCCTimes), "hrs"
    # print "shortest duration is: ", mccSearchGoyens.shortestDuration(MCCTimes), "hrs"
    # #print "Average duration is: ", mccSearchGoyens.convert_timedelta(mccSearchGoyens.averageMCCLength(MCCTimes))
    # print "Average duration is: ", mccSearchGoyens.averageDuration(MCCTimes), "hrs"
    # print "Average size is: ", mccSearchGoyens.averageFeatureSize(MCCList), "km^2" 
    
    # #print "Average duration is: ", mccSearchGoyens.convert_timedelta(mccSearchGoyens.averageMCCLength(MCCTimes))
    # hist, bin_edges = mccSearchGoyens.commonFeatureSize(allMCSsList)
    # print "Histogram is ", hist, bin_edges
    # plt.bar(bin_edges[:-1], hist, width = 10)
    # plt.xlim(min(bin_edges), max(bin_edges))
    # plt.show()   

    #some plots that work
    # mccSearchGoyens.plotAccTRMM(MCCList)
    # mccSearchGoyens.displayPrecip(MCCList)
    # mccSearchGoyens.plotAccuInTimeRange('2009-09-01_00:00:00', '2009-09-01_23:00:00')
    # mccSearchGoyens.displaySize(MCCList)
    # mccSearchGoyens.displayPrecip(MCCList)
    # mccSearchGoyens.plotHistograms(MCCList)
    #sys.exit()
    #
    print ("-"*80)

    # allCETRMMList = mccSearchGoyens.precipTotals(MCCList) #allMCSsList)
    # print "********** findPrecipRate found"
    # allCETRMMList = mccSearchGoyens.findPrecipRate(CEdirName,TRMMdirName)
    # allCETRMMList = mccSearchGoyens.precipTotals(MCCList) #allMCSsList)
    
    # allCETRMMList = mccSearchGoyens.precipTotals(MCCList) #allMCSsList)
    # print ("-"*80)
    # print "allCETRMMList List has been aquired ", len(allCETRMMList), allCETRMMList
    # print ("-"*80)
    # # sys.exit()
    
main()