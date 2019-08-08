import sys
from time import sleep

from typing import Optional, List

from ask_wrapper.backend import BaseBackend, CLIBackend
from ask_wrapper.cache import save_dict
from ask_wrapper.consts import Locale, DEFAULT_STAGE, STAGES


class Ask:
    def __init__(self, backend: Optional[BaseBackend] = None, stage: str = DEFAULT_STAGE, root_dir=''):
        self._skill_id: Optional[str] = None
        self._skill_name: Optional[str] = None
        self._isp_id: Optional[str] = None
        self._stage: str = stage
        self._root_dir: str = root_dir
        if backend is None:
            backend = CLIBackend()
        self._backend: BaseBackend = backend

    @property
    def skill_id(self):
        return self._skill_id

    @property
    def stage(self):
        return self._stage

    def set_stage(self, stage: str):
        assert stage in STAGES
        self._stage = stage

    def ask_api(self, command: List[str], drop_skill_id=False, drop_stage=False, is_json=True, stage: str=None):
        full_command = ['ask', 'api'] + command
        if self._skill_id and not drop_skill_id:
            full_command += ['--skill-id', self._skill_id]

        if not drop_stage:
            if stage:
                full_command += ['--stage', stage]
            elif self._stage:
                full_command += ['--stage', self._stage]

        return self._backend.cmd_and_parse(full_command, is_json=is_json)

    def _get_skill_id(self, skill_name: str):
        skills = self.list_skills()
        other_skills = set()
        for skill in skills:
            if skill_name in skill['nameByLocale'].values():
                return skill['skillId']
            other_skills |= set(skill['nameByLocale'].values())

        raise KeyError(f'Could not find skill {skill_name} in {", ".join(other_skills)}')

    def set_skill_by_name(self, skill_name: str):
        self._skill_id = self._get_skill_id(skill_name)
        self._skill_name = skill_name
        return self._skill_id

    def set_skill_by_id(self, skill_id: str):
        self._skill_id = skill_id

    def list_skills(self):
        skills_list = self.ask_api(['list-skills'], drop_stage=True).get('skills', [])
        return skills_list

    def get_skill(self, stage: str = None):
        assert self._skill_id is not None, 'Skill not set'
        return self.ask_api(['get-skill'], stage=stage)

    def get_skill_status(self):
        return self.ask_api(['get-skill-status'], drop_stage=True)

    def _get_skill_file_name(self):
        if self._skill_name:
            return self._skill_name
        else:
            return self._skill_id

    def update_skill(self, skill: dict):
        assert self._skill_id is not None, 'Skill not set'

        file_name = self._get_skill_file_name()

        return self.ask_api([
            'update-skill',
            '--file', save_dict(skill, f'skills/{file_name}', self._root_dir)
        ], is_json=False)

    def get_model(self, locale: Locale):
        return self.ask_api(['get-model', '--locale', locale.value])

    def set_model(self, locale: Locale, model: dict):
        assert self._skill_id is not None, 'Skill not set'

        skill_dir_name = self._get_skill_file_name()

        return self.ask_api([
            'update-model',
            '--locale', locale.value,
            '--file', save_dict(model, f'models/{skill_dir_name}/{locale.value}', self._root_dir)
        ], is_json=False)

    def wait_until_models_built(self, locales: List[Locale], print_progress=False):
        if print_progress:
            print('Waiting for models build completion... ', end='')
            sys.stdout.flush()
        is_locale_built = {l.value: False for l in locales}
        while not all(is_locale_built.values()):
            if print_progress:
                print(str(100 * sum(is_locale_built.values()) / len(locales)) + '%', end='')
                sys.stdout.flush()

            resp_obj = self.get_skill_status()
            for locale in locales:
                is_locale_built[locale.value] = \
                    resp_obj['interactionModel'][locale.value]['lastUpdateRequest']['status'] != 'IN_PROGRESS'

            if not all(is_locale_built.values()):
                sleep(1)

        if print_progress:
            print('100%')

    def submit(self):
        assert self._skill_id is not None, 'Skill not set'
        self.ask_api(['submit'], drop_stage=True, is_json=False)

    def list_isp_for_skill(self):
        assert self._skill_id is not None, 'Skill not set'
        return self.ask_api(['list-isp-for-skill'])

    def list_isp_id_for_skill(self):
        isp_list = self.list_isp_for_skill()
        return [product.get('productId') for product in isp_list]

    def _ask_api_isp_id(self, command, is_json=True):
        assert self._isp_id is not None, 'ISP id not set'
        return self.ask_api(command + ['--isp-id', self._isp_id], drop_skill_id=True, is_json=is_json)

    def set_isp_id(self, isp_id: str) -> dict:
        self._isp_id = isp_id
        return self._ask_api_isp_id(['get-isp'])

    def update_isp(self, product: dict):
        return self._ask_api_isp_id([
            'update-isp',
            '--file', product.save()
        ], is_json=False)
