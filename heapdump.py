#!/usr/bin/env python3
import argparse
import struct

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
    parser = argparse.ArgumentParser(
            prog='Heapdump',
            description='Dump formatted heap information')
    parser.add_argument('filename')
    parser.add_argument('-a', '--adjustment', type=lambda x: int(x, 0), default=0)
    args = parser.parse_args()

    extract_file(args.filename, args.adjustment)
