
import os
import Plot_Configs as PC
import Analyzer_Configs as AC
from ROOT import *

#####################################################################

def LoadNtuples(ana_cfg,year):
    ntuples = {}
    print " list of samp_names = "+str(ana_cfg.samp_names)
    for sample in ana_cfg.samp_names:
        if(sample=='data' or sample == 'ZX'):
            print "will open data file"
            #tmpfile = TFile(ana_cfg.sample_loc + '/2018_noDuplicates.root')
            ntuples[sample] = TChain("passedEvents","chain_" + sample)
            ntuples[sample]. Add(ana_cfg.sample_loc + '/%s_noDuplicates.root'%year)

        else:
            print "will open file"+ana_cfg.sample_loc + '/%s*.root' %sample
            #tmpfile = TFile(ana_cfg.sample_loc + '/%s_2018.root' %sample)
	    ntuples[sample] = TChain("passedEvents","chain_" + sample)
            ntuples[sample]. Add(ana_cfg.sample_loc + '/MC{0:s}/{1:s}*.root'.format(year,sample))
        if(ntuples[sample]):
            print " number of events = " + str(ntuples[sample].GetEntries())
            print " do a loop testing"
            for ievent,event in enumerate(ntuples[sample]):
                if ievent==1: break
                print " success to loop %s sample "%sample

    return ntuples


def AddHistos(histos,ana_cfg,var_name,year):
    tmpSimhisto = TH1D("Sim"+var_name+year,"Sim"+var_name+year,680,100,3500)
    tmpSimhisto.SetFillColor(kRed-7)
    tmpSimhisto.Sumw2()
    tmpGGZZhisto = TH1D("GGZZ"+var_name+year,"GGZZ"+var_name+year,680,100,3500)
    tmpGGZZhisto.SetFillColor(kAzure -1)
    tmpGGZZhisto.Sumw2()
    for sample in ana_cfg.sig_names:
        tmpSimhisto.Add(tmpSimhisto,histos[sample])
    for sample in ana_cfg.bkg_names:
        if(sample.find('GluGluToContinToZZ')!=-1):
            tmpGGZZhisto.Add(tmpGGZZhisto,histos[sample])
    return tmpSimhisto,tmpGGZZhisto

def MakeStack(histos, ana_cfg, var_name,Simhisto,GGZZhisto,SumZX,SumqqZZ):
    stacks = {}
    #stacks['data']  = THStack("h_stack_"+var_name, var_name)
    stacks['bkg']  = THStack("h_stack_"+var_name, var_name)
    #stacks['data'].Add(histos['data'])
    stacks['bkg'].Add(SumZX)
    stacks['bkg'].Add(GGZZhisto)
    stacks['bkg'].Add(SumqqZZ)
    stacks['bkg'].Add(Simhisto)
    return stacks


def CreateCanvas(canv_name):
    canv = TCanvas(canv_name, canv_name,650,500)
    canv.SetLogx()
    return canv


def MakeLumiLabel(lumi):
    tex = TLatex()
    tex.SetTextSize(0.035)
    tex.SetTextAlign(31)
    tex.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)' %lumi)
    return tex


def MakeCMSDASLabel():
    tex = TLatex()
    tex.SetTextSize(0.03)
    tex.DrawLatexNDC(0.15, 0.85, '#scale[1.5]{CMS}preliminary')
    return tex

def MakeDataLabel(stack_data,cat_name):
    histo = stack_data.GetStack().Last()
    histo.GetXaxis().SetTitle('m_{%s}'%cat_name)
    #histo.GetXaxis().SetTitleSize(0.20)
    histo.GetYaxis().SetTitle('Events / %.2f' %histo.GetBinWidth(1))
    #histo.GetYaxis().SetTitleSize(0.20)
    return histo



def ScaleSignal(plt_cfg,stack_sig,var_name):
    sig_hist = stack_sig.GetStack().Last()
    sig_hist.Scale(plt_cfg.sig_scale)
    sig_hist.SetLineColor(kRed)
    sig_hist.SetLineWidth(2)
    sig_hist.SetFillStyle(0)

    sig_hist.GetXaxis().SetTitle(var_name)
    sig_hist.GetXaxis().SetTitleSize(0.20)
    sig_hist.GetYaxis().SetTitle('Events / %.2f' %sig_hist.GetBinWidth(1))
    sig_hist.GetYaxis().SetTitleSize(0.20)
    return sig_hist

def MakeRatioPlot(h_data, h_MC, var_name):
    ratio_plot = TGraphAsymmErrors()
    ratio_plot.Divide(h_data, h_MC, "pois")
    ratio_plot.SetName("ratiograph_" + var_name)
    ratio_plot.SetMinimum(0.4)
    ratio_plot.SetMaximum(2.0)
    ratio_plot.SetMarkerStyle(20)

    ratio_plot.GetXaxis().SetRangeUser( h_data.GetXaxis().GetXmin(), h_data.GetXaxis().GetXmax() )
    ratio_plot.GetXaxis().SetLabelSize(0.15)
    ratio_plot.GetXaxis().SetTitle(var_name)
    ratio_plot.GetXaxis().SetTitleSize(0.20)
    ratio_plot.GetXaxis().SetTitleOffset(0.5)

    ratio_plot.GetYaxis().SetNdivisions(505)
    ratio_plot.GetYaxis().SetLabelSize(0.13)
    ratio_plot.GetYaxis().SetTitle("Data/MC")
    ratio_plot.GetYaxis().SetTitleSize(0.20)
    ratio_plot.GetYaxis().SetTitleOffset(0.2)

    return ratio_plot


def MakeLegend(plt_cfg, histos,Simhito,GGZZhito):
    legend = TLegend(0.65,0.65,0.85,0.85)
    legend.SetNColumns(1)
    legend.SetLineColor(10)

    legend.AddEntry(histos["data"], "data")
    legend.AddEntry(Simhito,"H(125)","f")
    legend.AddEntry(histos["ZZTo4L"],"qq->ZZ","f")
    legend.AddEntry(GGZZhito,"gg->ZZ","f")
    legend.AddEntry(histos["ZX"],"Z+X","f")
    #for sample in plt_cfg.ana_cfg.sig_names:
    #    legend.AddEntry(histos[sample], sample )
    #    legend.AddEntry(scaled_signal, "signal X%d" %plt_cfg.sig_scale)
    return legend


def DrawOnCanv(canv, var_name, plt_cfg, stacks, histos, scaled_sig,legend, lumi_label, cms_label):
    canv.cd()

    #histos['data'].GetXaxis().SetTitle(var_name)
    #hist.GetXaxis().SetTitleSize(0.20)
    #histos['data'].GetYaxis().SetTitle('Events / %.2f' %histos['data'].GetBinWidth(1))
    #hist.GetYaxis().SetTitleSize(0.20)
    #upper_pad = TPad("upperpad_"+var_name, "upperpad_"+var_name, 0,0.2, 1,1)
    #upper_pad.SetBottomMargin(0.05)
    #upper_pad.Draw()
    #upper_pad.cd()
    #if plt_cfg.logY:
        #upper_pad.SetLogy()
    	#stacks['all'].SetMinimum(1e-1)
        #stacks['all'].SetMaximum(1e8)
    #c2 = TCanvas()
    histos['data'].Draw('PE')
    stacks['bkg'].Draw("same histo")
    #histos['data'].SetMarkerStyle(20)
    histos['data'].Draw('SAME PE')
    #c2.SaveAs("plot/test.png")
    #scaled_sig.Draw('SAMEPE')
    #print "type of stacks = " + str(type(stacks['bkg']))

    legend.Draw()
    cms_label.DrawLatexNDC(0.10, 0.91, '#scale[1.5]{CMS}#font[12]{preliminary}')
    cms_label.Draw('same')
    lumi_label.DrawLatexNDC(0.90, 0.91, '%s fb^{-1} (13 TeV)' %plt_cfg.lumi)
    lumi_label.Draw('same')

    # draw x label
    x_low = 100
    x_up =3500
    step = 10
    latex={}
    label_margin = -0.40
    for i in range(100,3500,step):
        if(i==200 or i==300 or i==400 or i==500 or i==1000 or i==2000 or i==3000):
            i_x = i
            latex[i] = TLatex(i_x,label_margin,"%.0f"%i_x)
            latex[i].SetTextAlign(23)
            latex[i].SetTextFont (42)
            latex[i].SetTextSize (0.04)
            latex[i].Draw()
    #histos['data'].Draw('SAME PE')
    #scaled_sig.Draw('SAMEPE')
    #histos['data'].Draw('SAME E1')

    #canv.cd()
    #lower_pad = TPad("lowerpad_"+var_name, "lowerpad_"+var_name, 0, 0, 1,0.2)
    #lower_pad.SetTopMargin(0.05)
    #lower_pad.SetGridy()
    #lower_pad.Draw()
    #lower_pad.cd()
    #ratio_plot.Draw()


def SaveCanvPic(canv, save_dir, save_name):
    canv.cd()
    #canv.SaveAs(save_dir + '/' + save_name + '.pdf')
    canv.SaveAs(save_dir + '/' + save_name+ '.png')

def Getbkgweight(event,sample,lumi):
    if(sample=='GluGluHToZZTo4L'):
        weight=lumi*13.33*event.weight/event.cross
    elif(sample=='VBF_HToZZTo4L'):
        weight=lumi*1.044*event.weight/event.cross
    elif(sample=='WminusH_HToZZTo4L'):
        weight=lumi*0.147*event.weight/event.cross
    elif(sample=='WplusH_HToZZTo4L'):
        weight=lumi*0.232*event.weight/event.cross
    elif(sample=='ZH_HToZZ_4L'):
        weight=lumi*0.668*event.weight/event.cross
    elif(sample=='ttH_HToZZ'):
        weight=lumi*0.393*event.weight/event.cross
    elif(sample=='bbH_HToZZTo4L'):
        #weight=lumi*0.133*event.eventWeight/event.crossSection/207800.00
        weight=lumi*0.133*event.weight/event.cross
    elif(sample=='ZZTo4L'):
        weight=lumi*1000*1.256*event.weight*event.k_qq_qcd_M*event.k_qq_ewk/event.cross
    elif(sample=='GluGluToContinToZZTo2e2mu'):
        weight=lumi*1000*0.00319*event.weight*event.k_gg/event.cross
    elif(sample=='GluGluToContinToZZTo2e2tau'):
        weight=lumi*1000*0.00319*event.weight*event.k_gg/event.cross
    elif(sample=='GluGluToContinToZZTo2mu2tau'):
        weight=lumi*1000*0.00319*event.weight*event.k_gg/event.cross
    elif(sample=='GluGluToContinToZZTo4e'):
        weight=lumi*1000*0.00159*event.weight*event.k_gg/event.cross
    elif(sample=='GluGluToContinToZZTo4mu'):
        weight=lumi*1000*0.00159*event.weight*event.k_gg/event.cross
    elif(sample=='GluGluToContinToZZTo4tau'):
        weight=lumi*1000*0.00159*event.weight*event.k_gg/event.cross
    else:
        weight=1
    return weight
