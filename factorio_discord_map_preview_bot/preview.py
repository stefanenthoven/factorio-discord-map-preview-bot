import asyncio
import subprocess
import re
from collections import OrderedDict


def entity_count(name, log_string):
    m = re.search(r'Total {}: ([0-9,]+)'.format(name), log_string)
    if m:
        return float(m.group(1))
    else:
        return '???'


class SimplePreview:
    def __init__(self, factorio_binary):
        self.binary = factorio_binary
        self.lock = asyncio.Lock()
        self.entities = ['iron-ore', 'copper-ore', 'coal']

    async def __call__(self, map_gen_settings_path, image_path, log_path):
        with await self.lock:
            with open(log_path, 'w') as log_file:
                process = await asyncio.create_subprocess_exec(
                    self.binary,
                    '--generate-map-preview', image_path,
                    '--map-gen-settings', map_gen_settings_path,
                    '--report-quantities', ','.join(self.entities),
                    stdout=log_file, stderr=subprocess.STDOUT
                )
                # TODO use wait_for with timeout
                await process.wait()

            with open(log_path, 'r') as log_file:
                log_string = log_file.read()

            entities = OrderedDict(
                (name, entity_count(name, log_string))
                for name in self.entities
            )
            with open(log_path, 'w') as log_file:
                log_file.write(log_string)
            return entities