from string import Template

CHAPTER = Template('\chapter{Radar profile plots} %Appendix title\n\n')

SECTION = Template('\section{$date $location}\n\n')

SUBSECTION = Template('\subsection{Line $fn}\n\n')

FIGURE = Template('''\\begin{figure}[!h]
	\\includegraphics[width=1\\textwidth] %% make figure text width
	{$pfn} %% figure path
	\\caption{\\label{fig:$fn}$caption.} %% caption with label as basename
\\end{figure}\n''')

PCAPTION = Template('''Radar profile $fn in $location. Profile collected $date.''')

MCAPTION = Template('''Map of radar profile $fn in $location, collected $date.''')

CLEAR = Template('''\\clearpage\n\n''')

END = Template('''\\endinput\n''')
