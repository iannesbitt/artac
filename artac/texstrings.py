from string import Template

CHAPTER = Template('\chapter{Radar profile plots} %Appendix title\n')

SECTION = Template('\n\section{$date $location}\n')

SUBSECTION = Template('\n\subsection{Line $fn}\n\n')

FIGURE = Template('''\\begin{figure}[!h]
	\\includegraphics[width=1\\textwidth] %% make figure text width
	{$pfn} %% figure path
	\\caption{\\label{fig:$fn}$caption} %% caption with label as basename
\\end{figure}\n''')

PCAPTION = Template('''Radar profile $fn in $location. Profile collected $date. Processing parameters: gain=$gain, time zero=$zero, horizontal boxcar filter window length=$bgrwin, vertical triangular FIR filter range=$filt MHz.''')

MCAPTION = Template('''Map of profile $fn in $location, collected $date.''')

CLEAR = Template('''\\clearpage\n\n''')

END = Template('''\\endinput\n''')
