"""

Booklet Writer

Book creator using automatic engine analysis

Developed and tested using python 3.6.3 and python-chess 0.22.1 on windows 7 OS.

"""

import os, sys
import time
import chess
import chess.uci
import chess.pgn
import argparse
import datetime


APP_NAME = 'Booklet Writer'
APP_VER = 'v0.1.0'
APP_NAME_VER = APP_NAME + ' ' + APP_VER
APP_DESC = 'Generates pgn lines using an engine useful for\
            book creation. It uses depth-first search algorithm\
            to build the pgn lines.'
CHESS_STD_START_POS = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


def get_cnt_key(item):
    """ Sort score """
    return item[1]


class MyHandler(chess.uci.InfoHandler):
    """ Output engine analysis from python-chess module """
    def __init__(self):
        chess.uci.InfoHandler.__init__(self)
        
    def post_info(self):      
        """ Called whenever a complete *info* line has been processed """
        super(MyHandler, self).post_info()


class genbook():
    def __init__(self, g):
        self.eng = g['engine']
        self.hash = g['hash']  # in mb
        self.threads = g['threads']
        self.book_side = g['bookside']  # white or black
        self.wmultipv = g['wmultipv']
        self.bmultipv = g['bmultipv']
        self.movetime = g['movetime']  # in ms
        self.mrs = g['mrs']  # mrs = minimum relative score
        self.depth = g['depth']  # book depth
        self.outfn = g['output']  # output pgn filename
        self.move_penalty = g['movepenalty']  # Move penalty for book side
        self.pv = []
        self.book_line = 0
        self.analyzer = None
        self.pgnfile = g['pgnfile']

    def get_end_fen(self, pgnfn):
        pgn = open(pgnfn)
        game = chess.pgn.read_game(pgn)
        game_node = game
        end_node = game_node.end()
        end_board = end_node.board()

        return end_board.fen()

    def search(self, fen, d, ply):
        """ Search and extend moves based from current pos """
        if d == 0:
            return

        # Generate moves for the side to move
        mv = self.genmoves(fen, ply)

        # Search each move
        for i, m in enumerate(mv):
            if m[0] == ply:
                move = m[1]
                normalized_score = m[2]
                penalty = m[3]

            board = chess.Board(fen)

            # Limit analysis of a move depending on the min relative score
            if normalized_score < self.mrs:
                print()
                if board.turn == chess.WHITE:
                    print('skip move: %d. %s, rel_score %0.2f is below %0.2f'\
                          % ((ply+2)/2, move, normalized_score, self.mrs))
                else:
                    print('skip move: %d... %s, rel_score %0.2f is below %0.2f'\
                          % ((ply+2)/2, move, normalized_score, self.mrs))
                continue

            # Save searched data
            self.pv.append([i, ply, move, normalized_score, penalty])

            print()
            if board.turn == chess.WHITE:
                print('move to extend next: %d. %s {%0.2f}\n'\
                      % ((ply+2)/2, move, normalized_score))
            else:
                print('move to extend next: %d... %s {%0.2f}\n'\
                      % ((ply+2)/2, move, normalized_score))

            # Make the move
            move_data = board.parse_san(move)
            board.push(move_data)
            new_fen = board.fen()
            ply += 1

            # Search the new position
            self.search(new_fen, d-1, ply)
            
            # Unmake the move
            board.pop()

            # Save output to pgn file
            self.save_book_lines(ply)
                
            ply -= 1
            self.pv.pop()

    def genmoves(self, pos, ply):
        """ Generate moves using engine """
        mv = []
        fen = pos
        analysis_time = self.movetime
        board = chess.Board(fen)        
        stm = board.turn

        # Define search time
        if stm == chess.WHITE:
            search_multipv = self.wmultipv
        else:
            search_multipv = self.bmultipv
        analysis_time = analysis_time * search_multipv        

        # Start engine
        engine = chess.uci.popen_engine(self.eng)
        engine.uci()
        if self.analyzer is None:
            self.analyzer = engine.name

        engine.setoption({"Hash": self.hash})
        engine.setoption({"Threads": self.threads})
        engine.setoption({"MultiPV": search_multipv})
        
        info_handler = MyHandler()
        engine.info_handlers.append(info_handler)
        
        engine.ucinewgame()
        engine.position(board)
        enginemove, _ = engine.go(movetime=analysis_time)

        # Get score and pv moves
        for i in range(search_multipv):
            if i+1 in info_handler.info["score"]:
                depth = info_handler.info['depth']
                time = info_handler.info['time']
                ucimove = str(info_handler.info['pv'][i+1][0])
                move_data = chess.Move.from_uci(ucimove)
                san_move = board.san(move_data)
                try:
                    scorecp = info_handler.info["score"][i+1].cp
                    scorep = scorecp/100.0
                except:
                    print('Error in reading score!!')
                    continue
                depth = info_handler.info["depth"]
                mv.append([san_move, scorep, depth])
        
        engine.info_handlers.remove(info_handler)
        engine.quit()
            
        # Sort moves by score
        mv = sorted(mv, key=get_cnt_key, reverse=True)

        # Normalize score of the sorted moves
        nmv = self.normalize_score(mv, ply, stm)

        # Show log output to console
        print('current pos:')
        print('%s' % fen)
        print('Search at multipv = %d, movetime = %ds' % (search_multipv, analysis_time/1000))
        for n in nmv:
            if stm == chess.BLACK:
                print('%d... %s {scorecp: %d, depth: %d, rel_score: %0.2f, penalty: %0.2f}'\
                      % ((n[0]+2)/2, n[1], n[4], n[5], n[2], n[3]))
            else:
                print('%d. %s {scorecp: %d, depth: %d, rel_score: %0.2f, penalty: %0.2f}'\
                      % ((n[0]+2)/2, n[1], n[4], n[5], n[2], n[3]))

        return nmv

    def save_book_lines(self, ply):
        """ Save lines in pgn format """
        if self.pgnfile is not None:
            pgn = open(self.pgnfile)
            game = chess.pgn.read_game(pgn)

            game.headers['Annotator'] = self.analyzer
            game.headers['TimeControl'] = '%d/%d' % (1, self.movetime / 1000)

            game_node = game
            end_node = game_node.end()
            end_board = end_node.board()

            line_score = 0.0
            for i, n in enumerate(self.pv):
                line_score += n[3] + n[4]
                if i == 0:
                    node = end_node.add_variation(end_board.parse_san(n[2]))
                    node.comment = 'rel_score: %0.2f, line_score: %0.2f' % (
                        n[3], line_score)
                else:
                    node = node.add_variation(node.board().parse_san(n[2]))
                    node.comment = 'rel_score: %0.2f, line_score: %0.2f' % (
                        n[3], line_score)

            with open(self.outfn, 'a') as f:
                f.write('%s \n\n' % (game))

            self.book_line += 1

    def normalize_score(self, mv, ply, stm):
        """ Set max value to zero and adjust other score
            mv = [sanmove, score, depth]
            """
        nmv = []
        if len(mv):
            big_score = mv[0][1]
            for i, n in enumerate(mv):
                move = n[0]
                score = n[1]
                depth = n[2]
                nscore = score - big_score  # relative score
                move_penalty = 0.0  # For non-book side

                # Add penalty to book side, not really used as stopping rule ATM
                if (self.book_side == 'white' and stm == chess.WHITE)\
                   or (self.book_side == 'black' and stm == chess.BLACK):
                    move_penalty = self.move_penalty
                nmv.append([ply, move, nscore, move_penalty, score*100, depth])

        return nmv
    

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description=APP_DESC, epilog=APP_NAME_VER)
    parser.add_argument("-e", "--engine", help="input engine name",
                        required=True)
    parser.add_argument("--inpgn", help="input pgn file", required=True)
    parser.add_argument("-m", "--hash", help="engine hash usage in MB, "
                                             "default=64MB", default=64, type=int)
    parser.add_argument("-t", "--threads", help="engine threads to use, "
                                                "default=1", default=1, type=int)
    parser.add_argument("-d", "--depth", help="maximum depth of a book line, "
                        "default=4", default=4, type=int)
    parser.add_argument("-a", "--movetime", help="analysis time per position "
                        "in ms, in multipv=n where n > 1, the analysis time "
                        "will be extended to n times this movetime, default=1000",
                        default=1000, type=int)
    parser.add_argument("-f", "--wmultipv", help="number of pv for white, "
                        "default=1", default=1, type=int)
    parser.add_argument("-g", "--bmultipv",
                        help="number of pv for black, default=1",
                        default=1, type=int)
    parser.add_argument("-b", "--bookside",
                        help="white=book for white, black=book for black, "
                             "default=black", default='black')
    parser.add_argument("-r", "--relminscore", help="minimum relative score "
                        "that a given move will be extended if this is high "
                        "then less book lines will be generated, default=-0.3",
                        default=-0.3, type=float)
    parser.add_argument("-j", "--movepenalty", help="move penalty for the "
                                                    "book side, default=-0.1",
                        default=-0.1, type=float)

    args = parser.parse_args()
    
    ply = 0
    
    outfn = 'w_out.pgn' if args.bookside == 'white' else 'b_out.pgn'
        
    data = {'engine':args.engine,
            'hash':args.hash,
            'threads':args.threads,
            'movetime':args.movetime,
            'bookside':args.bookside,
            'wmultipv':args.wmultipv,
            'bmultipv':args.bmultipv,
            'depth':args.depth,
            'mrs':args.relminscore,
            'movepenalty':args.movepenalty,
            'pgnfile':args.inpgn,
            'output':outfn
            }
    
    print(':: Settings ::')
    print('Book for                   : %s' % args.bookside)
    print('Move penalty for book side : %0.2f' % args.movepenalty)
    print('Minimum relative score     : %0.2f' % args.relminscore)
    print('Max ply                    : %d' % args.depth)
    print('Movetime (ms)              : %d' % args.movetime)
    print('Hash (mb)                  : %d' % args.hash)
    print('Threads                    : %d\n' % args.threads)
    
    a = genbook(data)
    end_fen = a.get_end_fen(args.inpgn)
    a.search(end_fen, args.depth, ply)

