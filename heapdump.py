#!/usr/bin/env python3
import struct
import sys

def extract_file(filename, adjustment):
    data = open(filename, 'rb')
    word_size = 8
    data.seek(word_size)
    raw_data = data.read(word_size)
    while raw_data:
        value = struct.unpack('<Q', raw_data)[0]
        count = value & (~0x7)
        count -= word_size
        position = data.tell()
        data.seek(position + count)
        raw_data = data.read(word_size)
        if len(raw_data) < word_size:
            return
        value = struct.unpack('<Q', raw_data)[0]
        if value & 0x1 == 1:
            allocated = True
        else:
            allocated = False
        data.seek(position)
        if allocated:
            print('\nAllocation at {:016x}\nSize: {}\nData:'.format(data.tell() + adjustment, count))
            decoded = ""
            while count > 0:
                raw_data = data.read(word_size)
                if len(raw_data) < word_size:
                    return
                value = struct.unpack('<Q', raw_data)[0]
                print('{:016x}: {:016x}'.format(data.tell() - word_size + adjustment, value))
                decoded = decoded + raw_data.decode('ascii', 'ignore')
                count = count - word_size
            print("String: {}".format(decoded))
        else:
            offset = data.tell() + adjustment
            raw_data = data.read(word_size)
            fd = struct.unpack('<Q', raw_data)[0]
            raw_data = data.read(word_size)
            bk = struct.unpack('<Q', raw_data)[0]
            raw_data = data.read(word_size)
            fd_nextsize = struct.unpack('<Q', raw_data)[0]
            raw_data = data.read(word_size)
            bk_nextsize = struct.unpack('<Q', raw_data)[0]
            free_count = count - word_size*5
            data.seek(free_count, 1)
            print('\nFree at {:08x}. {} bytes'.format(data.tell() + adjustment, count))
            print('fd = {:08x}, bk = {:08x}, fd_nextsize = {:08x}, bk_nextsize = {:08x}'.format(fd, bk, fd_nextsize, bk_nextsize))
            while free_count > 0:
                print("{:08x}: Free".format(offset))
                offset += word_size
                free_count -= word_size
            raw_data = data.read(word_size)
            value = struct.unpack('<Q', raw_data)[0]
            if count != value - word_size:
                print("Possible corruption: chunk size mismatch actual: {} expected: {}".format(value, count + word_size))
        raw_data = data.read(word_size)

if __name__ == "__main__":
    adjustment = 0
    if len(sys.argv) > 2:
        adjustment = int(sys.argv[2], 0)
    extract_file(sys.argv[1], adjustment)
