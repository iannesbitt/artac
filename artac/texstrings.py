from string import Template

CHAPTER = Template('\chapter{Radar profile plots} %Appendix title')

SECTION = Template('\section{$date $location}')

SUBSECTION = Template('\subsection{Line $fn}')

FIGURE = Template('''\\begin{figure}[!h]
	\\includegraphics[width=1\\textwidth] %% make figure text width
	{$pfn} %% figure path
	\\caption{\\label{fig:$fn}$caption.} %% caption with label as basename
\\end{figure}''')

PCAPTION = Template('''Radar profile $fn in $location. Profile collected $date.''')

MCAPTION = Template('''Map of radar profile $fn in $location, collected $date.''')

CLEAR = Template('''\\clearpage\n\n''')

END = Template('''\\endinput\n''')
