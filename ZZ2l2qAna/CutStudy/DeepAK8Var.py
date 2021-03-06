from ROOT import *
import os,sys
import time
import math
sys.path.append("%s/../lib" %os.getcwd())
from deltaR import *
from plotHelper import *


samples = ['GluGluHToZZTo2L2Q_MAll','QCD']#'GluGluHToZZTo2L2Q_M1500','GluGluHToZZTo2L2Q_M2000','GluGluHToZZTo2L2Q_M2500','GluGluHToZZTo2L2Q_M3000'] #['ZZ','DYJets','WZ',
var_names = ['ZvsQCD','tau21','tau1','tau2','WvsQCD','ZvsQCD_de','WvsQCD_de','tau21_DDT']
var_tau1 = ['tau1_notZero_mass','tau1_notZero_SDmass','tau1_notZero_pt','tau1_notZero_eta','Z1_mass']
pt_bins = [200,600,1000,1400,1800,2200,2600,3000]
n_pt_bins = 8
PH = plotHelper(samples,2018) #initialize a plot class

#book out file to store raw histograms
outfilename = "../RawHistos/DeepAK8VarAll.root"
outfile = TFile(outfilename,"recreate")

#book histos
histos = {}
for sample in samples:
    histos[sample]={}
    histos[sample]['tau1_notZero_pt']={}
    histos[sample]['tau1_notZero_eta']={}
    histos[sample]['tau1_notZero_SDmass']={}
    histos[sample]['tau1_notZero_mass']={}
    histos[sample]['Z1_mass']={}
    for i_pt_bin in range(n_pt_bins-1):

        histos[sample]['tau1_notZero_pt'][pt_bins[i_pt_bin]] = TH1D(sample+'_tau1_notZero_pt'+"_"+str(pt_bins[i_pt_bin]),sample+'_tau1_notZero_pt'+"_"+str(pt_bins[i_pt_bin]),30,200,3000)
        histos[sample]['tau1_notZero_eta'][pt_bins[i_pt_bin]] = TH1D(sample+'_tau1_notZero_eta'+"_"+str(pt_bins[i_pt_bin]),sample+'_tau1_notZero_eta'+"_"+str(pt_bins[i_pt_bin]),10,-5,5)
        histos[sample]['tau1_notZero_SDmass'][pt_bins[i_pt_bin]] = TH1D(sample+'_tau1_notZero_SDmass'+"_"+str(pt_bins[i_pt_bin]),sample+'_tau1_notZero_SDmass'+"_"+str(pt_bins[i_pt_bin]),80,-5,155)
        histos[sample]['tau1_notZero_mass'][pt_bins[i_pt_bin]] = TH1D(sample+'_tau1_notZero_mass'+"_"+str(pt_bins[i_pt_bin]),sample+'_tau1_notZero_mass'+"_"+str(pt_bins[i_pt_bin]),80,-5,155)
        histos[sample]['Z1_mass'][pt_bins[i_pt_bin]] = TH1D(sample+'_Z1mass'+str(pt_bins[i_pt_bin]),sample+'_Z1mass'+str(pt_bins[i_pt_bin]),60,40,160)
    for var_name in var_names:
        histos[sample][var_name]={}
        for i_pt_bin in range(n_pt_bins-1):
            histos[sample][var_name][pt_bins[i_pt_bin]]=TH1D(sample+"_"+var_name+"_"+str(pt_bins[i_pt_bin]),sample+"_"+var_name+"_"+str(pt_bins[i_pt_bin]),50,0,1)
            PH.SetHistStyles(histos[sample][var_name][pt_bins[i_pt_bin]],sample,var_name)

for sample in samples:
    for var_name in var_tau1:
        for i_pt_bin in range(n_pt_bins-1):
            PH.SetHistStyles(histos[sample][var_name][pt_bins[i_pt_bin]],sample,var_name)

#book cut Number
number = {}
for sample in samples:
    number[sample]={}
    number[sample]['total'] = 0
    number[sample]['njetsleps_cut'] = 0
    number[sample]['Z1_cut'] = 0
    number[sample]['clearlep_cut'] = 0

#================================Ana==================================================
ntau1_Zero_ZZ = 0.0
ntau1_notZero_ZZ = 0.0
ntau1_notZero_DYJets = 0.
ntau1_Zero_DYJets = 0.
for sample in samples:
    tempTree = PH.trees[sample]
    number[sample]['total'] = tempTree.GetEntries()
    print "[INFO] Start %s analysis"%sample

    if(sample=='ZZ'):
        nZZtotal = tempTree.GetEntries()
    else:
        nDYJetstotal = tempTree.GetEntries()

    for ievent,event in enumerate(tempTree):
        #if(ievent==10000): break
        nlep = event.lep_pt.size()
        nmergedjets = event.mergedjet_pt.size()
        if(nmergedjets<1): continue
        number[sample]['njetsleps_cut'] +=1

        #find ZToll
        passedZ1Selection = False
        Zmass = 91.1876
        minZ1DeltaM = 99999.99
        n_Zs = 0
        Z_lepindex1 = []
        Z_lepindex2 = []
        massZ1 = 0

        #QCD ntuples needn't select a Z
        if(sample!='QCD'):
            for i in range(nlep):
                for j in range(i+1,nlep):
                    if(event.lep_id[i]+event.lep_id[j]!=0): continue
                    lifsr = TLorentzVector()
                    ljfsr = TLorentzVector()
                    lifsr.SetPtEtaPhiM(event.lepFSR_pt[i], event.lepFSR_eta[i], event.lepFSR_phi[i], event.lepFSR_mass[i])
                    ljfsr.SetPtEtaPhiM(event.lepFSR_pt[j], event.lepFSR_eta[j], event.lepFSR_phi[j], event.lepFSR_mass[j])
                    Z = TLorentzVector()
                    Z = (lifsr + ljfsr)
                    if(Z.M()>0):
                        n_Zs +=1
                        Z_lepindex1.append(i)
                        Z_lepindex2.append(j)
            #consider all Z
            for i in range(n_Zs):
                i1 = Z_lepindex1[i]
                i2 = Z_lepindex2[i]
                lep1 = TLorentzVector()
                lep2 = TLorentzVector()
                lep1.SetPtEtaPhiM(event.lepFSR_pt[i1],event.lepFSR_eta[i1],event.lepFSR_phi[i1],event.lepFSR_mass[i1])
                lep2.SetPtEtaPhiM(event.lepFSR_pt[i2],event.lepFSR_eta[i2],event.lepFSR_phi[i2],event.lepFSR_mass[i2])

                Z1 = lep1+lep2
                Z1DeltaM = abs(Z1.M()-Zmass)
                Z1_lepindex = [0,0]

                # Check Leading and Subleading pt Cut
                if(lep1.Pt()>lep2.Pt()):
                    Z1_lepindex[0] = i1
                    Z1_lepindex[1] = i2
                    if(lep1.Pt()<20 or lep2.Pt()<10): continue
                else:
                    Z1_lepindex[0] = i2
                    Z1_lepindex[1] = i1
                    if(lep2.Pt()<20 or lep1.Pt()<10): continue

                # Check dR(li,lj)>0.02 for any i,j
                if (deltaR(lep1.Eta(),lep1.Phi(),lep2.Eta(),lep2.Phi())<0.02): continue

                # Check M(l+,l-)>4.0 GeV for any OS pair , Do not include FSR photons
                lep1_noFSR = TLorentzVector()
                lep2_noFSR = TLorentzVector()
                lep1_noFSR.SetPtEtaPhiM(event.lep_pt[i1],event.lep_eta[i1],event.lep_phi[i1],event.lep_mass[i1])
                lep2_noFSR.SetPtEtaPhiM(event.lep_pt[i2],event.lep_eta[i2],event.lep_phi[i2],event.lep_mass[i2])
                if((lep1_noFSR+lep2_noFSR).M()<4.0): continue

                # Check isolation cut (without FSR ) for Z1 leptons
                if( event.lep_RelIsoNoFSR[Z1_lepindex[0]]>0.35): continue
                if( event.lep_RelIsoNoFSR[Z1_lepindex[1]]>0.35): continue

                # Check tight ID cut for Z1 leptons
                if (not event.lep_tightId[Z1_lepindex[0]]): continue
                if (not event.lep_tightId[Z1_lepindex[1]]): continue

                # check the masswindow
                if(Z1.M()<76 or Z1.M()>106): continue
                if(Z1.Pt()<200): continue
                if(Z1DeltaM<minZ1DeltaM):
                    minZ1DeltaM = Z1DeltaM
                    massZ1 = Z1.M()
                    passedZ1Selection = True

        if((not passedZ1Selection) and sample!="QCD"): continue
        number[sample]['Z1_cut'] +=1

        #mergedjet analysis
        for i in range(0,nmergedjets):
            tempDeltaR = 999.0
            isclean_H4l = True

            #select the leading jet
            #temp_pt = 0.0
            leadingIndex = 0
            #for k in range(0,nmergedjets):
            #    if(event.mergedjet_pt[k]>temp_pt):
            #        temp_pt = event.mergedjet_pt[k]
            #        leadingIndex = k

            #select the jetmass closest Zmass
            deltaM=9999.9
            for k in range(0,nmergedjets):
                if(abs(event.mergedjet_softdropmass[k]-Zmass)<deltaM):
                    deltaM = abs(event.mergedjet_softdropmass[k]-Zmass)
                    leadingIndex = k

            #MassWindow pt and eta check
            if(event.mergedjet_softdropmass[leadingIndex]>105 or event.mergedjet_softdropmass[leadingIndex]<65): continue
            #if(not abs(event.mergedjet_eta[leadingIndex])>1.5): continue
            if(not event.mergedjet_pt[leadingIndex]>200): continue


            #leptons and photons clear
            nlep =event.lep_pt.size()
            for j in range(nlep):
                if(not event.lep_tightId[j]): continue
                if(event.lep_RelIsoNoFSR[j]>0.35): continue
                thisLep = TLorentzVector()
                thisLep.SetPtEtaPhiM(event.lep_pt[j],event.lep_eta[j],event.lep_phi[j],event.lep_mass[j])
                tempDeltaR = deltaR(event.mergedjet_eta[i],event.mergedjet_phi[i],thisLep.Eta(),thisLep.Phi())
                if(tempDeltaR<0.8):
                    isclean_H4l = False

            nfsrphoton = event.fsrPhotons_pt.size()
            for j in range(nfsrphoton):
                if(not event.lep_tightId[event.fsrPhotons_lepindex[j]]): continue
                RelIsoNoFSR=event.lep_RelIsoNoFSR[event.fsrPhotons_lepindex[j]]
                if(RelIsoNoFSR>0.35): continue
                thispho = TLorentzVector()
                thispho.SetPtEtaPhiM(event.fsrPhotons_pt[j],event.fsrPhotons_eta[j],event.fsrPhotons_phi[j],0.0)
                tempDeltaR = deltaR(event.mergedjet_eta[i],event.mergedjet_phi[i],thispho.Eta(),thispho.Phi())
                if(tempDeltaR<0.8):
                    isclean_H4l = False

            #only passed leptons clear jets
            if(isclean_H4l):

                number[sample]['clearlep_cut'] +=1
                #fill histos in each pt bin
                for i_pt_bin in range(n_pt_bins-1):
                    this_pt = event.mergedjet_pt[leadingIndex]
                    if(this_pt>=pt_bins[i_pt_bin+1] or this_pt<pt_bins[i_pt_bin]): continue

                    if(sample!='QCD'): histos[sample]['Z1_mass'][pt_bins[i_pt_bin]].Fill(massZ1)
                    tempNsubjet = event.mergedjet_nsubjet[leadingIndex]
                    temptau1 = event.mergedjet_tau1[leadingIndex]
                    temptau2 = event.mergedjet_tau2[leadingIndex]
                    histos[sample]['tau1'][pt_bins[i_pt_bin]].Fill(temptau1)
                    histos[sample]['tau2'][pt_bins[i_pt_bin]].Fill(temptau2)

                    if(temptau1 != 0):
                        if(sample=='ZZ'):
                            ntau1_notZero_ZZ +=1
                        else:
                            ntau1_notZero_DYJets +=1
                        histos[sample]['ZvsQCD'][pt_bins[i_pt_bin]].Fill(event.mergedjet_ZvsQCD[leadingIndex])
                        histos[sample]['WvsQCD'][pt_bins[i_pt_bin]].Fill(event.mergedjet_WvsQCD[leadingIndex])
                        histos[sample]['ZvsQCD_de'][pt_bins[i_pt_bin]].Fill(event.mergedjet_ZvsQCD_de[leadingIndex])
                        histos[sample]['WvsQCD_de'][pt_bins[i_pt_bin]].Fill(event.mergedjet_WvsQCD_de[leadingIndex])
                        histos[sample]['tau21'][pt_bins[i_pt_bin]].Fill(temptau2/temptau1)
                        histos[sample]['tau1_notZero_pt'][pt_bins[i_pt_bin]].Fill(event.mergedjet_pt[leadingIndex])
                        histos[sample]['tau1_notZero_eta'][pt_bins[i_pt_bin]].Fill(event.mergedjet_eta[leadingIndex])
                        histos[sample]['tau1_notZero_mass'][pt_bins[i_pt_bin]].Fill(event.mergedjet_mass[leadingIndex])
                        temp_tauDDT = temptau2/temptau1 + 0.082*math.log((event.mergedjet_softdropmass[leadingIndex]*event.mergedjet_softdropmass[leadingIndex])/event.mergedjet_pt[leadingIndex])
                        #print "[TEST] temp_tauDDT = "+str(temp_tauDDT)
                        histos[sample]['tau21_DDT'][pt_bins[i_pt_bin]].Fill(temp_tauDDT)
                        Sumsubjet = TLorentzVector()
                        for i in range(0,tempNsubjet):
                            tempsubjet = TLorentzVector()
                            tempsubjet.SetPtEtaPhiM(event.mergedjet_subjet_pt[leadingIndex][i],event.mergedjet_subjet_eta[leadingIndex][i],event.mergedjet_subjet_phi[leadingIndex][i],event.mergedjet_subjet_mass[leadingIndex][i])
                            Sumsubjet += tempsubjet
                        #histos[sample]['tau1_notZero_SDmass'].Fill(Sumsubjet.M())
                        histos[sample]['tau1_notZero_SDmass'][pt_bins[i_pt_bin]].Fill(event.mergedjet_softdropmass[leadingIndex])

#======================================================================================

#Write raw histograms into rootfile
outfile.cd()
for sample in samples:
    for var_name in var_names:
        for i_pt_bin in range(n_pt_bins-1):
            histos[sample][var_name][pt_bins[i_pt_bin]].Write()

for sample in samples:
    for var_name in var_tau1:
        for i_pt_bin in range(n_pt_bins-1):
            histos[sample][var_name][pt_bins[i_pt_bin]].Write()

#normalize to one
for sample in samples:
    for var_name in var_names:
        for i_pt_bin in range(n_pt_bins-1):
            print "[INFO] start Integral {0:s} {1:s} {2}".format(sample,var_name,pt_bins[i_pt_bin])
            if(histos[sample][var_name][pt_bins[i_pt_bin]].Integral()==0):
                print "[WARNING] {0:s} {1:s} {2} Integral to Zero".format(sample,var_name,pt_bins[i_pt_bin])
                continue
            histos[sample][var_name][pt_bins[i_pt_bin]].Scale(1/histos[sample][var_name][pt_bins[i_pt_bin]].Integral())


for sample in samples:
    for var_name in var_tau1:
        for i_pt_bin in range(n_pt_bins-1):
            if(sample=="QCD" and var_name=="Z1_mass"): continue
            if(histos[sample][var_name][pt_bins[i_pt_bin]].Integral()==0):
                print "[WARNING] {0:s} {1:s} {2} Integral to Zero".format(sample,var_name,pt_bins[i_pt_bin])
                continue
            histos[sample][var_name][pt_bins[i_pt_bin]].Scale(1/histos[sample][var_name][pt_bins[i_pt_bin]].Integral())


#Draw Plots
print "[INFO] Start draw plots on canvas"
for var_name in var_names:
    for i_pt_bin in range(n_pt_bins-1):
        PH.DrawTogetherEeachBin(histos,samples,var_name,pt_bins[i_pt_bin])

for var_name in var_tau1:
    for i_pt_bin in range(n_pt_bins-1):
        PH.DrawTogetherEeachBin(histos,samples,var_name,pt_bins[i_pt_bin])

outfile.Close()
