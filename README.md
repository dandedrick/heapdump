#### heapdump

My hacked together glibc (ptmalloc) heap dumper. This will take a glibc heap and
dump formatted information about each allocation or free chunk. There is
probably something better than this out there but I just threw it together
quickly to solve a problem I was looking at.

Usage:
```heapdump.py --word-size 8 --adjustment 0x12340000 heap.data```
heap.data should be the raw memory at the location of the heap. This can be done
in gdb by using the ```dump binary memory``` command.

The `--word-size` option specifies the word size of the architecture that the
dump comes from. For 64 bit this should be 8 and for 32 bit this should be 4.

The `adjustment` option is an optional offset which will be added to the
formatted addresses. Without this the addresses printed will start at 0. This
is useful for referencing the address of memory for a particular allocation
instead of the relative address from the start of the heap.
