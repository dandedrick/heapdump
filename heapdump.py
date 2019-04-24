#!/usr/bin/env python3
import struct
import sys

def extract_file(filename, adjustment):
    data = open(filename, 'rb')
    data.seek(4)
    raw_data = data.read(4)
    while raw_data:
        value = struct.unpack('<I', raw_data)[0]
        if value & 0x1 == 1:
            allocated = True
        else:
            allocated = False
        count = value & (~0x3)
        count -= 4
        if allocated:
            print('\nAllocation at {:08x}\nSize: {}\nData:'.format(data.tell() + adjustment, count))
            decoded = ""
            while count > 0:
                raw_data = data.read(4)
                if len(raw_data) < 4:
                    return
                value = struct.unpack('<I', raw_data)[0]
                print('{:08x}: {:08x}'.format(data.tell() - 4 + adjustment, value))
                decoded = decoded + raw_data.decode('ascii', 'ignore')
                count = count - 4
            print("String: {}".format(decoded))
        else:
            offset = data.tell() + adjustment
            data.seek(count, 1)
            print('\nFree at {:08x}. {} bytes'.format(data.tell() + adjustment, count))
            while count > 0:
                print("{:08x}: Free".format(offset))
                offset += 4
                count = count - 4;
        raw_data = data.read(4)

if __name__ == "__main__":
    adjustment = 0
    if len(sys.argv) > 2:
        adjustment = int(sys.argv[2], 0)
    extract_file(sys.argv[1], adjustment)
