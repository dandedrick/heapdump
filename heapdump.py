#!/usr/bin/env python3
import argparse
import humanize
import struct


class HeapDumper:
    def __init__(self, args):
        match args.word_size:
            case 4:
                self._unpack_format = '<I'
            case 8:
                self._unpack_format = '<Q'
            case _:
                raise NotImplementedError(f"Word size of {args.word_size} not "
                                          "supported")
        self._word_size = args.word_size
        self._adjustment = args.adjustment
        self._data = open(args.filename, "rb")

    def _unpack_word(self, raw_word):
        return struct.unpack(self._unpack_format, raw_word)[0]

    def _read_raw_word(self):
        return self._data.read(self._word_size)

    def _read_word(self):
        raw_word = self._read_raw_word()
        if raw_word:
            return self._unpack_word(raw_word)
        return None

    def _get_offset(self):
        return self._data.tell() + self._adjustment

    def _process_allocation(self, size):
        offset = self._get_offset()
        print(f'\nAllocation at {offset:08x}\nSize: {size}\nData:')
        decoded = ""
        while size > 0 and ((raw_data := self._read_raw_word()) is not None):
            value = self._unpack_word(raw_data)
            print(f'{offset:016x}: {value:016x}')
            decoded = decoded + raw_data.decode('ascii', 'ignore')
            size = size - self._word_size
            offset = self._get_offset()
        print("String: {}".format(decoded))

    def _process_free(self, size):
        offset = self._get_offset()
        print(f'\nFree at {offset:08x}. {size} bytes')
        while size > 0:
            print(f"{offset:08x}: Free")
            offset += self._word_size
            size = size - self._word_size

    def process(self):
        self._data.seek(self._word_size, 0)
        while (value := self._read_word()) is not None:
            if value & 0x1 == 1:
                allocated = True
            else:
                allocated = False
            count = value & (~0x3)
            count -= self._word_size

            # The processing functions aren't required to read all of the data
            # so we save away where we need to seek to for the next chunk.
            next_offset = self._data.tell() + count
            if allocated:
                self._process_allocation(count)
            else:
                self._process_free(count)
            self._data.seek(next_offset, 0)


class HeapStatDumper(HeapDumper):
    def __init__(self, args):
        self._allocated_size = 0
        self._free_size = 0
        self._allocated_count = 0
        self._free_count = 0
        self._allocated_chunk_sizes = {}
        self._free_chunk_sizes = {}
        super().__init__(args)

    def _process_allocation(self, size):
        self._allocated_size += size
        self._allocated_count += 1
        if size in self._allocated_chunk_sizes:
            self._allocated_chunk_sizes[size] += 1
        else:
            self._allocated_chunk_sizes[size] = 1

    def _process_free(self, size):
        self._free_size += size
        self._free_count += 1
        if size in self._free_chunk_sizes:
            self._free_chunk_sizes[size] += 1
        else:
            self._free_chunk_sizes[size] = 1

    def print_stats(self):
        alloc_size = humanize.naturalsize(self._allocated_size)
        alloc_count = humanize.intcomma(self._allocated_count)
        print(f"Allocations: {alloc_size} in {alloc_count} allocations")
        free_size = humanize.naturalsize(self._free_size)
        free_count = humanize.intcomma(self._free_count)
        print(f"Free chunks: {free_size} in {free_count} chunks")
        sorted_allocs = sorted(self._allocated_chunk_sizes.items(),
                               key=lambda item: item[1], reverse=True)
        print("Top 5 allocated chunk sizes:")
        index = 1
        for entry in sorted_allocs[:5]:
            size = humanize.naturalsize(entry[0])
            count = humanize.intcomma(entry[1])
            print(f"  {index}: Chunk size: {size} Count: {count}")
            index += 1
        sorted_frees = sorted(self._free_chunk_sizes.items(),
                              key=lambda item: item[1], reverse=True)
        print("Top 5 free chunk sizes:")
        index = 1
        for entry in sorted_frees[:5]:
            size = humanize.naturalsize(entry[0])
            count = humanize.intcomma(entry[1])
            print(f"  {index}: Chunk size: {size} Count: {count}")
            index += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='Heapdump',
            description='Dump formatted heap information')
    parser.add_argument('filename')
    parser.add_argument('-a', '--adjustment', type=lambda x: int(x, 0),
                        default=0)
    parser.add_argument('-w', '--word-size', type=int, default=8)
    parser.add_argument('-s', '--stats', action='store_true')
    args = parser.parse_args()

    if args.stats:
        dumper = HeapStatDumper(args)
    else:
        dumper = HeapDumper(args)
    dumper.process()
    if args.stats:
        dumper.print_stats()
