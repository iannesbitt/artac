from string import Template

CHAPTER = Template('\chapter{Radar profile plots} %Appendix title')

SECTION = Template('\section{$date $location}')

SUBSECTION = Template('\subsection{Line $fn}')

FIGURE = Template('''
\\begin{figure}[!h]
	\\includegraphics[width=1\\textwidth]
	{figures/data/$fn.png}
	\\caption{\\label{fig:$fn}$caption.}
\\end{figure}
''')

PCAPTION = Template('''Radar profile $fn in $location. Profile collected $date.''')

MCAPTION = Template('''Map of radar profile $fn in $location, collected $date.''')

CLEAR = Template('''\\clearpage''')

END = Template('''\\endinput''')