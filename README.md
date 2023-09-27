# Transfer test generator

## The idea

We are having issues with our transfer server - it's experiencing slow download speeds and
having isseues with directories with a large number of files. I suspect that long paths
are also a problem.

What I'd like is a way to reproducibly generate a directory of test data. The files should be
random/uncompressible but also with predictable contents, so I'll want to generate them from
a fixed seed. That bit should eb easy-ish.

So I want a Python script that takes a config file and generates a data directory.

## The config

Parameters I care about are:

1) Size of files
2) Number of directories
3) Files per directory
4) Length of file/directory names
5) Depth of paths

I think 2+3 can be combined into a list.

Then the length and depth of paths will be minimum values.

~~~
small_files:
    size: '10'
    number: [100, 1000, 11000, 111000]
    pathnamelen: 20
    pathdepth: 4
    extn: '.txt'
    base64: true
large_file:
    size: '10G'
    number: [1]
~~~

Given this sample config I should run:

~~~
transfer_test_maker.py -o ./ttmaker ttmaker.yaml
~~~

and get:

~~~
small_files/size_10_files_100_xxx/subdir_1_xxxxxxxxxxxx/subdir_2_xxxxxxxxxxx/subdir_3_xxxxxxxxxxx/
  size_10_00000000_xxxxxxxxxxxxxx.txt
small_files/size_10_files_100_xxx/subdir_1_xxxxxxxxxxxx/subdir_2_xxxxxxxxxxx/subdir_3_xxxxxxxxxxx/
  size_10_00000001_xxxxxxxxxxxxxx.txt
~~~

etc. Actually, I think rather than xxxxx maybe "paddingPADDING" repeated is better.

And without a '-o' flag the script should just print a list of files it would generate.

I think there is a Python module that lets me interpret "2G" as "2 * 1024^3" and I don't need to
reinvent this.

## Scripting tasks

1) `def pad_filename(name, minlen=0, pad="paddingPADDING", extn="")`

2) `def convert_bytes(val)`

3) `def fill_file(filename, bytes, seed=None)`

4) `def gen_path(filepath, bytes)`

and more.
