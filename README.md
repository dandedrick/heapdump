#### Allocdump

My hacked together glibc (ptmalloc) heap dumper. This will take a glibc heap and
dump formatted information about each allocation or free chunk. There is
probably something better than this out there but I just threw it together
quickly to solve a problem I was looking at.

Usage:
```heapdump.py heap.data 0x12340000```
heap.data should be the raw memory at the location of the heap. The can be done
in gdb by using the ```dump binary memory``` command.

The 0x12340000 is an option offset which will be added the the formatted
addresses. Without the addresses printed will start at 0. This is useful for
referencing the address of memory for a particular allocation instead of the
relative address from the start of the heap.
