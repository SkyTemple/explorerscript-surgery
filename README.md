ExplorerScript Surgery
======================

We collect weird and non-functioning ExplorerScript test cases here. All of these should be fixed and eventually be integrated
as test cases in ExplorerScript and SkyTemple Files.

Each sub-directory is a case. The cases also contain info about their current status.

## Generate case

To generate a case, install Python 3 and the requirements in `requirements.txt` (`pip3 install -r requirements.txt`).

After this generate a new case like this:

`./generate.py <output-dir> <edition> <path-to-problematic-ssb> <path-to-original-source-code>`

This will decompile the SSB and all the graphs generated on each step of the decompilation process and output them into `<output-dir>`.
It will also generate the README template for you.

`<edition>` is one of the recognized edition codes: https://github.com/SkyTemple/skytemple-files/blob/master/skytemple_files/_resources/ppmdu_config/pmd2data.xml#L37-L51

GraphViz (`dot`) must be installed and in `PATH`.
