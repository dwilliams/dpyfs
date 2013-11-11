dpyfs
=====

A python based network distributed file system project.

This is starting off as a "because I can" or a "because I want to learn more
about it" type of project.  My goals are going to be as follows:

 * Simple: Simplicity is the key to making things useable and maintainable.
 * Redundant: What's the use in storing anything if it's going to get wiped out?
 * Embedded (not quite, but close): I want to run this on small, power efficent
   ARM processors or Atom processors (ones that will run OpenBSD).

I'm looking to trade speed (because I don't really need much of it) for
simplicity and redundancy.  I've lost too many files to complicated systems
that, while providing redundancy, were too complicated to maintain or recover
from some error.  Thus, with a little boredom, this project was born.  The
system will draw a bit from filesystems like Ceph or XtreemFS, but won't
actually copy them.  While this will help with the licensing, in reality I'm
just to lazy to try to decrypt their source.

dpyfs (pronounced dippy-F-S) will feature three main components: the storage
daemon, the director daemon, and the client.  There will probably end up being
more than one client, but for now I'll focus on something FUSE-ish.

Storage Daemon
--------------
The initial plan for the storage daemon is to be a simple key value store.  I
know, I know, I can just use MongoDB or something, but I want less horsepower
and simpler features.  I plan to use a file based backing store with some basic
algorithms to glean information from the system the daemon is running on.  The
information will include things like system load, disk usage, file numbers, etc.
The storage daemon should also have some basic integrity checking functionality.
The storage daemon will be accessed via HTTP initially, and updated to use HTTPS
with some sort of certificate authority structure in the future (maybe leverage
Puppet for handling this?).  Any file chunk that is to be stored will use hashes
for it's key.  I'm going to enforce the storage daemons to store chunks, not
files.  While this does slightly increase complexity, it allows for added
benefits like deduplication and internal integrity checking more easily.

Director Daemon
---------------
The director daemon will provide the main interaction point with the cluster.
Any client that wishes to access a file will talk to a director daemon.  While
this isn't the most performant solution available, it will provide a small
number of (redundant) points to handle control and integrity of the cluster.
The plan is to have the director be a file backed key value store that
translates the file path into a list of chunks.  The director will either gather
or disperse the chunks based on the file operation.  The director will be a
proxy for all file accesses to the cluster.  This will hopefully allow features
like read ahead to be added in the near future.  It also lets the clients be
much lighter weight as the client doesn't have to deal with load the chunks,
checking them, and reassembling them.

Client
------
Will initially be a ReSTful client similar to Amazon S3 storage.  Will make a
FUSE-ish file system in the future for setting up Windows shares and UPnP media
servers.
