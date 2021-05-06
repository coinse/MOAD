from .line_factor_manager import LineFactorManager
from .music_factor_manager import MusicFactorManager
from .srcml_factor_manager import SrcMLFactorManager


def get_factor_manager(factor_level, proj_name, program_space):
    if factor_level == 'line':
        return LineFactorManager(program_space)
    elif factor_level == 'music':
        return MusicFactorManager(proj_name, program_space)
    elif factor_level == 'srcml':
        return SrcMLFactorManager(proj_name, program_space)
    else:
        raise Exception('Invalid factor_level: {}'.format(factor_level))
