import os

# Defaults
HOME = os.path.expanduser("~")
DIR_IN = os.path.join(HOME, "AppData", "Local", "PokerTracker 4", "Processed", "PokerStars")
FILE_IN = os.path.join(HOME, "Personal", "Hands.txt")
FILE_OUT = os.path.join("C:\\", "Laurent", "Personalia", "Poker", "Hands_NoCO.txt")


class PSNoCashOut:
    @staticmethod
    def extract_hand_id(line):
        # PokerStars Zoom Hand #205218686091:  Hold'em No Limit ($0.01/$0.02) - 2019/10/15 16:58:02 ET
        start = line.index('#') + 1  # Let program crash if '#' not found
        nb = ''
        for c in line[start:]:
            if c.isdecimal():
                nb += c
            else:
                break

        return int(nb)

    @staticmethod
    def _dump_hand(hand_buffer, file_out):
        with open(file_out, 'a', encoding='utf-8') as fout:
            for line in hand_buffer:
                fout.write(line + '\n')
            fout.write('\n')

    @classmethod
    def collect_processed_hands(cls, file):
        # First, collect hands that were already processed
        processed_hands = set()
        if os.path.isfile(file):
            with open(file) as fin:
                for line in fin:
                    if line.startswith("PokerStars "):
                        processed_hands.add(cls.extract_hand_id(line))
        return processed_hands

    @classmethod
    def process_dir(cls, dir_in=DIR_IN, file_out=FILE_OUT, b_recursive=True, b_write_all=False):
        for entry in os.listdir(dir_in):
            full_path = os.path.join(dir_in, entry)
            if os.path.isdir(full_path) and b_recursive:
                cls.process_dir(full_path, file_out, b_recursive, b_write_all)
            elif full_path.endswith('.txt'):
                cls.process_file(full_path, file_out, b_write_all)

    @classmethod
    def process_file(cls, file_in=FILE_IN, file_out=FILE_OUT, b_write_all=False):
        print(f"Processing file [{file_in}]...")

        processed_hands = cls.collect_processed_hands(file_out)

        hand_buffer = []
        hand_id = -1
        prev_hand_id = -1
        b_in_hand = False
        b_cashed_out = False
        hands_converted = 0
        hands_written = 0

        at_hand = 0
        with open(file_in, 'r', encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                # Write buffered hand to output if necessary, and reset buffer
                if not b_in_hand:
                    if line.startswith("PokerStars "):
                        at_hand += 1
                        print(f'\rAt hand {at_hand}...', end='')

                        # Write buffered hand if requested
                        if hand_buffer and (hand_id not in processed_hands) and (b_write_all or b_cashed_out):
                            cls._dump_hand(hand_buffer, file_out)
                            hands_written += 1

                        hand_buffer = []
                        hand_id = cls.extract_hand_id(line)
                        hand_buffer.append(line)
                        b_in_hand = True
                        b_cashed_out = False
                else:
                    # First empty line after start of hand marks end of hand
                    if not line:
                        b_in_hand = False

                    if 'cashed out the hand' in line:
                        if prev_hand_id != hand_id:
                            hands_converted += 1
                        prev_hand_id = hand_id
                        b_cashed_out = True
                        continue
                    elif line.endswith(' (cashed out).'):
                        line = line[:-14]
                    elif line.endswith(' (pot not awarded as player cashed out)'):
                        line = line[:-39]
                    hand_buffer.append(line)

        # Don't forget to process last hand!
        if hand_buffer and hand_id not in processed_hands and (b_write_all or b_cashed_out):
            cls._dump_hand(hand_buffer, file_out)
            hands_written += 1

        print('\n')
        print(f'Hands converted: {hands_converted}')
        print(f'Hands written  : {hands_written}')


if __name__ == '__main__':
    ps_conv = PSNoCashOut()
    ps_conv.process_dir()
    # ps_conv.process_file(file_in=os.path.join(HOME, "Personal", "Hands2.txt"), b_write_all=True)
