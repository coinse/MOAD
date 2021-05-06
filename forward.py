from dm.program_space import ProgramSpace
# from dm.factor.factor import get_factor_manager
# from dm.response_manager import ResponseManager
# from dm.doe.doe import get_doe_manager
from dm.log import create_root_logger, add_outputpath_log_handler
import argparse
import logging
import os
import numpy as np
import glob


create_root_logger()
logger = logging.getLogger()


FILENAME = {
    'mbe': 'mbe.c',
}


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--proj_name', help='Target project path', required=True)
    parser.add_argument(
        '-d', '--doe_strategy', help='Design of experiment strategy')
    parser.add_argument(
        '-i', '--inference', help='Inference algorithm',
        choices=['once_success', 'logistic', 'simple_bayes'], required=True)
    parser.add_argument('-c', '--cached', help='Use existing factors in the \
        output of the model.py', action='store_true', default=True)
    parser.add_argument(
        '-o', '--output_path', help='Output(model) saving folder name',
        default=None)
    parser.add_argument('--seed', help='Random seed', default=None)
    return parser


def get_data(data_dir_path, sub_sample: float):
    data_path_list = sorted(list(filter(lambda x: os.path.basename(
        x).startswith('expr'), glob.glob(os.path.join(data_dir_path, '*')))))
    logger.debug('data_path_list: {}'.format(data_path_list))
    data_path = data_path_list[0]
    with open(data_path) as f:
        logger.info(f.readline().lstrip('# ').rstrip())
    data = np.genfromtxt(data_path, delimiter=',', skip_header=1).astype(bool)

    for data_path in data_path_list[1:]:
        with open(data_path) as f:
            logger.info(f.readline().lstrip('# ').rstrip())
        data = np.vstack((data, np.genfromtxt(
            data_path, delimiter=',', skip_header=1).astype(bool)))
    logger.info('expr_cnt: {}'.format(len(data)))
    sample_size = int(len(data) * sub_sample)
    logger.info('sub_sample: {}, sample_size: {}'.format(sub_sample,
                                                         sample_size))
    data = data[np.random.choice(len(data), sample_size, replace=False), :]
    return data


def get_criteria(proj_name):
    proj_path = os.path.join('output', 'original', proj_name)
    criteria_path = os.path.join(proj_path, 'scripts/test/criteria')
    if os.path.exists(criteria_path):
        with open(criteria_path) as f:
            logger.info('Criteria path loaded (path:{})'.format(criteria_path))
            return list(map(str.rstrip, f.readlines()))
    else:
        logger.info('No criteria path exists.')


def get_moad_uc_matrix(proj_name, doe_strategy, inference,
                       cached, output_path):
    logger.info('get moad uc_matrix.')
    uc_matrix = []
    criteria_list = get_criteria(proj_name)
    if cached:
        for i in range(1, len(criteria_list) + 1):
            factor_path = os.path.join('output', 'model', proj_name,
                                       doe_strategy, inference,
                                       str(i), 'factor')
            logger.debug('factor_path: {}'.format(factor_path))
            if not os.path.exists(factor_path):
                err_msg = 'No factor path: {}'.format(factor_path)
                logger.error(err_msg)
                raise Exception(err_msg)
            with open(factor_path) as f:
                factor = list(
                    map(int,
                        f.read().lstrip('[').rstrip(']').split(', ')))
                logger.debug('factor({:3d}): {}'.format(i, factor))
            uc_matrix.append(factor)
    else:
        raise Exception('Not implemented yet.')
    uc_matrix = np.invert(np.array(uc_matrix, dtype=np.bool))
    uc_matrix_path = os.path.join(output_path, 'uc_matrix.csv')
    with open(uc_matrix_path, 'w') as f:
        np.savetxt(f, uc_matrix, fmt='%d', delimiter=',')
    logger.info('moad uc_matrix save(path: {})'.format(uc_matrix_path))
    return uc_matrix


def get_torbs_uc_matrix(proj_name, cached, factor_size):
    logger.info('get orbs uc_matrix.')
    output_path = os.path.join('output', 'forward', args.proj_name, 'orbs')
    uc_matrix_path = os.path.join(output_path, 'uc_matrix.csv')
    if os.path.exists(uc_matrix_path):
        with open(uc_matrix_path) as f:
            uc_matrix = np.genfromtxt(f, dtype=int, delimiter=',')
    else:
        os.makedirs(os.path.dirname(uc_matrix_path), exist_ok=True)
        uc_matrix = []
        criteria_list = get_criteria(proj_name)
        if cached:
            for i in range(1, len(criteria_list) + 1):
                factor_path = os.path.join('output', 'orbs', proj_name,
                                           str(i), 'work', 'factor')
                logger.debug('factor_path: {}'.format(factor_path))
                if os.path.exists(factor_path):
                    with open(factor_path) as f:
                        factor = list(
                            map(int,
                                f.read().lstrip('[').rstrip(']').split(', ')))
                    logger.debug('factor({:3d}): {}'.format(i, factor))
                else:
                    oracle_sanity_path = os.path.join('output', 'orbs',
                                                      proj_name, str(i),
                                                      'work', 'logs',
                                                      'oracle_sanity.log')
                    if os.path.exists(oracle_sanity_path):
                        logger.debug('ORBS sanity check failed.')
                        logger.debug(
                            'Assume the criterion depends on all units.')
                        factor = None  # later will be converted to zero vector
                    else:
                        err_msg = 'No factor path: {}'.format(factor_path)
                        logger.error(err_msg)
                        raise Exception(err_msg)
                uc_matrix.append(factor)
        else:
            raise Exception('Not implemented yet.')
        uc_matrix = [x if x else [0] * factor_size for x in uc_matrix]
        uc_matrix = np.invert(np.array(uc_matrix, dtype=np.bool))
        with open(uc_matrix_path, 'w') as f:
            np.savetxt(f, uc_matrix, fmt='%d', delimiter=',')
        logger.info('orbs uc_matrix save(path: {})'.format(uc_matrix_path))
    return uc_matrix


def get_uc_mapping(proj_name: str, unit_dir: str, factor_size: int):
    ret = {}
    for i in range(factor_size):
        unit_code_path = os.path.join(
            unit_dir, FILENAME[proj_name] + '_{}.c'.format(i))
        with open(unit_code_path) as f:
            log_node_list = list(
                filter(lambda x: x.startswith('// log'), f.readlines()))
        criteria_list = []
        for log_node_str in log_node_list:
            splitted = log_node_str.split(', ')
            line, col, name = splitted[-4], splitted[-3], splitted[-1].rstrip(
                ');\n')
            criteria_list.append(':'.join(['ORBS', line, col, name]))
        criteria_list = list(set(criteria_list))
        ret[i] = criteria_list
    return ret


def uc_to_uu(proj_name: str, unit_dir: str, uc_matrix: np.array,
             factor_size: int) -> np.array:
    criteria_list = get_criteria(proj_name)
    uc_mapping = get_uc_mapping(proj_name, unit_dir, factor_size)
    uu_matrix = []
    for i in range(factor_size):
        uu_matrix.append([False] * factor_size)
        uu_matrix[i][i] = True
        if len(uc_mapping[i]):
            for criteria in uc_mapping[i]:
                criteria_idx = criteria_list.index(criteria)
                affecting_factor = uc_matrix[:, criteria_idx]
                uu_matrix[i] = np.logical_or(uu_matrix[i], affecting_factor)
    uu_matrix = np.array(uu_matrix)
    return uu_matrix


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    if args.output_path is None:
        output_path = os.path.join('output', 'forward', args.proj_name,
                                   args.doe_strategy, args.inference)
    else:
        output_path = args.output_path
    program_space = ProgramSpace(args.proj_name)
    program_space.base_work_dir = output_path
    add_outputpath_log_handler(output_path, logger)
    logger.info('output_path: {}'.format(output_path))

    unit_dir = os.path.join('output', 'unit', args.proj_name, 'unit', 'src')
    factor_size = len(glob.glob(os.path.join(unit_dir, '*')))
    moad_uc_matrix = get_moad_uc_matrix(args.proj_name, args.doe_strategy,
                                        args.inference, args.cached,
                                        output_path).T
    orbs_uc_matrix = get_torbs_uc_matrix(args.proj_name, args.cached,
                                         factor_size).T
    if moad_uc_matrix.shape != orbs_uc_matrix.shape:
        err_msg = 'different uc_matrix shape: moad:{}, orbs:{}'.format(
            moad_uc_matrix.shape, orbs_uc_matrix.shape)
        logger.error(err_msg)
        raise Exception(err_msg)

    uu_matrix_path = os.path.join(output_path, 'uu_matrix.csv')
    moad_uu_matrix = uc_to_uu(args.proj_name, unit_dir,
                              moad_uc_matrix, factor_size)
    with open(uu_matrix_path, 'w') as f:
        np.savetxt(f, moad_uu_matrix, fmt='%d', delimiter=',')
    logger.info('moad uu_matrix save(path: {})'.format(uu_matrix_path))

    logger.info('Calculate diff.')
    diff = []
    for i in range(len(moad_uc_matrix)):
        moad_forward = moad_uc_matrix[i]
        orbs_forward = orbs_uc_matrix[i]
        xor = np.logical_xor(moad_forward, orbs_forward).astype(int)
        logger.debug('    xor({:3d}): {}'.format(i, list(xor)))
        diff.append(np.sum(xor))
    diff_path = os.path.join(output_path, 'diff.csv')
    with open(diff_path, 'w') as f:
        np.savetxt(f, diff, fmt='%d', delimiter=',')
    logger.info('save diff(path: {})'.format(diff_path))
