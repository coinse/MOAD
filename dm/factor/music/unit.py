from functools import total_ordering


@total_ordering
class MusicPosition:
    def __init__(self, line, col):
        self._line = line
        self._col = col

    @property
    def line(self):
        return self._line

    @property
    def col(self):
        return self._col

    def __eq__(self, other):
        return isinstance(other, MusicPosition) and (self.line, self.col) == (other.line, other.col)

    def __lt__(self, other):
        # print('lt', self, other)
        if self.line < other.line:
            return True
        elif self.line == other.line:
            return self.col < other.col
        else:
            return False

    def __repr__(self):
        return "{}:{}".format(self.line, self.col)

    @staticmethod
    def parse_str(s):
        splitted_str = s.split(':')
        return MusicPosition(int(splitted_str[0]), int(splitted_str[1]))


class MusicRange:
    def __init__(self, start, end):
        if end < start:
            raise Exception('start:{} > end:{}'.format(start, end))
        self._start = start
        self._end = end

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def __eq__(self, other):
        return isinstance(other, MusicRange), self._start == other._start and self._end == other._end

    def __add__(self, other):
        start = self.start if self.start < other.start else other.start
        end = self.end if self.end > other.end else other.end
        return MusicRange(start, end)

    def __repr__(self):
        return "[{} - {}]".format(self.start, self.end)

    def __hash__(self):
        return hash(self.__repr__())


    def overlap(self, other):
        front, back = (self, other) if self.start < other.start else (other, self)
        return front.end > back.start

    def contains(self, other):
        return self.start <= other.start and self.end >= other.end

    @staticmethod
    def parse_str(s):
        splitted_str = s.lstrip('[').rstrip(']').split(' - ')
        return MusicRange(MusicPosition.parse_str(splitted_str[0]),
                          MusicPosition.parse_str(splitted_str[1]))


def merge_deletion_range(deletion_range_list):
    merged_deletion_range_list = []
    for deletion_range in sorted(deletion_range_list, key=lambda x: x.start):
        merged = False
        for merged_range in merged_deletion_range_list:
            if merged_range.overlap(deletion_range):
                merged_deletion_range_list.remove(merged_range)
                merged_deletion_range_list.append(merged_range + deletion_range)
                merged = True
                break
        if not merged:
            merged_deletion_range_list.append(deletion_range)
    return merged_deletion_range_list
