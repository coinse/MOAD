import os
import shutil
import logging
from .factor_manager import FactorManager
from .music.unit import MusicRange, merge_deletion_range


SOURCE_PATH = {
    'mbe': 'mbe.c',
    'printtokens': 'source/print_tokens.c'
}
root_logger = logging.getLogger()


def delete_range(work_dir, filename, deletion_range):
    lines = []
    with open(os.path.join(work_dir, filename)) as f:
        lines = f.readlines()

    line_range = list(range(deletion_range.start.line - 1, deletion_range.end.line))

    if len(line_range) == 0:
        raise Exception('Invalid position:{}'.format(deletion_range))
    elif len(line_range) == 1:
        # one line
        target_line = lines[line_range[0]]
        wo_blank_modified_line = target_line[:deletion_range.start.col - 1] + ';' + target_line[deletion_range.end.col - 1:]
        lines[line_range[0]] = target_line[:deletion_range.start.col - 1] + (
                ' ' * (len(target_line) - len(wo_blank_modified_line))) + ';' + target_line[deletion_range.end.col - 1:]
        assert(len(target_line) == len(lines[line_range[0]]))
    else:
        # first line
        first_line = lines[line_range[0]]
        lines[line_range[0]] = first_line[:deletion_range.start.col - 1] + ';\n'
        for middle_line_idx in line_range[1:-1]:
            lines[middle_line_idx] = '\n'
        last_line = lines[line_range[-1]]
        n_tab = 0
        for idx in range(len(last_line)):
            if last_line[idx] != '\t':
                break
            n_tab += 1
        if deletion_range.end.col > n_tab:
            wo_blank_modified_line = last_line[deletion_range.end.col - 1:]
            lines[line_range[-1]] = ('\t' * n_tab) + \
                                    (' ' * (len(last_line) - n_tab - len(wo_blank_modified_line))) + \
                                    last_line[deletion_range.end.col - 1:]
        assert(len(last_line) == len(lines[line_range[-1]]))

    with open(os.path.join(work_dir, filename), 'w') as f:
        f.write(''.join(lines))


class MusicFactorManager(FactorManager):
    def __init__(self, project_name, program_space):
        super().__init__(program_space)
        self._factor = []

        work_dir = os.path.join('output', 'unit', project_name)
        unit_gen_dir = os.path.join(work_dir, 'unit_gen')

        for filename in self._program_space.files:
            unit_output_dir = os.path.join(unit_gen_dir, os.path.dirname(
                filename))
            deletion_range_list = []
            for idx in range(len(os.listdir(unit_output_dir))):
                with open(os.path.join(unit_output_dir,
                                       os.path.basename(filename)[
                                       :-2] + '_unit_{}'.format(idx + 1))) as g:
                    deletion_range_list.append(MusicRange.parse_str(
                        g.readline().rstrip()))
            self._factor += list(map(lambda deletion_range: (filename,
                                                             deletion_range),
                                     deletion_range_list))

        self._size = len(self._factor)

        # Debug
        root_logger.debug('self._size = {}'.format(self._size))
        root_logger.debug('self._factor[0] = {}'.format(self._factor[0]))

    def create_program(self, factor, iter_cnt, save_flag, only_code=False):
        work_dir = super().create_program(factor, iter_cnt, save_flag,
                                          only_code)

        deletion_factor = [self._factor[i]
                           for i in range(self._size) if factor[i] == 1]

        for filename in self._program_space.files:
            deletion_range_list = list(map(lambda x: x[1], filter(lambda x: x[0] == filename, deletion_factor)))
            merged_deletion_range_list = merge_deletion_range(deletion_range_list)

            for deletion_range in merged_deletion_range_list:
                delete_range(work_dir, filename, deletion_range)

            with open(os.path.join(work_dir, filename)) as f:
                root_logger.debug('Filename:{} Code:\n{}'.format(filename, f.read()))

        return work_dir

    def revise_factor(self, factor):
        revised_factor = list(factor)
        deletion_factor = [self._factor[i]
                           for i in range(self._size) if factor[i] == 1]

        for filename, deletion_range in deletion_factor:
            for idx in range(self._size):
                if filename == self._factor[idx][0] and \
                        deletion_range.contains(self._factor[idx][1]):
                    # print(str(deletion_range), 'contains', str(self._factor[
                    #                                                idx][1]))
                    revised_factor[idx] = 1
        # print('factor', factor)
        # print('revise', revised_factor)
        # print()
        return revised_factor

    @property
    def size(self):
        return self._size
