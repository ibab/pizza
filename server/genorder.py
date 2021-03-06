# encoding: UTF-8
"""
    Pizzaboy
    Automated generation of pizza orders.

    Authors: Igor Babuschkin <igor.babuschkin@udo.edu>
             Kevin Dungs <kevin.dungs@udo.edu>
    Version: 1.0 (2013-01-30)
"""

from __future__ import print_function

from datetime import datetime
from decimal import Decimal
from os import remove
from re import findall, MULTILINE
from subprocess import Popen

def cents_to_euros(cents):
    return u'{},{:02d} €'.format(int(cents / 100), cents % 100)

def escape_latex(pizzas):
    return pizzas #pizzas.replace("\\", "\\\\").replace("%", "\\%").replace("&", "\\&")

def sanitize_tex(text):
    return text.replace('\\', '').replace('{','\\{').replace('}', '\\}')

def print_order(pizzas, prices):

    coststring = u"Preis (mit Rabatt): {} ({})".format(
        cents_to_euros(sum(prices)),
        cents_to_euros(int(round(0.9 * sum(prices))))
    )

    pizzas = map(sanitize_tex, pizzas)
    pizzas = '\\item ' + escape_latex(' \\ \n \\item '.join(pizzas))
    identifier = "pizza-{}".format(datetime.now().strftime("%Y-%m-%d"))
    filename = "/tmp/{}.tex".format(identifier)
    with open(filename, 'w') as texfile:
        texfile.write(
            TEMPLATE.decode('utf-8')
            .replace(u"%PIZZA", pizzas)
            .replace(u"%PRICE", coststring)
            .encode('utf-8'))
    p = Popen(
        "lualatex --interaction=batchmode {}".format(filename),
        shell=True
    )
    ret = p.wait()
    remove("{}.aux".format(identifier))
    remove("{}.log".format(identifier))
    return '{}.pdf'.format(identifier)
    #if ret == 0:
    #    Popen(
    #        "cat {}.pdf | lpr -P Kyocera_Mita_FS-3820N_FS-3820N -o Duplex=DuplexNoTumble".format(identifier),
    #        shell=True
    #    )
    #    print("Druckauftrag an KYOA abgeschickt.")

TEMPLATE = r"""
\documentclass{scrartcl}

\usepackage[ngerman]{babel}
\usepackage{fontspec}
\usepackage{microtype}
\usepackage{rotating}
\usepackage{scrtime}
\linespread{0.9}

\setmainfont{DejaVu Sans}

\setlength{\parindent}{0pt}
\pagestyle{empty}

\title{Pizzabestellung}
\author{Generated by Pizzaboy.}

\begin{document}
\begin{flushright}
\today{} \thistime
\end{flushright}

Hallo, \\

hier kommt unsere heutige Bestellung. \\
Unsere Kundennummer ist 138. \\
Lieferung bitte erst ab 18:00 Uhr.\\

\begin{itemize}
\itemsep-0.3em

%PIZZA
\end{itemize}

Lieferadresse: \\

Herr Holger Stevens \\
Fa. TU Dortmund - Abt. Physik \\
Otto-Hahn-Str. 4 \\
44227 Dortmund \\

Einfahrt 29, Raum: P2-01-513 (1 Stockwerk nach oben, durch das Foyer ins Gebäude P2, 1 Stockwerk nach oben. Oder einfach anrufen) \\
Bei Fragen bitte unter 02317553665 anrufen! Schöne Grüße und bis gleich!


\newpage

.\\[40em]
\begin{turn}{180}
    \Huge FAX: 0231 28 097 29
\end{turn} \\ [2cm]
\begin{turn}{180}
    \normalsize %PRICE
\end{turn}

\end{document}
"""
