#!/usr/bin/env python3
import os, sys, re
import logging as L
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from random import Random
from itertools import repeat

""" Generate some download test data
"""
def main(args):

    L.basicConfig(level=(L.DEBUG if args.debug else L.INFO))

    config = load_config(args.config)

    if args.outdir:
        # This fails if the directory exists
        os.mkdir(args.outdir)

    total_files = []

    for subdir, params in config.items():
        L.debug(f"Looking at {subdir} in config")
        total_files.append(0)

        # Mandatory stuff
        if type(params['size']) == int:
            file_size = params['size']
        else:
            file_size = convert_to_bytes(params['size'])

        assert type(params['number']) == list
        assert len(params['number']) > 0

        file_numbers = params['number']

        # Optional stuff
        pad_len = int(params.get('pathnamelen', 0))
        path_depth = int(params.get('pathdepth', 0))
        text_files = bool(params.get('base64', False))
        file_extn = params.get('extn', '.txt' if text_files else '.dat')

        for fnum in file_numbers:
            for fname in gen_names( fnum,
                                    params['size'], # Human readable version
                                    pad_len,
                                    path_depth,
                                    file_extn ):
                total_files[-1] += 1
                L.info(fname)
                if args.outdir:
                    fill_file( os.path.join(outdir, fname),
                               nbytes = file_size,
                               seed = fname, # Avoid including outdir in seed!
                               text = text_files )

        L.debug(f"Generated {total_files[-1]} files in {subdir}")

    L.debug(f"Generated {sum(total_files)} in {len(total_files)} subdirectories")

def gen_names(fnum, fsize, pad_len, path_depth, file_extn):
    """Generate a list of names as per the design.
    """
    top_dir = pad_filename(f"size_{fsize}_files_{fsize}", pad_len)

    for n in range(1, path_depth):
        top_dir += "/" + pad_filename(f"subdir_{n}", pad_len)

    # See how many digits in fnum
    fnum_pad = min(4, len(str(fnum-1)))

    for n in range(fnum):
        yield top_dir + "/" + pad_filename( f"subdir_{n}",
                                            minlne = pad_len,
                                            extn = file_extn )

def parse_args(*args):
    description = """Given a config file, generates a directory of files for us to try
                     downloading.
                  """
    argparser = ArgumentParser( description=description,
                                formatter_class = ArgumentDefaultsHelpFormatter )
    argparser.add_argument("config", nargs="+",
                            help="Config file(s) to process.")
    argparser.add_argument("-o", "--outdir",
                            help="Directory to create. Must not exist. If none, the list"
                                 " of files will just be printed.")
    argparser.add_argument("-d", "--debug", action="store_true",
                            help="Print more verbose debugging messages.")

    return argparser.parse_args(*args)


def convert_to_bytes(val):
    """Convert '20k' to 20*1024 etc.
    """
    # There's probably a module but whatever...
    scalings = dict( k = 1024,
                     M = 1024**2,
                     G = 1024**3,
                     T = 1024**4, )
    if val[-1] in scalings:
        return int(val[:-1]) * scalings[val[-1]]
    else:
        return int(val)

def fill_file(filename, nbytes, seed=None, text=False):
    """File a file with n bytes of "random" data.
    """
    seed = seed if seed is not None else filename
    rng = Random(seed)
    rbsize = 8 # Maybe making this larger speeds us up?


    with open(filename, 'wb') as fh:
        written_chunks = 0

        if text:
            linelen = (rbsize * 4) + 1
            chunks = nbytes // linelen
            extra = nbytes % linelen

            char_src = ( b64encode(random.getrandbits(8*n).to_bytes(n, 'big'))
                         for n in repeat(rbsize*3, chunks) )

            for bstring in bit_src:
                fh.write(bstring + "\n")

            if extra:
                extra_bits = random.getrandbits(8*rbsize*3).to_bytes(rbsize*3, 'big')
                extra_chars = b64encode(extra_bits)[:extra-1]
                fh.write(extra_chars + "\n")

        else:
            chunks = nbytes // rbsize
            extra = nbytes % rbsize

            bit_src = ( random.getrandbits(8*n).to_bytes(n, 'big')
                        for n in repeat(rbsize, chunks) )

            # TODO - can I avoid the loop here?
            for bstring in bit_src:
                fh.write(bstring)

            if extra:
                fh.write(random.getrandbits(8*extra).to_bytes(extra, 'big'))

def gen_path(filepath, nbytes, _path_cache=set(), **fill_file_args):
    """Make the directory path if it does not exist, then
       fill the file with data
    """
    dn = os.path.dirname(filepath)
    if dn not in _path_cache:
        os.makedirs(dn)
        _path_cache.add(dn)

    fill_file(filepath, nbytes, **fill_file_args)

def pad_filename(filename, minlen=0, pad="paddingPADDING", extn=""):
    """Pad out a filename.
    """
    # Make a string long enough to pad even an empty filename
    plenty_padding = pad * (minlen + 1 / len(pad))

    pad_to_add = minlen - (len(filename) + len(extn))

    if pad_to_add == 1:
        # Decided to never pad by 1
        return filename + extn
    elif pad_to_add > 0:
        return filename + "_" + plenty_padding[:pad_to_add-1] + extn
    else:
        return filename + extn

def load_config(conf_files):
    """Load and merge the config files.
    """
    res = {}

    for cf in conf_files:
        with open(cf) as cfh:
            conf_dict = yaml.safe_load(cfh)

        dupes = [k for k in conf_dict.keys() if k in res]
        if dupes:
            raise KeyError(f"Duplicate key seen in {cf}: {dupes}")

        res.update(conf_dict)

    return res

if __name__ == "__main__":
    main(parse_args())

