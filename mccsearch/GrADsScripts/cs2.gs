'reinit'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE1.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE2.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE3.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE4.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE5.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE6.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE7.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE8.ctl'
'open /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/MERGnetcdfCEs/ctlFiles/cloudElements2009-08-31_23:00:00F7CE9.ctl'
'set grads off'
'set mpdset hires'
'set gxout shaded'
'set csmooth on'
'set gxout shaded on'
*'set lat 12.0234 16.8594'
*'set lon -7.98438 7.91406'

*set colors taken from colormap.gs
*Blues
   'set rgb 16 255 255 255'
   'set rgb 17 108 20 156'
   'set rgb 18 77 50 183'
   'set rgb 19 48 83 213'
   'set rgb 20 22 107 236'
   'set rgb 21 0 193 254'
   'set rgb 22 42 166 255'
   'set rgb 23 66 197 249' 
   'set rgb 24 92 226 255'
   'set rgb 25 124 255 249'
   
*Greens
   'set rgb 26 132 252 204'
   'set rgb 27 135 252 145'
   'set rgb 28 151 255 130'
   'set rgb 29 209 255 128'

*Yellows/Reds
   'set rgb 30 255 246 117'
   'set rgb 31 255 189 58'
   'set rgb 32 249 136 6'
   'set rgb 33 241 110 0'
   'set rgb 34 212 93 1'
   'set rgb 35 208 68 0'
   'set rgb 36 182 48 10'
   'set rgb 37 163 29 2'
   'set rgb 38 138 15 0'
   'set rgb 39 255 255 255'


   set_plot(198,312,5)
   say '-------------------------------'
   say 'Color Scale set to Color Infrared 1.'
   say '-------------------------------'

*'set gxout shaded on'

*'run cbarn'

'd ch4.9'
'd ch4.8'
'd ch4.7'
'd ch4.6'
'd ch4.5'
'd ch4.4'
'd ch4.3'
'd ch4.2'
'd ch4.1'



'run cbarn'
'printim /Users/kimwhitehall/Documents/HU/research/mccsearch/caseStudy1/images/cloudElements2009-08-31_23:00:00F7.gif x800 y600 white'
'quit'





function set_plot(min,max,int)

    value = min
    cval=16
    c_levs = ''
    c_cols = ''

    while( value <= max )
      c_levs = c_levs ' ' value
      c_cols = c_cols ' ' cval
      value = value + int
      cval=cval+1
    endwhile
    c_cols=c_cols' 'cval-1

    say '-------------------------------'
    say 'Contour levels set to: 'c_levs
    say 'Color Values set to: 'c_cols
    say '-------------------------------'

    'set clevs 'c_levs
    'set ccols 'c_cols

return

