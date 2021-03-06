from ROOT import *
import os,sys
import time
from array import array
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *

#================================================================================
#this macro does not do any analysis, just get plots for RawHistos and draw singal and background efficiency
#================================================================================
DY_pt100To250 = ['DYJetsToLL_Pt-100To250_01','DYJetsToLL_Pt-100To250_02','DYJetsToLL_Pt-100To250_03','DYJetsToLL_Pt-100To250_04','DYJetsToLL_Pt-100To250_05','DYJetsToLL_Pt-100To250_06','DYJetsToLL_Pt-100To250_07']
DY_pt250To400 = ['DYJetsToLL_Pt-250To400_01','DYJetsToLL_Pt-250To400_02','DYJetsToLL_Pt-250To400_03','DYJetsToLL_Pt-250To400_04','DYJetsToLL_Pt-250To400_05','DYJetsToLL_Pt-250To400_06','DYJetsToLL_Pt-250To400_07','DYJetsToLL_Pt-250To400_08','DYJetsToLL_Pt-250To400_09','DYJetsToLL_Pt-250To400_10','DYJetsToLL_Pt-250To400_11','DYJetsToLL_Pt-250To400_12','DYJetsToLL_Pt-250To400_13']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
DY_pt_400ToInf = ['DYJetsToLL_Pt-400To650','DYJetsToLL_Pt-650ToInf']
DYBJet = ['DYBJetsToLL_M-50_Zpt-100to200','DYBJetsToLL_M-50_Zpt-200toInf']
samples = DY_pt100To250+DY_pt250To400+DY_pt_400ToInf+['BulkGraviton_ggF_ZZ_ZlepZhad_narrow_M1000']
#samples = DY_pt100To250+DY_pt250To400+DY_pt_400ToInf+DYBJet
signal = 'GluGluHToZZTo2L2Q_M3000'
bkg = 'QCD'
var_names = ['ZvsQCD_de','tau21_DDT','particleNet_ZvsQCD_de']
#var_names = ['ZbbvsZlight_de','particleNet_Zbbvslight_de']

PH = plotHelper(samples,'2018Legacy') #initialize plot

#book ROOT file storing raw histos
files={}
for sample in samples:
    files[sample] = TFile("../RawHistos/%s_particleNetDeepTau.root"%sample)

#book histos and efficiency
histos={}
efficiency={}
efficiency['SIG']={}
efficiency['BKG']={}
for sample in samples:
    histos[sample]={}
    for var_name in var_names:
        #histos[sample][var_name] = TH1D()
        histos[sample][var_name] = files[sample].Get(sample+"_"+var_name)
for var_name in var_names:
    efficiency['SIG'][var_name] = array('f',[])
    efficiency['BKG'][var_name] = array('f',[])


histosBKG = {}
histosSIG = {}
for var_name in var_names:
    histosBKG[var_name] = TH1D('bkg'+var_name,'bkg'+var_name,100,0,1)
    histosSIG[var_name] = TH1D('SIG'+var_name,'SIG'+var_name,100,0,1)
    histosBKG[var_name].Sumw2()
    histosSIG[var_name].Sumw2()
    for sample in samples:
        if(sample.find('DYJets')!=-1):
        #if(sample.find('DYJets')!=-1 or sample.find('DYBJets')!=-1):
            histosBKG[var_name].Add(histos[sample][var_name])
            print "[INFO] add bkg: "+sample
        else:
            histosSIG[var_name].Add(histos[sample][var_name])
            print "[INFO] add singal: "+sample

#substract BJets for all jets
#for var_name in var_names:
#    for sample in samples:
#        if(sample.find('DYBJet')!=-1):
#            histosBKG[var_name].Add(histos[sample][var_name],-1)
#            print "[INFO] reduce DYBJets: "+sample

#start to caculate efficiency in each setted cut
for i in range(0,100):
    cut = Double(i)/100
    for var_name in var_names:
        binx1 = histosSIG[var_name].GetXaxis().FindBin(cut)
        binx2 = histosSIG[var_name].GetXaxis().FindBin(1)

        temp_numerator = histosSIG[var_name].Integral(binx1,binx2)
        temp_denominator = histosSIG[var_name].Integral()
        temp_efficiency = temp_numerator/temp_denominator

        if(var_name=='tau21' or var_name =='tau21_DDT'):
            efficiency['SIG'][var_name].append(1-temp_efficiency)
        else:
            efficiency['SIG'][var_name].append(temp_efficiency)

        temp_numerator = histosBKG[var_name].Integral(binx1,binx2)
        temp_denominator = histosBKG[var_name].Integral()
        temp_efficiency = temp_numerator/temp_denominator

        if(var_name=='tau21' or var_name =='tau21_DDT'):
            efficiency['BKG'][var_name].append(1-temp_efficiency)
        else:
            efficiency['BKG'][var_name].append(temp_efficiency)





#for sample in samples:
#    for var_name in var_names:
#        efficiency[sample][var_name].sort()

vector_X = {} #for singal
vector_Y ={}  #for backgrounds
graph = {}
for var_name in var_names:
    vector_X[var_name] = efficiency['SIG'][var_name]
    vector_Y[var_name] = efficiency['BKG'][var_name]

    graph[var_name] = TGraph( len(vector_X[var_name]) , vector_X[var_name] , vector_Y[var_name] )


graphs = TMultiGraph()
#graphs.SetLogy()
for var_name in var_names:
    graphs.Add(graph[var_name])

    #graph['ZvsQCD'].SetLineColor(kRed)
    #graph['ZvsQCD'].SetTitle("ZvsQCD")

    graph['ZvsQCD_de'].SetLineColor(kRed)
    graph['ZvsQCD_de'].SetTitle("ZvsQCD_decorrelated")
    graph['ZvsQCD_de'].SetLineStyle(2)

    #graph['ZbbvsQCD_de'].SetLineColor(kGreen)
    #graph['ZbbvsQCD_de'].SetTitle("ZbbvsQCD_decorrelated")
    #graph['ZbbvsQCD_de'].SetLineStyle(2)

    #graph['ZbbvsZlight_de'].SetLineColor(kRed)
    #graph['ZbbvsZlight_de'].SetTitle("ZvsQCD_decorrelated")
    #graph['ZbbvsZlight_de'].SetLineStyle(2)

    #graph['WvsQCD'].SetLineColor(kBlue)
    #graph['WvsQCD'].SetTitle("WvsQCD")

    #graph['WvsQCD_de'].SetLineColor(kBlue)
    #graph['WvsQCD_de'].SetLineStyle(2)
    #graph['WvsQCD_de'].SetTitle("WvsQCD_decorrelated")

    #graph['tau21'].SetLineColor(kBlack)
    #graph['tau21'].SetTitle("tau21")

    graph['tau21_DDT'].SetLineColor(kBlack)
    graph['tau21_DDT'].SetTitle("tau21_DDT")
    graph['tau21_DDT'].SetLineStyle(2)

    graph['particleNet_ZvsQCD_de'].SetLineColor(kBlue)
    graph['particleNet_ZvsQCD_de'].SetTitle("particleNet_ZvsQCD_de")
    graph['particleNet_ZvsQCD_de'].SetLineStyle(2)

    #graph['particleNet_Zbbvslight_de'].SetLineColor(kYellow)
    #graph['particleNet_Zbbvslight_de'].SetTitle("particleNet_ZvsQCD_de")
    #graph['particleNet_Zbbvslight_de'].SetLineStyle(2)


graphs.GetXaxis().SetTitle("Signal efficiency")
graphs.GetYaxis().SetTitle("Background efficiency")

c = TCanvas('efficiency','efficiency',700,700)
graphs.Draw("AC")

leg = PH.MakeLegend('left')
#leg.AddEntry(graph['ZvsQCD'], 'ZvsQCD')
#leg.AddEntry(graph['tau21'], 'tau21')
#leg.AddEntry(graph['WvsQCD'], 'WvsQCD')
#leg.AddEntry(graph['WvsQCD_de'], 'WvsQCD_decorrelated')
leg.AddEntry(graph['ZvsQCD_de'], 'ZvsQCD_decorrelated')
#eg.AddEntry(graph['ZbbvsQCD_de'], 'ZbbvsQCD_decorrelated')
leg.AddEntry(graph['tau21_DDT'], 'tau21_DDT')
leg.AddEntry(graph['particleNet_ZvsQCD_de'],'particleNet_decorrelated')
#leg.AddEntry(graph['ZbbvsZlight_de'], 'Zbbvslight_decorrelated')
#leg.AddEntry(graph['particleNet_Zbbvslight_de'],'particleNet_Zbbvslightdecorrelated')
leg.Draw()


savename = "../plot/efficiency"
PH.SavePlots(c,savename)
