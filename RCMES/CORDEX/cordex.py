import os
import sys
import subprocess
import jinja2
from metadata_extractor import CORDEXMetadataExtractor, obs4MIPSMetadataExtractor

# These should be modified. TODO: domains can also be made into separate group
# CORDEX domain

user_input = sys.argv[1:]
if len(user_input) == 4:
    domain, workdir, obs_dir, models_dir = user_input[:]
else:
    domain = 'NAM-44'

    # The output directory
    workdir = os.getcwd()+'/'+domain+'_analysis'

    # Location of osb4Mips files
    obs_dir = '/proj3/data/obs4mips'

    # Location of CORDEX files
    models_dir = '/proj3/data/CORDEX/{domain}/*'.format(domain=domain)

# Extract metadata from model and obs files, pairing up files with the same
# variables for separate evaluations
obs_extractor = obs4MIPSMetadataExtractor(obs_dir)
models_extractor = CORDEXMetadataExtractor(models_dir)
groups = obs_extractor.group(models_extractor, 'variable')

# Configuration file template, to be rendered repeatedly for each evaluation
# run
env =  jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'),
                          trim_blocks=True, lstrip_blocks=True)
t = env.get_template('CORDEX.yaml.template')

# Each group represents a single evaluation. Repeat the evaluation for
# three seasons: Summer, Winter, and Annual.
seasons = ['annual', 'winter', 'summer']
errored = []
for group in groups:
    obs_info, models_info = group
    instrument = obs_info['instrument']
    variable = obs_info['variable']
    for season in seasons:
        configfile_basename = '_'.join([domain, instrument, variable, season]) + '.yaml'
        configfile_path = os.path.join(workdir, domain, instrument,
                                       variable, season)
        if not os.path.exists(configfile_path):
            os.makedirs(configfile_path)
        configfile_path = os.path.join(configfile_path, configfile_basename)
        with open(configfile_path, 'w') as configfile:
            configfile.write(t.render(obs_info=obs_info, models_info=models_info,
                                      season=season, output_dir=workdir))

        # TODO: Do this in parallel. Will change this once this approach
        # is well tested.
        code = subprocess.call([sys.executable, '../run_RCMES.py', configfile_path])
        if code:
            errored.append(configfile_path)

print("All runs done. The following ended with an error: {}".format(errored))
