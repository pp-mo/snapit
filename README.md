
Directory snapshotting.
=======================

Constructs a chain of version 'snapshots' of a directory, where identical files
are linked by softlinks.

Originally designed for time-tracking conda-mirror channels content.

This is suited to cases where code repositories are unsuitable, because :
  * content files are large
  * changes consist of adding/removing whole files rather than partial changes
  * content is compressed

Usage examples:
---------------

    $ cd ~/mystuff_snaps/mystuff
    $ ls
    file_1.txt

Add a comment to a logfile.

    $ snap-comment "first version"
    $ ls
    comments_log.txt  file_1.txt

Make a snapshot.  
(N.B. it is unwise to be *in* the snapshot dir, as it gets renamed)

    $ cd ..
    $ snapit mystuff
    $ find . -ls
    60351732    4 drwxr-xr-x   4 itpp     avd          4096 Sep 28 23:52 .
    60351736    4 drwxr-xr-x   2 itpp     avd          4096 Sep 28 23:52 ./mystuff
    60351737    0 lrwxrwxrwx   1 itpp     avd            50 Sep 28 23:52 ./mystuff/file_1.txt -> ../snapshot_mystuff_2017-09-28_23:52:46/file_1.txt
    60351738    0 lrwxrwxrwx   1 itpp     avd            56 Sep 28 23:52 ./mystuff/comments_log.txt -> ../snapshot_mystuff_2017-09-28_23:52:46/comments_log.txt
    60351733    4 drwxr-xr-x   2 itpp     avd          4096 Sep 28 23:52 ./snapshot_mystuff_2017-09-28_23:52:46
    60351734    0 -rw-r--r--   1 itpp     avd            17 Sep 28 23:52 ./snapshot_mystuff_2017-09-28_23:52:46/file_1.txt
    60351735    0 -rw-r--r--   1 itpp     avd            38 Sep 28 23:52 ./snapshot_mystuff_2017-09-28_23:52:46/comments_log.txt

Make additional changes.

    $ cd mystuff
    $ echo "new file" > new_file.txt
    $ snap-comment "added extra file"
    $ cd ..
    $ find . -ls
    60351732    4 drwxr-xr-x   4 itpp     avd          4096 Sep 28 23:52 .
    60351736    4 drwxr-xr-x   2 itpp     avd          4096 Sep 28 23:53 ./mystuff
    60351737    0 lrwxrwxrwx   1 itpp     avd            50 Sep 28 23:52 ./mystuff/file_1.txt -> ../snapshot_mystuff_2017-09-28_23:52:46/file_1.txt
    60351738    4 -rw-r--r--   1 itpp     avd            78 Sep 28 23:53 ./mystuff/comments_log.txt
    60351739    0 -rw-r--r--   1 itpp     avd             9 Sep 28 23:53 ./mystuff/new_file.txt
    60351733    4 drwxr-xr-x   2 itpp     avd          4096 Sep 28 23:52 ./snapshot_mystuff_2017-09-28_23:52:46
    60351734    0 -rw-r--r--   1 itpp     avd            17 Sep 28 23:52 ./snapshot_mystuff_2017-09-28_23:52:46/file_1.txt
    60351735    0 -rw-r--r--   1 itpp     avd            38 Sep 28 23:52 ./snapshot_mystuff_2017-09-28_23:52:46/comments_log.txt

Note (1) the "file_1.txt" files are the same file.  
Note (2) but the (successor) log files are different.

    $ cat snapshot_*/comments_log.txt
    2017-09-28_23:52:33 :  first version
    
    $ cat mystuff/comments_log.txt
    2017-09-28_23:53:02 :  added extra file
    2017-09-28_23:52:33 :  first version
