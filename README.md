### Booklet Writer
A program that will generate chess book lines automatically using a chess engine by depth-first search algorithm.  
This is developed under windows 7 OS along with the installation of the items in requirements below.

### Requirements
1. Python 3.x  
https://www.python.org/  
2. Python-chess  
https://pypi.python.org/pypi/python-chess  
2. UCI engine such as Stockfish and others  
https://stockfishchess.org/

### Usage
<pre>
usage: booklet-writer.py [-h] -e ENGINE [-m HASH] [-t THREADS] [-d DEPTH]
                         [-a MOVETIME] [-f WMULTIPV] [-g BMULTIPV]
                         [-b BOOKSIDE] [-r RELMINSCORE] [-j MOVEPENALTY]

Generates pgn lines using an engine useful for book creation. It uses depth-
first search algorithm to build the pgn lines.

optional arguments:
  -h, --help            show this help message and exit
  -e ENGINE, --engine ENGINE
                        input engine name
  -m HASH, --hash HASH  engine hash usage in MB, default=64MB
  -t THREADS, --threads THREADS
                        engine threads to use, default=1
  -d DEPTH, --depth DEPTH
                        maximum depth of a book line, default=4
  -a MOVETIME, --movetime MOVETIME
                        analysis time per position in ms, in multipv=n where n
                        > 1, the analysis time will be extended to n times
                        this movetime, default=1000
  -f WMULTIPV, --wmultipv WMULTIPV
                        number of pv for white, default=1
  -g BMULTIPV, --bmultipv BMULTIPV
                        number of pv for black, default=1
  -b BOOKSIDE, --bookside BOOKSIDE
                        white = book for white, black = book for black,
                        default=black
  -r RELMINSCORE, --relminscore RELMINSCORE
                        minimum relative score that a given move will be
                        extended if this is high then less book lines will be
                        generated, default=-0.3
  -j MOVEPENALTY, --movepenalty MOVEPENALTY
                        move penalty for the book side, default=-0.1

Booklet Writer v0.1.0
</pre>

To generate a book for black using stockfish engine, you may set black multipv to 1 and white multipv to 4 and movetime of 1000 ms.  

`booklet-writer.py --engine stockfish.exe --hash 128 --threads 1 --movetime 1000 --bmultipv 1 --wmultipv 4 --bookside black`

### Output
The output currently is a pgn file and this is in append mode.

<pre>
[Event "Black book lines generation"]
[Site "?"]
[Date "2018.03.05"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Annotator "Stockfish 9 64 POPCNT"]
[TimeControl "1/1"]

1. e4 {rel_score: 0.00, line_score: 0.00} 1... e5 {rel_score: 0.00, line_score: -0.10} 2. Nf3 {rel_score: 0.00, line_score: -0.10} 2... Nf6 {rel_score: 0.00, line_score: -0.20} *

[Event "Black book lines generation"]
[Site "?"]
[Date "2018.03.05"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Annotator "Stockfish 9 64 POPCNT"]
[TimeControl "1/1"]

1. e4 {rel_score: 0.00, line_score: 0.00} 1... e5 {rel_score: 0.00, line_score: -0.10} 2. d4 {rel_score: -0.09, line_score: -0.19} 2... exd4 {rel_score: 0.00, line_score: -0.29} *

[Event "Black book lines generation"]
[Site "?"]
[Date "2018.03.05"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Annotator "Stockfish 9 64 POPCNT"]
[TimeControl "1/1"]

1. e4 {rel_score: 0.00, line_score: 0.00} 1... e5 {rel_score: 0.00, line_score: -0.10} 2. Bc4 {rel_score: -0.09, line_score: -0.19} 2... Nf6 {rel_score: 0.00, line_score: -0.29} *
</pre>
