#!/usr/bin/env python3
import argparse
import struct


def extract_file(filename, adjustment, word_size=8):
    match word_size:
        case 4:
            unpack_format = '<I'
        case 8:
            unpack_format = '<Q'
        case _:
            raise NotImplementedError(f"Word size of {word_size} not supported")

    data = open(filename, 'rb')
    data.seek(word_size)
    raw_data = data.read(word_size)
    while raw_data:
        value = struct.unpack(unpack_format, raw_data)[0]
        if value & 0x1 == 1:
            allocated = True
        else:
            allocated = False
        count = value & (~0x3)
        count -= word_size
        if allocated:
            offset = data.tell() + adjustment
            print(f'\nAllocation at {offset:08x}\nSize: {count}\nData:')
            decoded = ""
            while count > 0:
                raw_data = data.read(word_size)
                if len(raw_data) < word_size:
                    return
                value = struct.unpack(unpack_format, raw_data)[0]
                offset = data.tell() - word_size + adjustment
                print(f'{offset:016x}: {value:016x}')
                decoded = decoded + raw_data.decode('ascii', 'ignore')
                count = count - word_size
            print("String: {}".format(decoded))
        else:
            offset = data.tell() + adjustment
            print(f'\nFree at {offset:08x}. {count} bytes')
            data.seek(count, 1)
            while count > 0:
                print(f"{offset:08x}: Free")
                offset += word_size
                count = count - word_size
        raw_data = data.read(word_size)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='Heapdump',
            description='Dump formatted heap information')
    parser.add_argument('filename')
    parser.add_argument('-a', '--adjustment', type=lambda x: int(x, 0),
                        default=0)
    parser.add_argument('-w', '--word-size', type=int, default=8)
    args = parser.parse_args()

    extract_file(args.filename, args.adjustment, args.word_size)
